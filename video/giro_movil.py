"""Vídeo: ¿Cómo sabe tu móvil que lo has girado?

Formato: objeto que tienes en la mano con un mecanismo oculto, una metáfora central que se
transforma (móvil → chip → masa con muelles → peines de silicio), etiquetas técnicas con medidas,
subtítulos arriba en 2 líneas con una palabra clave y cada elemento sincronizado con su palabra.

Datos y fuentes:
- Acelerómetro en encapsulado LGA de 2 × 2 mm: hojas de datos Bosch BMA400 y ST LIS2DW12.
- Masa suspendida por muelles con dientes móviles entre electrodos fijos; mide capacidad
  (distancia entre dientes): Make Tech Easier "How phone accelerometers detect orientation";
  PMC11434136 (acelerómetro de peine).
- Dientes de ~4 µm de ancho y 1 µm de separación: JKSUS, "Design of MEMS capacitive comb accelerometer".
- Pelo humano: 17-180 µm (Museum of Science, Boston); ~70 µm típico.
- La gravedad tira siempre de la masa: así el móvil sabe dónde está el suelo y gira la pantalla;
  el mismo sensor cuenta los pasos.

Uso: python3 video/giro_movil.py [--voz santa|dora|alex] [--sin-voz]  ->  video/out/giro-movil/
     python3 video/giro_movil.py --preview [png]
"""
import math
import os
import sys

from engine import clamp, ease_in_out, ease_out_back, prog
from piezas import CYAN, GREEN, ORANGE, WHITE, appear, phone, tag, tech_bg
from rich import (TOP, YELLOW, Scene, cta_button, disc, fill_rr, glow, linear, poly, preview, radial,
                  render, rgba, soft_ellipse, source, stroke, text, word_time)

SILVER = (0.78, 0.81, 0.88)
SILICON = (0.16, 0.18, 0.24)


def scene_of(fn):
    return next(s for s in SCENES if s.draw is fn)


def dur(fn):
    return scene_of(fn).duration


def w(fn, needle):
    """Segundo en que la voz dice esa palabra en la escena de fn."""
    return word_time(scene_of(fn), needle)


# ---------- la foto de la pantalla y el giro ----------

def photo(ctx, size=820):
    """Paisaje sencillo: así se ve si la imagen está derecha o torcida."""
    h = size / 2
    ctx.rectangle(-h, -h, size, size)
    ctx.set_source(linear(0, -h, 0, h * 0.3, [(0, (0.30, 0.55, 0.95)), (1, (1.0, 0.70, 0.45))]))
    ctx.fill()
    disc(ctx, 120, -120, 70, radial(120, -120, 70, [(0, (1, 0.98, 0.85)), (1, (1, 0.85, 0.40))]))
    glow(ctx, 120, -120, 220, (1, 0.9, 0.5), 0.5)
    poly(ctx, [(-h, 120), (-220, -60), (-60, 80), (90, -20), (h, 140), (h, h), (-h, h)], (0.30, 0.36, 0.55))
    poly(ctx, [(-h, 200), (-120, 60), (60, 170), (240, 70), (h, 190), (h, h), (-h, h)], (0.16, 0.24, 0.36))
    ctx.rectangle(-h, 230, size, h)
    ctx.set_source(linear(0, 230, 0, h, [(0, (0.25, 0.45, 0.75)), (1, (0.10, 0.20, 0.40))]))
    ctx.fill()


def rotating_phone(ctx, t, x, y, s, start, direction=-1, from_landscape=False):
    """Móvil que gira 90° y, un instante después, endereza la imagen (como al girarlo de verdad)."""
    a0 = direction * math.pi / 2 if from_landscape else 0.0
    a1 = 0.0 if from_landscape else direction * math.pi / 2
    rot = a0 + (a1 - a0) * ease_in_out(prog(t, start, 0.6))
    ui_from = -a0
    ui_to = -a1
    rel = ui_from + (ui_to - ui_from) * ease_in_out(prog(t, start + 0.55, 0.35))

    def screen(c, tt):
        c.save()
        c.rotate(rel)
        photo(c)
        c.restore()

    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    phone(ctx, 0, 0, s, screen, t, cable=False)
    ctx.restore()
    return rot


