"""Vídeo: tus auriculares quitan el ruido añadiendo más ruido (cancelación activa de ruido).

Estilo del vídeo viral de referencia: paradoja de gancho, un objeto central que se transforma
(auriculares → corte del auricular → ondas), cámara que no para, transiciones que atraviesan la
imagen, subtítulos de 1-3 palabras, datos en directo y cierre para compartir.

Datos y fuentes:
- El auricular genera "antirruido": la misma onda desfasada 180° (al revés); al sumarse se anulan.
  Micrófonos por fuera (feedforward) captan el ruido antes de que llegue; por dentro (feedback)
  vigilan lo que oyes y corrigen; el ciclo se repite cientos de veces por segundo.
  Jabra: https://www.jabra.com/discover/noise-cancelling
- Funciona mejor con ruidos graves y constantes (aviones, trenes, aire acondicionado) y peor con
  las voces. Sony: https://helpguide.sony.net/mdr/wf1000xm3/v1/en/contents/TP0002289916.html
- Las voces y los sonidos agudos son menos predecibles y el retraso del cálculo impide anularlos
  bien. ScienceABC (divulgación): https://www.scienceabc.com/innovation/why-are-noise-canceling-headphones-less-effective-at-blocking-high-pitched-sounds
- El sonido viaja a ~343 m/s: recorrer 2,5 cm le lleva unos 73 µs (cálculo directo).

Uso: python3 video/auriculares.py [--voz santa|dora|alex|eleven] [--sin-voz]  ->  video/out/auriculares/
     python3 video/auriculares.py --preview [png]
"""
import math
import os
import random
import sys

import cairo

from engine import clamp, ease_in_out, prog
from piezas import (CYAN, GREEN, RED, WHITE, appear, mini_tag, panel, person, phone, share_screen, spaced, tech_bg)
from rich import (TOP_SHORT, YELLOW, Scene, disc, fill_rr, glow, linear, mix, poly, preview, radial, render,
                  rgba, soft_ellipse, source, stroke, word_time)

NOISE = (1.0, 0.36, 0.30)
ANTI = CYAN
SKIN = (0.90, 0.68, 0.56)
GRAPHITE = (0.20, 0.21, 0.25)


def scene_of(fn):
    return next(s for s in SCENES if s.draw is fn)


def dur(fn):
    return scene_of(fn).duration


def w(fn, needle):
    return word_time(scene_of(fn), needle)


# ---------- ondas ----------

def wave(x0, x1, y, amp, cycles, phase, inv=1.0, n=220, env=None):
    pts = []
    for k in range(n):
        u = k / (n - 1)
        a = amp * (env(u) if env else 1.0)
        v = math.sin(2 * math.pi * cycles * u + phase) + 0.28 * math.sin(4 * math.pi * cycles * u + 2 * phase + 0.7)
        pts.append((x0 + (x1 - x0) * u, y - inv * a * v / 1.28))
    return pts


def glow_line(ctx, pts, col, width=7, a=1.0):
    if a <= 0 or len(pts) < 2:
        return
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_ADD)
    stroke(ctx, pts, rgba(col, 0.18 * a), width * 5)
    stroke(ctx, pts, rgba(col, 0.35 * a), width * 2.2)
    ctx.restore()
    stroke(ctx, pts, rgba(mix(col, WHITE, 0.35), a), width)


# ---------- los auriculares ----------

