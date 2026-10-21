"""Motor v2: escenas a pantalla completa con degradados, luces, brillos y profundidad.

Cada escena dibuja el fotograma entero con draw(ctx, t). El motor añade encima la
viñeta, el grano, los subtítulos y la barra de progreso, funde una escena con la
siguiente y genera la pista de sonido (ambiente + efectos).
"""
import math
import random
import re
import subprocess
import wave
from dataclasses import dataclass, field
from typing import Callable

import cairo
import numpy as np

from engine import FONT, FPS, H, W, clamp, ease_in_out, ease_out_back, prog

INK = (0.07, 0.07, 0.10)
YELLOW = (1.0, 0.80, 0.24)
TRANSITION = 0.3


# ---------- color y pintura ----------

def rgba(c, a=None):
    if a is not None:
        return (c[0], c[1], c[2], a)
    return (c[0], c[1], c[2], c[3] if len(c) > 3 else 1.0)


def mix(a, b, f):
    return tuple(x + (y - x) * f for x, y in zip(a, b))


def mul(c, k):
    return tuple(min(1.0, x * k) for x in c[:3])


def linear(x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for off, col in stops:
        g.add_color_stop_rgba(off, *rgba(col))
    return g


def radial(cx, cy, r, stops, r0=0.0, fx=None, fy=None):
    g = cairo.RadialGradient(cx if fx is None else fx, cy if fy is None else fy, r0, cx, cy, r)
    for off, col in stops:
        g.add_color_stop_rgba(off, *rgba(col))
    return g


def source(ctx, src):
    if isinstance(src, cairo.Pattern):
        ctx.set_source(src)
    else:
        ctx.set_source_rgba(*rgba(src))


def path(ctx, pts, close=True):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()


def poly(ctx, pts, src):
    path(ctx, pts)
    source(ctx, src)
    ctx.fill()


def rr(ctx, x, y, w, h, r):
    r = max(0.0, min(r, w / 2, h / 2))
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def fill_rr(ctx, x, y, w, h, r, src):
    rr(ctx, x, y, w, h, r)
    source(ctx, src)
    ctx.fill()


def disc(ctx, x, y, r, src):
    ctx.new_sub_path()
    ctx.arc(x, y, max(r, 0.01), 0, 2 * math.pi)
    source(ctx, src)
    ctx.fill()


def glow(ctx, x, y, r, col, a=1.0, add=False):
    """Halo de luz: degradado radial que se desvanece."""
    if r <= 0 or a <= 0:
        return
    if add:
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
    disc(ctx, x, y, r, radial(x, y, r, [(0, rgba(col, a)), (0.25, rgba(col, a * 0.5)), (1, rgba(col, 0))]))
    if add:
        ctx.restore()


def soft_ellipse(ctx, x, y, rx, ry, col, a):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(rx, ry)
    disc(ctx, 0, 0, 1, radial(0, 0, 1, [(0, rgba(col, a)), (1, rgba(col, 0))]))
    ctx.restore()


def stroke(ctx, pts, col, width, close=False, cap=cairo.LINE_CAP_ROUND):
    path(ctx, pts, close)
    source(ctx, col)
    ctx.set_line_width(width)
    ctx.set_line_cap(cap)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()


def bezier(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        u = i / n
        a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def text(ctx, s, x, y, size, col=(1, 1, 1), weight=cairo.FONT_WEIGHT_BOLD, anchor="center", outline=None, ow=8):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, weight)
    ctx.set_font_size(size)
    ext = ctx.text_extents(s)
    dx = {"center": ext.x_advance / 2, "left": 0, "right": ext.x_advance}[anchor]
    ctx.move_to(x - dx, y + size * 0.36)
    ctx.text_path(s)
    if outline:
        source(ctx, outline)
        ctx.set_line_width(ow)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
    source(ctx, col)
    ctx.fill()


# ---------- piezas comunes ----------

def blurred(ctx, draw_fn, factor=6):
    """Dibuja a baja resolución y escala: desenfoque barato para fondos."""
    small = cairo.ImageSurface(cairo.FORMAT_ARGB32, W // factor, H // factor)
    c2 = cairo.Context(small)
    c2.scale(1 / factor, 1 / factor)
    draw_fn(c2)
    ctx.save()
    ctx.scale(factor, factor)
    ctx.set_source_surface(small, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_BILINEAR)
    ctx.paint()
    ctx.restore()


def badge(ctx, x, y, p, ok=True, r=62):
    s = ease_out_back(p)
    if s <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    col = (0.18, 0.75, 0.42) if ok else (0.95, 0.20, 0.22)
    glow(ctx, 0, 0, r * 2.2, col, 0.5, add=True)
    disc(ctx, 0, 0, r, radial(-r * 0.3, -r * 0.3, r * 1.3, [(0, mul(col, 1.3)), (1, col)]))
    if ok:
        stroke(ctx, [(-r * 0.42, 0), (-r * 0.1, r * 0.32), (r * 0.45, -r * 0.32)], (1, 1, 1), 15)
    else:
        stroke(ctx, [(-r * 0.32, -r * 0.32), (r * 0.32, r * 0.32)], (1, 1, 1), 15)
        stroke(ctx, [(r * 0.32, -r * 0.32), (-r * 0.32, r * 0.32)], (1, 1, 1), 15)
    ctx.restore()


def label(ctx, s, x, y, size=40):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    w = ctx.text_extents(s).x_advance
    fill_rr(ctx, x, y - size * 0.75, w + 44, size * 1.5, size * 0.75, (0, 0, 0, 0.55))
    text(ctx, s, x + 22, y, size, anchor="left")


def cta_button(ctx, t, cx=540, cy=900):
    """Botón de SEGUIR que aparece, se pulsa y deja una onda."""
    press = 1 - 0.08 * math.sin(math.pi * prog(t, 1.3, 0.25))
    p = ease_out_back(prog(t, 0.05, 0.45)) * press
    if p > 0:
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(p, p)
        glow(ctx, 0, 0, 480, (1.0, 0.3, 0.35), 0.45, add=True)
        fill_rr(ctx, -290, -86, 580, 172, 86, linear(0, -86, 0, 86, [(0, (1.0, 0.42, 0.42)), (1, (0.82, 0.12, 0.24))]))
        fill_rr(ctx, -290, -86, 580, 172, 86, linear(0, -86, 0, -10, [(0, (1, 1, 1, 0.28)), (1, (1, 1, 1, 0))]))
        text(ctx, "SEGUIR", 0, 0, 86)
        ctx.restore()
    rp = prog(t, 1.3, 0.8)
    if 0 < rp < 1:
        ctx.arc(cx + 160, cy + 60, 40 + 140 * rp, 0, 2 * math.pi)
        source(ctx, (1, 1, 1, 1 - rp))
        ctx.set_line_width(8)
        ctx.stroke()
    hp = prog(t, 0.5, 0.6)
    if hp > 0:
        hx, hy = cx + 160 + 120 * (1 - ease_in_out(hp)), cy + 60 + 160 * (1 - ease_in_out(hp))
        cursor = [(0, 0), (0, 150), (38, 112), (70, 178), (98, 166), (66, 100), (118, 100)]
        ctx.save()
        ctx.translate(hx, hy)
        path(ctx, cursor)
        source(ctx, (1, 1, 1))
        ctx.fill_preserve()
        source(ctx, (0.05, 0.05, 0.1))
        ctx.set_line_width(8)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()
        ctx.restore()


# ---------- escenas ----------

@dataclass
class Scene:
    text: str
    draw: Callable[[cairo.Context, float], None]
    duration: float = 0.0
    sfx: list = field(default_factory=list)  # [(segundo, "pop" | "chime" | "thunk" | "whoosh" | ...)]
    voice: str = ""  # lo que dice la voz si no coincide con el subtítulo (números, siglas)
    key: str = ""  # palabra clave resaltada (estilo TOP)
    audio: object = field(default=None, repr=False)

    def __post_init__(self):
        self.min_duration = self.duration
        if not self.duration:
            self.duration = max(2.6, 0.29 * len(self.text.split()) + 1.1)


VOICE_LEAD = 0.12


def narrate(scenes, narrator, sr=44100):
    """Genera la locución de cada escena y ajusta su duración a la de la frase."""
    for sc in scenes:
        sc.audio = narrator.say(sc.voice or sc.text)
        gap = getattr(narrator, "gap", 0.45)  # silencio tras la frase antes de la escena siguiente
        sc.duration = max(VOICE_LEAD + len(sc.audio) / sr + gap, sc.min_duration, getattr(narrator, "min_scene", 2.2))


def _syllables(w):
    w = w.lower()
    if any(ch.isdigit() for ch in w):
        return 2 + sum(ch.isdigit() for ch in w)
    if "km/h" in w:
        return 7
    if w.strip(".,;:!?¿¡…") == "km":
        return 4
    return max(1, len(re.findall(r"[aeiouáéíóúü]+", w))) + (0.8 if w[-1:] in ",.;:?!…" else 0)


def word_times(scene, sr=44100):
    words = scene.text.split()
    if scene.audio is None:
        span = min(scene.duration * 0.7, 0.3 * len(words))
        return words, [0.06 + span * i / len(words) for i in range(len(words))]
    weights = [_syllables(w) for w in words]
    total, acc, times = sum(weights), 0.0, []
    for w in weights:
        times.append(VOICE_LEAD + len(scene.audio) / sr * 0.97 * acc / total)
        acc += w
    return words, times


def word_time(scene, needle):
    """Instante en que la voz dice la primera palabra que contiene `needle`."""
    words, times = word_times(scene)
    for w, tt in zip(words, times):
        if needle.lower() in w.lower():
            return tt
    raise ValueError(f"'{needle}' no está en: {scene.text}")


def sfx_time(scene, at):
    """Los efectos pueden ir a un segundo fijo o a una palabra: "@palabra"."""
    return word_time(scene, at[1:]) if isinstance(at, str) else at


# Subtítulos abajo con la palabra que suena resaltada (vídeos antiguos), o arriba, fuera de la
# zona que tapa la interfaz de Reels, en páginas de 2 líneas y con una palabra clave resaltada.
BOTTOM = {"caption_y": 1560, "max_lines": 0, "highlight": "current", "shade": "bottom"}
TOP = {"caption_y": 330, "max_lines": 2, "highlight": "key", "shade": "top"}


def _norm(w):
    return w.strip("¿?¡!.,:;…\"«»").lower()


def _layout(items, ctx, space, max_w=940):
    lines, cur, cur_w = [], [], 0.0
    for i, w in items:
        ww = ctx.text_extents(w).x_advance
        if cur and cur_w + space + ww > max_w:
            lines.append((cur, cur_w))
            cur, cur_w = [], 0.0
        cur_w += (space if cur else 0) + ww
        cur.append((i, w, ww))
    lines.append((cur, cur_w))
    return lines


def _pages(words, ctx, space, n_pages):
    """Reparte la frase en n páginas de longitud parecida, cortando mejor tras una coma o un punto."""
    widths = [ctx.text_extents(w).x_advance + space for w in words]
    total, cuts, acc = sum(widths), [], 0.0
    cum = []
    for wd in widths:
        acc += wd
        cum.append(acc)
    for k in range(1, n_pages):
        target = total * k / n_pages
        best = min(range(len(words) - 1), key=lambda i: abs(cum[i] - target) - (0.12 * total if words[i][-1] in ",.;:?!…" else 0))
        cuts.append(best + 1)
    bounds = [0] + sorted(set(cuts)) + [len(words)]
    return [_layout([(i, words[i]) for i in range(a, b)], ctx, space) for a, b in zip(bounds, bounds[1:]) if b > a]


def caption(ctx, scene, t, style=BOTTOM, size=82):
    y0 = style["caption_y"]
    words, times = word_times(scene)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    space = ctx.text_extents(" ").x_advance
    lines, cur, cur_w = [], [], 0.0
    for i, w in enumerate(words):
        ww = ctx.text_extents(w).x_advance
        if cur and cur_w + space + ww > 940:
            lines.append((cur, cur_w))
            cur, cur_w = [], 0.0
        cur_w += (space if cur else 0) + ww
        cur.append((i, w, ww))
    lines.append((cur, cur_w))
    lh = size * 1.28
    current = max([i for i, wt in enumerate(times) if t >= wt], default=-1)
    if style["max_lines"] and len(lines) > style["max_lines"]:
        pages = _pages(words, ctx, space, math.ceil(len(lines) / style["max_lines"]))
        lines = next((p for p in pages if any(i == current for line, _ in p for i, _, _ in line)), pages[0])
    if style["highlight"] == "key":
        key = _norm(scene.key)
        marked = next((i for i, w in enumerate(words) if key and _norm(w) == key), -1)
    else:
        marked = current
    y = y0 - (len(lines) - 1) * lh / 2
    for line, lw in lines:
        x = W / 2 - lw / 2
        for i, w, ww in line:
            if t >= times[i]:
                s = 0.55 + 0.45 * ease_out_back((t - times[i]) / 0.22)
                ctx.save()
                ctx.translate(x + ww / 2, y)
                ctx.scale(s, s)
                if i == marked:
                    fill_rr(ctx, -ww / 2 - 14, -size * 0.64, ww + 28, size * 1.24, 20, (0, 0, 0, 0.25))
                    fill_rr(ctx, -ww / 2 - 14, -size * 0.68, ww + 28, size * 1.24, 20, YELLOW)
                    text(ctx, w, 0, -size * 0.04, size, col=INK, anchor="center")
                else:
                    text(ctx, w, 0, 4, size, col=(0, 0, 0, 0.35), anchor="center")
                    text(ctx, w, 0, 0, size, col=(1, 1, 1), anchor="center", outline=(0.05, 0.05, 0.1), ow=10)
                ctx.restore()
            x += ww + space
        y += lh


def make_grain():
    rng = np.random.default_rng(3)
    n = 512
    g = np.clip(128 + rng.normal(0, 38, (n, n)), 0, 255).astype(np.uint8)
    bgra = np.dstack([g, g, g, np.full((n, n), 255, np.uint8)])
    data = bytearray(bgra.tobytes())
    surf = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, n, n, n * 4)
    return surf, data


def overlays(ctx, frame, total_t, total, grain, shade="bottom"):
    # viñeta
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(radial(W / 2, H * 0.45, 1150, [(0, (0, 0, 0, 0)), (0.6, (0, 0, 0, 0)), (1, (0, 0, 0, 0.5))]))
    ctx.fill()
    # degradado detrás de los subtítulos para que se lean
    if shade == "top":
        ctx.rectangle(0, 0, W, 640)
        ctx.set_source(linear(0, 0, 0, 640, [(0, (0, 0, 0, 0.6)), (0.6, (0, 0, 0, 0.4)), (1, (0, 0, 0, 0))]))
    else:
        ctx.rectangle(0, 1250, W, H - 1250)
        ctx.set_source(linear(0, 1250, 0, H, [(0, (0, 0, 0, 0)), (0.5, (0, 0, 0, 0.45)), (1, (0, 0, 0, 0.6))]))
    ctx.fill()
    # grano animado
    rnd = random.Random(frame)
    pat = cairo.SurfacePattern(grain)
    pat.set_extend(cairo.EXTEND_REPEAT)
    pat.set_matrix(cairo.Matrix(x0=rnd.randint(0, 511), y0=rnd.randint(0, 511)))
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT)
    ctx.set_source(pat)
    ctx.paint_with_alpha(0.28)
    ctx.restore()
    # barra de progreso
    fill_rr(ctx, 90, 120, W - 180, 10, 5, (1, 1, 1, 0.22))
    fill_rr(ctx, 90, 120, max(10, (W - 180) * total_t / total), 10, 5, YELLOW)