def turn_arrow(ctx, x, y, r, p, col=CYAN):
    if p <= 0:
        return
    a0, a1 = -math.pi * 0.15, -math.pi * 0.15 - math.pi * 0.7 * ease_in_out(p)
    ctx.new_sub_path()
    ctx.arc_negative(x, y, r, a0, a1)
    source(ctx, rgba(col, clamp(p * 2)))
    ctx.set_line_width(12)
    ctx.stroke()
    hx, hy = x + r * math.cos(a1), y + r * math.sin(a1)
    d = a1 - math.pi / 2
    stroke(ctx, [(hx + 34 * math.cos(d - 0.6), hy + 34 * math.sin(d - 0.6)), (hx, hy),
                 (hx + 34 * math.cos(d + 0.6 + math.pi), hy + 34 * math.sin(d + 0.6 + math.pi))], rgba(col, clamp(p * 2)), 12)


# ---------- el chip por dentro ----------

def to_world(cx, cy, s, rot, x, y):
    return cx + s * (x * math.cos(rot) - y * math.sin(rot)), cy + s * (x * math.sin(rot) + y * math.cos(rot))


def spring(x0, x1, y, turns=5, amp=34):
    pts = [(x0, y)]
    for k in range(1, 2 * turns + 1):
        x = x0 + (x1 - x0) * (k - 0.5) / (2 * turns)
        pts.append((x, y + (amp if k % 2 else -amp)))
    pts.append((x1, y))
    return pts


def mems(ctx, cx, cy, s, rot, dx, dy, t, lid=0.0):
    """Vista superior del acelerómetro: marco, anclajes, muelles, masa perforada y peines."""
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(rot)
    ctx.scale(s, s)
    soft_ellipse(ctx, 0, 30, 470, 380, (0, 0, 0), 0.55)
    fill_rr(ctx, -390, -310, 780, 620, 34, linear(0, -310, 0, 310, [(0, (0.26, 0.29, 0.36)), (1, (0.11, 0.12, 0.16))]))
    fill_rr(ctx, -350, -270, 700, 540, 22, linear(0, -270, 0, 270, [(0, (0.04, 0.05, 0.08)), (1, (0.07, 0.08, 0.12))]))
    for ax in (-330, 270):
        fill_rr(ctx, ax, -44, 60, 88, 10, (0.36, 0.39, 0.47))
    mx0, mx1, my0, my1 = -200 + dx, 200 + dx, -125 + dy, 125 + dy
    stroke(ctx, spring(-270, mx0, dy * 0.85), (0.70, 0.74, 0.82), 9)
    stroke(ctx, spring(mx1, 270, dy * 0.85), (0.70, 0.74, 0.82), 9)
    # peines: dientes fijos (del marco) y móviles (de la masa)
    for k in range(8):
        x = -175 + 50 * k
        for sgn in (-1, 1):
            base = my0 if sgn < 0 else my1
            fill_rr(ctx, x + dx - 7, base - 92 if sgn < 0 else base, 14, 92, 4, SILVER)
            fx = x + 25
            fill_rr(ctx, fx - 7, -270 if sgn < 0 else 270 - 120, 14, 120, 4, (0.40, 0.44, 0.52))
    fill_rr(ctx, mx0, my0, 400, 250, 14, linear(0, my0, 0, my1, [(0, (0.86, 0.89, 0.95)), (1, (0.50, 0.54, 0.62))]))
    for i in range(7):
        for j in range(4):
            fill_rr(ctx, mx0 + 34 + 52 * i, my0 + 32 + 52 * j, 24, 24, 4, (0.12, 0.14, 0.20))
    glow(ctx, dx, dy, 260, CYAN, 0.12, add=True)
    if lid > 0:  # tapa negra del chip que se levanta
        ctx.save()
        ctx.translate(0, -420 * (1 - lid))
        fill_rr(ctx, -400, -320, 800, 640, 36, rgba((0.07, 0.07, 0.09), lid))
        ctx.restore()
    ctx.restore()


