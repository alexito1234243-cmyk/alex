"""Vídeo: ¿Por qué apagan las luces del avión al aterrizar de noche? (versión elaborada)

Uso: python3 video/avion_luces.py [--voz dora|alex|santa] [--sin-voz]  ->  vídeo en video/out/avion-luces/
     python3 video/avion_luces.py --preview [png]                     ->  hoja de contactos con un fotograma por escena
"""
import math
import os
import random
import sys

import cairo

from engine import H, W, clamp, ease_in_out, ease_out_back, prog
from rich import (Scene, badge, bezier, blurred, cta_button, disc, fill_rr, glow, label, linear, mix, mul, path,
                  poly, preview, radial, render, rgba, rr, soft_ellipse, source, stroke, text)

_rng = random.Random(42)
STARS = [(_rng.uniform(0, W), _rng.uniform(0, 1150), _rng.uniform(1.0, 3.0), _rng.uniform(0, 6.3)) for _ in range(170)]
HORIZON = 1330
CITY_COLS = [(1, 0.82, 0.45), (1, 0.66, 0.35), (0.92, 0.94, 1.0), (1, 0.9, 0.7)]
CITY = []
for _ in range(380):
    d = _rng.random() ** 2.2
    CITY.append((_rng.uniform(0, W), HORIZON + 6 + d * 560, 1.0 + d * 4.5, _rng.choice(CITY_COLS), _rng.uniform(0, 6.3)))
CLOUDS = [(_rng.uniform(-200, W + 200), _rng.uniform(250, 1150), _rng.uniform(220, 420), _rng.uniform(40, 80),
           _rng.uniform(10, 35), _rng.uniform(0.06, 0.14)) for _ in range(9)]
PANE_LIGHTS = [(_rng.uniform(0, 520), _rng.uniform(70, 330), _rng.uniform(1.5, 4.0), _rng.choice(CITY_COLS)) for _ in range(60)]

GREEN_LIGHT = (0.15, 1.0, 0.45)
RED = (0.95, 0.20, 0.22)


def dur(fn):
    """Duración real de la escena que dibuja fn (cambia con la locución)."""
    return next(s.duration for s in SCENES if s.draw is fn)


# ---------- exterior: cielo, ciudad, pista ----------

def sky(ctx, t):
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(linear(0, 0, 0, HORIZON, [(0, (0.02, 0.03, 0.10)), (0.5, (0.07, 0.08, 0.22)),
                                              (0.82, (0.22, 0.14, 0.34)), (1, (0.50, 0.26, 0.36))]))
    ctx.fill()
    for x, y, r, ph in STARS:
        a = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(t * 2.0 + ph))
        disc(ctx, x, y, r, (1, 1, 1, 0.85 * a))
    mx, my = 820, 330
    glow(ctx, mx, my, 340, (0.70, 0.78, 1.0), 0.22)
    disc(ctx, mx, my, 72, radial(mx - 22, my - 22, 95, [(0, (1, 0.98, 0.92)), (1, (0.78, 0.78, 0.76))]))
    for cx, cy, cr in [(-20, -15, 14), (24, 18, 10), (12, -32, 7), (-26, 28, 8)]:
        disc(ctx, mx + cx, my + cy, cr, (0.5, 0.5, 0.58, 0.18))


def clouds(ctx, t, front=False):
    for i, (x, y, rx, ry, sp, a) in enumerate(CLOUDS):
        if (i % 3 == 0) != front:
            continue
        xx = (x - t * sp * (2.5 if front else 1)) % (W + 800) - 400
        soft_ellipse(ctx, xx, y, rx, ry, (0.55, 0.45, 0.72), a * (1.6 if front else 1))


def ground(ctx, t, drift=0.0):
    pts = [(0, H)] + [(x, HORIZON - 26 - 22 * math.sin(x / 130 + 1) - 12 * math.sin(x / 53)) for x in range(0, W + 21, 20)] + [(W, H)]
    poly(ctx, pts, (0.10, 0.07, 0.18))
    ctx.rectangle(0, HORIZON, W, H - HORIZON)
    ctx.set_source(linear(0, HORIZON, 0, H, [(0, (0.06, 0.05, 0.13)), (1, (0.02, 0.02, 0.05))]))
    ctx.fill()
    ctx.rectangle(0, HORIZON - 140, W, 220)
    ctx.set_source(linear(0, HORIZON - 140, 0, HORIZON + 80, [(0, (0.6, 0.32, 0.42, 0)), (0.6, (0.6, 0.32, 0.42, 0.28)), (1, (0.6, 0.32, 0.42, 0))]))
    ctx.fill()
    for x, y, s, col, ph in CITY:
        xx = (x - drift * (0.3 + (y - HORIZON) / 500)) % W
        a = 0.65 + 0.35 * math.sin(t * 3 + ph)
        if s > 2.4:
            glow(ctx, xx, y, s * 5, col, 0.35 * a)
        disc(ctx, xx, y, s, rgba(col, a))


def runway(ctx, t):
    vx, vy = 640, HORIZON + 8
    for k in range(18):
        u = ((k / 18) + t * 0.10) % 1
        u2 = u * u
        y = vy + (H + 300 - vy) * u2
        for side in (-1, 1):
            x = vx + side * (26 + 560 * u2)
            glow(ctx, x, y, 6 + 40 * u2, (1, 0.88, 0.55), 0.7, add=True)
            disc(ctx, x, y, 1.5 + 7 * u2, (1, 0.95, 0.8))
    # el "conejo": destellos que corren hacia la pista
    k = int(t * 12) % 10
    u = 0.5 - k * 0.045
    glow(ctx, vx, vy + (H + 300 - vy) * u * u, 60 * u + 10, (1, 1, 1), 0.9, add=True)


