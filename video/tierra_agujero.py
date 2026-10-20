"""Vídeo: ¿Qué pasaría si saltaras por un agujero que atraviesa la Tierra?

Datos: con la densidad real de la Tierra, la caída de polo a polo dura unos 38 min
(Klotz, American Journal of Physics, 2015). Velocidad máxima en el centro: más de
28.000 km/h (28.460 km/h con densidad uniforme, algo más con la real). El pozo
de Kola llegó a 12.262 m. Núcleo interno: unos 5.200 °C; superficie del Sol: unos 5.500 °C.

Uso: python3 video/tierra_agujero.py            ->  vídeo en video/out/tierra-agujero/
     python3 video/tierra_agujero.py --preview  ->  hoja de contactos
"""
import math
import os
import random
import sys

import cairo

from engine import H, W, clamp, ease_in_out, ease_out_back, prog
from rich import (Scene, badge, cta_button, disc, fill_rr, glow, label, linear, mix, mul, poly, preview,
                  radial, render, rgba, rr, soft_ellipse, source, stroke, text)

_rng = random.Random(7)
STARS = [(_rng.uniform(0, W), _rng.uniform(0, H), _rng.uniform(0.8, 2.6), _rng.uniform(0, 6.3)) for _ in range(260)]

# continentes estilizados: grupos de círculos (longitud, latitud, radio en grados)
CONT = []
for lon0, lat0, slon, slat, n in [(-100, 45, 16, 12, 26), (-60, -15, 10, 14, 20), (20, 5, 12, 18, 26), (15, 50, 12, 6, 12),
                                  (90, 45, 30, 12, 36), (135, -25, 10, 6, 10), (-42, 70, 5, 3, 4)]:
    for _ in range(n * 2):
        CONT.append((lon0 + _rng.gauss(0, slon), lat0 + _rng.gauss(0, slat), _rng.uniform(4, 8)))
LAND_SPOTS = [(lon + _rng.uniform(-3, 3), lat + _rng.uniform(-3, 3), r * 0.45) for lon, lat, r in CONT[::3]]
CLOUD_SPOTS = [(_rng.uniform(-180, 180), _rng.uniform(-60, 60), _rng.uniform(4, 9)) for _ in range(70)]
GRAIN_BLOBS = [(_rng.uniform(-1, 1), _rng.uniform(-1, 1), _rng.uniform(0.04, 0.10), _rng.uniform(0, 6.3)) for _ in range(90)]
MAGMA = [(_rng.uniform(0, 2 * math.pi), _rng.uniform(0.6, 0.92), _rng.uniform(0.05, 0.11), _rng.uniform(-0.2, 0.2)) for _ in range(26)]

TILT = 0.35
CX, CY, CR = 540, 800, 430
R_FALL = CR - 60  # recorrido del astronauta dentro del túnel
VMAX = 28460

MANTLE_IN, MANTLE_OUT = (1.0, 0.58, 0.16), (0.62, 0.16, 0.08)
OUTER_CORE = (1.0, 0.76, 0.26)
INNER_CORE = (1.0, 0.97, 0.80)


def kmh(v):
    return f"{v:,.0f}".replace(",", ".")


# ---------- fondo y planeta ----------

def space(ctx, t):
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(linear(0, 0, 0, H, [(0, (0.01, 0.01, 0.04)), (1, (0.03, 0.02, 0.09))]))
    ctx.fill()
    soft_ellipse(ctx, 230, 480, 640, 320, (0.38, 0.14, 0.58), 0.20)
    soft_ellipse(ctx, 880, 1350, 600, 300, (0.08, 0.30, 0.58), 0.18)
    soft_ellipse(ctx, 700, 250, 400, 180, (0.10, 0.25, 0.50), 0.12)
    for x, y, r, ph in STARS:
        disc(ctx, x, y, r, (1, 1, 1, 0.25 + 0.6 * (0.5 + 0.5 * math.sin(t * 1.8 + ph))))


def project(lon, lat, rot):
    lam, ph = math.radians(lon + rot), math.radians(lat)
    x, y, z = math.cos(ph) * math.sin(lam), math.sin(ph), math.cos(ph) * math.cos(lam)
    return x, y * math.cos(TILT) - z * math.sin(TILT), y * math.sin(TILT) + z * math.cos(TILT)