def chip_package(ctx, x, y, size, t, label_p=1.0):
    fill_rr(ctx, x - size / 2 - 8, y - size / 2 - 8, size + 16, size + 16, 14, (0.55, 0.57, 0.62))
    fill_rr(ctx, x - size / 2, y - size / 2, size, size, 12, linear(x - size / 2, y - size / 2, x + size / 2, y + size / 2,
                                                                     [(0, (0.16, 0.16, 0.19)), (1, (0.05, 0.05, 0.07))]))
    for k in range(4):
        off = -size * 0.3 + size * 0.2 * k
        for px, py in ((x + off, y - size / 2 - 8), (x + off, y + size / 2 + 8), (x - size / 2 - 8, y + off), (x + size / 2 + 8, y + off)):
            fill_rr(ctx, px - 9, py - 9, 18, 18, 3, (0.85, 0.75, 0.45))
    disc(ctx, x - size * 0.32, y - size * 0.32, size * 0.05, (0.35, 0.35, 0.40))
    text(ctx, "3-AXIS", x, y, size * 0.13, col=(1, 1, 1, 0.35 * label_p))


def dimension(ctx, x0, x1, y, lab, p, col=WHITE):
    if p <= 0:
        return
    a = clamp(p * 1.5)
    xm = x0 + (x1 - x0) * ease_in_out(p)
    stroke(ctx, [(x0, y - 18), (x0, y + 18)], rgba(col, a), 4)
    stroke(ctx, [(x0, y), (xm, y)], rgba(col, a), 4)
    if p >= 1:
        stroke(ctx, [(x1, y - 18), (x1, y + 18)], rgba(col, a), 4)
    text(ctx, lab, (x0 + x1) / 2, y + 48, 42, col=rgba(col, a), outline=(0, 0, 0, a), ow=7)


def lentil(ctx, x, y, r):
    """Lenteja vista desde arriba: disco plano con el borde más oscuro."""
    soft_ellipse(ctx, x + 8, y + 22, r * 1.05, r * 1.0, (0, 0, 0), 0.5)
    disc(ctx, x, y, r, (0.48, 0.30, 0.14))
    disc(ctx, x, y, r * 0.9, radial(x - r * 0.15, y - r * 0.2, r, [(0, (0.86, 0.62, 0.34)), (1, (0.66, 0.43, 0.20))]))
    soft_ellipse(ctx, x - r * 0.25, y - r * 0.3, r * 0.4, r * 0.22, (1, 1, 1), 0.22)


# ---------- peines vistos de cerca ----------

def combs(ctx, t, shift, hair=0.0, field=0.0):
    if hair > 0:  # sección de un pelo a la misma escala (dientes de 4 µm = 40 px → pelo de 70 µm = 700 px)
        a = clamp(hair)
        disc(ctx, 1230, 980, 350, radial(1150, 900, 420, [(0, rgba((0.45, 0.28, 0.16), a)), (1, rgba((0.25, 0.14, 0.08), a))]))
        for k in range(6):
            ctx.new_sub_path()
            ctx.arc(1230, 980, 350 - 22 * k, math.pi * 0.6, math.pi * 1.4)
            source(ctx, (0, 0, 0, 0.12 * a))
            ctx.set_line_width(3)
            ctx.stroke()
    fill_rr(ctx, 90, 560, 900, 60, 12, linear(0, 560, 0, 620, [(0, (0.88, 0.90, 0.96)), (1, (0.55, 0.58, 0.66))]))
    fill_rr(ctx, 90, 1330, 900, 60, 12, linear(0, 1330, 0, 1390, [(0, (0.44, 0.47, 0.55)), (1, (0.22, 0.24, 0.30))]))
    for k in range(6):
        xm = 170 + 150 * k + shift
        fill_rr(ctx, xm - 20, 610, 40, 540, 8, linear(xm - 20, 0, xm + 20, 0, [(0, (0.62, 0.65, 0.74)), (0.5, (0.92, 0.94, 0.98)), (1, (0.58, 0.61, 0.70))]))
        xf = 245 + 150 * k
        if xf < 990:
            fill_rr(ctx, xf - 20, 790, 40, 545, 8, linear(xf - 20, 0, xf + 20, 0, [(0, (0.30, 0.33, 0.40)), (0.5, (0.52, 0.55, 0.63)), (1, (0.28, 0.31, 0.38))]))
        if field > 0 and xf < 990:  # campo eléctrico entre cada pareja de dientes: más intenso cuanto más cerca
            gap_l = (xf - 20) - (xm + 20)
            inten = clamp(28 / max(6, gap_l)) * field
            for yy in range(820, 1140, 46):
                stroke(ctx, [(xm + 22, yy), (xf - 22, yy)], rgba(CYAN, 0.55 * inten), 4)
            glow(ctx, (xm + xf) / 2, 980, 90, CYAN, 0.35 * inten, add=True)