# ---------- el avión ----------

def plane(ctx, t, x, y, s=1.0, rot=0.0, win=lambda i: 1.0, beam=True):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    if beam:  # foco de aterrizaje
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        poly(ctx, [(300, 92), (1400, -140), (1400, 620)],
             linear(300, 92, 1150, 240, [(0, (1, 0.95, 0.8, 0.42)), (1, (1, 0.95, 0.8, 0))]))
        ctx.restore()
    # ala y estabilizador del lado lejano
    poly(ctx, [(60, -30), (-60, -30), (-170, -100), (-140, -104)], (0.20, 0.22, 0.33))
    poly(ctx, [(-330, -35), (-445, -90), (-468, -86), (-395, -28)], (0.20, 0.22, 0.33))
    # fuselaje
    ctx.move_to(-440, -32)
    ctx.curve_to(-380, -52, -320, -58, -260, -58)
    ctx.line_to(280, -58)
    ctx.curve_to(350, -58, 402, -36, 420, 0)
    ctx.curve_to(410, 30, 378, 52, 300, 52)
    ctx.line_to(-200, 52)
    ctx.curve_to(-300, 52, -390, 18, -440, -32)
    ctx.close_path()
    ctx.set_source(linear(0, -58, 0, 52, [(0, (0.86, 0.89, 0.98)), (0.35, (0.66, 0.70, 0.84)), (1, (0.20, 0.22, 0.36))]))
    ctx.fill_preserve()
    ctx.save()
    ctx.clip()
    ctx.rectangle(-460, 12, 900, 9)
    source(ctx, (0.85, 0.22, 0.26))
    ctx.fill()
    ctx.rectangle(-460, -62, 900, 16)
    ctx.set_source(linear(0, -62, 0, -46, [(0, (1, 1, 1, 0.55)), (1, (1, 1, 1, 0))]))
    ctx.fill()
    for dx in (252, -214):
        rr(ctx, dx - 14, -46, 28, 82, 8)
        source(ctx, (0.1, 0.1, 0.2, 0.35))
        ctx.set_line_width(2.5)
        ctx.stroke()
    ctx.restore()
    # ventanillas
    for i in range(16):
        wx = 225 - i * 30
        on = clamp(win(i))
        fill_rr(ctx, wx - 7, -41, 14, 20, 6, mix((0.10, 0.11, 0.22), (1.0, 0.88, 0.58), on))
        if on > 0:
            glow(ctx, wx, -31, 26, (1.0, 0.8, 0.45), 0.55 * on, add=True)
    # cabina de mando
    poly(ctx, [(332, -38), (372, -34), (392, -18), (338, -20)],
         linear(332, -38, 392, -18, [(0, (0.05, 0.07, 0.15)), (1, (0.25, 0.32, 0.5))]))
    stroke(ctx, [(340, -33), (366, -31)], (1, 1, 1, 0.4), 2)
    # cola
    poly(ctx, [(-250, -56), (-392, -218), (-455, -218), (-440, -36)],
         linear(0, -218, 0, -40, [(0, (0.62, 0.14, 0.20)), (1, (0.88, 0.24, 0.28))]))
    stroke(ctx, [(-402, -190), (-332, -110)], (1, 1, 1, 0.85), 7)
    stroke(ctx, [(-427, -160), (-367, -92)], (1, 1, 1, 0.85), 7)
    poly(ctx, [(-330, -8), (-470, -58), (-492, -50), (-400, 8)],
         linear(0, -58, 0, 8, [(0, (0.75, 0.78, 0.9)), (1, (0.35, 0.37, 0.5))]))
    # tren de aterrizaje
    stroke(ctx, [(-40, 50), (-40, 104)], (0.45, 0.47, 0.55), 10)
    for wx in (-56, -24):
        disc(ctx, wx, 110, 17, (0.06, 0.06, 0.09))
        disc(ctx, wx, 110, 6, (0.5, 0.5, 0.55))
    stroke(ctx, [(298, 48), (298, 92)], (0.45, 0.47, 0.55), 8)
    disc(ctx, 298, 98, 13, (0.06, 0.06, 0.09))
    disc(ctx, 298, 98, 4, (0.5, 0.5, 0.55))
    # ala cercana y motor
    poly(ctx, [(110, 28), (-195, 138), (-252, 143), (-55, 30)],
         linear(0, 28, 0, 143, [(0, (0.78, 0.80, 0.9)), (1, (0.36, 0.38, 0.52))]))
    poly(ctx, [(-195, 138), (-226, 92), (-240, 92), (-252, 143)], (0.55, 0.57, 0.7))
    poly(ctx, [(25, 30), (75, 30), (55, 52), (0, 52)], (0.45, 0.47, 0.58))
    rr(ctx, -75, 44, 180, 62, 31)
    ctx.set_source(linear(0, 44, 0, 106, [(0, (0.82, 0.85, 0.95)), (1, (0.25, 0.27, 0.40))]))
    ctx.fill()
    ctx.save()
    ctx.translate(105, 75)
    ctx.scale(12, 31)
    disc(ctx, 0, 0, 1, (0.05, 0.05, 0.10))
    ctx.restore()
    poly(ctx, [(-75, 56), (-110, 75), (-75, 94)], (0.30, 0.30, 0.38))
    # luces: anticolisión roja, navegación verde (ala derecha) y estroboscópicas
    if (t * 1.1) % 1 < 0.12:
        glow(ctx, -60, -60, 55, (1, 0.15, 0.1), 0.9, add=True)
        glow(ctx, -40, 54, 45, (1, 0.15, 0.1), 0.8, add=True)
    glow(ctx, -250, 142, 40, GREEN_LIGHT, 0.75, add=True)
    if (t * 0.85 + 0.4) % 1 < 0.06:
        glow(ctx, -250, 142, 130, (1, 1, 1), 1.0, add=True)
        glow(ctx, -458, -40, 110, (1, 1, 1), 0.9, add=True)
    ctx.restore()