def headphones(ctx, x, y, s, t):
    """Auriculares de diadema vistos de frente."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    soft_ellipse(ctx, 0, 330, 420, 70, (0, 0, 0), 0.55)
    ctx.new_sub_path()
    ctx.arc(0, 40, 300, math.pi * 1.08, math.pi * 1.92)
    source(ctx, (0.12, 0.12, 0.15))
    ctx.set_line_width(46)
    ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(0, 40, 300, math.pi * 1.15, math.pi * 1.85)
    source(ctx, (1, 1, 1, 0.18))
    ctx.set_line_width(6)
    ctx.stroke()
    for side in (-1, 1):
        cx = side * 300
        fill_rr(ctx, cx - 26, -10, 52, 120, 14, (0.55, 0.57, 0.62))
        fill_rr(ctx, cx - 120, 80, 240, 300, 110, linear(cx - 120, 0, cx + 120, 0, [(0, (0.30, 0.31, 0.36)), (0.5, (0.46, 0.47, 0.53)), (1, (0.20, 0.21, 0.25))]))
        fill_rr(ctx, cx - 92, 112, 184, 236, 86, linear(0, 112, 0, 348, [(0, (0.17, 0.18, 0.21)), (1, (0.09, 0.09, 0.11))]))
        disc(ctx, cx + side * -60, 150, 8, CYAN)
        glow(ctx, cx + side * -60, 150, 30, CYAN, 0.6 * (0.6 + 0.4 * math.sin(t * 4)), add=True)
    ctx.restore()


def ear(ctx, x, y, s):
    """Oreja de perfil (lado derecho de la imagen)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(-30, -260)
    ctx.curve_to(150, -300, 210, -60, 120, 80)
    ctx.curve_to(80, 150, 90, 230, 10, 260)
    ctx.curve_to(-60, 280, -80, 200, -40, 150)
    ctx.line_to(-40, -200)
    ctx.close_path()
    source(ctx, radial(40, -40, 320, [(0, SKIN), (1, mul_c(SKIN, 0.72))]))
    ctx.fill()
    ctx.move_to(-10, -190)
    ctx.curve_to(110, -210, 140, -50, 70, 40)
    source(ctx, (0.55, 0.32, 0.26, 0.55))
    ctx.set_line_width(14)
    ctx.stroke()
    disc(ctx, 0, 20, 34, (0.30, 0.14, 0.12))
    ctx.restore()


def mul_c(c, k):
    return tuple(min(1, v * k) for v in c)


def cup_section(ctx, x, y, s, t, vib=0.0, glow_out=0.0, glow_in=0.0, chip=0.0, labels=None):
    """Corte del auricular: carcasa, almohadilla, altavoz que vibra, micrófonos, chip y la oreja."""
    labels = labels or {}
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ear(ctx, 250, 0, 1.0)
    # carcasa: media elipse gruesa
    pts_o = [(60 + 250 * math.cos(a), 340 * math.sin(a)) for a in [math.pi / 2 + k * math.pi / 40 for k in range(41)]]
    pts_i = [(60 + 205 * math.cos(a), 295 * math.sin(a)) for a in [math.pi * 1.5 - k * math.pi / 40 for k in range(41)]]
    poly(ctx, pts_o + pts_i, linear(-200, 0, 60, 0, [(0, (0.36, 0.37, 0.43)), (1, (0.20, 0.21, 0.25))]))
    # almohadilla (dos secciones)
    for sy in (-1, 1):
        fill_rr(ctx, 40, sy * 240 - 70 if sy > 0 else -310, 110, 140, 55, linear(40, 0, 150, 0, [(0, (0.22, 0.22, 0.26)), (1, (0.14, 0.14, 0.17))]))
    # placa y chip
    fill_rr(ctx, -150, 150, 120, 26, 6, (0.08, 0.30, 0.22))
    fill_rr(ctx, -128, 118, 70, 34, 6, (0.05, 0.05, 0.07))
    if chip > 0:
        glow(ctx, -93, 135, 80, YELLOW, 0.6 * chip, add=True)
    # altavoz: imán, cono y membrana que vibra
    off = vib * 14 * math.sin(t * 2 * math.pi * 7)
    fill_rr(ctx, -110, -70, 60, 140, 12, (0.10, 0.10, 0.12))
    poly(ctx, [(-50, -60), (-50 + 0, 60), (40 + off, 190), (40 + off, -190)], linear(-50, 0, 40, 0, [(0, (0.55, 0.57, 0.63)), (1, (0.80, 0.82, 0.88))]))
    stroke(ctx, [(40 + off, -190), (40 + off, 190)], (0.25, 0.26, 0.30), 8)
    disc(ctx, -5 + off * 0.5, 0, 34, (0.32, 0.33, 0.38))
    # micrófonos
    for (mx, my, gp) in ((-198, -150, glow_out), (108, 130, glow_in)):
        fill_rr(ctx, mx - 16, my - 22, 32, 44, 10, (0.15, 0.15, 0.18))
        disc(ctx, mx, my, 9, mix((0.35, 0.36, 0.42), CYAN, gp))
        if gp > 0:
            glow(ctx, mx, my, 60, CYAN, 0.7 * gp, add=True)
    ctx.restore()

    def P(px, py):
        return x + s * px, y + s * py
    spots = {"outer": ((-198, -150), (-60, -380)), "inner": ((108, 130), (60, 500)), "chip": ((-93, 135), (-20, 430)),
             "driver": ((40, -120), (150, -520)), "ear": ((300, 20), (180, 370))}
    names = {"outer": "MICRÓFONO EXTERIOR", "inner": "MICRÓFONO INTERIOR", "chip": "CHIP", "driver": "ALTAVOZ", "ear": "TU OÍDO"}
    for key, p in labels.items():
        (ax, ay), (lx, ly) = spots[key]
        X, Y = P(ax, ay)
        LX, LY = P(lx, ly)
        mini_tag(ctx, names[key], X, Y, LX, LY, p, col=YELLOW if key == "chip" else (CYAN if key != "ear" else WHITE))


