"""Vídeo: ¿sabías que Lamborghini nació por un insulto de Ferrari? (tema 25, lote 2: marcas famosas)

Gancho de rivalidad → tractores → sus Ferrari fallan → se queja y Ferrari le desprecia → funda su marca →
dato wow (el toro, porque era Tauro) → pregunta fácil (¿Ferrari o Lamborghini?). La pelea es una anécdota
contada por el propio Ferruccio, así que va como «según contaba él».

Datos y fuentes:
- Ferruccio Lamborghini (28-4-1916) fundó Lamborghini Trattori en 1948 y Automobili Lamborghini en 1963.
  Sus Ferrari 250 GT tenían embragues malos que había que llevar una y otra vez a Maranello; se quejó a
  Enzo Ferrari y este le despreció. En una entrevista de 1991 (Thoroughbred & Classic Cars) Ferruccio contó
  que Enzo le dijo: «Lamborghini, puede que sepas conducir un tractor, pero nunca sabrás manejar un
  Ferrari», y que entonces decidió hacer el coche perfecto. Wikipedia advierte que es «tanto leyenda como
  hecho» y que pesaron también motivos económicos: https://en.wikipedia.org/wiki/Ferruccio_Lamborghini
- Las versiones de la anécdota cambian (si se vieron en persona, si el embrague era el de sus tractores):
  https://jalopnik.com/1759745487 · https://www.lambocars.com/ferruccio-lamborghini-a-biography/
  Lo de «el embrague era la misma pieza que la de sus tractores» se deja fuera: no hay fuente sólida.
- El toro: Ferruccio era Tauro y le apasionaban los toros de lidia: https://en.wikipedia.org/wiki/Lamborghini
- No se copian logos: coches, tractor y toro están dibujados y son genéricos.

Uso: python3 video/lamborghini_ferrari.py [--voz santa|dora|alex|eleven] [--sin-voz]  ->  video/out/lamborghini-ferrari/
     python3 video/lamborghini_ferrari.py --preview [png]
"""
import math
import os
import sys

import cairo

from engine import clamp, ease_in_out, ease_out_back
from piezas import RED, WHITE, appear, bolt, mini_tag, panel, person, spaced, tech_bg
from rich import (TOP_SHORT, YELLOW, Scene, badge, bezier, disc, fill_rr, glow, linear, mix, mul, poly, preview,
                  radial, render, rgba, soft_ellipse, source, stroke, text, word_time)

OUT = "lamborghini-ferrari"
FER = (0.86, 0.09, 0.10)
LAMBO = (1.0, 0.74, 0.06)
TRAC = (0.22, 0.45, 0.80)
GOLD = (0.95, 0.72, 0.22)
SKY = (0.55, 0.65, 0.80)


def scene_of(fn):
    return next(s for s in SCENES if s.draw is fn)


def dur(fn):
    return scene_of(fn).duration


def w(fn, needle):
    """Instante (s) en que la voz dice la primera palabra de la escena que contiene `needle`."""
    return word_time(scene_of(fn), needle)


# ---------- coches y tractor (genéricos, sin marcas) ----------

def wheel(ctx, x, y, r, t, spin=1.0, rim=(0.78, 0.80, 0.85)):
    disc(ctx, x, y, r, (0.05, 0.05, 0.06))
    disc(ctx, x, y, r * 0.62, radial(x - r * 0.2, y - r * 0.2, r * 0.8, [(0, mix(rim, WHITE, 0.4)), (1, mul(rim, 0.6))]))
    a0 = -t * 9 * spin
    for k in range(10):
        a = a0 + k * math.pi / 5
        stroke(ctx, [(x, y), (x + r * 0.58 * math.cos(a), y + r * 0.58 * math.sin(a))], (0.35, 0.36, 0.40), 3)
    disc(ctx, x, y, r * 0.16, (0.25, 0.26, 0.30))


def _gt_path(ctx):
    ctx.new_path()
    ctx.move_to(-300, -36)
    ctx.curve_to(-314, -70, -302, -100, -255, -112)
    ctx.curve_to(-200, -150, -140, -172, -60, -172)
    ctx.curve_to(-10, -172, 30, -150, 70, -118)
    ctx.curve_to(150, -108, 260, -104, 305, -88)
    ctx.curve_to(326, -78, 326, -50, 312, -34)
    ctx.close_path()