def globe(ctx, t, cx, cy, R, rot=0.0):
    disc(ctx, cx, cy, R * 1.16, radial(cx, cy, R * 1.16, [(0, (0.35, 0.70, 1.0, 0.5)), (0.84, (0.35, 0.70, 1.0, 0.5)), (1, (0.35, 0.70, 1.0, 0))]))
    ctx.save()
    ctx.arc(cx, cy, R, 0, 2 * math.pi)
    ctx.clip()
    disc(ctx, cx, cy, R, radial(cx, cy, R * 1.4, [(0, (0.20, 0.50, 0.92)), (0.55, (0.08, 0.30, 0.70)), (1, (0.02, 0.08, 0.25))],
                                fx=cx - 0.35 * R, fy=cy - 0.35 * R))
    # tierra firme en tres pasadas: borde, relleno y manchas de relieve
    for k, (spots, grow, dark) in enumerate([(CONT, 1.12, 0.62), (CONT, 1.0, 1.0), (LAND_SPOTS, 1.0, 1.22)]):
        for lon, lat, r in spots:
            x, y, z = project(lon, lat, rot)
            if z <= 0:
                continue
            col = mix((0.27, 0.58, 0.27), (0.72, 0.64, 0.40), clamp((22 - abs(lat - 18)) / 22) * 0.7)
            disc(ctx, cx + R * x, cy - R * y, R * math.radians(r) * (0.45 + 0.55 * z) * grow, mul(col, dark))
    for lon, lat, r in CLOUD_SPOTS:
        x, y, z = project(lon, lat, rot * 1.35 + 40)
        if z <= 0:
            continue
        ctx.save()
        ctx.translate(cx + R * x, cy - R * y)
        ctx.scale(R * math.radians(r) * 1.8, R * math.radians(r) * 0.6 * (0.4 + 0.6 * z))
        disc(ctx, 0, 0, 1, radial(0, 0, 1, [(0, (1, 1, 1, 0.45)), (1, (1, 1, 1, 0))]))
        ctx.restore()
    ctx.rectangle(cx - R, cy - R, 2 * R, 2 * R)
    ctx.set_source(linear(cx - 0.2 * R, cy - 0.5 * R, cx + R, cy + 0.9 * R, [(0, (0, 0, 0.02, 0)), (0.55, (0, 0, 0.02, 0.35)), (1, (0, 0, 0.02, 0.85))]))
    ctx.fill()
    disc(ctx, cx, cy, R, radial(cx, cy, R, [(0, (0, 0, 0, 0)), (0.75, (0, 0, 0, 0)), (1, (0, 0, 0.05, 0.45))]))
    soft_ellipse(ctx, cx - 0.38 * R, cy - 0.42 * R, 0.35 * R, 0.25 * R, (1, 1, 1), 0.16)
    ctx.restore()


def pole_hole(cx, cy, R):
    return cx, cy - R * math.cos(TILT), 0.11 * R, 0.11 * R * math.sin(TILT) * 1.2


def draw_hole(ctx, cx, cy, R):
    hx, hy, rx, ry = pole_hole(cx, cy, R)
    ctx.save()
    ctx.translate(hx, hy)
    ctx.scale(rx * 1.25, ry * 1.25)
    disc(ctx, 0, 0, 1, (0.35, 0.25, 0.18))
    ctx.restore()
    ctx.save()
    ctx.translate(hx, hy)
    ctx.scale(rx, ry)
    disc(ctx, 0, 0, 1, radial(0, 0.35, 1, [(0, (0, 0, 0)), (0.7, (0.03, 0.02, 0.02)), (1, (0.25, 0.10, 0.05))]))
    ctx.restore()


# ---------- la Tierra cortada por la mitad ----------

