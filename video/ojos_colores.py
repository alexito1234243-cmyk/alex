"""Vídeo: ¿por qué ves colores al frotarte los ojos? (fosfenos de presión)

Gancho con la experiencia que todos han vivido, giro («no es luz»), el mecanismo en 4 pasos
(apretar → la retina se estira → sus neuronas se disparan → el cerebro lo lee como luz), el dato
de Newton y una pregunta fácil de contestar al final. El gancho, la cabeza con el nervio óptico, los
fosfenos y el retrato de Newton son imágenes generadas con Flow (video/assets/ojos-colores/); el resto está dibujado.

Datos y fuentes:
- Fosfeno (del griego phôs, «luz», y phainein, «mostrar»): ver luz sin que entre luz en el ojo. Los más
  comunes son los de presión, al frotar o apretar los ojos cerrados. https://en.wikipedia.org/wiki/Phosphene
- Al deformar el globo ocular en total oscuridad se activan las células ganglionares de la retina (las
  neuronas cuyas fibras forman el nervio óptico) de forma parecida a como lo hacen con la luz; la hipótesis
  es que el estiramiento de la retina despolariza sus neuronas. Grüsser et al. (1989), registro en gatos:
  https://fis.uke.de/portal/en/publications/responses-of-retinal-ganglion-cells-to-eyeball-deformation-a-neurophysiological-basis-for-pressure-phosphenes(482ecb92-4ecf-41b3-bba3-db388b8573c2).html
- La presión se ve y no se siente como tacto porque esas conexiones van «cableadas» a la vista (Morgagni,
  Helmholtz); el mecanismo molecular sigue sin aclararse. Križaj (2016), Adv Exp Med Biol 854:693-698:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC5111544/
- Newton se metió un punzón romo («bodkin») entre el ojo y el hueso y vio círculos blancos, oscuros y de
  colores. Cuaderno de la Biblioteca de la Universidad de Cambridge, hacia 1665-1666 (la fecha exacta se
  discute): https://exhibitions.lib.cam.ac.uk/linesofthought/?p=140

Uso: python3 video/ojos_colores.py [--voz santa|dora|alex|eleven] [--sin-voz]  ->  video/out/ojos-colores/
     python3 video/ojos_colores.py --preview [png]
"""
import functools
import math
import os
import random
import sys

import cairo

from engine import clamp, ease_in_out, ease_out_back
from piezas import CYAN, GREEN, ORANGE, RED, WHITE, appear, mini_tag, panel, spaced, tech_bg
from rich import (TOP_SHORT, YELLOW, Scene, Still, bezier, clip_bg, disc, fade_top, fill_rr, glow, linear, mul, poly, preview, radial, render,
                  rgba, rr, soft_ellipse, source, stroke, text, word_time)

SKIN = (0.88, 0.66, 0.54)
RETINA = (1.0, 0.48, 0.34)
NERVE = (0.96, 0.86, 0.62)
PINK = (1.0, 0.36, 0.78)
VIOLET = (0.58, 0.42, 1.0)
INK = (0.24, 0.17, 0.11)
PHOS = [CYAN, PINK, YELLOW, GREEN, VIOLET, ORANGE]


def scene_of(fn):
    return next(s for s in SCENES if s.draw is fn)


def dur(fn):
    return scene_of(fn).duration


def w(fn, needle):
    return word_time(scene_of(fn), needle)


# ---------- lo que se ve: fosfenos ----------

_r = random.Random(12)
BLOBS = [(_r.uniform(0.4, 1.0), _r.uniform(0.4, 1.0), _r.uniform(0, 6.3), _r.uniform(0, 6.3), _r.uniform(0.2, 0.4), PHOS[k % 6])
         for k in range(14)]
SPARKS = [(_r.uniform(0, 6.3), math.sqrt(_r.random()), _r.uniform(0, 6.3), _r.uniform(2, 5)) for _ in range(70)]