# ---------- sonido ----------

def synth_audio(fname, scenes, total, sr=44100, ambient=True):
    n = int((total + 1) * sr)
    out = np.zeros(n)
    rng = np.random.default_rng(1)

    def add(at, sig):
        s = int(at * sr)
        if s >= n:
            return
        e = min(n, s + len(sig))
        out[s:e] += sig[: e - s]

    def env_exp(L, k):
        return np.exp(-np.arange(L) / sr * k)

    def pop():
        L = int(0.09 * sr)
        tt = np.arange(L) / sr
        f = 900 * np.exp(-tt * 25) + 300
        return 0.18 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 45)

    def whoosh():
        L = int(0.4 * sr)
        noise = np.convolve(rng.normal(0, 1, L), np.ones(40) / 40, mode="same")
        return 0.55 * noise * np.sin(np.linspace(0, np.pi, L)) ** 2

    def tone(f, L, k, amp):
        tt = np.arange(L) / sr
        return amp * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * env_exp(L, k)

    def chime():  # el "ding-dong" de cabina
        L = int(1.6 * sr)
        sig = tone(1046.5, L, 2.6, 0.16)
        sig[int(0.42 * sr):] += tone(830.6, L - int(0.42 * sr), 2.6, 0.16)
        return sig

    def thunk():  # golpe grave de corte de luz
        L = int(0.5 * sr)
        tt = np.arange(L) / sr
        return 0.5 * np.sin(2 * np.pi * (55 + 40 * np.exp(-tt * 20)) * tt) * env_exp(L, 9)

    def riser():  # viento que crece: caída que acelera
        L = int(3.0 * sr)
        tt = np.arange(L) / sr
        noise = rng.normal(0, 1, L)
        lo = np.convolve(noise, np.ones(60) / 60, mode="same")
        hi = noise - np.convolve(noise, np.ones(8) / 8, mode="same")
        k = tt / tt[-1]
        return (0.5 * lo + 0.12 * hi * k) * k ** 1.5 * 0.8

    def tick():
        L = int(0.03 * sr)
        return 0.25 * rng.normal(0, 1, L) * env_exp(L, 180)

    def boom():
        L = int(1.2 * sr)
        tt = np.arange(L) / sr
        return 0.6 * np.sin(2 * np.pi * (38 + 30 * np.exp(-tt * 6)) * tt) * env_exp(L, 3.5)

    kinds = {"pop": pop, "whoosh": whoosh, "chime": chime, "thunk": thunk, "riser": riser, "tick": tick, "boom": boom}
    voiced = any(sc.audio is not None for sc in scenes)
    fx = 0.55 if voiced else 1.0  # con voz, los efectos quedan por debajo
    voice = np.zeros(n)
    start = 0.0
    for i, sc in enumerate(scenes):
        if i:
            add(max(0, start - 0.15), fx * whoosh())
        for at, kind in sc.sfx:
            add(start + sfx_time(sc, at), fx * kinds[kind]())
        if sc.audio is not None:
            s = int((start + VOICE_LEAD) * sr)
            e = min(n, s + len(sc.audio))
            voice[s:e] += sc.audio[: e - s]
        start += sc.duration

    if ambient:  # zumbido de fondo: ruido marrón filtrado, que baja cuando habla la voz
        brown = np.cumsum(rng.normal(0, 1, n))
        brown -= np.convolve(brown, np.ones(4000) / 4000, mode="same")
        brown = np.convolve(brown, np.ones(60) / 60, mode="same")
        brown /= np.max(np.abs(brown)) + 1e-9
        fade = np.clip(np.minimum(np.arange(n) / sr / 1.0, (total - np.arange(n) / sr) / 1.0), 0, 1)
        duck = 1.0
        if voiced:
            env = np.convolve(np.abs(voice), np.ones(sr // 5) / (sr // 5), mode="same")
            duck = 1 - 0.6 * np.clip(env / (env.max() + 1e-9) * 3, 0, 1)
        out += (0.07 if voiced else 0.10) * brown * fade * duck

    out += voice
    out = out / max(1.0, np.max(np.abs(out)) / 0.95)
    with wave.open(fname, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((out * 32767).astype(np.int16).tobytes())


# ---------- render ----------

def draw_scene(ctx, scene, t):
    ctx.save()
    scene.draw(ctx, t)
    ctx.restore()


def frame_surface(scenes, i, t, start, total, frame, grain, style=BOTTOM):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    draw_scene(ctx, scenes[i], t)
    if i > 0 and t < TRANSITION:  # fundido desde la escena anterior
        prev = scenes[i - 1]
        ctx.push_group()
        draw_scene(ctx, prev, prev.duration + t)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - ease_in_out(t / TRANSITION))
    overlays(ctx, frame, start + t, total, grain, style["shade"])
    caption(ctx, scenes[i], t, style)
    return surf


def render(scenes, out_mp4, cover_png=None, cover_at=(0, 1.5), narrator=None, style=BOTTOM):
    if narrator:
        narrate(scenes, narrator)
    grain, _keep = make_grain()
    total = sum(s.duration for s in scenes)
    audio = out_mp4.replace(".mp4", "_sfx.wav")
    synth_audio(audio, scenes, total)
    proc = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", audio,
        "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",  # volumen estándar de Reels/TikTok
        "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", "-movflags", "+faststart", out_mp4,
    ], stdin=subprocess.PIPE)
    frame, start = 0, 0.0
    for i, sc in enumerate(scenes):
        for k in range(int(round(sc.duration * FPS))):
            t = k / FPS
            surf = frame_surface(scenes, i, t, start, total, frame, grain, style)
            proc.stdin.write(bytes(surf.get_data()))
            if cover_png and (i, k) == (cover_at[0], int(cover_at[1] * FPS)):
                surf.write_to_png(cover_png)
            frame += 1
        start += sc.duration
    proc.stdin.close()
    proc.wait()
    import os
    os.remove(audio)
    return total


def preview(scenes, png, at=0.8, cols=5, narrator=None, style=BOTTOM):
    """Hoja de contactos: un fotograma de cada escena."""
    if narrator:
        narrate(scenes, narrator)
    grain, _keep = make_grain()
    total = sum(s.duration for s in scenes)
    thumbs = []
    start = 0.0
    for i, sc in enumerate(scenes):
        t = sc.duration * at
        thumbs.append(frame_surface(scenes, i, t, start, total, i, grain, style))
        start += sc.duration
    tw, th = 360, 640
    rows = math.ceil(len(thumbs) / cols)
    sheet = cairo.ImageSurface(cairo.FORMAT_ARGB32, cols * tw, rows * th)
    ctx = cairo.Context(sheet)
    for k, s in enumerate(thumbs):
        ctx.save()
        ctx.translate((k % cols) * tw, (k // cols) * th)
        ctx.scale(tw / W, th / H)
        ctx.set_source_surface(s, 0, 0)
        ctx.paint()
        ctx.restore()
    sheet.write_to_png(png)