# ---------- interior de la cabina (perspectiva de un punto) ----------

VP = (540, 690)
F = 900
CAM_Y = 0.55
PROFILE = [(-1, 0), (1, 0), (1, 0.80), (0.66, 1.10), (-0.66, 1.10), (-1, 0.80)]
SURF_COLS = [(0.20, 0.22, 0.32), (0.86, 0.83, 0.78), (0.93, 0.93, 0.95), (0.97, 0.97, 0.98), (0.93, 0.93, 0.95), (0.86, 0.83, 0.78)]
ROWS = [1.15 + 0.62 * k for k in range(10)]
Z_FAR = 7.4
SEAT_X = [(0.25, 0.48), (0.50, 0.73), (0.75, 0.98)]
HAIR = [(0.10, 0.07, 0.05), (0.25, 0.15, 0.08), (0.55, 0.40, 0.22), (0.45, 0.45, 0.48)]


def P(X, Y, Z, cz):
    z = max(0.05, Z - cz)
    return (VP[0] + X * F / z, VP[1] + (CAM_Y - Y) * F / z)


def cabin(ctx, t, light=1.0, mood=(1.0, 0.93, 0.82), cz=0.0, floor_lights=0.0, exit_glow=0.0, sleeper=False):
    dark = (0.012, 0.015, 0.035)

    def L(base, k=1.0):
        lit = tuple(min(1, b * m * k) for b, m in zip(base, mood))
        return mix(mix(dark, mul(base, 0.05), 0.5), lit, light)

    zn = cz + 0.3
    ctx.rectangle(0, 0, W, H)
    source(ctx, L((0.4, 0.4, 0.42), 0.4))
    ctx.fill()
    # paredes, techo, compartimentos y suelo
    for j in range(len(PROFILE)):
        a, b = PROFILE[j], PROFILE[(j + 1) % len(PROFILE)]
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        col = L(SURF_COLS[j])
        n0, n1 = P(*m, zn + 0.4, cz), P(*m, Z_FAR, cz)
        poly(ctx, [P(*a, zn, cz), P(*b, zn, cz), P(*b, Z_FAR, cz), P(*a, Z_FAR, cz)],
             linear(*n0, *n1, [(0, col), (1, mul(col, 0.42))]))
    # moqueta del pasillo
    poly(ctx, [P(-0.22, 0.001, zn, cz), P(0.22, 0.001, zn, cz), P(0.22, 0.001, Z_FAR, cz), P(-0.22, 0.001, Z_FAR, cz)],
         linear(*P(0, 0, zn + 0.4, cz), *P(0, 0, Z_FAR, cz), [(0, L((0.30, 0.18, 0.22))), (1, L((0.13, 0.08, 0.10)))]))
    # mamparo del fondo con su puerta y el letrero de salida
    poly(ctx, [P(x, y, Z_FAR, cz) for x, y in PROFILE], L((0.80, 0.78, 0.74), 0.5))
    x0, y0 = P(-0.30, 0.80, Z_FAR, cz)
    x1, y1 = P(0.30, 0.0, Z_FAR, cz)
    fill_rr(ctx, x0, y0, x1 - x0, y1 - y0, 6, L((0.55, 0.55, 0.58), 0.5))
    sx0, sy0 = P(-0.20, 1.00, Z_FAR, cz)
    sx1, sy1 = P(0.20, 0.87, Z_FAR, cz)
    on = max(exit_glow, 0.25 * light)
    fill_rr(ctx, sx0, sy0, sx1 - sx0, sy1 - sy0, 4, mix((0.04, 0.12, 0.07), (0.25, 1.0, 0.55), on))
    glow(ctx, (sx0 + sx1) / 2, (sy0 + sy1) / 2, (sx1 - sx0) * 2.4, GREEN_LIGHT, 0.55 * exit_glow, add=True)
    # ventanillas en las paredes
    for z in ROWS:
        zz = z + 0.31
        if zz - cz < 0.35:
            continue
        for side in (-1, 1):
            q = [P(side, 0.42, zz - 0.13, cz), P(side, 0.66, zz - 0.13, cz), P(side, 0.66, zz + 0.13, cz), P(side, 0.42, zz + 0.13, cz)]
            poly(ctx, q, (0.05, 0.07, 0.16))
            path(ctx, q)
            source(ctx, L((0.7, 0.7, 0.72), 0.6))
            ctx.set_line_width(max(1.5, 0.02 * F / (zz - cz)))
            ctx.stroke()
    # tiras de luz del techo
    for side in (-1, 1):
        q = [P(side * 0.58, 1.1, zn, cz), P(side * 0.66, 1.1, zn, cz), P(side * 0.66, 1.1, Z_FAR, cz), P(side * 0.58, 1.1, Z_FAR, cz)]
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        poly(ctx, q, rgba(mix((0, 0, 0), mood, 1.0), 0.9 * light))
        ctx.restore()
    # filas de asientos, de la más lejana a la más cercana
    for k in reversed(range(len(ROWS))):
        z = ROWS[k]
        zc = z - cz
        if zc < 0.32:
            continue
        sc = F / zc
        for side in (-1, 1):
            for j, (xa, xb) in enumerate(SEAT_X):
                X0, X1 = sorted((side * xa, side * xb))
                rnd = random.Random(k * 31 + j * 7 + side)
                occupied = rnd.random() < 0.6
                is_sleeper = sleeper and k == 1 and side == -1 and j == 1
                if occupied or is_sleeper:
                    hx = (X0 + X1) / 2 + (0.05 if is_sleeper else 0)
                    hy = 0.97 if is_sleeper else 1.0 + rnd.uniform(-0.02, 0.04)
                    cx, cy = P(hx, hy, z + 0.14, cz)
                    hr = 0.105 * F / (z + 0.14 - cz)
                    hair = HAIR[rnd.randrange(len(HAIR))]
                    disc(ctx, cx, cy, hr, radial(cx - hr * 0.3, cy - hr * 0.4, hr * 1.2, [(0, L(mul(hair, 1.9))), (1, L(hair))]))
                ax, ay = P(X0, 0.95, z, cz)
                bx, by = P(X1, 0.30, z, cz)
                fill_rr(ctx, ax, ay, bx - ax, by - ay, 0.05 * sc,
                        linear(0, ay, 0, by, [(0, L((0.24, 0.32, 0.58))), (1, L((0.10, 0.14, 0.28)))]))
                hx0, hy0 = P(X0 + 0.02, 0.94, z - 0.005, cz)
                hx1, hy1 = P(X1 - 0.02, 0.80, z - 0.005, cz)
                fill_rr(ctx, hx0, hy0, hx1 - hx0, hy1 - hy0, 0.03 * sc, L((0.93, 0.93, 0.96)))
            # sombra bajo la fila
            ax, ay = P(side * 0.25, 0.30, z + 0.05, cz)
            bx, by = P(side * 0.98, 0.0, z + 0.4, cz)
            ctx.rectangle(min(ax, bx), ay, abs(bx - ax), by - ay)
            source(ctx, (0, 0, 0, 0.35))
            ctx.fill()
    # luces de emergencia del suelo, con un destello que corre hacia la salida
    if floor_lights > 0:
        z = 0.75
        while z < Z_FAR:
            if z - cz > 0.3:
                chase = 0.5 + 0.5 * max(0.0, math.cos((z - cz - t * 3.2) * 1.6)) ** 4
                for side in (-1, 1):
                    x, y = P(side * 0.235, 0.004, z, cz)
                    r = 0.02 * F / (z - cz)
                    glow(ctx, x, y, r * 6, (1, 0.82, 0.45), 0.6 * floor_lights * chase, add=True)
                    disc(ctx, x, y, r, rgba((1, 0.92, 0.7), floor_lights))
            z += 0.3