def _wedge_path(ctx):
    path_pts = [(-322, -40), (-326, -96), (-205, -122), (-70, -152), (150, -100), (318, -64), (324, -40)]
    ctx.new_path()
    ctx.move_to(*path_pts[0])
    for p in path_pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()


def car(ctx, x, y, s, col, t, kind="gt", spin=0.0, flip=False, shake=0.0, blue=0.0):
    """Coche de perfil con el morro a la derecha (flip lo gira). kind: "gt" (gran turismo de los 60)
    o "wedge" (deportivo en cuña). (x, y) es el punto del suelo bajo el centro. blue lo tapa con su plano."""
    ctx.save()
    ctx.translate(x + shake * 6 * math.sin(t * 60), y)
    ctx.scale(-s if flip else s, s)
    soft_ellipse(ctx, 0, 4, 340, 26, (0, 0, 0), 0.6)
    (_gt_path if kind == "gt" else _wedge_path)(ctx)
    ctx.set_source(linear(0, -172, 0, -34, [(0, mix(col, WHITE, 0.28)), (0.45, col), (1, mul(col, 0.5))]))
    ctx.fill_preserve()
    ctx.save()
    ctx.clip()  # pasos de rueda y detalles, dentro de la carrocería
    wheels = (-190, 200) if kind == "gt" else (-205, 195)
    for wx in wheels:
        disc(ctx, wx, -50, 64, (0.04, 0.04, 0.05))
    if kind == "wedge":
        poly(ctx, [(-150, -58), (-70, -100), (-40, -58)], (0.05, 0.05, 0.06))  # toma de aire
    ctx.restore()
    if kind == "gt":
        glass = [(-205, -116), (-125, -158), (-40, -160), (35, -120)]
        poly(ctx, glass, linear(0, -160, 0, -116, [(0, (0.60, 0.70, 0.85)), (1, (0.12, 0.15, 0.22))]))
        stroke(ctx, [(-92, -158), (-98, -117)], mul(col, 0.5), 5)
        stroke(ctx, bezier((-290, -82), (-150, -100), (100, -98), (302, -82), 20), rgba(WHITE, 0.35), 3)
        soft_ellipse(ctx, 300, -72, 14, 10, (1, 0.95, 0.75), 1.0)
    else:
        glass = [(-175, -120), (-70, -144), (95, -106), (-150, -106)]
        poly(ctx, glass, linear(0, -144, 0, -106, [(0, (0.60, 0.70, 0.85)), (1, (0.12, 0.15, 0.22))]))
        stroke(ctx, [(-320, -90), (-200, -114), (-70, -144), (150, -98), (316, -62)], rgba(WHITE, 0.35), 3)
        fill_rr(ctx, 280, -66, 34, 8, 4, (1, 0.95, 0.75))
    for wx in wheels:
        wheel(ctx, wx, -50, 50, t, spin=spin)
    if blue > 0:  # plano: relleno azul y contorno discontinuo que corre
        (_gt_path if kind == "gt" else _wedge_path)(ctx)
        source(ctx, (0.05, 0.14, 0.28, 0.95 * blue))
        ctx.fill_preserve()
        ctx.set_dash([16, 9], -t * 40)
        source(ctx, (0.45, 0.80, 1.0, blue))
        ctx.set_line_width(4)
        ctx.stroke()
        for wx in wheels:
            ctx.new_sub_path()
            ctx.arc(wx, -50, 50, 0, 2 * math.pi)
            ctx.stroke()
        ctx.set_dash([])
    ctx.restore()