def section(ctx, t, cx=CX, cy=CY, R=CR, tunnel=True, heat=1.0):
    disc(ctx, cx, cy, R * 1.12, radial(cx, cy, R * 1.12, [(0, (0.35, 0.70, 1.0, 0.55)), (0.86, (0.35, 0.70, 1.0, 0.55)), (1, (0.35, 0.70, 1.0, 0))]))
    disc(ctx, cx, cy, R, (0.12, 0.38, 0.78))
    ctx.set_line_width(R * 0.035)
    for a0, a1 in [(-2.6, -1.9), (-1.2, -0.3), (0.5, 1.4), (2.0, 2.7)]:
        ctx.new_sub_path()
        ctx.arc(cx, cy, R * 0.982, a0, a1)
        source(ctx, (0.30, 0.62, 0.30))
        ctx.stroke()
    disc(ctx, cx, cy, R * 0.965, radial(cx, cy, R * 0.965, [(0.9, (0.42, 0.30, 0.22)), (1, (0.56, 0.42, 0.30))]))
    disc(ctx, cx, cy, R * 0.94, radial(cx, cy, R * 0.94, [(0.58, MANTLE_IN), (1, MANTLE_OUT)]))
    # corrientes de convección del manto
    ctx.save()
    ctx.set_line_width(R * 0.03)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_dash([R * 0.06, R * 0.09], -t * R * 0.12)
    for k in range(8):
        a = k * math.pi / 4 + 0.3
        mx, my = cx + 0.745 * R * math.cos(a), cy + 0.745 * R * math.sin(a)
        ctx.new_sub_path()
        ctx.arc(mx, my, 0.14 * R, 0, 2 * math.pi) if k % 2 else ctx.arc_negative(mx, my, 0.14 * R, 0, -2 * math.pi)
        source(ctx, (1.0, 0.85, 0.45, 0.16))
        ctx.stroke()
    ctx.restore()
    for a, r, s, sp in MAGMA:
        aa = a + t * sp * 0.4
        soft_ellipse(ctx, cx + r * R * math.cos(aa), cy + r * R * math.sin(aa), s * R * 1.6, s * R, (1.0, 0.85, 0.4), 0.18)
    disc(ctx, cx, cy, R * 0.546, radial(cx, cy, R * 0.546, [(0.3, (1.0, 0.86, 0.36)), (1, (0.98, 0.58, 0.16))]))
    disc(ctx, cx, cy, R * 0.546, radial(cx, cy, R * 0.546, [(0.92, (0.6, 0.15, 0.05, 0)), (1, (0.6, 0.15, 0.05, 0.5))]))
    disc(ctx, cx, cy, R * 0.19, radial(cx, cy, R * 0.19, [(0, INNER_CORE), (1, (1.0, 0.86, 0.45))], fx=cx - 0.05 * R, fy=cy - 0.05 * R))
    if tunnel:
        w = 30
        ctx.rectangle(cx - w, cy - R - 4, 2 * w, 2 * R + 8)
        ctx.set_source(linear(cx - w, 0, cx + w, 0, [(0, (0.55, 0.22, 0.08)), (0.18, (0.06, 0.03, 0.03)),
                                                     (0.82, (0.06, 0.03, 0.03)), (1, (0.55, 0.22, 0.08))]))
        ctx.fill()
        y = cy - R
        while y < cy + R:
            stroke(ctx, [(cx - w, y), (cx + w, y)], (1, 0.7, 0.4, 0.10), 2)
            y += 26
    pulse = 0.85 + 0.15 * math.sin(t * 3)
    glow(ctx, cx, cy, R * 0.62, (1, 0.8, 0.35), 0.35 * heat * pulse, add=True)
    glow(ctx, cx, cy, R * 0.32, (1, 0.97, 0.8), 0.55 * heat * pulse, add=True)


def layer_labels(ctx, t, start=0.0):
    items = [("CORTEZA", 0.955, 0), ("MANTO", 0.75, 1), ("NÚCLEO EXTERNO", 0.37, 2), ("NÚCLEO INTERNO", 0.08, 3)]
    for name, r, i in items:
        p = prog(t, start + i * 0.35, 0.35)
        if p <= 0:
            continue
        a = math.radians(205)
        px, py = CX + r * CR * math.cos(a), CY + r * CR * math.sin(a) - (i - 1.5) * 18
        ly = 470 + i * 140
        stroke(ctx, [(px, py), (170 + 40 * i, ly + 28)], (1, 1, 1, 0.55 * p), 3)
        disc(ctx, px, py, 7, (1, 1, 1, p))
        ctx.save()
        ctx.translate(50, ly)
        ctx.scale(0.8 + 0.2 * ease_out_back(p), 0.8 + 0.2 * ease_out_back(p))
        label(ctx, name, 0, 0, 32)
        ctx.restore()


# ---------- astronauta ----------