def phosphenes(ctx, cx, cy, R, t, a=1.0, kind="mix", burst=0.0, base=True):
    """Lo que se ve al frotarse los ojos: manchas de color, un damero que gira, anillos y chispas.
    kind: "mix" (todo), "dots" (puntos), "stripes" (rayas) o "colors" (manchas de color).
    base=False los pinta sin fondo oscuro, encima de una foto."""
    if a <= 0:
        return
    ctx.push_group()
    if base:
        disc(ctx, cx, cy, R, (0.015, 0.012, 0.03))
    ctx.set_operator(cairo.OPERATOR_ADD)
    if kind == "mix":  # damero en anillos que giran en sentidos alternos
        for i in range(5):
            r0, r1 = R * i / 5, R * (i + 1) / 5
            rot = t * 0.45 * (1 if i % 2 else -1)
            for j in range(0, 16, 2):
                a0 = 2 * math.pi * (j + i % 2) / 16 + rot
                ctx.new_path()
                ctx.arc(cx, cy, r1, a0, a0 + 2 * math.pi / 16)
                ctx.arc_negative(cx, cy, r0, a0 + 2 * math.pi / 16, a0)
                ctx.close_path()
                source(ctx, rgba(PHOS[(i + j // 2) % len(PHOS)], 0.11))
                ctx.fill()
    if kind in ("mix", "colors"):
        k = 1.4 if kind == "colors" else 1.0
        for fx, fy, px, py, rs, col in BLOBS:
            x = cx + R * 0.55 * math.sin(fx * t * 1.3 + px)
            y = cy + R * 0.55 * math.sin(fy * t * 1.3 + py)
            glow(ctx, x, y, R * rs * k * (1 + 0.5 * burst), col, 0.5 * (0.65 + 0.35 * math.sin(t * 3 + px)))
    if kind == "mix":  # anillos que se abren desde el centro
        for j in range(3):
            u = (t * 0.35 + j / 3) % 1
            ctx.new_sub_path()
            ctx.arc(cx, cy, R * u, 0, 2 * math.pi)
            source(ctx, rgba(PHOS[j * 2], 0.45 * (1 - u)))
            ctx.set_line_width(10)
            ctx.stroke()
    if kind == "stripes":
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(t * 0.5)
        step = R / 6.5
        for j in range(-7, 8):
            pts = [(xx, j * step + 14 * math.sin(xx / 45 + t * 3 + j)) for xx in range(-int(R), int(R) + 1, 16)]
            stroke(ctx, pts, rgba(PHOS[j % len(PHOS)], 0.6), step * 0.42, cap=cairo.LINE_CAP_BUTT)
        ctx.restore()
    if kind in ("mix", "dots"):
        n, k = (70, 1.7) if kind == "dots" else (40, 1.0)
        for ang, rad, ph, sz in SPARKS[:n]:
            x = cx + R * 0.92 * rad * math.cos(ang + t * 0.2)
            y = cy + R * 0.92 * rad * math.sin(ang + t * 0.2)
            tw = 0.5 + 0.5 * math.sin(t * 5 + ph)
            glow(ctx, x, y, sz * 4 * k, WHITE, 0.6 * tw)
            disc(ctx, x, y, sz * 0.8 * k, (1, 1, 1, 0.9 * tw))
    ctx.set_operator(cairo.OPERATOR_OVER)
    pat = ctx.pop_group()
    ctx.set_source(pat)
    ctx.mask(radial(cx, cy, R, [(0, (0, 0, 0, a)), (0.78, (0, 0, 0, a)), (1, (0, 0, 0, 0))]))


# ---------- el ojo por fuera ----------

def finger(ctx, x, y, ang, length=520, s=1.0):
    """Dedo con la yema en (x, y); el resto de la mano queda en la dirección `ang`."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    soft_ellipse(ctx, length * 0.45, 40, length * 0.55, 90, (0, 0, 0), 0.35)
    fill_rr(ctx, -10, -60, length, 120, 60, linear(0, -60, 0, 60, [(0, mul(SKIN, 1.06)), (0.55, SKIN), (1, mul(SKIN, 0.70))]))
    fill_rr(ctx, 2, -50, 122, 58, 26, linear(0, -50, 0, 8, [(0, (0.99, 0.88, 0.84)), (1, (0.90, 0.72, 0.66))]))  # uña
    for kx in (200, 222):  # pliegue del nudillo
        stroke(ctx, [(kx, -44), (kx + 6, 34)], rgba(mul(SKIN, 0.68), 0.7), 4)
    ctx.restore()


# ---------- el ojo por dentro (corte de perfil, mira a la izquierda) ----------

R_EYE = 300
TH_PRESS = -2.3  # el dedo aprieta arriba y por delante


def _adiff(a, b):
    return math.atan2(math.sin(a - b), math.cos(a - b))


def eye_r(th, press):
    """Radio del globo en la dirección th: se hunde donde aprieta el dedo y se abomba un poco el resto."""
    return R_EYE * (1 + 0.035 * press - 0.22 * press * math.exp(-(_adiff(th, TH_PRESS) / 0.42) ** 2))


def deform(pts, press):
    """Lleva la deformación del globo a las piezas de delante (córnea, iris, cristalino)."""
    out = []
    for px, py in pts:
        f = eye_r(math.atan2(py, px), press) / R_EYE
        out.append((px * f, py * f))
    return out


def eye_pts(off, press, a0=-math.pi, a1=math.pi, n=160):
    pts = []
    for k in range(n + 1):
        th = a0 + (a1 - a0) * k / n
        r = eye_r(th, press) + off
        pts.append((r * math.cos(th), r * math.sin(th)))
    return pts


NERVE_PATH = bezier((R_EYE - 30, 40), (R_EYE + 90, 60), (R_EYE + 170, 120), (R_EYE + 320, 150))
CORNEA_C, CORNEA_R = -205, 150


def retina_glow(ctx, x, y, s, t, press=0.0, lit=0.0, phos=0.0):
    """La retina encendida: en amarillo (más donde se estira) o de colores, como un fosfeno."""
    if lit <= 0 and phos <= 0:
        return
    back = eye_pts(-12, press, -2.05, 2.05, 120)
    for k in range(0, len(back), 6):
        th = -2.05 + 4.1 * k / (len(back) - 1)
        px, py = x + s * back[k][0], y + s * back[k][1]
        st = math.exp(-(_adiff(th, TH_PRESS) / 0.8) ** 2)
        if lit > 0:
            glow(ctx, px, py, 48 * s, YELLOW, lit * (0.15 + 0.85 * st) * (0.7 + 0.3 * math.sin(t * 12 + k)), add=True)
        if phos > 0:
            glow(ctx, px, py, 54 * s, PHOS[(k // 6) % len(PHOS)], phos * (0.5 + 0.5 * math.sin(t * 4 + k * 0.7)), add=True)


def eye_section(ctx, x, y, s, t, press=0.0, lit=0.0, strain=0.0, phos=0.0, pulses=()):
    """Corte del ojo: esclerótica, córnea, iris, cristalino, la retina al fondo y el nervio óptico detrás.
    lit: la retina se enciende (más donde se estira); phos: se enciende de colores; strain: flechas de
    estiramiento; pulses: posiciones (0-1) de impulsos que salen por el nervio."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    soft_ellipse(ctx, 40, 370, 400, 60, (0, 0, 0), 0.5)
    stroke(ctx, NERVE_PATH, mul(NERVE, 0.68), 88, close=False)
    stroke(ctx, NERVE_PATH, NERVE, 64, close=False)
    for u in pulses:
        px, py = NERVE_PATH[min(len(NERVE_PATH) - 1, int(u * (len(NERVE_PATH) - 1)))]
        glow(ctx, px, py, 64, YELLOW, 0.9, add=True)
        disc(ctx, px, py, 13, (1, 1, 0.85))
    poly(ctx, eye_pts(14, press), radial(-60, -90, 430, [(0, (0.98, 0.98, 1.0)), (1, (0.72, 0.73, 0.80))]))
    poly(ctx, eye_pts(-4, press), (0.42, 0.10, 0.13))
    poly(ctx, eye_pts(-20, press), radial(-40, 0, 330, [(0, (0.15, 0.17, 0.30)), (1, (0.05, 0.06, 0.12))]))
    stroke(ctx, eye_pts(-12, press, -2.05, 2.05, 120), RETINA, 12, close=False)
    retina_glow(ctx, 0, 0, 1, t, press, lit, phos)
    if strain > 0:  # la retina se estira junto a la zona apretada
        col = rgba(YELLOW, strain)
        for th in (-1.6, -1.15, -0.7):
            r = eye_r(th, press) - 50
            px, py = r * math.cos(th), r * math.sin(th)
            tx, ty = -math.sin(th), math.cos(th)
            nx, ny = -ty, tx
            L = 24 + 16 * strain * (0.5 + 0.5 * math.sin(t * 10))
            for d in (-1, 1):
                ex, ey = px + d * L * tx, py + d * L * ty
                stroke(ctx, [(px, py), (ex, ey)], col, 5, close=False)
                stroke(ctx, [(ex - d * 12 * tx + 9 * nx, ey - d * 12 * ty + 9 * ny), (ex, ey),
                             (ex - d * 12 * tx - 9 * nx, ey - d * 12 * ty - 9 * ny)], col, 5, close=False)
    lens = [(-225 + 40 * math.cos(a), 108 * math.sin(a)) for a in [k * math.pi / 30 for k in range(61)]]
    poly(ctx, deform(lens, press), (0.86, 0.92, 1.0, 0.6))
    for sy in (-1, 1):  # iris
        stroke(ctx, deform([(-272, sy * 44), (-272, sy * 128)], press), (0.30, 0.55, 0.92), 16, close=False)
    cornea = [(CORNEA_C + CORNEA_R * math.cos(a), CORNEA_R * math.sin(a)) for a in [math.pi - 1.0 + k * 2.0 / 40 for k in range(41)]]
    poly(ctx, deform(cornea, press), (0.75, 0.88, 1.0, 0.22))
    stroke(ctx, deform(cornea, press), (0.86, 0.93, 1.0, 0.9), 6, close=False)
    ctx.restore()


def eye_point(x, y, s, th, press, off=0.0):
    """Punto de la superficie del ojo en coordenadas de pantalla."""
    r = eye_r(th, press) + off
    return x + s * r * math.cos(th), y + s * r * math.sin(th)


# ---------- iconos ----------

def bulb(ctx, x, y, s, on):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    if on > 0:
        glow(ctx, 0, 0, 170, YELLOW, 0.55 * on, add=True)
    disc(ctx, 0, 0, 52, rgba((1.0, 0.95, 0.70) if on > 0.5 else (0.32, 0.33, 0.38), 1))
    fill_rr(ctx, -26, 40, 52, 46, 8, (0.62, 0.63, 0.68))
    for k in range(3):
        stroke(ctx, [(-26, 52 + 12 * k), (26, 52 + 12 * k)], (0.40, 0.41, 0.45), 3, close=False)
    ctx.restore()


def eye_icon(ctx, x, y, s, lit=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    top = bezier((-80, 0), (-40, -52), (40, -52), (80, 0), 16)
    bottom = bezier((80, 0), (40, 52), (-40, 52), (-80, 0), 16)
    poly(ctx, top + bottom, (0.95, 0.95, 0.98))
    disc(ctx, 0, 0, 30, (0.30, 0.55, 0.92))
    disc(ctx, 0, 0, 13, (0.03, 0.03, 0.05))
    if lit > 0:
        glow(ctx, 0, 0, 90, YELLOW, 0.5 * lit, add=True)
    stroke(ctx, top + bottom, (0.12, 0.13, 0.18), 5)
    ctx.restore()


_rb = random.Random(5)
FOLDS = [[(_rb.uniform(-1, 1), _rb.uniform(-1, 1)) for _ in range(4)] for _ in range(18)]


def brain(ctx, x, y, s, t, lit=0.0, back_lit=0.0):
    """Cerebro de perfil (delante a la izquierda) con circunvoluciones; back_lit enciende la zona de la vista."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    disc(ctx, 70, 78, 38, (0.78, 0.48, 0.58))  # cerebelo
    ctx.save()
    ctx.scale(1.0, 0.78)
    disc(ctx, 0, 0, 120, radial(-30, -40, 150, [(0, (0.98, 0.70, 0.78)), (1, (0.80, 0.46, 0.58))]))
    ctx.new_sub_path()
    ctx.arc(0, 0, 120, 0, 2 * math.pi)
    ctx.restore()
    ctx.save()
    ctx.clip()
    for pts in FOLDS:
        p = [(x_ * 110, y_ * 80) for x_, y_ in pts]
        stroke(ctx, bezier(*p, 12), (0.62, 0.30, 0.42, 0.55), 5, close=False)
    ctx.restore()
    if back_lit > 0:
        glow(ctx, 92, 4, 90, YELLOW, 0.8 * back_lit * (0.75 + 0.25 * math.sin(t * 9)), add=True)
    if lit > 0:
        glow(ctx, 0, 0, 200, YELLOW, 0.5 * lit, add=True)
    ctx.restore()


# ---------- fotos (generadas con Flow / Nano Banana) ----------

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "ojos-colores")
HOOK_DY = 200  # la foto del gancho baja para que sus colores no queden bajo los subtítulos
HOOK_TOP = (0.024, 0.046, 0.077)  # color de la parte de arriba de esa foto
SWIRL = (545, 445 + HOOK_DY)  # centro de los colores de esa foto
NEWTON_TOP = (0.051, 0.037, 0.025)
# el nervio amarillo de la foto del cerebro, medido sobre ella (coordenadas de pantalla)
NERVE_PTS = [(339, 1069), (387, 1069), (435, 1061), (484, 1035), (532, 991), (581, 973), (629, 974), (677, 989),
             (726, 1004), (774, 1006), (810, 975), (840, 930)]
BRAIN_SPOT = (845, 925)  # la zona de la vista, al fondo del cerebro
PHOS_C = (542, 960)  # centro del damero de la foto de los fosfenos


@functools.lru_cache(maxsize=None)
def photo(name):
    return Still(os.path.join(ASSETS, name))


def along(pts, u):
    """Punto a una fracción u (0-1) del recorrido de una polilínea."""
    segs = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    d = clamp(u) * sum(segs)
    for (a, b), L in zip(zip(pts, pts[1:]), segs):
        if d <= L:
            f = d / L
            return a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        d -= L
    return pts[-1]


def swirl(ctx, t, k):
    """Aviva los colores de la foto del gancho: los vuelve a pintar encima sumando luz y girando despacio."""
    if k <= 0:
        return
    cx, cy = SWIRL
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_ADD)
    ctx.translate(cx, cy)
    ctx.rotate(0.22 * math.sin(t * 1.3))
    ctx.scale(1 + 0.05 * math.sin(t * 2.1), 1 + 0.05 * math.sin(t * 2.1))
    ctx.translate(-cx, -cy)
    ctx.set_source_surface(photo("escena-01-ojo.jpg").frame(t), 0, HOOK_DY)
    ctx.mask(radial(cx, cy, 340, [(0, (0, 0, 0, k)), (0.7, (0, 0, 0, k)), (1, (0, 0, 0, 0))]))
    ctx.restore()


# ---------- escenas ----------

def s_hook(ctx, t):
    burst = ease_out_back(appear(t, w(s_hook, "colores"), 0.5))
    source(ctx, HOOK_TOP)
    ctx.paint()
    clip_bg(ctx, photo("escena-01-ojo.jpg"), t, dim=0.0, dy=HOOK_DY)
    fade_top(ctx, HOOK_TOP, HOOK_DY - 10, HOOK_DY + 200)
    swirl(ctx, t, 0.45 + 0.75 * burst)
    phosphenes(ctx, *SWIRL, 300, t, a=0.25 + 0.45 * burst, kind="dots", base=False)


def s_dark(ctx, t):
    tech_bg(ctx, t)
    x, y, s = 610, 1110, 1.05
    no = appear(t, w(s_dark, "luz") + 0.15, 0.45)
    off = appear(t, w(s_dark, "oscuras"), 0.4)
    focus = (x + s * 280, y + s * 70)
    if no < 1:  # la luz entra por la córnea y se enfoca en la retina
        a = 1 - no
        for dy in (-60, 0, 60):
            cx_, cy_ = x + s * (CORNEA_C - CORNEA_R + 6), y + s * dy
            stroke(ctx, [(200, 700), (cx_, cy_), focus], rgba(YELLOW, 0.75 * a), 6, close=False)
    eye_section(ctx, x, y, s, t, lit=0.6 * (1 - no))
    bulb(ctx, 200, 690, 1.0, 1 - off)
    if no > 0:  # «no es luz»
        k = ease_out_back(no)
        for d in (-1, 1):
            stroke(ctx, [(250 - 50 * k, 900 - 50 * k * d), (250 + 50 * k, 900 + 50 * k * d)], rgba(RED, clamp(no * 2)), 16, close=False)
    if off > 0:  # la habitación a oscuras… y la retina se enciende igual
        ctx.rectangle(0, 0, 1080, 1920)
        source(ctx, (0, 0, 0.02, 0.5 * off))
        ctx.fill()
        retina_glow(ctx, x, y, s, t, phos=appear(t, w(s_dark, "oscuras") + 0.25, 0.6))
    panel(ctx, 600, 470, "LUZ QUE ENTRA", "0", "%", off, col=WHITE)


def s_press(ctx, t):
    tech_bg(ctx, t)
    x, y, s = 610, 1130, 1.05
    t0 = w(s_press, "aprietas")
    p = ease_in_out(clamp((t - t0 + 0.2) / (w(s_press, "deforma") - t0 + 0.3)))
    press = p * (0.88 + 0.12 * math.sin(t * 10))
    lit = appear(t, w(s_press, "retina"), 0.4)
    eye_section(ctx, x, y, s, t, press=press, lit=lit, strain=appear(t, w(s_press, "estira"), 0.4))
    approach = 160 * (1 - ease_in_out(clamp((t + 0.1) / (t0 + 0.2))))
    fx, fy = eye_point(x, y, s, TH_PRESS, press, off=24 + approach)
    finger(ctx, fx, fy, TH_PRESS, length=480, s=0.95)
    mini_tag(ctx, "PRESIÓN", fx + 16, fy + 10, fx + 300, fy - 150, appear(t, t0, 0.4), col=YELLOW)
    rx, ry = eye_point(x, y, s, 0.4, press, off=-12)
    mini_tag(ctx, "RETINA", rx, ry, 760, 1500, lit, col=RETINA)


@functools.lru_cache(maxsize=None)
def spikes(cell, t0, horizon=9.0):
    """Instantes de disparo de una neurona: casi en reposo y, desde t0, mucho más seguidos."""
    rng = random.Random(100 + cell)
    out, tt = [], 0.0
    while tt < horizon:
        rate = 0.8 if tt < t0 else 0.8 + 9.0 * clamp((tt - t0) / 0.5)
        tt += rng.expovariate(1.0) / rate
        out.append(tt)
    return tuple(out)


GANG = [(150 + 156 * k, 900) for k in range(6)]


def s_neurons(ctx, t):
    tech_bg(ctx, t)
    t0 = w(s_neurons, "disparan")
    stretch = 0.5 + 0.5 * math.sin(t * 7)
    ctx.save()
    ctx.translate(540, 0)
    ctx.scale(1 + 0.05 * stretch, 1)
    ctx.translate(-540, 0)
    fill_rr(ctx, 50, 680, 980, 820, 40, linear(0, 680, 0, 1500, [(0, (0.17, 0.08, 0.14)), (1, (0.09, 0.04, 0.08))]))
    fill_rr(ctx, 50, 1440, 980, 60, 20, (0.22, 0.11, 0.07))  # capa de pigmento
    for k in range(22):  # fotorreceptores
        px = 84 + 43.5 * k
        fill_rr(ctx, px - 9, 1270, 18, 165, 9, linear(px - 9, 0, px + 9, 0, [(0, (0.80, 0.42, 0.22)), (1, (1.0, 0.62, 0.36))]))
    for k in range(10):  # bipolares
        bx = 120 + 93 * k
        stroke(ctx, [(bx, 1150), (bx, 1270)], (0.62, 0.45, 0.95, 0.7), 4, close=False)
        gx, gy = min(GANG, key=lambda g: abs(g[0] - bx))
        stroke(ctx, [(bx, 1090), (gx, gy + 30)], (0.62, 0.45, 0.95, 0.5), 4, close=False)
        soft_ellipse(ctx, bx, 1120, 22, 32, (0.62, 0.45, 0.95), 1.0)
    for k, (gx, gy) in enumerate(GANG):  # ganglionares y sus fibras hacia el nervio óptico
        ay = 740 + 9 * k
        axon = [(gx, gy - 30), (gx, ay), (1030, ay)]
        stroke(ctx, axon, (0.30, 0.85, 0.70, 0.55), 5, close=False)
        fire = 0.0
        for ts in spikes(k, round(t0, 3)):
            if ts > t:
                break
            age = t - ts
            fire = max(fire, math.exp(-age / 0.12))
            if age < 0.6:  # el impulso viaja por la fibra
                L1, L2 = gy - 30 - ay, 1030 - gx
                d = (L1 + L2) * age / 0.6
                px, py = (gx, gy - 30 - d) if d < L1 else (gx + d - L1, ay)
                glow(ctx, px, py, 34, YELLOW, 0.9, add=True)
        disc(ctx, gx, gy, 36, radial(gx - 10, gy - 10, 46, [(0, (0.55, 1.0, 0.85)), (1, (0.18, 0.62, 0.50))]))
        if fire > 0.02:
            glow(ctx, gx, gy, 110, YELLOW, 0.9 * fire, add=True)
    ctx.restore()
    for d in (-1, 1):  # el tejido se estira
        ax_ = 540 + d * (495 + 25 * stretch)
        stroke(ctx, [(ax_, 1100), (ax_ + d * 34, 1100)], rgba(YELLOW, 0.8), 6, close=False)
        stroke(ctx, [(ax_ + d * 20, 1084), (ax_ + d * 34, 1100), (ax_ + d * 20, 1116)], rgba(YELLOW, 0.8), 6, close=False)
    level = 0.06 + 0.86 * ease_in_out(clamp((t - t0) / 0.8)) + 0.04 * math.sin(t * 23)
    a = appear(t, 0.1, 0.4)
    fill_rr(ctx, 600, 470, 380, 132, 22, (0.02, 0.03, 0.08, 0.72 * a))
    spaced(ctx, "SEÑAL DE LA RETINA", 624, 500, 22, col=(0.65, 0.78, 1.0, a))
    fill_rr(ctx, 624, 540, 332, 34, 17, (1, 1, 1, 0.10 * a))
    fill_rr(ctx, 624, 540, 332 * clamp(level), 34, 17, linear(624, 0, 956, 0, [(0, rgba(GREEN, a)), (1, rgba(YELLOW, a))]))
    mini_tag(ctx, "NEURONAS", GANG[1][0], GANG[1][1] - 40, 380, 640, appear(t, w(s_neurons, "neuronas"), 0.4), col=GREEN)


def s_nerve(ctx, t):
    clip_bg(ctx, photo("escena-05-cerebro.jpg"), t, dim=0.0)
    arrive = appear(t, w(s_nerve, "cerebro"), 0.5)
    go = appear(t, w(s_nerve, "señal") - 0.2, 0.3)
    if go > 0:  # los impulsos recorren el nervio de la foto
        for k in range(4):
            px, py = along(NERVE_PTS, ((t - w(s_nerve, "señal")) * 0.9 + k / 4) % 1)
            glow(ctx, px, py, 46, YELLOW, 0.9 * go, add=True)
            disc(ctx, px, py, 10, (1, 1, 0.85, go))
    if arrive > 0:
        glow(ctx, *BRAIN_SPOT, 170, YELLOW, 0.7 * arrive * (0.75 + 0.25 * math.sin(t * 9)), add=True)
    nx, ny = along(NERVE_PTS, 0.4)
    mini_tag(ctx, "NERVIO ÓPTICO", nx, ny + 10, 560, 1300, appear(t, w(s_nerve, "nervio"), 0.4), col=NERVE)
    mini_tag(ctx, "CEREBRO", BRAIN_SPOT[0], BRAIN_SPOT[1] - 30, 760, 520, arrive, col=YELLOW)


def channel(ctx, t, y, label, col, src, out_p, t_on):
    """Una fila: de dónde viene la señal → ojo → impulsos → cerebro → «LUZ»."""
    spaced(ctx, label, 110, y - 150, 30, col=col)
    src(ctx)
    eye_icon(ctx, 360, y, 0.62)
    stroke(ctx, [(420, y), (760, y)], rgba(NERVE, 0.5), 10, close=False)
    if t >= t_on:
        for k in range(3):  # el mismo tren de impulsos en las dos filas
            u = ((t - t_on) * 0.8 + k / 3) % 1
            glow(ctx, 420 + 340 * u, y, 38, YELLOW, 0.9, add=True)
            disc(ctx, 420 + 340 * u, y, 9, (1, 1, 0.85))
    brain(ctx, 860, y, 0.85, t, lit=out_p)
    if out_p > 0:
        s = ease_out_back(out_p)
        fill_rr(ctx, 860 - 90 * s, y + 92, 180 * s, 64, 32, rgba(YELLOW, clamp(out_p * 2)))
        if out_p > 0.5:
            text(ctx, "LUZ", 860, y + 124, 38, col=(0.08, 0.06, 0.02))


def s_same(ctx, t):
    tech_bg(ctx, t)
    t_on = 0.0
    out = appear(t, w(s_same, "luz"), 0.4)

    def real(c):
        bulb(c, 170, 780, 0.8, 1.0)

    def pressed(c):
        finger(c, 395, 1212, -0.95, length=300, s=0.6)
    channel(ctx, t, 780, "LUZ DE VERDAD", YELLOW, real, out, t_on)
    channel(ctx, t, 1250, "PRESIÓN", PINK, pressed, out, t_on)
    eq = appear(t, w(s_same, "todo"), 0.4)
    if eq > 0:
        for dy in (-12, 12):
            stroke(ctx, [(830, 1015 + dy), (890, 1015 + dy)], rgba(WHITE, eq), 8, close=False)


def s_phos(ctx, t):
    name = appear(t, w(s_phos, "fosfenos"), 0.5)
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    pic = photo("escena-07-fosfenos.jpg").frame(t)
    cx, cy = PHOS_C
    k = 1 + 0.08 * ease_out_back(name)
    ctx.save()  # el damero gira despacio y, al decir «fosfenos», crece y se enciende
    ctx.translate(cx, cy)
    ctx.rotate(0.07 * t)
    ctx.scale(k, k)
    ctx.translate(-cx, -cy)
    ctx.set_source_surface(pic, 0, 0)
    ctx.paint()
    if name > 0:
        ctx.set_operator(cairo.OPERATOR_ADD)
        ctx.set_source_surface(pic, 0, 0)
        ctx.paint_with_alpha(0.6 * name)
    ctx.restore()
    phosphenes(ctx, cx, cy, 430, t, a=0.3 + 0.3 * name, kind="dots", base=False)
    mini_tag(ctx, "LUZ REAL: 0", 800, 690, 640, 590, appear(t, w(s_phos, "existe"), 0.4), col=WHITE)
    if name > 0:
        s = ease_out_back(name)
        ctx.save()
        ctx.translate(540, 1500)
        ctx.scale(s, s)
        glow(ctx, 0, 0, 260, YELLOW, 0.25 * name, add=True)
        spaced(ctx, "FOSFENOS", 0, 0, 84, col=YELLOW, anchor="center")
        ctx.restore()
        spaced(ctx, "DEL GRIEGO «LUZ» + «MOSTRAR»", 540, 1580, 24, col=(1, 1, 1, 0.7 * clamp(name * 2 - 1)), anchor="center")


def notebook(ctx, pz, rings, t):
    """Página del cuaderno: el ojo y el borde de la órbita a tinta, el punzón (pz: cuánto ha entrado) entre
    los dos y los anillos de colores que vio. Devuelve un punto del punzón para la etiqueta."""
    ctx.save()
    ctx.translate(540, 1060)
    ctx.rotate(-0.035)
    soft_ellipse(ctx, 10, 30, 470, 520, (0, 0, 0), 0.5)
    fill_rr(ctx, -400, -460, 800, 920, 16, linear(0, -460, 0, 460, [(0, (0.94, 0.88, 0.73)), (1, (0.83, 0.75, 0.57))]))
    for sx, sy, srx, sry in ((-250, -300, 120, 80), (220, 280, 150, 100), (300, -380, 80, 60)):
        soft_ellipse(ctx, sx, sy, srx, sry, (0.55, 0.40, 0.20), 0.18)
    rr(ctx, -400, -460, 800, 920, 16)
    source(ctx, (0.50, 0.38, 0.22, 0.5))
    ctx.set_line_width(4)
    ctx.stroke()
    rng = random.Random(7)
    for yy in [-400 + 42 * k for k in range(4)] + [330 + 42 * k for k in range(3)]:  # renglones manuscritos
        x1 = rng.uniform(150, 340)
        pts = [(xx, yy + 4 * math.sin(xx / 9 + rng.random() * 6)) for xx in range(-340, int(x1), 6)]
        stroke(ctx, pts, rgba(INK, 0.45), 3, close=False)
    ctx.new_sub_path()
    ctx.arc(-40, 0, 150, 0, 2 * math.pi)
    source(ctx, INK)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(-150, 0, 80, math.pi - 1.0, math.pi + 1.0)
    ctx.stroke()
    disc(ctx, -218, 0, 15, INK)
    bone = bezier((60, -280), (240, -220), (270, 80), (215, 230), 30)  # borde de la órbita
    stroke(ctx, bone, INK, 9, close=False)
    for k in range(2, 30, 4):  # rayado del hueso
        bx, by = bone[k]
        stroke(ctx, [(bx, by), (bx + 26, by + 14)], rgba(INK, 0.6), 3, close=False)
    bodkin = bezier((330, 430), (250, 330), (170, 200), (130, 40), 30)  # entra entre el ojo y el hueso
    if pz > 0:
        stroke(ctx, bodkin[: max(2, int(len(bodkin) * pz))], INK, 6, close=False)
        stroke(ctx, [(330, 430), (292, 380)], INK, 22, close=False)  # mango
    if rings > 0:  # los círculos de colores que vio, al otro lado del ojo
        for k, col in enumerate((PINK, CYAN, YELLOW)):
            r = (30 + 28 * k) * ease_out_back(rings)
            ctx.new_sub_path()
            ctx.arc(-255, 10, r, 0, 2 * math.pi)
            source(ctx, rgba(col, 0.9 * clamp(rings * 2) * (0.75 + 0.25 * math.sin(t * 6 + k))))
            ctx.set_line_width(10)
            ctx.stroke()
        glow(ctx, -255, 10, 140, WHITE, 0.25 * rings, add=True)
    ctx.restore()
    return 540 + bodkin[12][0], 1060 + bodkin[12][1]


def s_newton(ctx, t):
    """Primero su retrato (para que se le reconozca) y, al decir «punzón», su cuaderno."""
    t_pz = w(s_newton, "punzón")
    fade = ease_in_out(clamp((t - t_pz + 0.2) / 0.3))
    tech_bg(ctx, t)
    if fade > 0:
        spaced(ctx, "CUADERNO DE NEWTON", 540, 560, 30, col=(1, 1, 1, 0.8 * fade), anchor="center")
        bx, by = notebook(ctx, ease_in_out(appear(t, t_pz, 0.8)), appear(t, w(s_newton, "verlos"), 0.6), t)
        mini_tag(ctx, "PUNZÓN", bx, by, 650, 1580, appear(t, t_pz + 0.3, 0.4), col=YELLOW)
    if fade < 1:  # el retrato se acerca y se funde
        ctx.push_group()
        ctx.translate(540, 900)
        ctx.scale(1 + 0.15 * fade, 1 + 0.15 * fade)
        ctx.translate(-540, -900)
        source(ctx, NEWTON_TOP)
        ctx.paint()
        clip_bg(ctx, photo("escena-08-newton.jpg"), t, dim=0.0)
        fade_top(ctx, NEWTON_TOP, 430, 620)
        spaced(ctx, "ISAAC NEWTON", 540, 1560, 44, col=YELLOW, anchor="center")
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - fade)


def s_ask(ctx, t):
    tech_bg(ctx, t)
    for k, (word, kind) in enumerate((("puntos", "dots"), ("rayas", "stripes"), ("colores", "colors"))):
        cy = 720 + 330 * k
        on = appear(t, w(s_ask, word), 0.4)
        s = 1 + 0.08 * ease_out_back(on)
        phosphenes(ctx, 360, cy, 140 * s, t + k, a=0.45 + 0.55 * on, kind=kind)
        ctx.new_sub_path()
        ctx.arc(360, cy, 140 * s, 0, 2 * math.pi)
        source(ctx, rgba(YELLOW if on > 0.5 else WHITE, 0.25 + 0.6 * on))
        ctx.set_line_width(4)
        ctx.stroke()
        spaced(ctx, word.upper(), 560, cy, 50, col=rgba(YELLOW if on > 0.5 else WHITE, 0.45 + 0.55 * on))


SCENES = [
    Scene("¿Por qué ves colores al frotarte los ojos?", s_hook, key="colores", sfx=[("@colores", "whoosh")]),
    Scene("No es luz: pasa igual en una habitación a oscuras.", s_dark, key="luz", duration=3.9, sfx=[("@luz", "pop"), ("@oscuras", "thunk")]),
    Scene("Cuando aprietas, el ojo se deforma y estira la retina.", s_press, key="retina",
          sfx=[("@aprietas", "pop"), ("@retina", "pop")]),
    Scene("Sus neuronas se disparan como si les llegara luz.", s_neurons, key="disparan",
          sfx=[("@neuronas", "pop")] + [(f"@disparan+{d}", "tick") for d in
                                         (0.0, 0.16, 0.3, 0.42, 0.52, 0.61, 0.69, 0.76, 0.83, 0.9, 0.96, 1.02, 1.08, 1.14)]),
    Scene("Luego mandan la señal por el nervio óptico al cerebro.", s_nerve, key="nervio",
          sfx=[("@nervio", "pop"), ("@cerebro", "pop")]),
    Scene("Para tu cerebro, todo lo que llega por ese nervio es luz.", s_same, key="luz", sfx=[("@todo", "pop"), ("@luz", "pop")]),
    Scene("Ves luz que no existe: se llaman fosfenos.", s_phos, key="fosfenos", sfx=[("@fosfenos", "whoosh")]),
    Scene("Newton se metió un punzón entre el ojo y el hueso para verlos.", s_newton, key="punzón",
          sfx=[("@punzón", "thunk"), ("@verlos", "pop")]),
    Scene("Cuéntame: ¿qué ves tú, puntos, rayas o colores?", s_ask, key="colores", duration=4.2,
          sfx=[("@puntos", "pop"), ("@rayas", "pop"), ("@colores", "pop")]),
]

POST = """¿Por qué ves colores al frotarte los ojos? 👁️
Cuéntame: ¿qué ves tú, puntos, rayas o colores?
"""

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "out", "ojos-colores")
    os.makedirs(out, exist_ok=True)
    narrator = None
    if "--sin-voz" not in sys.argv:
        from voz import narrator_from_args
        narrator = narrator_from_args(sys.argv, speed=1.04)
        narrator.gap = 0.22
        narrator.min_scene = 1.6
    if "--preview" in sys.argv:
        i = sys.argv.index("--preview")
        dest = sys.argv[i + 1] if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith("--") else os.path.join(out, "preview.png")
        preview(SCENES, dest, narrator=narrator, style=TOP_SHORT)
        print("preview:", dest)
    else:
        total = render(SCENES, os.path.join(out, "ojos-colores.mp4"), cover_png=os.path.join(out, "fotograma.png"),
                       cover_at=(0, 1.5), narrator=narrator, style=TOP_SHORT)
        os.remove(os.path.join(out, "fotograma.png"))
        with open(os.path.join(out, "texto-del-post.txt"), "w") as f:
            f.write(POST)
        print(f"OK: {total:.1f} s")