def tractor(ctx, x, y, s, t, spin=1.0, col=TRAC):
    """Tractor de los años 50 de perfil (morro a la derecha), con humo por el escape."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    soft_ellipse(ctx, 20, 4, 290, 24, (0, 0, 0), 0.6)
    for k in range(4):  # humo
        u = (t * 0.8 + k / 4) % 1
        disc(ctx, 130 + 40 * u + 10 * math.sin(k * 2 + t), -290 - 170 * u, 14 + 28 * u, (0.55, 0.55, 0.58, 0.45 * (1 - u)))
    stroke(ctx, [(130, -190), (130, -290)], (0.22, 0.22, 0.25), 14)
    fill_rr(ctx, -60, -120, 270, 40, 12, mul(col, 0.45))
    fill_rr(ctx, -60, -205, 300, 100, 22, linear(0, -205, 0, -105, [(0, mix(col, WHITE, 0.3)), (1, mul(col, 0.6))]))
    fill_rr(ctx, 222, -196, 26, 80, 8, (0.12, 0.12, 0.14))
    for k in range(5):
        stroke(ctx, [(226, -186 + 15 * k), (244, -186 + 15 * k)], (0.4, 0.4, 0.45), 3)
    stroke(ctx, [(-50, -200), (-84, -268)], (0.2, 0.2, 0.22), 8)  # columna del volante
    ctx.save()
    ctx.translate(-88, -272)
    ctx.scale(1, 0.28)
    ctx.new_sub_path()
    ctx.arc(0, 0, 36, 0, 2 * math.pi)
    ctx.restore()
    source(ctx, (0.15, 0.15, 0.17))
    ctx.set_line_width(7)
    ctx.stroke()
    fill_rr(ctx, -190, -245, 74, 22, 8, (0.15, 0.15, 0.17))  # asiento
    stroke(ctx, [(-150, -225), (-140, -170)], (0.15, 0.15, 0.17), 10)
    rear, front = (-135, -112, 112), (195, -56, 56)
    ctx.new_sub_path()  # guardabarros
    ctx.arc(rear[0], rear[1], 128, math.pi * 1.02, math.pi * 1.98)
    source(ctx, col)
    ctx.set_line_width(20)
    ctx.stroke()
    for cx, cy, r in (rear, front):
        disc(ctx, cx, cy, r, (0.06, 0.06, 0.07))
        a0 = -t * 6 * spin * 112 / r
        for k in range(18 if r > 80 else 12):  # tacos del neumático
            a = a0 + k * 2 * math.pi / (18 if r > 80 else 12)
            stroke(ctx, [(cx + r * 0.86 * math.cos(a), cy + r * 0.86 * math.sin(a)),
                         (cx + r * 1.02 * math.cos(a + 0.12), cy + r * 1.02 * math.sin(a + 0.12))], (0.18, 0.18, 0.2), r * 0.12)
        disc(ctx, cx, cy, r * 0.55, radial(cx - r * 0.15, cy - r * 0.15, r * 0.7, [(0, (0.98, 0.98, 1)), (1, (0.70, 0.72, 0.78))]))
        disc(ctx, cx, cy, r * 0.18, mul(col, 0.7))
    ctx.restore()


def ground(ctx, y, t, speed=0.0, field=False):
    """Suelo: carretera con línea discontinua que corre, o campo arado."""
    if field:
        ctx.rectangle(0, y, 1080, 1920 - y)
        ctx.set_source(linear(0, y, 0, 1920, [(0, (0.30, 0.22, 0.13)), (1, (0.10, 0.07, 0.05))]))
        ctx.fill()
        for k in range(8):
            yy = y + 30 + k * k * 9
            stroke(ctx, [(0, yy), (1080, yy)], (0, 0, 0, 0.25), 3 + k)
        return
    ctx.rectangle(0, y, 1080, 230)
    ctx.set_source(linear(0, y, 0, y + 230, [(0, (0.12, 0.12, 0.14)), (1, (0.05, 0.05, 0.06))]))
    ctx.fill()
    off = (t * speed) % 160
    for k in range(-1, 9):
        x0 = k * 160 - off
        fill_rr(ctx, x0, y + 110, 90, 12, 6, (1, 1, 1, 0.55))


# ---------- piezas ----------

def clutch(ctx, x, y, r, t, broken=0.0):
    """Disco de embrague: forro con remaches, placa con muelles y cubo estriado."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(t * (1.2 - 1.1 * broken))
    disc(ctx, 0, 0, r, radial(0, 0, r, [(0, (0.35, 0.28, 0.22)), (0.75, (0.47, 0.38, 0.29)), (1, (0.28, 0.22, 0.17))]))
    for k in range(16):
        a = k * math.pi / 8
        disc(ctx, 0.82 * r * math.cos(a), 0.82 * r * math.sin(a), r * 0.035, (0.78, 0.72, 0.62))
    disc(ctx, 0, 0, r * 0.62, radial(-r * 0.2, -r * 0.2, r * 0.8, [(0, (0.85, 0.87, 0.92)), (1, (0.45, 0.47, 0.53))]))
    for k in range(6):
        ctx.save()
        ctx.rotate(k * math.pi / 3)
        fill_rr(ctx, r * 0.28, -r * 0.09, r * 0.24, r * 0.18, r * 0.05, (0.35, 0.37, 0.42))
        for j in range(4):
            stroke(ctx, [(r * (0.31 + 0.055 * j), -r * 0.08), (r * (0.31 + 0.055 * j), r * 0.08)], (0.62, 0.65, 0.72), 2)
        ctx.restore()
    disc(ctx, 0, 0, r * 0.2, (0.2, 0.21, 0.24))
    disc(ctx, 0, 0, r * 0.09, (0.05, 0.05, 0.06))
    if broken > 0:
        a = clamp(broken * 2)
        for pts in ([(0.95, -0.2), (0.7, -0.1), (0.62, -0.28), (0.4, -0.2)], [(-0.9, 0.4), (-0.66, 0.3), (-0.6, 0.46)],
                    [(0.1, 0.96), (0.05, 0.72), (0.2, 0.64)]):
            stroke(ctx, [(r * px, r * py) for px, py in pts], (0.05, 0.02, 0.02, a), 6, close=False)
    ctx.restore()
    if broken > 0:
        glow(ctx, x, y, r * 1.5, RED, 0.45 * broken * (0.75 + 0.25 * math.sin(t * 14)), add=True)