# ---------- letrero de salida ----------

def exit_sign(ctx, x, y, s=1.0, on=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    glow(ctx, 0, 0, 560, (0.2, 1.0, 0.5), 0.40 * on, add=True)
    for dx in (-200, 200):
        fill_rr(ctx, dx - 8, -360, 16, 240, 6, (0.22, 0.24, 0.27))
    fill_rr(ctx, -360, -130, 720, 260, 30, linear(0, -130, 0, 130, [(0, (0.85, 0.87, 0.9)), (1, (0.40, 0.42, 0.47))]))
    fill_rr(ctx, -332, -104, 664, 208, 18, linear(0, -104, 0, 104, [
        (0, mix((0.05, 0.25, 0.12), (0.30, 1.0, 0.58), on)), (1, mix((0.03, 0.14, 0.08), (0.04, 0.62, 0.30), on))]))
    white = (1, 1, 1)
    rr(ctx, -150, -76, 82, 152, 4)
    source(ctx, white)
    ctx.set_line_width(9)
    ctx.stroke()
    disc(ctx, -205, -52, 16, white)
    stroke(ctx, [(-212, -30), (-232, 18)], white, 19)
    stroke(ctx, [(-214, -24), (-188, -6), (-170, -20)], white, 13)
    stroke(ctx, [(-216, -22), (-240, -4), (-258, -12)], white, 13)
    stroke(ctx, [(-232, 18), (-208, 40), (-214, 74)], white, 15)
    stroke(ctx, [(-232, 18), (-258, 36), (-284, 30)], white, 15)
    text(ctx, "SALIDA", 135, 0, 98, col=white)
    ctx.rectangle(-332, -104, 664, 90)
    ctx.set_source(linear(0, -104, 0, -14, [(0, (1, 1, 1, 0.22)), (1, (1, 1, 1, 0))]))
    ctx.fill()
    ctx.restore()


# ---------- el ojo ----------

IRIS_FIBERS = [(_rng.uniform(0, 2 * math.pi), _rng.uniform(0.75, 1.0), _rng.choice([(0.85, 0.75, 0.40), (0.20, 0.32, 0.20), (0.55, 0.70, 0.45)]),
                _rng.uniform(0.15, 0.4)) for _ in range(140)]


def eye(ctx, x, y, s=1.0, pupil=40, light=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    # piel alrededor
    soft_ellipse(ctx, 0, -10, 430, 300, (0.30, 0.14, 0.12), 0.45)
    # ceja
    up = bezier((-340, -300), (-160, -400), (150, -410), (340, -300), 30)
    pts = []
    for i, (px, py) in enumerate(up):
        u = i / 30
        th = 46 * math.sin(math.pi * min(1, u * 1.15)) ** 0.6 + 6
        pts.append((px, py - th / 2))
    for i, (px, py) in reversed(list(enumerate(up))):
        u = i / 30
        th = 46 * math.sin(math.pi * min(1, u * 1.15)) ** 0.6 + 6
        pts.append((px, py + th / 2))
    poly(ctx, pts, (0.22, 0.13, 0.09, 0.95))
    # pliegue del párpado
    stroke(ctx, bezier((-270, -70), (-150, -260), (160, -270), (285, -80)), (0.35, 0.16, 0.13, 0.45), 9)

    def almond():
        ctx.move_to(-300, 0)
        ctx.curve_to(-180, -195, 170, -205, 300, -12)
        ctx.curve_to(180, 150, -170, 160, -300, 0)
        ctx.close_path()

    almond()
    ctx.save()
    ctx.clip()
    ctx.rectangle(-320, -220, 640, 400)
    ctx.set_source(radial(0, -20, 330, [(0, (0.98, 0.97, 0.95)), (0.7, (0.92, 0.88, 0.86)), (1, (0.78, 0.62, 0.60))]))
    ctx.fill()
    ix, iy, ir = 0, -18, 132
    disc(ctx, ix, iy, ir, radial(ix, iy, ir, [(0, (0.82, 0.66, 0.30)), (0.35, (0.50, 0.62, 0.38)),
                                               (0.85, (0.24, 0.40, 0.28)), (1, (0.08, 0.13, 0.10))]))
    for ang, ln, col, a in IRIS_FIBERS:
        r0 = pupil + 4
        r1 = r0 + (ir - 6 - r0) * ln
        stroke(ctx, [(ix + r0 * math.cos(ang), iy + r0 * math.sin(ang)),
                     (ix + r1 * math.cos(ang + 0.05), iy + r1 * math.sin(ang + 0.05))], rgba(col, a), 3)
    disc(ctx, ix, iy, pupil + 6, radial(ix, iy, pupil + 6, [(0, (0.01, 0.01, 0.02)), (0.85, (0.02, 0.02, 0.03)), (1, (0.02, 0.02, 0.03, 0))]))
    # sombra del párpado superior sobre el ojo
    ctx.rectangle(-320, -220, 640, 220)
    ctx.set_source(linear(0, -200, 0, -60, [(0, (0.15, 0.05, 0.05, 0.55)), (1, (0, 0, 0, 0))]))
    ctx.fill()
    # brillos
    ctx.save()
    ctx.translate(-48, -70)
    ctx.scale(30, 21)
    disc(ctx, 0, 0, 1, (1, 1, 1, 0.92 * (0.4 + 0.6 * light)))
    ctx.restore()
    disc(ctx, 42, 28, 8, (1, 1, 1, 0.5 * light))
    ctx.restore()
    # párpados y pestañas
    upper = bezier((-300, 0), (-180, -195), (170, -205), (300, -12), 26)
    stroke(ctx, upper, (0.20, 0.10, 0.08), 11)
    stroke(ctx, bezier((300, -12), (180, 150), (-170, 160), (-300, 0)), (0.80, 0.52, 0.46, 0.8), 8)
    for i in range(3, 25):
        (px, py), (qx, qy) = upper[i - 1], upper[i + 1]
        dx, dy = qx - px, qy - py
        nl = math.hypot(dx, dy) or 1
        nx, ny = dy / nl, -dx / nl  # normal hacia fuera (arriba)
        u = i / 26
        ln = 34 + 44 * u
        tx, ty = px + nx * ln * 0.6 + dx / nl * ln * 0.35, py + ny * ln * 0.6 + dy / nl * ln * 0.35
        ex, ey = px + nx * ln + dx / nl * ln * 0.75, py + ny * ln * 0.9 + dy / nl * ln * 0.4
        ctx.move_to(px, py)
        ctx.curve_to(tx, ty, tx, ty, ex, ey)
        source(ctx, (0.10, 0.06, 0.05))
        ctx.set_line_width(4.5)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    ctx.restore()


def skin(ctx, x0, y0, w, h, k=1.0):
    ctx.rectangle(x0, y0, w, h)
    ctx.set_source(radial(x0 + w / 2, y0 + h * 0.42, max(w, h) * 0.75,
                          [(0, mul((0.88, 0.64, 0.52), k)), (1, mul((0.52, 0.32, 0.28), k))]))
    ctx.fill()


# ---------- ventanilla ----------

def cabin_wall(ctx, light):
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(linear(0, 0, W, H, [(0, mul((0.82, 0.80, 0.82), light)), (1, mul((0.45, 0.43, 0.50), light))]))
    ctx.fill()
    for x in (70, 1010):
        stroke(ctx, [(x, 0), (x, H)], (0, 0, 0, 0.18), 4)
    stroke(ctx, [(0, 1240), (W, 1240)], (0, 0, 0, 0.18), 4)


def outside_night(ctx, t, fire=0.0):
    ctx.rectangle(-220, -340, 440, 680)
    ctx.set_source(linear(0, -330, 0, 70, [(0, (0.03, 0.04, 0.12)), (1, (0.30, 0.17, 0.33))]))
    ctx.fill()
    for i in range(14):
        disc(ctx, -190 + (i * 97) % 380, -300 + (i * 61) % 300, 1.8, (1, 1, 1, 0.5 + 0.5 * math.sin(t * 2 + i)))
    ctx.rectangle(-220, 70, 440, 280)
    source(ctx, (0.04, 0.04, 0.09))
    ctx.fill()
    for bx, by, s, col in PANE_LIGHTS:
        xx = (bx - t * 260 * (0.4 + (by - 70) / 260)) % 520 - 260
        glow(ctx, xx, by, s * 5, col, 0.35)
        disc(ctx, xx, by, s * 0.8, col)
    # ala derecha con su motor
    flick = 0.8 + 0.2 * math.sin(t * 23) * math.sin(t * 7)
    poly(ctx, [(-260, 170), (140, 62), (165, 80), (-260, 330)],
         linear(-260, 300, 160, 70, [(0, mix((0.45, 0.47, 0.58), (1.0, 0.55, 0.30), 0.6 * fire * flick)), (1, (0.16, 0.17, 0.26))]))
    poly(ctx, [(140, 62), (150, 8), (162, 10), (165, 80)], (0.22, 0.23, 0.33))
    glow(ctx, 156, 40, 46, GREEN_LIGHT, 0.8, add=True)
    rr(ctx, -210, 196, 220, 88, 44)
    ctx.set_source(linear(0, 196, 0, 284, [(0, mix((0.62, 0.64, 0.74), (1, 0.6, 0.3), 0.5 * fire * flick)), (1, (0.12, 0.13, 0.20))]))
    ctx.fill()
    ctx.save()
    ctx.translate(10, 240)
    ctx.scale(14, 44)
    disc(ctx, 0, 0, 1, (0.03, 0.03, 0.06))
    ctx.restore()
    if fire > 0:
        for i in range(16):  # humo
            ph = (t * 0.45 + i / 16) % 1
            disc(ctx, -90 - ph * 300, 170 - ph * 420, 30 + ph * 120, (0.22, 0.20, 0.24, fire * 0.28 * (1 - ph)))
        glow(ctx, -80, 200, 420, (1, 0.5, 0.15), 0.5 * fire * flick, add=True)
        for i in range(44):  # llamas
            rnd = random.Random(i)
            ph = (t * 1.7 + i * 0.137) % 1
            x = -80 + rnd.uniform(-80, 70) - ph * 170 * rnd.uniform(0.6, 1.2)
            y = 200 - ph * 300 * rnd.uniform(0.7, 1.1)
            r = (34 + rnd.uniform(0, 30)) * (1 - ph * 0.65)
            glow(ctx, x, y, r * 1.9, mix((1, 0.95, 0.6), (1, 0.32, 0.05), ph), fire * (1 - ph) * 0.85, add=True)


def window(ctx, t, shade=0.0, fire=0.0, light=0.6, cx=540, cy=720, s=1.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    soft_ellipse(ctx, 0, 40, 380, 500, (0, 0, 0), 0.40)
    fill_rr(ctx, -280, -410, 560, 820, 270, linear(0, -410, 0, 410, [(0, mul((0.95, 0.94, 0.96), light * 1.25)), (1, mul((0.60, 0.59, 0.64), light * 1.25))]))
    fill_rr(ctx, -238, -362, 476, 724, 232, linear(0, -362, 0, 362, [
        (0, mul((0.28, 0.28, 0.34), light * 1.2)), (0.3, mul((0.55, 0.55, 0.62), light * 1.2)), (1, mul((0.82, 0.82, 0.86), light * 1.2))]))
    rr(ctx, -200, -318, 400, 636, 196)
    ctx.save()
    ctx.clip()
    outside_night(ctx, t, fire)
    if shade > 0:
        y1 = -318 + 636 * shade
        ctx.rectangle(-210, -330, 420, y1 + 330)
        ctx.set_source(linear(0, -330, 0, y1, [(0, mul((0.95, 0.94, 0.91), light * 1.3)), (1, mul((0.80, 0.79, 0.76), light * 1.3))]))
        ctx.fill()
        yy = -300
        while yy < y1 - 30:
            stroke(ctx, [(-210, yy), (210, yy)], (0, 0, 0, 0.05), 2)
            yy += 34
        ctx.rectangle(-210, y1, 420, 44)
        ctx.set_source(linear(0, y1, 0, y1 + 44, [(0, (0, 0, 0, 0.4)), (1, (0, 0, 0, 0))]))
        ctx.fill()
        fill_rr(ctx, -210, y1 - 24, 420, 24, 6, mul((0.72, 0.71, 0.70), light * 1.3))
        stroke(ctx, [(-200, y1 - 21), (200, y1 - 21)], (1, 1, 1, 0.35), 2)
        fill_rr(ctx, -45, y1 - 17, 90, 10, 5, (0, 0, 0, 0.3))
    poly(ctx, [(-210, -110), (-60, -330), (20, -330), (-210, 0)], (1, 1, 1, 0.06))
    poly(ctx, [(-210, 60), (90, -330), (125, -330), (-210, 105)], (1, 1, 1, 0.04))
    ctx.restore()
    rr(ctx, -200, -318, 400, 636, 196)
    source(ctx, (0, 0, 0, 0.45))
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.restore()


# ---------- iconos ----------

def warning(ctx, x, y, p, t):
    s = ease_out_back(p) * (1 + 0.06 * math.sin(t * 9))
    if s <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    glow(ctx, 0, 10, 220, RED, 0.6, add=True)
    ctx.move_to(0, -100)
    ctx.line_to(105, 80)
    ctx.line_to(-105, 80)
    ctx.close_path()
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(26)
    source(ctx, RED)
    ctx.stroke_preserve()
    ctx.fill()
    text(ctx, "!", 0, 18, 130, col=(1, 1, 1))
    ctx.restore()



# ---------- escenas ----------

def s_hook(ctx, t):
    sky(ctx, t)
    clouds(ctx, t)
    ground(ctx, t, drift=t * 40)
    runway(ctx, t)
    plane(ctx, t, 420 + 55 * t, 770 + 22 * t, s=1.0, rot=0.045, win=lambda i: 1 - prog(t, 2.2 + i * 0.05, 0.06))
    clouds(ctx, t, front=True)


def s_sleep(ctx, t):
    cabin(ctx, t, light=0.55, mood=(0.62, 0.55, 1.0), sleeper=True)
    hx, hy = P(-0.56, 0.97, ROWS[1] + 0.14, 0)
    for i in range(3):
        ph = (t * 0.6 + i / 3) % 1
        text(ctx, "Z", hx + 40 + ph * 110, hy - 70 - ph * 200, 50 + 40 * ph, col=(1, 1, 1, 1 - ph), outline=(0.2, 0.2, 0.5, 1 - ph), ow=6)
    p = ease_out_back(prog(t, 0.9, 0.35))
    if p > 0:
        ctx.save()
        ctx.translate(hx + 40, hy - 60)
        ctx.scale(p, p)
        glow(ctx, 0, 0, 330, RED, 0.45, add=True)
        ctx.arc(0, 0, 190, 0, 2 * math.pi)
        source(ctx, RED)
        ctx.set_line_width(34)
        ctx.stroke()
        stroke(ctx, [(-134, 134), (134, -134)], RED, 34)
        ctx.restore()


def s_evacuate(ctx, t):
    pulse = 0.5 + 0.5 * math.sin(t * 6)
    blurred(ctx, lambda c: cabin(c, t, light=0.18, mood=(1.0, 0.25, 0.25), floor_lights=1.0, exit_glow=1.0))
    ctx.rectangle(0, 0, W, H)
    source(ctx, (0.9, 0.05, 0.05, 0.10 + 0.18 * pulse))
    ctx.fill()
    shake = 4 * math.sin(t * 37) * (t < 1.5)
    exit_sign(ctx, 540 + shake, 700, s=1.25 * (0.85 + 0.15 * ease_out_back(prog(t, 0, 0.45))), on=0.75 + 0.25 * pulse)


def blackout_level(t, t0):
    v = 1.0
    for dt, val in [(0.0, 0.15), (0.07, 0.85), (0.13, 0.10), (0.20, 0.6), (0.27, 0.0)]:
        if t >= t0 + dt:
            v = val
    return v


def s_dark(ctx, t):
    lv = blackout_level(t, 1.0)
    cabin(ctx, t, light=0.08 + 0.92 * lv, mood=(1.0, 0.93, 0.82))
    if t > 1.27:
        ctx.rectangle(0, 0, W, H)
        source(ctx, (0, 0, 0.01, 0.9))
        ctx.fill()
        p = prog(t, 1.6, 0.4)
        if p > 0:
            ctx.save()
            ctx.translate(540, 700)
            s = ease_out_back(p)
            ctx.scale(s, s)
            glow(ctx, 0, 0, 260, (0.5, 0.6, 1.0), 0.25 * p, add=True)
            text(ctx, "?", 0, 0, 300, col=(1, 1, 1, p))
            ctx.restore()


def s_adapt(ctx, t):
    a = prog(t, 0.3, 2.6)
    skin(ctx, 0, 0, W, H, 0.9)
    eye(ctx, 540, 760, 1.25, pupil=36 + 66 * ease_in_out(a), light=0.4)
    ctx.rectangle(0, 0, W, H)
    source(ctx, (0.01, 0.02, 0.08, 0.80 - 0.32 * a))
    ctx.fill()
    # cronómetro
    cx, cy, r = 860, 340, 78
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    source(ctx, (1, 1, 1, 0.2))
    ctx.set_line_width(12)
    ctx.stroke()
    ctx.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * a)
    source(ctx, (1.0, 0.80, 0.24))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    text(ctx, "min", cx, cy, 40, col=(1, 1, 1, 0.9))


def s_ready(ctx, t):
    ctx.rectangle(0, 0, W, H)
    source(ctx, (0.03, 0.04, 0.09))
    ctx.fill()
    panels = [(250, 32, 0.80, "LUZ APAGADA DE GOLPE", False), (800, 98, 0.30, "LUZ BAJADA ANTES", True)]
    for i, (py, pupil, dark, lab, ok) in enumerate(panels):
        p = ease_out_back(prog(t, 0.05 + i * 0.25, 0.4))
        if p <= 0:
            continue
        ctx.save()
        ctx.translate(540, py + 260)
        ctx.scale(0.9 + 0.1 * p, 0.9 + 0.1 * p)
        ctx.translate(-540, -(py + 260))
        rr(ctx, 60, py, 960, 520, 44)
        ctx.save()
        ctx.clip()
        skin(ctx, 60, py, 960, 520, 0.9)
        eye(ctx, 540, py + 300, 0.68, pupil=pupil, light=0.4)
        ctx.rectangle(60, py, 960, 520)
        source(ctx, (0.01, 0.02, 0.08, dark))
        ctx.fill()
        ctx.restore()
        rr(ctx, 60, py, 960, 520, 44)
        source(ctx, (1, 1, 1, 0.15))
        ctx.set_line_width(4)
        ctx.stroke()
        label(ctx, lab, 92, py + 62)
        ctx.restore()
        badge(ctx, 930, py + 440, prog(t, 0.8 + i * 0.4, 0.35), ok=ok)


def s_shade(ctx, t):
    cabin_wall(ctx, 0.55)
    up = ease_in_out(prog(t, 0.5, 1.6))
    window(ctx, t, shade=1 - 0.93 * up, light=0.55)
    p = prog(t, 0.4, 0.3)
    if p > 0:
        bob = -24 * math.sin(t * 5)
        glow(ctx, 935, 720 + bob, 150, (1.0, 0.8, 0.25), 0.45 * p, add=True)
        stroke(ctx, [(935, 840 + bob), (935, 610 + bob)], rgba((1.0, 0.80, 0.24), p), 22)
        stroke(ctx, [(880, 665 + bob), (935, 605 + bob), (990, 665 + bob)], rgba((1.0, 0.80, 0.24), p), 22)


def s_danger(ctx, t):
    z = 1.0 + 0.08 * ease_in_out(t / dur(s_danger))
    cabin_wall(ctx, 0.5)
    fire = prog(t, 0.2, 0.6)
    glow(ctx, 540, 900, 900, (1, 0.45, 0.15), 0.18 * fire, add=True)
    window(ctx, t, shade=0.07, fire=fire, light=0.5, s=z)
    warning(ctx, 860, 300, prog(t, 0.9, 0.35), t)


def s_floor(ctx, t):
    cz = 1.3 * ease_in_out(t / dur(s_floor))
    cabin(ctx, t, light=0.14, mood=(0.55, 0.6, 1.0), cz=cz, floor_lights=1.0, exit_glow=1.0)
    ctx.rectangle(0, 0, W, 700)
    ctx.set_source(linear(0, 0, 0, 700, [(0, (0.3, 0.32, 0.4, 0.18)), (1, (0.3, 0.32, 0.4, 0))]))
    ctx.fill()


def s_cta(ctx, t):
    sky(ctx, t)
    ground(ctx, t, drift=t * 30)
    plane(ctx, t, 120 + 260 * t, 430 - 40 * t, s=0.5, rot=-0.08, beam=False)
    cta_button(ctx, t, 540, 900)

SCENES = [
    Scene("¿Por qué apagan las luces del avión al aterrizar de noche?", s_hook, sfx=[(0.7, "chime"), (2.2, "thunk")]),
    Scene("No es para que duermas.", s_sleep, sfx=[(0.9, "pop")]),
    Scene("Es por si hay que evacuar.", s_evacuate, sfx=[(0.05, "thunk")]),
    Scene("Si de repente todo se queda a oscuras…", s_dark, sfx=[(1.0, "thunk"), (1.6, "pop")]),
    Scene("…tus ojos tardan varios minutos en adaptarse.", s_adapt),
    Scene("Con la luz ya bajada, llegan preparados.", s_ready, sfx=[(0.8, "pop"), (1.2, "pop")]),
    Scene("Por eso también te piden subir la persiana.", s_shade, sfx=[(0.5, "whoosh")]),
    Scene("Así se ve si hay algún peligro fuera.", s_danger, sfx=[(0.9, "pop")]),
    Scene("Y las luces del suelo te guían hasta la salida.", s_floor),
    Scene("Síguenos para más curiosidades como esta.", s_cta, sfx=[(0.05, "pop"), (1.3, "pop")]),
]

POST = """¿Por qué apagan las luces del avión al aterrizar de noche? ✈️

No es para que duermas: si hubiera que evacuar, tus ojos ya estarían acostumbrados a la oscuridad. Si la luz se apaga de golpe, tardan varios minutos en adaptarse.

Por eso también te piden subir la persiana: así se ve si fuera hay algún peligro. Y las luces del suelo marcan el camino hasta la salida.

Síguenos para más curiosidades 👀

#curiosidades #sabiasque #aviones #viajar #datoscuriosos
"""

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "out", "avion-luces")
    os.makedirs(out, exist_ok=True)
    narrator = None
    if "--sin-voz" not in sys.argv:
        from voz import Narrator
        voice = sys.argv[sys.argv.index("--voz") + 1] if "--voz" in sys.argv else "dora"
        narrator = Narrator(voice)
    if "--preview" in sys.argv:
        i = sys.argv.index("--preview")
        dest = sys.argv[i + 1] if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith("--") else os.path.join(out, "preview.png")
        preview(SCENES, dest, narrator=narrator)
        print("preview:", dest)
    else:
        total = render(SCENES, os.path.join(out, "avion-luces.mp4"), cover_png=os.path.join(out, "portada.png"),
                       cover_at=(0, 1.8), narrator=narrator)
        with open(os.path.join(out, "texto-del-post.txt"), "w") as f:
            f.write(POST)
        print(f"OK: {total:.1f} s")