# ---------- escenas ----------

def s_hook(ctx, t):
    tech_bg(ctx, t)
    for k in range(3):
        glow_line(ctx, wave(40, 1040, 640 + 160 * k, 60 + 20 * k, 3 + k, -t * 6 + k), NOISE, 5, 0.55)
    headphones(ctx, 540, 980, 1.2, t)
    p = appear(t, w(s_hook, "añadiendo"), 0.5)
    if p > 0:
        for side in (-1, 1):
            for r in range(3):
                rad = 60 + ((t * 220 + r * 90) % 270)
                ctx.new_sub_path()
                ctx.arc(540 + side * 360, 1270, rad, math.pi * 1.1 if side < 0 else -math.pi * 0.1, math.pi * 1.9 if side < 0 else math.pi * 0.9)
                source(ctx, rgba(ANTI, p * (1 - (rad - 60) / 270)))
                ctx.set_line_width(8)
                ctx.stroke()
    mini_tag(ctx, "RUIDO", 180, 640, 230, 500, appear(t, 0.2, 0.4), col=NOISE)
    mini_tag(ctx, "+ MÁS RUIDO", 900, 1270, 860, 1480, p, col=ANTI)


def s_mics(ctx, t):
    tech_bg(ctx, t)
    m = appear(t, w(s_mics, "micrófonos"), 0.4)
    reach = clamp(t / 1.2)
    glow_line(ctx, wave(-20, -20 + 330 * reach, 830, 70, 2.2 * reach + 0.01, -t * 10), NOISE, 6)
    cup_section(ctx, 520, 1000, 1.25, t, glow_out=m, labels={"outer": m})


def s_wave(ctx, t):
    tech_bg(ctx, t)
    p = appear(t, w(s_wave, "onda"), 0.5)
    glow_line(ctx, wave(40, 1040, 1000, 230, 3.0, -t * 8), NOISE, 9, max(0.25, p))
    cyc = int(120 * clamp((t - w(s_wave, "cientos") + 0.2) / 1.0))
    panel(ctx, 640, 460, "FRECUENCIA", f"{cyc}", "Hz", appear(t, w(s_wave, "cientos") - 0.1, 0.3), col=NOISE)
    mini_tag(ctx, "SUBE", 220, 780, 300, 610, appear(t, w(s_wave, "sube"), 0.35), col=NOISE)
    mini_tag(ctx, "BAJA", 380, 1220, 460, 1400, appear(t, w(s_wave, "baja"), 0.35), col=NOISE)