def astronaut(ctx, x, y, s=1.0, rot=0.0, pose="fall", t=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    suit, shade, acc = (0.96, 0.96, 0.98), (0.66, 0.68, 0.78), (1.0, 0.45, 0.15)
    wig = math.sin(t * 13)
    if pose == "stand":
        arms = [((-18, -24), (-26, 6), (-24, 30)), ((18, -24), (26, 6), (24, 30))]
        legs = [((-10, 18), (-11, 40), (-12, 60)), ((10, 18), (11, 40), (12, 60))]
    elif pose == "float":
        arms = [((-18, -24), (-46, -30 + 5 * wig), (-68, -24)), ((18, -24), (46, -30 - 5 * wig), (68, -24))]
        legs = [((-10, 18), (-22, 40), (-30, 58)), ((10, 18), (22, 40), (30, 58))]
    else:  # cayendo: brazos arriba agitándose
        arms = [((-18, -24), (-38, -54 + 8 * wig), (-46, -84 + 10 * wig)), ((18, -24), (38, -54 - 8 * wig), (46, -84 - 10 * wig))]
        legs = [((-10, 18), (-20, 38 + 4 * wig), (-18, 60)), ((10, 18), (20, 38 - 4 * wig), (18, 60))]
    fill_rr(ctx, -25, -40, 50, 56, 12, shade)
    for a, b, c in legs:
        stroke(ctx, [a, b, c], suit, 17)
        stroke(ctx, [b, c], mix(suit, shade, 0.5), 17)
        stroke(ctx, [c, (c[0] + (4 if c[0] > 0 else -4), c[1] + 2)], (0.35, 0.36, 0.42), 19)
    fill_rr(ctx, -21, -38, 42, 60, 17, linear(-21, 0, 21, 0, [(0, suit), (1, shade)]))
    fill_rr(ctx, -21, -6, 42, 8, 3, acc)
    fill_rr(ctx, -9, -28, 18, 14, 4, (0.35, 0.55, 0.95))
    for a, b, c in arms:
        stroke(ctx, [a, b, c], suit, 14)
        disc(ctx, *c, 9, (0.35, 0.36, 0.42))
    disc(ctx, 0, -58, 26, radial(-8, -66, 34, [(0, (1, 1, 1)), (1, (0.70, 0.72, 0.80))]))
    ctx.save()
    ctx.translate(5, -58)
    ctx.scale(17, 13)
    disc(ctx, 0, 0, 1, radial(-0.3, -0.4, 1.2, [(0, (0.30, 0.45, 0.80)), (1, (0.04, 0.06, 0.16))]))
    ctx.restore()
    ctx.save()
    ctx.translate(-2, -63)
    ctx.scale(7, 4)
    disc(ctx, 0, 0, 1, (1, 1, 1, 0.75))
    ctx.restore()
    ctx.restore()


def fall_rot(phi):
    """Gira 180° al cruzar el centro: hacia allí está siempre su 'abajo'."""
    m = phi % (2 * math.pi)
    if m > math.pi:
        m = 2 * math.pi - m
    return math.pi * ease_in_out((m - 1.25) / 0.65)


def faller(ctx, t, phi, pose="fall", trail=False, dphi=0.0):
    y = CY - R_FALL * math.cos(phi)
    speed = abs(math.sin(phi))
    moving_down = math.sin(phi % (2 * math.pi)) > 0
    # estelas de velocidad, por detrás del movimiento
    if speed > 0.25 and pose == "fall":
        rnd = random.Random(int(t * 15))
        for k in range(7):
            dx = rnd.uniform(-22, 22)
            ln = (50 + rnd.uniform(0, 110)) * speed
            y0 = y - 70 if moving_down else y + 70
            y1 = y0 - ln if moving_down else y0 + ln
            stroke(ctx, [(CX + dx, y0), (CX + dx, y1)], (1, 1, 1, 0.35 * speed), 3)
    if trail:
        for k in range(1, 6):
            p2 = phi - dphi * k
            astr_y = CY - R_FALL * math.cos(p2)
            ctx.push_group()
            astronaut(ctx, CX, astr_y, 0.42, fall_rot(p2), pose, t)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(0.22 * (1 - k / 6))
    soft_ellipse(ctx, CX, y, 75, 85, (0.05, 0.02, 0.02), 0.55)
    astronaut(ctx, CX, y, 0.42, fall_rot(phi), pose, t)


def hud(ctx, title, value, unit, a=1.0, x=600, y=210):
    if a <= 0:
        return
    fill_rr(ctx, x, y, 420, 150, 30, (0.02, 0.03, 0.08, 0.62 * a))
    rr(ctx, x, y, 420, 150, 30)
    source(ctx, (1, 1, 1, 0.16 * a))
    ctx.set_line_width(3)
    ctx.stroke()
    text(ctx, title, x + 30, y + 40, 28, col=(0.65, 0.78, 1.0, a), anchor="left")
    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(66)
    vw = ctx.text_extents(value).x_advance
    text(ctx, value, x + 30, y + 98, 66, col=(1, 1, 1, a), anchor="left")
    text(ctx, unit, x + 44 + vw, y + 104, 34, col=(1.0, 0.80, 0.24, a), anchor="left")


# ---------- escenas ----------

def s_hook(ctx, t):
    space(ctx, t)
    z = 1 + 0.07 * ease_in_out(t / 4.6)
    ctx.translate(540, 760)
    ctx.scale(z, z)
    ctx.translate(-540, -760)
    gx, gy, R = 540, 1010, 400
    globe(ctx, t, gx, gy, R, rot=-20 + t * 6)
    draw_hole(ctx, gx, gy, R)
    hx, hy, hrx, hry = pole_hole(gx, gy, R)
    # recorrido del túnel en rayos X
    xp = prog(t, 1.2, 0.8)
    if xp > 0:
        ctx.save()
        ctx.set_dash([18, 14], -t * 60)
        sy = gy + R * math.cos(TILT)
        stroke(ctx, [(hx, hy), (hx, hy + (sy - hy) * xp)], (1.0, 0.80, 0.24, 0.85), 6)
        ctx.restore()
        glow(ctx, hx, hy + (gy + R * math.cos(TILT) - hy) * xp, 40, (1.0, 0.8, 0.3), 0.8, add=True)
    # el astronauta salta al agujero
    jp = prog(t, 2.7, 0.9)
    ax = 640 - 100 * ease_in_out(jp)
    ay = hy - 62 - 90 * math.sin(math.pi * min(1, jp * 1.25)) + 160 * max(0, jp - 0.6) ** 1.5 * 4
    ctx.save()
    ctx.rectangle(0, 0, W, hy)
    ctx.new_sub_path()
    ctx.save()
    ctx.translate(hx, hy)
    ctx.scale(hrx, hry)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.clip()
    astronaut(ctx, ax, ay, 0.9, -0.5 * ease_in_out(prog(t, 2.7, 0.4)), "stand" if t < 2.7 else "fall", t)
    ctx.restore()


def s_fall(ctx, t):
    space(ctx, t)
    section(ctx, t)
    phi = 1.15 * (t / 4.0)
    faller(ctx, t, phi)
    layer_labels(ctx, t, 0.6)
    hud(ctx, "VELOCIDAD", kmh(VMAX * math.sin(phi)), "km/h", a=prog(t, 0.2, 0.4))


def s_center(ctx, t):
    space(ctx, t)
    zt = ease_in_out(t / 3.7)
    z = 1 + 0.25 * zt
    ctx.save()
    ctx.translate(CX, CY)
    ctx.scale(z, z)
    ctx.translate(-CX, -CY)
    section(ctx, t)
    phi = 1.15 + (math.pi / 2 - 1.15) * min(1, t / 2.2) + 0.03 * max(0, t - 2.2)
    faller(ctx, t, phi)
    ctx.restore()
    hud(ctx, "VELOCIDAD", kmh(VMAX * math.sin(phi)), "km/h")
    if t > 2.2:
        glow(ctx, 810, 285, 260, (1.0, 0.8, 0.24), 0.25 * prog(t, 2.2, 0.3), add=True)


def s_weightless(ctx, t):
    space(ctx, t)
    z = 1.25 + 0.1 * ease_in_out(t / 3.1)
    ctx.save()
    ctx.translate(CX, CY)
    ctx.scale(z, z)
    ctx.translate(-CX, -CY)
    section(ctx, t)
    phi = math.pi / 2 + 0.06 * (t - 1.5)
    rot = math.pi * ease_in_out(t / 3.1)
    y = CY - R_FALL * math.cos(phi) + 6 * math.sin(t * 2.5)
    soft_ellipse(ctx, CX, y, 95, 95, (0.05, 0.02, 0.02), 0.6)
    astronaut(ctx, CX, y, 0.42, rot, "float", t * 0.3)
    ctx.restore()
    hud(ctx, "TU PESO", "0", "kg")
    for i in range(10):  # partículas flotando
        a = i * 0.63 + t * 0.4
        disc(ctx, CX + 120 * math.cos(a) * (1 + 0.2 * math.sin(i)), CY + 90 * math.sin(a * 1.3), 4, (1, 1, 1, 0.5))


def s_other_side(ctx, t):
    space(ctx, t)
    section(ctx, t)
    phi = math.pi / 2 + (math.pi / 2) * ease_in_out(t / 3.0) if t < 3.0 else math.pi
    faller(ctx, t, min(phi, math.pi - 0.001))
    hud(ctx, "VELOCIDAD", kmh(VMAX * abs(math.sin(phi))), "km/h")
    p = prog(t, 2.6, 0.5)
    if p > 0:
        ty = CY + R_FALL + 40
        glow(ctx, CX, ty, 120, (1.0, 0.8, 0.24), 0.5 * p, add=True)
        text(ctx, "¡Hola!", CX + 150, ty - 10, 50, col=(1, 1, 1, p), outline=(0.05, 0.05, 0.1, p), ow=8)


def s_time(ctx, t):
    space(ctx, t)
    section(ctx, t, heat=0.6)
    ctx.rectangle(0, 0, W, H)
    source(ctx, (0.01, 0.01, 0.04, 0.55))
    ctx.fill()
    ctx.save()
    ctx.set_dash([16, 14], -t * 80)
    stroke(ctx, [(CX, CY - R_FALL), (CX, CY + R_FALL)], (1.0, 0.80, 0.24, 0.7), 6)
    ctx.restore()
    p = ease_out_back(prog(t, 0.05, 0.45))
    frac = ease_in_out(prog(t, 0.3, 1.6))
    secs = 38 * 60 + 11
    shown = int(secs * frac)
    cx, cy, r = 540, 780, 250
    if p > 0:
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(p, p)
        glow(ctx, 0, 0, r * 1.7, (1.0, 0.8, 0.3), 0.35, add=True)
        fill_rr(ctx, -40, -r - 62, 80, 50, 14, (0.80, 0.82, 0.88))
        disc(ctx, 0, 0, r, radial(-r * 0.3, -r * 0.3, r * 1.4, [(0, (0.98, 0.98, 1.0)), (1, (0.62, 0.64, 0.72))]))
        disc(ctx, 0, 0, r * 0.86, (0.05, 0.06, 0.12))
        for k in range(60):
            a = k * math.pi / 30
            r0 = r * (0.72 if k % 5 == 0 else 0.78)
            stroke(ctx, [(r0 * math.cos(a), r0 * math.sin(a)), (r * 0.82 * math.cos(a), r * 0.82 * math.sin(a))],
                   (1, 1, 1, 0.6 if k % 5 == 0 else 0.25), 5 if k % 5 == 0 else 3)
        ctx.new_sub_path()
        ctx.arc(0, 0, r * 0.62, -math.pi / 2, -math.pi / 2 + 2 * math.pi * frac * 38 / 60)
        source(ctx, (1.0, 0.80, 0.24))
        ctx.set_line_width(18)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
        text(ctx, f"{shown // 60:02d}:{shown % 60:02d}", 0, -10, 120)
        text(ctx, "minutos", 0, 80, 40, col=(0.75, 0.82, 1.0))
        ctx.restore()


def s_forever(ctx, t):
    space(ctx, t)
    section(ctx, t)
    w = 2 * math.pi * 0.55
    phi = math.pi + w * t
    faller(ctx, t, phi, trail=True, dphi=w / 30)
    for side in (-1, 1):
        x = CX + side * 120
        a = 0.5 + 0.5 * math.sin(t * 6 + side)
        stroke(ctx, [(x, CY - 220), (x, CY + 220)], (1.0, 0.80, 0.24, 0.5 + 0.4 * a), 8)
        stroke(ctx, [(x - 26, CY - 190), (x, CY - 222), (x + 26, CY - 190)], (1.0, 0.80, 0.24, 0.5 + 0.4 * a), 8)
        stroke(ctx, [(x - 26, CY + 190), (x, CY + 222), (x + 26, CY + 190)], (1.0, 0.80, 0.24, 0.5 + 0.4 * a), 8)
    p = ease_out_back(prog(t, 1.2, 0.4))
    if p > 0:
        ctx.save()
        ctx.translate(860, 300)
        ctx.scale(p, p)
        glow(ctx, 0, 0, 160, (1.0, 0.8, 0.24), 0.5, add=True)
        disc(ctx, 0, 0, 85, (0.02, 0.03, 0.08, 0.7))
        text(ctx, "∞", 0, -6, 120, col=(1.0, 0.80, 0.24))
        ctx.restore()


def s_kola(ctx, t):
    space(ctx, t)
    x0, x1, y0, y1 = 330, 500, 360, 1210
    hgt = (y1 - y0) * ease_in_out(prog(t, 0.0, 0.9))
    layers = [(0.0, 0.006, (0.50, 0.38, 0.28), (0.45, 0.33, 0.24)), (0.006, 0.454, MANTLE_OUT, MANTLE_IN),
              (0.454, 0.808, (0.98, 0.60, 0.16), (1.0, 0.86, 0.36)), (0.808, 1.0, (1.0, 0.88, 0.5), INNER_CORE)]
    ctx.save()
    rr(ctx, x0, y0, x1 - x0, max(1, hgt), 18)
    ctx.clip()
    for f0, f1, c0, c1 in layers:
        ya, yb = y0 + (y1 - y0) * f0, y0 + (y1 - y0) * f1
        ctx.rectangle(x0, ya, x1 - x0, yb - ya + 1)
        ctx.set_source(linear(0, ya, 0, yb, [(0, c0), (1, c1)]))
        ctx.fill()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_source(linear(x0, 0, x1, 0, [(0, (0, 0, 0, 0.35)), (0.4, (1, 1, 1, 0.08)), (1, (0, 0, 0, 0.4))]))
    ctx.fill()
    ctx.restore()
    glow(ctx, (x0 + x1) / 2, y1 - 60, 200, (1, 0.9, 0.5), 0.4 * prog(t, 0.6, 0.4), add=True)
    fill_rr(ctx, x0 - 14, y0 - 10, x1 - x0 + 28, 14, 7, (0.30, 0.62, 0.30))
    for name, f, i in [("MANTO", 0.23, 0), ("NÚCLEO EXTERNO", 0.63, 1), ("NÚCLEO INTERNO", 0.9, 2)]:
        a = prog(t, 0.6 + i * 0.2, 0.3)
        if a > 0:
            text(ctx, name, x0 - 24, y0 + (y1 - y0) * f, 30, col=(1, 1, 1, a), anchor="right")
    a = prog(t, 0.9, 0.3)
    text(ctx, "6.371 km", (x0 + x1) / 2, y1 + 50, 46, col=(1, 1, 1, a))
    text(ctx, "hasta el centro", (x0 + x1) / 2, y1 + 98, 30, col=(0.75, 0.82, 1.0, a))
    # torre de perforación y zoom al agujero
    tx = (x0 + x1) / 2
    for dx in (-22, 22):
        stroke(ctx, [(tx + dx, y0 - 12), (tx, y0 - 92)], (0.85, 0.87, 0.92), 5)
    stroke(ctx, [(tx - 14, y0 - 40), (tx + 14, y0 - 40)], (0.85, 0.87, 0.92), 4)
    disc(ctx, tx, y0 - 2, 6, (1.0, 0.25, 0.25))
    cp = ease_out_back(prog(t, 1.5, 0.5))
    ccx, ccy, cr = 790, 560, 210
    if cp > 0:
        stroke(ctx, [(tx + 8, y0 - 2), (ccx - cr * 0.8, ccy - cr * 0.55)], (1, 1, 1, 0.5 * clamp(cp)), 3)
        stroke(ctx, [(tx + 8, y0 + 4), (ccx - cr * 0.75, ccy + cr * 0.65)], (1, 1, 1, 0.5 * clamp(cp)), 3)
        ctx.save()
        ctx.translate(ccx, ccy)
        ctx.scale(cp, cp)
        glow(ctx, 0, 0, cr * 1.5, (0.4, 0.7, 1.0), 0.25, add=True)
        ctx.arc(0, 0, cr, 0, 2 * math.pi)
        ctx.save()
        ctx.clip()
        ctx.rectangle(-cr, -cr, 2 * cr, 2 * cr)
        ctx.set_source(linear(0, -cr, 0, -80, [(0, (0.10, 0.12, 0.30)), (1, (0.30, 0.25, 0.45))]))
        ctx.fill()
        for k, col in enumerate([(0.30, 0.55, 0.28), (0.50, 0.38, 0.26), (0.42, 0.31, 0.22), (0.36, 0.26, 0.19), (0.30, 0.21, 0.16)]):
            ctx.rectangle(-cr, -80 + k * 60 - (12 if k == 0 else 0), 2 * cr, 62 + (12 if k == 0 else 0))
            source(ctx, col)
            ctx.fill()
        dp = ease_in_out(prog(t, 1.9, 1.2))
        stroke(ctx, [(0, -80), (0, -80 + 250 * dp)], (0.05, 0.03, 0.02), 10)
        glow(ctx, 0, -80 + 250 * dp, 26, (1, 0.6, 0.3), 0.8 * dp, add=True)
        for dx in (-34, 34):
            stroke(ctx, [(dx, -80), (0, -190)], (0.88, 0.90, 0.95), 7)
        for yy in (-110, -140, -165):
            stroke(ctx, [(-34 * (yy + 190) / 110, yy), (34 * (yy + 190) / 110, yy)], (0.88, 0.90, 0.95), 4)
        ctx.restore()
        ctx.arc(0, 0, cr, 0, 2 * math.pi)
        source(ctx, (1, 1, 1, 0.8))
        ctx.set_line_width(6)
        ctx.stroke()
        text(ctx, "12 km", 92, 40, 60, col=(1, 1, 1), outline=(0.05, 0.05, 0.1), ow=10)
        ctx.restore()
        lp = prog(t, 2.2, 0.4)
        if lp > 0:
            label(ctx, "POZO DE KOLA (RUSIA)", ccx - 205, ccy + cr + 60, 30)


def sun(ctx, t, cx, cy, r):
    glow(ctx, cx, cy, r * 2.6, (1.0, 0.55, 0.15), 0.55, add=True)
    for k in range(12):  # corona
        a = k * math.pi / 6 + t * 0.1
        soft_ellipse(ctx, cx + r * 1.05 * math.cos(a), cy + r * 1.05 * math.sin(a), r * 0.25, r * 0.12, (1, 0.7, 0.3), 0.25)
    disc(ctx, cx, cy, r, radial(cx, cy, r, [(0, (1, 0.97, 0.75)), (0.7, (1, 0.75, 0.25)), (1, (0.95, 0.45, 0.10))]))
    ctx.save()
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.clip()
    for bx, by, bs, ph in GRAIN_BLOBS:
        k = 0.5 + 0.5 * math.sin(t * 2 + ph)
        soft_ellipse(ctx, cx + bx * r, cy + by * r, bs * r * 1.5, bs * r, (1, 1, 0.85) if k > 0.5 else (0.85, 0.35, 0.05), 0.25)
    ctx.restore()


def s_hot(ctx, t):
    space(ctx, t)
    p1 = ease_out_back(prog(t, 0.0, 0.5))
    if p1 > 0:
        ctx.save()
        ctx.translate(540, 470)
        ctx.scale(p1, p1)
        sun(ctx, t, 0, 0, 200)
        ctx.restore()
        a = prog(t, 0.4, 0.3)
        text(ctx, "SUPERFICIE DEL SOL", 540, 730, 32, col=(1, 1, 1, 0.8 * a))
        text(ctx, "≈ 5.500 °C", 540, 790, 64, col=(1.0, 0.80, 0.24, a), outline=(0.05, 0.05, 0.1, a), ow=8)
    p2 = ease_out_back(prog(t, 1.0, 0.5))
    if p2 > 0:
        ctx.save()
        ctx.translate(540, 1100)
        ctx.scale(p2, p2)
        ctx.translate(-540, -1100)
        rr(ctx, 120, 880, 840, 330, 40)
        ctx.save()
        ctx.clip()
        section(ctx, t, cx=540, cy=1045, R=520, tunnel=False, heat=0.7)
        ctx.restore()
        rr(ctx, 120, 880, 840, 330, 40)
        source(ctx, (1, 1, 1, 0.2))
        ctx.set_line_width(4)
        ctx.stroke()
        ctx.restore()
        a = prog(t, 1.4, 0.3)
        label(ctx, "NÚCLEO DE LA TIERRA", 150, 925, 30)
        text(ctx, "≈ 5.200 °C", 540, 1268, 64, col=(1.0, 0.80, 0.24, a), outline=(0.05, 0.05, 0.1, a), ow=8)


def s_cta(ctx, t):
    space(ctx, t)
    globe(ctx, t, 540, 700, 330, rot=t * 12)
    cta_button(ctx, t, 540, 1180)


SCENES = [
    Scene("¿Qué pasaría si saltaras por un agujero que atraviesa la Tierra?", s_hook, sfx=[(2.7, "whoosh")]),
    Scene("Sin aire que te frene, caerías cada vez más rápido…", s_fall, sfx=[(0.6, "pop"), (0.95, "pop"), (1.3, "pop"), (1.65, "pop"), (1.0, "riser")]),
    Scene("…y cruzarías el centro a más de 28.000 km/h.", s_center, sfx=[(2.2, "boom")]),
    Scene("Justo en el centro no pesarías nada.", s_weightless),
    Scene("Después irías frenando hasta asomar al otro lado.", s_other_side, sfx=[(2.6, "pop")]),
    Scene("¿Cuánto tardarías? Unos 38 minutos.", s_time, duration=3.2,
          sfx=[(0.3 + k * 0.08, "tick") for k in range(20)] + [(1.95, "pop")]),
    Scene("Y si nadie te agarra, volverías a caer… una y otra vez.", s_forever, sfx=[(1.2, "pop")]),
    Scene("Pero el agujero más hondo que existe solo llega a 12 km.", s_kola, sfx=[(1.5, "pop"), (2.2, "pop")]),
    Scene("Y abajo hace tanto calor como en la superficie del Sol.", s_hot, sfx=[(0.0, "pop"), (1.0, "pop")]),
    Scene("Síguenos para más curiosidades como esta.", s_cta, sfx=[(0.05, "pop"), (1.3, "pop")]),
]

POST = """¿Qué pasaría si saltaras por un agujero que atraviesa la Tierra? 🌍🕳️

Sin aire que te frene, caerías cada vez más rápido y cruzarías el centro a más de 28.000 km/h. Allí no pesarías nada. Después irías frenando hasta asomar justo al otro lado… unos 38 minutos después. Y si nadie te agarra, volverías a caer una y otra vez.

El problema: el agujero más profundo que hemos hecho, el pozo de Kola, solo llega a 12 km de los 6.371 que hay hasta el centro. Y allí abajo hace tanto calor como en la superficie del Sol.

Síguenos para más curiosidades 👀

#curiosidades #ciencia #sabiasque #fisica #datoscuriosos
"""

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "out", "tierra-agujero")
    os.makedirs(out, exist_ok=True)
    if "--preview" in sys.argv:
        i = sys.argv.index("--preview")
        dest = sys.argv[i + 1] if len(sys.argv) > i + 1 else os.path.join(out, "preview.png")
        preview(SCENES, dest)
        print("preview:", dest)
    else:
        total = render(SCENES, os.path.join(out, "tierra-agujero.mp4"), cover_png=os.path.join(out, "portada.png"), cover_at=(0, 2.2))
        with open(os.path.join(out, "texto-del-post.txt"), "w") as f:
            f.write(POST)
        print(f"OK: {total:.1f} s")