def signal(ctx, t, x, y, wdt, amp_fn, p):
    if p <= 0:
        return
    fill_rr(ctx, x, y, wdt, 120, 20, (0.02, 0.03, 0.08, 0.7 * p))
    text(ctx, "SEÑAL", x + 22, y + 26, 24, col=(0.65, 0.78, 1.0, p), anchor="left")
    pts = []
    for k in range(80):
        u = k / 79
        tt = t - (1 - u) * 1.2
        pts.append((x + 20 + (wdt - 40) * u, y + 72 - 34 * amp_fn(tt)))
    stroke(ctx, pts, rgba(CYAN, p), 5)


# ---------- escenas ----------

def s_hook(ctx, t):
    tech_bg(ctx, t)
    ta = w(s_hook, "girado") - 0.1
    rotating_phone(ctx, t, 540, 960, 1.0, ta)
    turn_arrow(ctx, 540, 960, 500, prog(t, ta, 0.6))


def xray(c, t):
    fill_rr(c, -170, -360, 340, 720, 40, (0.03, 0.05, 0.08))
    fill_rr(c, -150, -330, 300, 300, 26, (0.08, 0.30, 0.22))
    for (x, y, w_, h_) in [(-120, -300, 110, 70), (20, -300, 100, 100), (-120, -200, 70, 140), (-30, -170, 160, 60)]:
        fill_rr(c, x, y, w_, h_, 8, (0.12, 0.13, 0.16))
    fill_rr(c, -150, -10, 300, 340, 30, (0.12, 0.14, 0.20))
    text(c, "BATERÍA", 0, 160, 30, col=(1, 1, 1, 0.3))
    for k in range(6):
        stroke(c, [(-140 + 50 * k, -30), (-140 + 50 * k + 30, -110)], (0.3, 0.7, 0.5, 0.35), 3)


def s_piece(ctx, t):
    tech_bg(ctx, t)
    jig = 6 * math.sin(t * 9) * prog(t, w(s_piece, "mueve") - 0.1, 0.2)
    phone(ctx, 540 + jig, 980, 1.0, xray, t, cable=False)
    hx, hy = 540 + jig + 50, 980 - 140
    p = appear(t, w(s_piece, "pieza"), 0.4)
    if p > 0:
        pulse = 1 + 0.15 * math.sin(t * 7)
        glow(ctx, hx, hy, 70 * pulse, CYAN, 0.8 * clamp(p), add=True)
        fill_rr(ctx, hx - 18, hy - 18, 36, 36, 6, (0.05, 0.05, 0.07))
        ctx.arc(hx, hy, 46 * pulse, 0, 2 * math.pi)
        source(ctx, rgba(CYAN, clamp(p)))
        ctx.set_line_width(5)
        ctx.stroke()
    tag(ctx, "ACELERÓMETRO", hx + 50, hy, 600, 560, appear(t, w(s_piece, "pieza") + 0.2, 0.5), col=CYAN, size=40)