def warning(ctx, x, y, s, p):
    if p <= 0:
        return
    k = ease_out_back(p) * s
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    poly(ctx, [(0, -52), (56, 44), (-56, 44)], YELLOW)
    stroke(ctx, [(0, -52), (56, 44), (-56, 44)], mul(YELLOW, 0.6), 6, close=True)
    text(ctx, "!", 0, 10, 58, col=(0.1, 0.08, 0.02))
    ctx.restore()


def coins(ctx, x, y, n, t):
    """Montón de monedas que crece (n puede ser fraccionario)."""
    for k in range(int(n)):
        yy = y - 18 * k
        ctx.save()
        ctx.translate(x + 3 * math.sin(k * 1.7), yy)
        ctx.scale(1, 0.32)
        disc(ctx, 0, 0, 70, mul(GOLD, 0.65))
        ctx.restore()
        ctx.save()
        ctx.translate(x + 3 * math.sin(k * 1.7), yy - 8)
        ctx.scale(1, 0.32)
        disc(ctx, 0, 0, 70, radial(-20, -20, 90, [(0, mix(GOLD, WHITE, 0.4)), (1, GOLD)]))
        ctx.restore()
    if n >= 1:
        glow(ctx, x, y - 18 * int(n), 120, GOLD, 0.35, add=True)


def bubble(ctx, x, y, w_, h, tip, p, draw=None):
    """Bocadillo de cómic que aparece con rebote, con el pico hacia `tip`; draw(ctx) pinta el contenido."""
    if p <= 0:
        return
    s = ease_out_back(p)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    tx, ty = (tip[0] - x) / max(s, 0.01), (tip[1] - y) / max(s, 0.01)
    poly(ctx, [(-34, h / 2 - 20), (34, h / 2 - 20), (tx, ty)], (0.97, 0.97, 0.99))
    fill_rr(ctx, -w_ / 2, -h / 2, w_, h, 46, (0.97, 0.97, 0.99))
    if draw:
        draw(ctx)
    ctx.restore()


