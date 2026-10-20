"""Motor mínimo para vídeos de curiosidades: dibujos a mano animados + subtítulos palabra a palabra.

Cada vídeo es una lista de escenas. Una escena tiene un texto (el subtítulo) y una
función draw(c, t) que dibuja la ilustración en el instante t (segundos desde el
inicio de la escena). El motor renderiza los fotogramas con cairo y los pasa a ffmpeg.
"""
import math
import random
import subprocess
import wave
from dataclasses import dataclass, field
from typing import Callable

import cairo
import numpy as np

W, H, FPS = 1080, 1920, 30
CENTER = (540, 800)
ART_SCALE = 1.18  # tamaño global de las ilustraciones  # centro de la zona de ilustración

PAPER = (0.957, 0.933, 0.882)
INK = (0.118, 0.118, 0.141)
RED = (0.910, 0.333, 0.239)
BLUE = (0.184, 0.435, 0.859)
YELLOW = (0.949, 0.757, 0.306)
GREEN = (0.231, 0.659, 0.416)
PINK = (0.953, 0.690, 0.667)
WHITE = (1, 1, 1)

FONT = "Inter"


# ---------- utilidades ----------

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_in_out(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out_back(x):
    x = clamp(x)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def prog(t, start, dur):
    return clamp((t - start) / dur) if dur > 0 else float(t >= start)


def ellipse(cx, cy, rx, ry, n=64, a0=-math.pi / 2):
    return [(cx + rx * math.cos(a0 + 2 * math.pi * i / n), cy + ry * math.sin(a0 + 2 * math.pi * i / n))
            for i in range(n + 1)]


def rrect(x, y, w, h, r, n=8):
    """Rectángulo redondeado como polilínea cerrada (sentido horario desde arriba-izquierda)."""
    r = min(r, w / 2, h / 2)
    pts = []
    corners = [(x + w - r, y + r, -math.pi / 2), (x + w - r, y + h - r, 0),
               (x + r, y + h - r, math.pi / 2), (x + r, y + r, math.pi)]
    for cx, cy, a in corners:
        for i in range(n + 1):
            ang = a + (math.pi / 2) * i / n
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    pts.append(pts[0])
    return pts


def densify(pts, step=14):
    """Añade puntos intermedios para que el temblor del trazo se reparta por toda la línea."""
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        for i in range(1, n + 1):
            out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    return out


def partial(pts, p):
    """Primer p (0..1) de la longitud de una polilínea."""
    if p >= 1:
        return pts
    if p <= 0:
        return pts[:1]
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    target = sum(seg) * p
    out = [pts[0]]
    for (a, b), L in zip(zip(pts, pts[1:]), seg):
        if target <= L:
            f = target / L if L else 0
            out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
            return out
        out.append(b)
        target -= L
    return out


# ---------- lienzo ----------

class Canvas:
    """Envoltorio de cairo con trazos 'a mano' (temblor que cambia cada pocos fotogramas)."""

    def __init__(self, ctx: cairo.Context, frame: int):
        self.ctx = ctx
        self.boil = frame // 4  # el trazo "hierve" 7-8 veces por segundo, como un dibujo animado
        self.events: list[str] = []

    def _jitter(self, pts, key, amp):
        rng = random.Random(hash((key, self.boil)))
        return [(x + rng.uniform(-amp, amp), y + rng.uniform(-amp, amp)) for x, y in pts]

    def _path(self, pts):
        ctx = self.ctx
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)

    def shape(self, pts, p=1.0, fill=None, stroke=INK, width=9, key=0, amp=2.2, fill_alpha=1.0, closed=True):
        """Dibuja una forma: el contorno se traza según p y el relleno aparece al terminar."""
        if p <= 0:
            return
        pts = self._jitter(densify(pts), key, amp)
        if fill is not None and closed:
            fa = fill_alpha * ease_in_out((p - 0.6) / 0.4)
            if fa > 0:
                self.ctx.set_source_rgba(*fill, fa)
                self._path(pts)
                self.ctx.close_path()
                self.ctx.fill()
        if stroke is not None and width > 0:
            seg = partial(pts, ease_in_out(p))
            if len(seg) > 1:
                self.ctx.set_source_rgb(*stroke)
                self.ctx.set_line_width(width)
                self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)
                self._path(seg)
                self.ctx.stroke()

    def line(self, pts, p=1.0, color=INK, width=9, key=0, amp=2.0):
        self.shape(pts, p=p, fill=None, stroke=color, width=width, key=key, amp=amp, closed=False)

    def dot(self, x, y, r, color, alpha=1.0):
        self.ctx.set_source_rgba(*color, alpha)
        self.ctx.arc(x, y, r, 0, 2 * math.pi)
        self.ctx.fill()

    def text(self, s, x, y, size, color=INK, weight=cairo.FONT_WEIGHT_BOLD, alpha=1.0, anchor="center"):
        ctx = self.ctx
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, weight)
        ctx.set_font_size(size)
        ext = ctx.text_extents(s)
        dx = {"center": ext.x_advance / 2, "left": 0, "right": ext.x_advance}[anchor]
        ctx.move_to(x - dx, y + size * 0.35)
        ctx.set_source_rgba(*color, alpha)
        ctx.show_text(s)

    def push(self, x=0, y=0, scale=1.0, rot=0.0):
        self.ctx.save()
        self.ctx.translate(x, y)
        self.ctx.rotate(rot)
        self.ctx.scale(scale, scale)

    def pop(self):
        self.ctx.restore()