def s_chip(ctx, t):
    tech_bg(ctx, t)
    # escala: 1 mm = 110 px
    chip_package(ctx, 300, 930, 220, t)
    tag(ctx, "ACELERÓMETRO", 300, 820, 360, 560, appear(t, 0.1, 0.4), col=CYAN, size=40)
    dimension(ctx, 190, 410, 1100, "2 mm", appear(t, w(s_chip, "chip"), 0.5), col=CYAN)
    lp = ease_out_back(appear(t, w(s_chip, "lenteja"), 0.45))
    if lp > 0:
        ctx.save()
        ctx.translate(740, 930)
        ctx.scale(lp, lp)
        lentil(ctx, 0, 0, 250)
        ctx.restore()
        dimension(ctx, 490, 990, 1230, "≈ 5 mm", appear(t, w(s_chip, "lenteja") + 0.3, 0.5), col=ORANGE)
        tag(ctx, "LENTEJA", 840, 800, 880, 640, appear(t, w(s_chip, "lenteja") + 0.1, 0.45), col=ORANGE, size=38)


def s_inside(ctx, t):
    tech_bg(ctx, t)
    lid = 1 - ease_in_out(prog(t, 0.0, 0.7))
    mems(ctx, 540, 960, 1.15, 0.0, 0, 0, t, lid=lid)
    tag(ctx, "MASA", 540, 960, 600, 520, appear(t, w(s_inside, "masa"), 0.45), col=CYAN, size=42)
    tag(ctx, "MUELLES", 270, 960, 330, 1400, appear(t, w(s_inside, "muelles"), 0.45), col=CYAN, size=42)


def s_gravity(ctx, t):
    tech_bg(ctx, t)
    g = ease_in_out(appear(t, w(s_gravity, "tira"), 0.5))
    bob = 3 * math.sin(t * 5) * g
    mems(ctx, 540, 940, 1.15, 0.0, 0, 22 * g + bob, t)
    p = appear(t, w(s_gravity, "gravedad"), 0.4)
    if p > 0:
        a = clamp(p * 1.5)
        y0, y1 = 1000, 1000 + 330 * ease_in_out(p)
        glow(ctx, 540, (y0 + y1) / 2, 160, YELLOW, 0.35 * a, add=True)
        stroke(ctx, [(540, y0), (540, y1)], rgba(YELLOW, a), 18)
        stroke(ctx, [(495, y1 - 50), (540, y1 + 4), (585, y1 - 50)], rgba(YELLOW, a), 18)
        text(ctx, "g", 610, y1 - 60, 90, col=rgba(YELLOW, a), outline=(0, 0, 0, a), ow=8)


def s_shift(ctx, t):
    tech_bg(ctx, t)
    ta = w(s_shift, "giras") - 0.1
    rot = -math.pi / 3 * ease_in_out(prog(t, ta, 0.8))
    # la gravedad sigue apuntando al suelo: en coordenadas del chip, la masa cae hacia su nuevo "abajo"
    gx, gy = 60 * math.sin(-rot), 60 * math.cos(rot) * 0.4 + 14
    mems(ctx, 540, 860, 0.85, rot, gx * 0.6, gy, t)
    stroke(ctx, [(540, 1150), (540, 1260)], rgba(YELLOW, 0.8), 12)
    stroke(ctx, [(508, 1224), (540, 1262), (572, 1224)], rgba(YELLOW, 0.8), 12)
    p = appear(t, w(s_shift, "pelo"), 0.4)
    if p > 0:  # comparación con un pelo
        a = clamp(p * 1.5)
        fill_rr(ctx, 90, 1300, 900, 150, 26, (0.02, 0.03, 0.08, 0.75 * a))
        fill_rr(ctx, 130, 1335, 560 * ease_in_out(p), 36, 18, rgba((0.55, 0.35, 0.20), a))
        text(ctx, "PELO ≈ 70 µm", 720, 1353, 32, col=rgba(WHITE, a), anchor="left")
        fill_rr(ctx, 130, 1402, 6, 22, 2, rgba(CYAN, a))
        text(ctx, "MOVIMIENTO < 1 µm", 160, 1414, 32, col=rgba(CYAN, a), anchor="left")