def factory(ctx, x, y, s):
    """Nave industrial con tejado de dientes de sierra y chimenea."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    stroke(ctx, [(170, -330), (170, -470)], (0.30, 0.30, 0.34), 30)
    pts = [(-220, 0), (-220, -300)]
    for k in range(4):
        pts += [(-220 + 110 * k + 110, -390), (-220 + 110 * k + 110, -300)]
    pts += [(220, 0)]
    poly(ctx, pts, linear(0, -390, 0, 0, [(0, (0.42, 0.40, 0.42)), (1, (0.22, 0.21, 0.23))]))
    for k in range(4):
        fill_rr(ctx, -190 + 105 * k, -250, 70, 90, 6, (1.0, 0.85, 0.5, 0.75))
    fill_rr(ctx, -70, -150, 140, 150, 8, (0.12, 0.11, 0.12))
    ctx.restore()


def bull_head(ctx, x, y, s, a=1.0):
    """Cabeza de toro de frente, enfadada (no es el escudo de la marca)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for sd in (-1, 1):
        outer = bezier((sd * 60, -40), (sd * 150, -40), (sd * 195, -110), (sd * 150, -195), 16)
        inner = bezier((sd * 150, -195), (sd * 168, -118), (sd * 130, -72), (sd * 55, -72), 16)
        poly(ctx, outer + inner, (0.96, 0.92, 0.82, a))
        poly(ctx, [(sd * 70, -42), (sd * 150, -16), (sd * 82, 8)], rgba(mul(GOLD, 0.62), a))
    ctx.new_path()
    ctx.move_to(-76, -72)
    ctx.curve_to(-84, 10, -62, 60, -52, 98)
    ctx.line_to(52, 98)
    ctx.curve_to(62, 60, 84, 10, 76, -72)
    ctx.curve_to(40, -98, -40, -98, -76, -72)
    ctx.close_path()
    ctx.set_source(linear(0, -98, 0, 98, [(0, rgba(mix(GOLD, WHITE, 0.25), a)), (1, rgba(mul(GOLD, 0.55), a))]))
    ctx.fill()
    ctx.save()
    ctx.translate(0, 88)
    ctx.scale(1, 0.62)
    disc(ctx, 0, 0, 64, rgba(mix(GOLD, WHITE, 0.45), a))
    ctx.restore()
    for sd in (-1, 1):
        disc(ctx, sd * 24, 92, 10, (0.25, 0.15, 0.05, a))
        disc(ctx, sd * 34, -12, 10, (0.08, 0.05, 0.02, a))
        stroke(ctx, [(sd * 62, -40), (sd * 16, -26)], (0.25, 0.15, 0.05, a), 8)
    ctx.restore()