# ---------- escenas y render ----------

@dataclass
class Scene:
    text: str
    draw: Callable[[Canvas, float], None]
    duration: float = 0.0  # 0 = automático según la longitud del texto
    pops: list[float] = field(default_factory=list)  # instantes (s) con sonido de "pop"

    def __post_init__(self):
        if not self.duration:
            words = len(self.text.split())
            self.duration = max(2.4, 0.28 * words + 1.0)


def word_times(scene: Scene):
    words = scene.text.split()
    span = min(scene.duration * 0.7, 0.3 * len(words))
    return words, [0.08 + span * i / max(1, len(words)) for i in range(len(words))]


def layout_caption(ctx, words, size, max_w):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    space = ctx.text_extents(" ").x_advance
    lines, cur, cur_w = [], [], 0
    for i, w in enumerate(words):
        ww = ctx.text_extents(w).x_advance
        if cur and cur_w + space + ww > max_w:
            lines.append((cur, cur_w))
            cur, cur_w = [], 0
        cur_w += (space if cur else 0) + ww
        cur.append((i, w, ww))
    if cur:
        lines.append((cur, cur_w))
    return lines, space


def draw_caption(c: Canvas, scene: Scene, t: float, y0=1500, size=80):
    words, times = word_times(scene)
    ctx = c.ctx
    lines, space = layout_caption(ctx, words, size, 920)
    lh = size * 1.32
    y = y0 - (len(lines) - 1) * lh / 2
    current = max([i for i, wt in enumerate(times) if t >= wt], default=-1)
    for line, lw in lines:
        x = W / 2 - lw / 2
        for i, w, ww in line:
            if t >= times[i]:
                s = 0.6 + 0.4 * ease_out_back((t - times[i]) / 0.22)
                cx, cy = x + ww / 2, y
                ctx.save()
                ctx.translate(cx, cy)
                ctx.scale(s, s)
                if i == current:
                    ctx.set_source_rgb(*YELLOW)
                    pad = 12
                    _round_rect(ctx, -ww / 2 - pad, -size * 0.62, ww + 2 * pad, size * 1.2, 16)
                    ctx.fill()
                ctx.move_to(-ww / 2, size * 0.36)
                ctx.set_source_rgb(*INK)
                ctx.show_text(w)
                ctx.restore()
            x += ww + space
        y += lh