def s_combs(ctx, t):
    tech_bg(ctx, t)
    combs(ctx, t, 6 * math.sin(t * 3), hair=appear(t, w(s_combs, "pelo"), 0.6))
    tag(ctx, "PEINES DE SILICIO", 470, 700, 600, 470, appear(t, w(s_combs, "peines"), 0.45), col=CYAN, size=38)
    dimension(ctx, 300, 340, 1460 - 40, "4 µm", appear(t, w(s_combs, "finos"), 0.4), col=CYAN)
    tag(ctx, "PELO ≈ 70 µm", 900, 760, 700, 1440, appear(t, w(s_combs, "pelo") + 0.2, 0.5), col=ORANGE, size=36)


def s_measure(ctx, t):
    tech_bg(ctx, t)
    mv = prog(t, w(s_measure, "mueve") - 0.1, 0.3)
    shift = 32 * math.sin(t * 2.6) * mv
    combs(ctx, t, shift, field=appear(t, w(s_measure, "distancia"), 0.4))
    p = appear(t, w(s_measure, "distancia"), 0.4)
    if p > 0:
        a = clamp(p * 1.5)
        xm, xf = 170 + 150 * 2 + shift + 20, 245 + 150 * 2 - 20
        stroke(ctx, [(xm, 760), (xf, 760)], rgba(YELLOW, a), 5)
        for xx in (xm, xf):
            stroke(ctx, [(xx, 740), (xx, 780)], rgba(YELLOW, a), 5)
        tag(ctx, "DISTANCIA", (xm + xf) / 2, 760, 700, 1450, p, col=YELLOW, size=38)
    signal(ctx, t, 90, 440, 900, lambda tt: math.sin(tt * 2.6) * prog(tt, w(s_measure, "mueve") - 0.1, 0.3),
           appear(t, w(s_measure, "mide"), 0.4))


def s_floor(ctx, t):
    tech_bg(ctx, t)
    ta = w(s_floor, "gira") - 0.15
    rotating_phone(ctx, t, 540, 880, 0.85, ta, direction=-1, from_landscape=True)
    p = appear(t, w(s_floor, "suelo"), 0.4)
    if p > 0:
        a = clamp(p * 1.5)
        stroke(ctx, [(140, 1380), (940, 1380)], rgba(WHITE, 0.5 * a), 6)
        for k in range(9):
            stroke(ctx, [(160 + 95 * k, 1384), (130 + 95 * k, 1420)], rgba(WHITE, 0.3 * a), 4)
        stroke(ctx, [(900, 700), (900, 1340)], rgba(YELLOW, a), 14)
        stroke(ctx, [(868, 1300), (900, 1342), (932, 1300)], rgba(YELLOW, a), 14)
        text(ctx, "SUELO", 900, 640, 44, col=rgba(YELLOW, a), outline=(0, 0, 0, a), ow=7)


def footprint(ctx, x, y, left, a):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-1 if left else 1, 1)
    ctx.rotate(0.12)
    ctx.save()
    ctx.scale(42, 70)
    disc(ctx, 0, 0, 1, rgba(CYAN, 0.85 * a))
    ctx.restore()
    for k, (tx, ty, r) in enumerate([(-24, -86, 13), (-4, -96, 12), (14, -92, 11), (28, -82, 9), (38, -68, 8)]):
        disc(ctx, tx, ty, r, rgba(CYAN, 0.85 * a))
    glow(ctx, 0, 0, 110, CYAN, 0.3 * a, add=True)
    ctx.restore()


def s_steps(ctx, t):
    tech_bg(ctx, t)
    t0 = w(s_steps, "cuenta") - 0.2
    steps = int(clamp((t - t0) / 0.38, 0, 7))
    for k in range(steps):
        footprint(ctx, 440 if k % 2 == 0 else 640, 1360 - 125 * k, k % 2 == 0, 1 - 0.08 * (steps - 1 - k))
    pts = []
    for k in range(90):
        u = k / 89
        tt = t - (1 - u) * 2.4
        ph = (tt - t0) / 0.38
        spike = math.exp(-((ph % 1) - 0.15) ** 2 * 60) if tt > t0 else 0.0
        pts.append((110 + 860 * u, 600 - 70 * spike))
    fill_rr(ctx, 90, 460, 900, 190, 24, (0.02, 0.03, 0.08, 0.7))
    text(ctx, "ACELERÓMETRO", 116, 490, 24, col=(0.65, 0.78, 1.0), anchor="left")
    stroke(ctx, pts, CYAN, 5)
    text(ctx, f"PASOS  {1024 + steps:,}".replace(",", "."), 960, 490, 30, col=GREEN, anchor="right")