def chip_icon(ctx, x, y, s, t, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    glow(ctx, 0, 0, 220, YELLOW, 0.35 * a * (0.8 + 0.2 * math.sin(t * 8)), add=True)
    for k in range(5):
        off = -80 + 40 * k
        for px, py in ((off, -118), (off, 118), (-118, off), (118, off)):
            fill_rr(ctx, px - 8, py - 8, 16, 16, 3, (0.85, 0.75, 0.45))
    fill_rr(ctx, -105, -105, 210, 210, 18, linear(-105, -105, 105, 105, [(0, (0.18, 0.18, 0.21)), (1, (0.05, 0.05, 0.07))]))
    spaced(ctx, "ANC", 0, 0, 44, col=(1, 1, 1, 0.6), anchor="center")
    ctx.restore()


def s_invert(ctx, t):
    tech_bg(ctx, t)
    chip_icon(ctx, 540, 660, 0.9, t)
    glow_line(ctx, wave(40, 1040, 960, 150, 3.0, -t * 8), NOISE, 7)
    p = ease_in_out(appear(t, w(s_invert, "revés") - 0.3, 0.7))
    pts = wave(40, 1040, 1300, 150, 3.0, -t * 8, inv=-1)
    glow_line(ctx, pts[: max(2, int(len(pts) * p))], ANTI, 7, 1.0 if p > 0 else 0)
    mini_tag(ctx, "CHIP", 640, 640, 800, 520, appear(t, w(s_invert, "chip"), 0.4), col=YELLOW)
    mini_tag(ctx, "ANTIRRUIDO", 860, 1300, 760, 1470, appear(t, w(s_invert, "revés"), 0.4), col=ANTI)


def s_updown(ctx, t):
    tech_bg(ctx, t)
    y = 1000
    glow_line(ctx, wave(40, 1040, y, 220, 2.0, -t * 3), NOISE, 8)
    glow_line(ctx, wave(40, 1040, y, 220, 2.0, -t * 3, inv=-1), ANTI, 8)
    xs = 40 + 1000 * ((0.25 - (-t * 3) / (2 * math.pi)) % 0.5 / 2.0)
    for word, col, d in (("sube", NOISE, -1), ("baja", ANTI, 1)):
        p = appear(t, w(s_updown, word), 0.35)
        if p > 0:
            a = clamp(p * 1.5)
            y1 = y + d * 300 * ease_in_out(p)
            stroke(ctx, [(xs, y), (xs, y1)], rgba(col, a), 12)
            stroke(ctx, [(xs - 26, y1 - d * 36), (xs, y1), (xs + 26, y1 - d * 36)], rgba(col, a), 12)
            spaced(ctx, "SUBE" if d < 0 else "BAJA", xs + 40, y1, 34, col=rgba(col, a))


def s_cancel(ctx, t):
    tech_bg(ctx, t)
    y = 1000
    m = ease_in_out(prog(t, w(s_cancel, "suman") - 0.2, 0.7))
    z = ease_in_out(prog(t, w(s_cancel, "anulan") - 0.1, 0.5))
    amp = 200 * (1 - z)
    glow_line(ctx, wave(40, 1040, y - 260 * (1 - m), amp, 2.0, -t * 5), NOISE, 7, 1 - 0.7 * z)
    glow_line(ctx, wave(40, 1040, y + 260 * (1 - m), amp, 2.0, -t * 5, inv=-1), ANTI, 7, 1 - 0.7 * z)
    if z > 0:
        glow_line(ctx, [(40, y), (1040, y)], WHITE, 6, z)
        glow(ctx, 540, y, 380, (0.8, 0.9, 1.0), 0.25 * z, add=True)
    panel(ctx, 640, 460, "SUMA", "0" if z > 0.6 else f"{2 * (1 - m):.1f}".replace(".", ","), "", appear(t, w(s_cancel, "suman"), 0.3),
          col=WHITE if z > 0.6 else YELLOW)


def s_silence(ctx, t):
    tech_bg(ctx, t)
    s = 1.2
    cup_section(ctx, 470, 1000, s, t, vib=1.0, glow_out=0.6, labels={"driver": appear(t, w(s_silence, "altavoz"), 0.4),
                                                                      "ear": appear(t, w(s_silence, "silencio"), 0.4)})
    glow_line(ctx, wave(-20, 220, 820, 70, 1.4, -t * 10), NOISE, 6, 0.8)
    for r in range(4):  # el altavoz suena hacia la oreja
        rad = 40 + ((t * 260 + r * 60) % 240)
        ctx.new_sub_path()
        ctx.arc(470 + s * 40, 1000, rad, -0.6, 0.6)
        source(ctx, rgba(ANTI, 0.8 * (1 - (rad - 40) / 240)))
        ctx.set_line_width(7)
        ctx.stroke()
    p = appear(t, w(s_silence, "silencio"), 0.4)
    if p > 0:
        glow_line(ctx, [(820, 1450), (1040, 1450)], WHITE, 5, p)


def s_race(ctx, t):
    tech_bg(ctx, t)
    x0, x1, y = 140, 880, 1060
    stroke(ctx, [(x0, y + 120), (x1, y + 120)], (1, 1, 1, 0.12), 3)
    fill_rr(ctx, x0 - 20, y - 60, 40, 60, 10, (0.15, 0.15, 0.18))
    disc(ctx, x0, y - 30, 10, CYAN)
    ear(ctx, x1 + 40, y - 80, 0.6)
    t0 = w(s_race, "antes") - 0.3
    u = clamp((t - t0) / 2.2)
    xs = x0 + (x1 - x0) * u
    glow_line(ctx, wave(x0, max(x0 + 2, xs), y - 30, 50, 4 * u + 0.01, -t * 12), NOISE, 6)
    ue = clamp((t - t0) / 0.35)  # la señal eléctrica va mucho más rápido
    path = [(x0, y - 30), (x0, y - 220), (540, y - 220), (x1 - 90, y - 220), (x1 - 90, y - 60)]
    seg_pts = []
    total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:]))
    d = total * ue
    acc = 0.0
    seg_pts.append(path[0])
    for a, b in zip(path, path[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if acc + L <= d:
            seg_pts.append(b)
            acc += L
        else:
            f = (d - acc) / L
            seg_pts.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
            break
    stroke(ctx, path, (1, 1, 1, 0.12), 6)
    glow_line(ctx, seg_pts, YELLOW, 6, 1.0 if ue > 0 else 0)
    chip_icon(ctx, 540, y - 220, 0.35, t)
    if ue >= 1:
        glow(ctx, x1 - 90, y - 60, 80, ANTI, 0.8, add=True)
    us = int(73 * u)
    panel(ctx, 640, 460, "EL RUIDO TARDA", f"{us}", "µs", appear(t, t0, 0.3), col=NOISE)
    mini_tag(ctx, "2,5 CM", 540, y + 120, 540, y + 230, appear(t, t0 + 0.2, 0.4), col=WHITE)


def s_feedback(ctx, t):
    tech_bg(ctx, t)
    c = appear(t, w(s_feedback, "corrige"), 0.6)
    cup_section(ctx, 470, 1000, 1.2, t, vib=0.6, glow_in=appear(t, w(s_feedback, "micrófono"), 0.4), chip=c,
                labels={"inner": appear(t, w(s_feedback, "micrófono"), 0.4), "chip": c})
    res = 40 * (1 - 0.85 * ease_in_out(c))
    glow_line(ctx, wave(820, 1060, 1180, res, 2.0, -t * 9), mix(NOISE, WHITE, 0.4), 5)
    if c > 0:  # bucle de corrección: micrófono interior → chip
        a = clamp(c * 1.5)
        ctx.save()
        ctx.set_dash([14, 10], -t * 60)
        stroke(ctx, [(470 + 1.2 * 108, 1000 + 1.2 * 160), (470 + 1.2 * 60, 1000 + 1.2 * 260), (470 - 1.2 * 93, 1000 + 1.2 * 200)], rgba(YELLOW, a), 5)
        ctx.restore()


def s_spectrum(ctx, t):
    tech_bg(ctx, t)
    ox, oy, gw, gh = 110, 1300, 860, 620
    stroke(ctx, [(ox, oy - gh - 10), (ox, oy), (ox + gw + 10, oy)], (1, 1, 1, 0.5), 3)
    n = 24
    red_p = appear(t, w(s_spectrum, "graves") - 0.2, 0.6)
    for k in range(n):
        u = (k + 0.5) / n
        x = ox + gw * u
        base = 0.85 - 0.35 * u + 0.08 * math.sin(k * 1.7 + t * 2)
        after = base * (0.18 + 0.82 * clamp((u - 0.15) / 0.55) ** 1.2)
        bw = gw / n * 0.62
        fill_rr(ctx, x - bw / 2, oy - gh * base, bw, gh * base, 6, rgba(NOISE, 0.35))
        if red_p > 0:
            h = gh * (base + (after - base) * ease_in_out(red_p))
            fill_rr(ctx, x - bw / 2, oy - h, bw, h, 6, linear(0, oy - h, 0, oy, [(0, rgba(ANTI, 1)), (1, rgba(ANTI, 0.4))]))
    spaced(ctx, "GRAVES", ox + 20, oy + 46, 28, col=ANTI)
    spaced(ctx, "AGUDOS", ox + gw, oy + 46, 28, col=NOISE, anchor="right")
    mini_tag(ctx, "AVIÓN", ox + gw * 0.06, oy - gh * 0.3, ox + 60, oy - gh - 40, appear(t, w(s_spectrum, "avión"), 0.4), col=ANTI)
    mini_tag(ctx, "METRO", ox + gw * 0.16, oy - gh * 0.25, ox + 300, oy - gh - 40, appear(t, w(s_spectrum, "metro"), 0.4), col=ANTI)


_rv = random.Random(3)
VOICE_ENV = [abs(_rv.gauss(0, 1)) for _ in range(40)]


def voice_wave(x0, x1, y, amp, t, shift=0.0, inv=1.0, n=260):
    pts = []
    for k in range(n):
        u = k / (n - 1)
        tt = u * 3 - t * 1.6 + shift
        e = VOICE_ENV[int(tt * 6) % 40] * (0.6 + 0.4 * math.sin(tt * 7))
        v = math.sin(tt * 55) * 0.6 + math.sin(tt * 91 + 1.3) * 0.4
        pts.append((x0 + (x1 - x0) * u, y - inv * amp * e * v))
    return pts


def s_voices(ctx, t):
    tech_bg(ctx, t)
    y = 980
    vw = voice_wave(40, 1040, y, 120, t)
    glow_line(ctx, vw, NOISE, 5)
    lag = voice_wave(40, 1040, y, 120, t, shift=-0.06, inv=-1)
    glow_line(ctx, lag, ANTI, 5, 0.85)
    p = appear(t, w(s_voices, "rápido"), 0.4)
    if p > 0:
        rest = [(a[0], 1300 + (a[1] - y) + (b[1] - y)) for a, b in zip(vw, lag)]
        glow_line(ctx, rest, WHITE, 4, p)
        mini_tag(ctx, "LO QUE SE CUELA", 820, 1300, 700, 1460, p, col=WHITE)
    mini_tag(ctx, "VOZ", 200, 900, 260, 560, appear(t, w(s_voices, "voces"), 0.4), col=NOISE)


def small_headphones(ctx, x, y, s):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.new_sub_path()
    ctx.arc(0, 0, 120, math.pi * 1.05, math.pi * 1.95)
    source(ctx, (0.10, 0.10, 0.12))
    ctx.set_line_width(22)
    ctx.stroke()
    for side in (-1, 1):
        fill_rr(ctx, side * 120 - 34, -10, 68, 110, 30, (0.25, 0.26, 0.30))
    ctx.restore()


def s_plane(ctx, t):
    ctx.rectangle(0, 0, 1080, 1920)
    ctx.set_source(radial(540, 950, 1100, [(0, (0.10, 0.11, 0.18)), (1, (0.02, 0.02, 0.05))]))
    ctx.fill()
    # ventanilla y motor fuera
    fill_rr(ctx, 70, 560, 220, 320, 100, (0.55, 0.57, 0.63))
    fill_rr(ctx, 95, 585, 170, 270, 80, linear(0, 585, 0, 855, [(0, (0.30, 0.55, 0.95)), (1, (0.85, 0.70, 0.55))]))
    for sx in (480, 820):  # asientos
        fill_rr(ctx, sx - 150, 780, 300, 640, 70, linear(0, 780, 0, 1420, [(0, (0.22, 0.30, 0.55)), (1, (0.10, 0.14, 0.28))]))
        fill_rr(ctx, sx - 120, 800, 240, 120, 40, (0.90, 0.90, 0.93))
    person(ctx, 480, 1000, 0.95, look=1)
    small_headphones(ctx, 480, 1000, 0.95)
    person(ctx, 820, 1000, 0.95, look=-1)
    m = appear(t, w(s_plane, "motor"), 0.4)
    glow_line(ctx, wave(0, 330, 720, 60, 1.5, -t * 7), NOISE, 7, 1 - 0.85 * m)
    if m > 0:
        a = clamp(m * 1.5)
        stroke(ctx, [(110, 620), (250, 820)], rgba(RED, a), 12)
        stroke(ctx, [(250, 620), (110, 820)], rgba(RED, a), 12)
        mini_tag(ctx, "MOTOR", 180, 900, 180, 1080, m, col=NOISE)
    v = appear(t, w(s_plane, "sigues"), 0.4)
    if v > 0:
        for r in range(3):
            rad = 30 + ((t * 160 + r * 50) % 150)
            ctx.new_sub_path()
            ctx.arc(760, 1010, rad, math.pi * 0.8, math.pi * 1.2)
            source(ctx, rgba(YELLOW, v * (1 - (rad - 30) / 150)))
            ctx.set_line_width(7)
            ctx.stroke()
    mini_tag(ctx, "AL DE AL LADO", 860, 900, 760, 640, appear(t, w(s_plane, "lado"), 0.4), col=YELLOW)


def s_share(ctx, t):
    tech_bg(ctx, t)
    fol = appear(t, w(s_share, "Síguenos"), 0.4)
    pk = appear(t, w(s_share, "amigo"), 0.35)
    hp = appear(t, w(s_share, "cascos"), 0.4)
    snt = appear(t, w(s_share, "escucharte") + 0.2, 0.3)

    def thumb(c, tt):
        c.rectangle(-200, -170, 400, 340)
        source(c, (0.05, 0.06, 0.10))
        c.fill()
        for k in range(2):
            glow_line(c, wave(-200, 200, -60 + 120 * k, 40, 2.0, -tt * 5, inv=1 if k == 0 else -1), NOISE if k == 0 else ANTI, 4)

    def badge(c, x, y, s):
        small_headphones(c, x, y + 10, 0.16 * s)
    phone(ctx, 540, 930, 1.1, share_screen(pk, hp, snt, fol, thumb=thumb, badge=badge), t, cable=False)
    if snt > 0:
        glow(ctx, 540, 1250, 300, GREEN, 0.35 * snt, add=True)


SCENES = [
    Scene("Tus auriculares quitan el ruido… añadiendo más ruido.", s_hook, key="añadiendo", duration=3.6,
          sfx=[("@añadiendo", "whoosh")]),
    Scene("Por fuera llevan micrófonos que escuchan el ruido de tu alrededor.", s_mics, key="micrófonos", sfx=[("@micrófonos", "pop")]),
    Scene("Cada sonido es una onda que sube y baja cientos de veces por segundo.", s_wave, key="onda",
          sfx=[("@sube", "pop"), ("@baja", "pop")]),
    Scene("Luego, un chip calcula esa misma onda, pero al revés.", s_invert, key="revés", sfx=[("@chip", "pop"), ("@revés", "whoosh")]),
    Scene("Donde el ruido sube, el auricular baja.", s_updown, key="baja", sfx=[("@sube", "pop"), ("@baja", "pop")]),
    Scene("Las dos ondas se suman… y se anulan.", s_cancel, key="anulan", duration=3.2, sfx=[("@anulan", "thunk")]),
    Scene("Por eso oyes silencio, aunque el altavoz no para de sonar.", s_silence, key="silencio", sfx=[("@silencio", "pop")]),
    Scene("Tiene que hacerlo antes de que el ruido llegue a tu oído.", s_race, key="antes", duration=3.6, sfx=[("@antes", "tick")]),
    Scene("Por dentro, otro micrófono escucha lo que queda y lo corrige.", s_feedback, key="corrige", sfx=[("@corrige", "pop")]),
    Scene("Funciona genial con ruidos graves y constantes, como un avión o el metro.", s_spectrum, key="graves",
          sfx=[("@avión", "pop"), ("@metro", "pop")]),
    Scene("Pero las voces cambian demasiado rápido.", s_voices, key="voces", duration=2.8, sfx=[("@rápido", "thunk")]),
    Scene("Por eso en el avión dejas de oír el motor… pero sigues oyendo al de al lado.", s_plane, key="lado",
          sfx=[("@motor", "thunk"), ("@lado", "pop")]),
    Scene("Síguenos y mándaselo a ese amigo que se pone los cascos para no escucharte.", s_share, key="amigo", duration=5.2,
          sfx=[("@Síguenos", "pop"), ("@amigo", "pop"), ("@cascos", "pop"), ("@escucharte", "chime")]),
]

POST = """Tus auriculares quitan el ruido… añadiendo más ruido 🎧

Unos micrófonos escuchan el ruido de fuera y un chip crea la misma onda al revés. Al sumarse, se anulan: oyes silencio aunque el altavoz no para de sonar. Por dentro, otro micrófono corrige lo que se cuela.

Funciona genial con ruidos graves y constantes, como el motor del avión o el metro. Con las voces no tanto: cambian demasiado rápido.

Mándaselo a ese amigo que se pone los cascos para no escucharte 👀

#curiosidades #tecnologia #ciencia #auriculares #sabiasque
"""

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "out", "auriculares")
    os.makedirs(out, exist_ok=True)
    narrator = None
    if "--sin-voz" not in sys.argv:
        from voz import narrator_from_args
        narrator = narrator_from_args(sys.argv, speed=1.04)  # ritmo natural: acelerar Kokoro lo hace sonar más artificial
        narrator.gap = 0.22  # frases encadenadas, como una narración seguida
        narrator.min_scene = 1.6
    if "--preview" in sys.argv:
        i = sys.argv.index("--preview")
        dest = sys.argv[i + 1] if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith("--") else os.path.join(out, "preview.png")
        preview(SCENES, dest, narrator=narrator, style=TOP_SHORT)
        print("preview:", dest)
    else:
        total = render(SCENES, os.path.join(out, "auriculares.mp4"), cover_png=os.path.join(out, "fotograma.png"),
                       cover_at=(0, 1.5), narrator=narrator, style=TOP_SHORT)
        os.remove(os.path.join(out, "fotograma.png"))
        with open(os.path.join(out, "texto-del-post.txt"), "w") as f:
            f.write(POST)
        print(f"OK: {total:.1f} s")