def _round_rect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def paper_surface():
    rng = np.random.default_rng(7)
    base = np.array(PAPER) * 255
    noise = rng.normal(0, 5, (H, W, 1))
    yy, xx = np.mgrid[0:H, 0:W]
    vignette = 1 - 0.10 * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 4
    rgb = np.clip(base * vignette[..., None] + noise, 0, 255).astype(np.uint8)
    bgra = np.dstack([rgb[..., 2], rgb[..., 1], rgb[..., 0], np.full((H, W), 255, np.uint8)])
    data = bytearray(bgra.tobytes())
    return cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, W, H, W * 4), data


def render_frame(scenes, i_scene, t, total_t, total_dur, frame, label, bg):
    scene = scenes[i_scene]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.set_source_surface(bg, 0, 0)
    ctx.paint()
    c = Canvas(ctx, frame)

    # cabecera: etiqueta + barra de progreso
    ctx.set_source_rgba(*INK, 0.12)
    _round_rect(ctx, 90, 150, W - 180, 12, 6)
    ctx.fill()
    ctx.set_source_rgb(*RED)
    _round_rect(ctx, 90, 150, max(12, (W - 180) * total_t / total_dur), 12, 6)
    ctx.fill()
    c.text(label, W / 2, 230, 38, color=INK, alpha=0.55)

    # ilustración, con un ligero zoom continuo y entrada/salida suaves
    enter = ease_out_back(t / 0.35)
    leave = 1 - ease_in_out((t - (scene.duration - 0.18)) / 0.18)
    zoom = ART_SCALE * (0.85 + 0.15 * enter) * (1 + 0.03 * t / scene.duration)
    ctx.push_group()
    c.push(*CENTER, scale=zoom)
    scene.draw(c, t)
    c.pop()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(clamp(min(enter, 1) * leave))

    draw_caption(c, scene, t)
    return surf


def synth_audio(path, scenes, total_dur, sr=44100):
    """Pista de efectos sin voz: 'whoosh' en cada cambio de escena y 'pop' en los elementos."""
    n = int(total_dur * sr) + sr
    out = np.zeros(n)
    rng = np.random.default_rng(1)

    def whoosh(at):
        L = int(0.35 * sr)
        env = np.sin(np.linspace(0, np.pi, L)) ** 2
        noise = rng.normal(0, 1, L)
        noise = np.convolve(noise, np.ones(30) / 30, mode="same")
        s = int(at * sr)
        out[s:s + L] += 0.25 * env * noise[: len(out[s:s + L])]

    def pop(at):
        L = int(0.09 * sr)
        tt = np.arange(L) / sr
        f = 900 * np.exp(-tt * 25) + 300
        s = int(at * sr)
        tone = 0.22 * np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 45)
        out[s:s + L] += tone[: len(out[s:s + L])]

    start = 0.0
    for sc in scenes:
        if start > 0:
            whoosh(start - 0.12)
        for p in sc.pops:
            pop(start + p)
        start += sc.duration
    out = np.clip(out, -1, 1)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((out * 32767).astype(np.int16).tobytes())


def render(scenes, out_mp4, label="CURIOSIDADES", cover_png=None, cover_frame_at=1.6):
    bg, _keep = paper_surface()
    total = sum(s.duration for s in scenes)
    audio = out_mp4.replace(".mp4", "_sfx.wav")
    synth_audio(audio, scenes, total)

    proc = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", audio,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out_mp4,
    ], stdin=subprocess.PIPE)

    frame, start = 0, 0.0
    for i, sc in enumerate(scenes):
        nf = int(round(sc.duration * FPS))
        for k in range(nf):
            t = k / FPS
            surf = render_frame(scenes, i, t, start + t, total, frame, label, bg)
            proc.stdin.write(bytes(surf.get_data()))
            if cover_png and i == 0 and k == int(cover_frame_at * FPS):
                surf.write_to_png(cover_png)
            frame += 1
        start += sc.duration
    proc.stdin.close()
    proc.wait()
    return total