def s_cta(ctx, t):
    tech_bg(ctx, t)
    rotating_phone(ctx, t, 540, 760, 0.6, 0.4)
    cta_button(ctx, t, 540, 1250)


SCENES = [
    Scene("¿Cómo sabe tu móvil que lo has girado?", s_hook, key="girado", sfx=[("@girado", "whoosh")]),
    Scene("Tiene una pieza que se mueve, aunque no lo notes.", s_piece, key="pieza", sfx=[("@pieza", "pop")]),
    Scene("Se esconde en un chip más pequeño que una lenteja.", s_chip, key="lenteja", sfx=[("@chip", "pop"), ("@lenteja", "pop")]),
    Scene("Por dentro hay una masa diminuta colgada de muelles.", s_inside, key="muelles", sfx=[("@masa", "pop"), ("@muelles", "pop")]),
    Scene("La gravedad siempre tira de ella hacia abajo.", s_gravity, key="gravedad", sfx=[("@gravedad", "thunk")]),
    Scene("Si giras el móvil, la masa se mueve menos que el grosor de un pelo.", s_shift, key="pelo",
          sfx=[("@giras", "whoosh"), ("@pelo", "pop")]),
    Scene("Pegados a ella hay peines de silicio, más finos que un pelo.", s_combs, key="peines", sfx=[("@peines", "pop")]),
    Scene("Cuando se mueve, cambia la distancia entre los dientes, y el chip lo mide.", s_measure, key="distancia",
          sfx=[("@distancia", "pop")]),
    Scene("Por eso sabe dónde está el suelo y gira la pantalla.", s_floor, key="suelo", sfx=[("@suelo", "pop"), ("@gira", "whoosh")]),
    Scene("La misma pieza cuenta tus pasos.", s_steps, key="pasos", sfx=[("@cuenta", "tick"), ("@pasos", "tick")]),
    Scene("Síguenos para más curiosidades.", s_cta, key="curiosidades", sfx=[(0.05, "pop"), (1.3, "pop")]),
]

POST = """¿Cómo sabe tu móvil que lo has girado? 📱

Tiene una pieza que se mueve: una masa de silicio colgada de muelles, dentro de un chip de 2 mm. La gravedad tira de ella y unos peines más finos que un pelo miden cuánto se desplaza. Así sabe dónde está el suelo… y cuenta tus pasos.

¿Sabías que tu móvil tenía piezas que se mueven? 👇

#curiosidades #tecnologia #movil #ciencia #sabiasque
"""

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "out", "giro-movil")
    os.makedirs(out, exist_ok=True)
    narrator = None
    if "--sin-voz" not in sys.argv:
        from voz import Narrator
        voice = sys.argv[sys.argv.index("--voz") + 1] if "--voz" in sys.argv else "santa"
        narrator = Narrator(voice, speed=1.14)
    if "--preview" in sys.argv:
        i = sys.argv.index("--preview")
        dest = sys.argv[i + 1] if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith("--") else os.path.join(out, "preview.png")
        preview(SCENES, dest, narrator=narrator, style=TOP)
        print("preview:", dest)
    else:
        total = render(SCENES, os.path.join(out, "giro-movil.mp4"), cover_png=os.path.join(out, "fotograma.png"),
                       cover_at=(0, 1.5), narrator=narrator, style=TOP)
        os.remove(os.path.join(out, "fotograma.png"))
        with open(os.path.join(out, "texto-del-post.txt"), "w") as f:
            f.write(POST)
        print(f"OK: {total:.1f} s")