def taurus(ctx, x, y, s, col, a=1.0):
    """El símbolo de Tauro: un círculo con dos cuernos encima."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.new_sub_path()
    ctx.arc(0, 30, 50, 0, 2 * math.pi)
    ctx.new_sub_path()
    ctx.arc(0, -82, 62, math.pi * 0.12, math.pi * 0.88)
    source(ctx, rgba(col, a))
    ctx.set_line_width(14)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.restore()


def sunglasses(ctx, x, y, s, look):
    ex = x + s * 40 * look
    fill_rr(ctx, ex - 40 * s, y - 6 * s, 80 * s, 30 * s, 12 * s, (0.04, 0.04, 0.05))
    stroke(ctx, [(ex - 40 * s * look, y + 2 * s), (x - 70 * s * look, y - 2 * s)], (0.04, 0.04, 0.05), 6 * s)


# ---------- escenas ----------

def s_hook(ctx, t):
    tech_bg(ctx, t)
    ground(ctx, 1250, t)
    hit = appear(t, w(s_hook, "insulto"), 0.35)
    glow(ctx, 540, 1150, 170, YELLOW, 0.22 * (0.6 + 0.4 * math.sin(t * 23)), add=True)  # chispas entre los morros
    for k in range(5):
        a = k * 1.3 + t * 7
        stroke(ctx, [(540, 1150), (540 + 60 * math.cos(a), 1150 + 40 * math.sin(a))], rgba(YELLOW, 0.5 * abs(math.sin(t * 11 + k))), 3)
    car(ctx, 268, 1250, 0.82, FER, t, shake=0.3 * hit * (1 - clamp((t - w(s_hook, "insulto")) / 0.8)))
    car(ctx, 812, 1250, 0.82, LAMBO, t, kind="wedge", flip=True, shake=hit * (1 - clamp((t - w(s_hook, "insulto")) / 1.2)))
    if hit > 0:
        glow(ctx, 540, 1130, 280, YELLOW, 0.5 * hit, add=True)
        bolt(ctx, 540, 1130, 1.7 * ease_out_back(hit), YELLOW)

    def grawlix(c):
        text(c, "#@%!", 0, 0, 74, col=RED)
    bubble(ctx, 300, 820, 330, 170, (280, 1100), hit, grawlix)
    spaced(ctx, "FERRARI", 268, 1420, 34, col=rgba(FER, 0.9 * appear(t, w(s_hook, "Ferrari"), 0.4)), anchor="center")
    spaced(ctx, "LAMBORGHINI", 790, 1420, 34, col=rgba(LAMBO, 0.9 * appear(t, w(s_hook, "Lamborghini"), 0.4)), anchor="center")


def s_tractors(ctx, t):
    tech_bg(ctx, t)
    ground(ctx, 1330, t, field=True)
    tractor(ctx, 420, 1330, 1.1, t)
    rich_ = clamp((t - w(s_tractors, "rico") + 0.1) / 0.9)
    coins(ctx, 860, 1320, 7 * ease_in_out(rich_), t)
    mini_tag(ctx, "1948 · TRACTORES", 520, 1130, 560, 860, appear(t, w(s_tractors, "tractores"), 0.4), col=SKY)
    mini_tag(ctx, "FERRUCCIO LAMBORGHINI", 230, 1060, 300, 700, appear(t, w(s_tractors, "creador"), 0.4), col=WHITE)


def s_cars(ctx, t):
    tech_bg(ctx, t)
    spots = [(300, 1000, "dinero"), (780, 1000, "cuantos"), (540, 1420, "Ferrari")]
    for x, y, word in spots:
        p = appear(t, w(s_cars, word), 0.4)
        soft_ellipse(ctx, x, y + 10, 260, 40, (1, 1, 1), 0.06 * p)
        ctx.push_group()
        ctx.translate(x, y)
        k = 0.9 + 0.1 * ease_out_back(p)
        ctx.scale(k, k)
        car(ctx, 0, 0, 0.62, FER, t)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(0.12 + 0.88 * p)
    mini_tag(ctx, "FERRARI 250 GT", 560, 1330, 600, 1180, appear(t, w(s_cars, "Ferrari") + 0.2, 0.4), col=FER)


def s_clutch(ctx, t):
    tech_bg(ctx, t)
    ground(ctx, 1450, t)
    fail = appear(t, w(s_clutch, "fallaba"), 0.4)
    car(ctx, 540, 1450, 1.0, FER, t, shake=0.4 * fail)
    if fail > 0:  # humo bajo el coche
        for k in range(5):
            u = (t * 0.9 + k / 5) % 1
            disc(ctx, 520 + 60 * math.sin(k * 2.1) + 120 * u, 1400 - 200 * u, 20 + 40 * u, (0.6, 0.6, 0.62, 0.45 * (1 - u) * fail))
    zoom = appear(t, w(s_clutch, "embrague"), 0.45)
    if zoom > 0:
        k = ease_out_back(zoom)
        stroke(ctx, [(540, 1360), (540, 1060)], rgba(WHITE, 0.4 * zoom), 3)
        disc(ctx, 540, 840, 230 * k, (0.05, 0.05, 0.07, 0.92))
        ctx.save()
        ctx.new_sub_path()
        ctx.arc(540, 840, 225 * k, 0, 2 * math.pi)
        ctx.clip()
        clutch(ctx, 540, 840, 180 * k, t, broken=fail)
        ctx.restore()
        ctx.new_sub_path()
        ctx.arc(540, 840, 230 * k, 0, 2 * math.pi)
        source(ctx, rgba(WHITE, 0.6 * zoom))
        ctx.set_line_width(5)
        ctx.stroke()
        mini_tag(ctx, "EMBRAGUE", 640, 650, 600, 560, zoom, col=WHITE)
    for word, (x, y) in (("una", (210, 760)), ("otra", (870, 900)), ("vez", (230, 1050))):
        warning(ctx, x, y, 0.9, appear(t, w(s_clutch, word), 0.3))


def s_complain(ctx, t):
    tech_bg(ctx, t)
    person(ctx, 250, 1160, 0.95, look=1)
    factory(ctx, 770, 1450, 0.95)
    car(ctx, 770, 1460, 0.42, FER, t)
    mini_tag(ctx, "MARANELLO", 770, 1080, 700, 650, appear(t, w(s_complain, "fábrica"), 0.4), col=FER)

    def angry(c):
        clutch(c, -60, 0, 52, t, broken=1.0)
        text(c, "!!", 60, 0, 90, col=RED)
    bubble(ctx, 300, 760, 300, 190, (260, 1040), appear(t, w(s_complain, "quejarse"), 0.4), angry)
    spaced(ctx, "SEGÚN CONTABA ÉL EN 1991", 540, 1585, 26, col=(1, 1, 1, 0.75 * appear(t, w(s_complain, "contaba"), 0.4)),
           anchor="center")


def s_reply(ctx, t):
    tech_bg(ctx, t)
    person(ctx, 230, 1200, 0.9, look=1)
    mad = appear(t, w(s_reply, "enfadado"), 0.4)
    if mad > 0:
        glow(ctx, 850, 1180, 260, RED, 0.45 * mad * (0.8 + 0.2 * math.sin(t * 12)), add=True)
    person(ctx, 850, 1200, 0.9, look=-1)
    sunglasses(ctx, 850, 1200, 0.9, -1)
    spaced(ctx, "FERRUCCIO", 230, 1020, 28, col=LAMBO, anchor="center")
    spaced(ctx, "ENZO FERRARI", 850, 1020, 28, col=FER, anchor="center")
    yes = appear(t, w(s_reply, "tractor"), 0.4)
    no = appear(t, w(s_reply, "nunca"), 0.4)

    def answer(c):
        tractor(c, -130, 50, 0.32, t)
        badge(c, -130, -70, yes, ok=True, r=34)
        car(c, 140, 40, 0.34, FER, t)
        badge(c, 140, -70, no, ok=False, r=34)
    bubble(ctx, 600, 760, 520, 260, (790, 1010), appear(t, w(s_reply, "contestó"), 0.4), answer)


def s_perfect(ctx, t):
    tech_bg(ctx, t)
    ground(ctx, 1380, t)
    rev = appear(t, w(s_perfect, "perfecto") - 0.3, 0.6)
    if rev > 0:  # foco desde arriba
        poly(ctx, [(470, 560), (610, 560), (900, 1390), (180, 1390)], (1, 0.95, 0.75, 0.10 * rev))
        glow(ctx, 540, 1300, 420, LAMBO, 0.35 * rev, add=True)
    if rev < 1:  # cuadrícula del plano
        for k in range(13):
            a = 0.25 * (1 - rev)
            stroke(ctx, [(160 + 63 * k, 1020), (160 + 63 * k, 1380)], (0.45, 0.80, 1.0, a), 2)
        for k in range(7):
            stroke(ctx, [(160, 1020 + 60 * k), (920, 1020 + 60 * k)], (0.45, 0.80, 1.0, 0.25 * (1 - rev)), 2)
    car(ctx, 540, 1380, 0.95 * (1 + 0.05 * ease_out_back(rev)), LAMBO, t, blue=1 - rev)
    for j in range(8):
        u = (t * 0.7 + j / 8) % 1
        if rev > 0:
            disc(ctx, 240 + 600 * ((j * 0.37) % 1), 1300 - 380 * u, 5, (1, 1, 0.85, rev * (1 - u)))
    panel(ctx, 580, 470, "NACE LAMBORGHINI", "1963", "", appear(t, w(s_perfect, "decidió"), 0.4), col=LAMBO, wdt=400)


def s_bull(ctx, t):
    tech_bg(ctx, t)
    bull = appear(t, w(s_bull, "toro"), 0.5)
    sign = appear(t, w(s_bull, "Tauro"), 0.5)
    ring = appear(t, 0.05, 0.5)
    ctx.save()  # rueda del zodiaco que gira despacio
    ctx.translate(540, 930)
    ctx.rotate(t * 0.15)
    ctx.new_sub_path()
    ctx.arc(0, 0, 340, 0, 2 * math.pi)
    source(ctx, rgba(GOLD, 0.35 * ring))
    ctx.set_line_width(4)
    ctx.stroke()
    for k in range(12):
        a = k * math.pi / 6
        stroke(ctx, [(318 * math.cos(a), 318 * math.sin(a)), (362 * math.cos(a), 362 * math.sin(a))], rgba(GOLD, 0.5 * ring), 4)
        disc(ctx, 340 * math.cos(a + math.pi / 12), 340 * math.sin(a + math.pi / 12), 7, rgba(GOLD, 0.6 * ring))
    ctx.restore()
    if bull > 0:
        glow(ctx, 540, 900, 420, GOLD, 0.35 * bull, add=True)
        bull_head(ctx, 540, 930, 1.6 * ease_out_back(bull), a=clamp(bull * 2))
    if sign > 0:
        glow(ctx, 540, 1400, 200, YELLOW, 0.4 * sign, add=True)
        taurus(ctx, 540, 1420, 1.15 * ease_out_back(sign), YELLOW, clamp(sign * 2))
        spaced(ctx, "TAURO · 28 DE ABRIL DE 1916", 540, 1575, 30, col=(1, 1, 1, 0.8 * sign), anchor="center")


def s_ask(ctx, t):
    tech_bg(ctx, t)
    f = appear(t, w(s_ask, "Ferrari"), 0.4)
    lb = appear(t, w(s_ask, "Lamborghini"), 0.4)
    for y, col, kind, name, on in ((930, FER, "gt", "FERRARI", f), (1420, LAMBO, "wedge", "LAMBORGHINI", lb)):
        if on > 0:
            glow(ctx, 540, y - 80, 380, col, 0.3 * on, add=True)
        car(ctx, 540, y, 0.8 * (1 + 0.06 * ease_out_back(on)), col, t, kind=kind)
        spaced(ctx, name, 540, y - 230, 44, col=rgba(col if on > 0.5 else WHITE, 0.45 + 0.55 * on), anchor="center")
    text(ctx, "VS", 540, 1060, 70, col=(1, 1, 1, 0.85), outline=(0, 0, 0, 0.6), ow=10)


SCENES = [
    Scene("¿Sabías que Lamborghini nació por un insulto de Ferrari?", s_hook, key="insulto",
          sfx=[("@insulto", "whoosh")]),
    Scene("Su creador, Ferruccio Lamborghini, fabricaba tractores y se hizo rico.", s_tractors, key="tractores",
          voice="Su creador, Ferruchio Lamborghini, fabricaba tractores y se hizo rico.",
          sfx=[("@tractores", "pop"), ("@rico", "pop"), ("@rico+0.3", "pop"), ("@rico+0.6", "pop")]),
    Scene("Con ese dinero se compró unos cuantos Ferrari.", s_cars, key="Ferrari",
          sfx=[("@dinero", "pop"), ("@cuantos", "pop"), ("@Ferrari", "pop")]),
    Scene("Pero el embrague fallaba una y otra vez.", s_clutch, key="embrague",
          sfx=[("@embrague", "pop"), ("@fallaba", "thunk"), ("@una", "tick"), ("@otra", "tick"), ("@vez", "tick")]),
    Scene("Según contaba él, fue a quejarse a la fábrica de Ferrari.", s_complain, key="quejarse",
          sfx=[("@quejarse", "pop"), ("@fábrica", "pop")]),
    Scene("Muy enfadado, el dueño de Ferrari le contestó: «Sabrás llevar un tractor, pero nunca un Ferrari».", s_reply,
          key="nunca", sfx=[("@enfadado", "thunk"), ("@contestó", "pop"), ("@tractor", "pop"), ("@nunca", "thunk")]),
    Scene("Tan picado se quedó que decidió fabricar el coche perfecto.", s_perfect, key="perfecto",
          sfx=[("@perfecto", "whoosh")]),
    Scene("Por cierto, eligió un toro como emblema porque era Tauro.", s_bull, key="toro",
          sfx=[("@toro", "boom"), ("@Tauro", "pop")]),
    Scene("¿Con cuál te quedas: Ferrari o Lamborghini?", s_ask, key="Lamborghini", duration=3.6,
          sfx=[("@Ferrari", "pop"), ("@Lamborghini", "pop")]),
]

POST = """¿Sabías que Lamborghini nació por un insulto de Ferrari? 🏎️
¿Con cuál te quedas: Ferrari o Lamborghini?
"""

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "out", OUT)
    os.makedirs(out, exist_ok=True)
    narrator = None
    if "--sin-voz" not in sys.argv:
        from voz import narrator_from_args
        narrator = narrator_from_args(sys.argv, speed=1.04)  # ritmo natural: acelerar Kokoro suena más artificial
        narrator.gap = 0.22
        narrator.min_scene = 1.6
    if "--preview" in sys.argv:
        i = sys.argv.index("--preview")
        dest = sys.argv[i + 1] if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith("--") else os.path.join(out, "preview.png")
        preview(SCENES, dest, narrator=narrator, style=TOP_SHORT)
        print("preview:", dest)
    else:
        total = render(SCENES, os.path.join(out, f"{OUT}.mp4"), cover_png=os.path.join(out, "fotograma.png"),
                       cover_at=(0, 1.5), narrator=narrator, style=TOP_SHORT)
        os.remove(os.path.join(out, "fotograma.png"))
        with open(os.path.join(out, "texto-del-post.txt"), "w") as f:
            f.write(POST)
        print(f"OK: {total:.1f} s")
