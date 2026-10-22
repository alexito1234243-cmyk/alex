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
- Imágenes de Flow (Nano Banana) en video/assets/lamborghini-ferrari/, una por escena, pedidas sin logos: la IA
  deforma los escudos y los coches se reconocen por la forma y el color. La escena 6 (Enzo y Ferruccio) es un
  cuadro pintado y va marcada «RECREACIÓN»: una foto realista de dos personas reales sería falsa. El coche
  amarillo de la escena 7 se parece a un Ferrari 275 GTB, así que no se etiqueta como «el primer Lamborghini».

Uso: python3 video/lamborghini_ferrari.py [--voz santa|dora|alex|eleven] [--sin-voz]  ->  video/out/lamborghini-ferrari/
     python3 video/lamborghini_ferrari.py --preview [png]
"""
import functools
import math
import os
import sys

import cairo

from engine import clamp, ease_in_out, ease_out_back
from piezas import RED, WHITE, appear, mini_tag, panel, spaced
from rich import (TOP_SHORT, YELLOW, Scene, Still, badge, bezier, clip_bg, disc, fade_top, fill_rr, glow,
                  light_up, linear, mix, mul, poly, preview, radial, render, rgba, soft_ellipse, source, stroke, text,
                  word_time)

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


# ---------- fotos (Flow) y lo que se mide sobre ellas, en coordenadas de pantalla ----------

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "lamborghini-ferrari")
SPARK = (550, 1190)  # chispa entre los morros (foto 1)
CARS3 = [(190, 1030), (470, 1035), (800, 1050)]  # los tres Ferrari del garaje (foto 3)
BULL_DY = 200  # la foto del toro baja para que la constelación no quede bajo los subtítulos
BULL_TOP = (0.034, 0.112, 0.19)
ALDEBARAN = (568, 370 + BULL_DY)


@functools.lru_cache(maxsize=None)
def photo(name):
    return Still(os.path.join(ASSETS, name))


def pill(ctx, s, x, y, size=26, col=WHITE, a=1.0, anchor="center"):
    """Texto espaciado sobre una píldora oscura, para que se lea encima de una foto clara."""
    if a <= 0:
        return
    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    width = sum(ctx.text_extents(ch).x_advance + size * 0.18 for ch in s) - size * 0.18
    x0 = {"center": x - width / 2, "left": x, "right": x - width}[anchor]
    fill_rr(ctx, x0 - 18, y - size * 0.85, width + 36, size * 1.7, size * 0.85, (0.02, 0.02, 0.04, 0.72 * a))
    spaced(ctx, s, x0, y, size, col=rgba(col, a))


def ptag(ctx, s, ax, ay, lx, ly, p, col=WHITE, size=28):
    """mini_tag para fotos: la misma línea, con el texto sobre una píldora oscura."""
    if p <= 0:
        return
    mini_tag(ctx, "", ax, ay, lx, ly, p, col=col)
    if p > 0.5:
        right = lx >= ax
        pill(ctx, s, lx + (14 if right else -14), ly, size, col, clamp((p - 0.5) / 0.5), "left" if right else "right")


# ---------- escenas ----------

def s_hook(ctx, t):
    hit = appear(t, w(s_hook, "insulto"), 0.35)
    jolt = hit * (1 - clamp((t - w(s_hook, "insulto")) / 0.6))
    ctx.save()  # sacudida de cámara con el insulto
    ctx.translate(12 * jolt * math.sin(t * 70), 7 * jolt * math.cos(t * 55))
    clip_bg(ctx, photo("escena-01.jpg"), t, dim=0.0)
    ctx.restore()
    flick = 0.5 + 0.5 * math.sin(t * 31) * math.sin(t * 17)
    light_up(ctx, photo("escena-01.jpg"), t, *SPARK, 170, 0.3 + 0.3 * flick + 0.6 * hit)  # la chispa está viva
    if hit > 0:
        glow(ctx, *SPARK, 320, (0.6, 0.85, 1.0), 0.6 * hit, add=True)

    def grawlix(c):
        text(c, "#@%!", 0, 0, 74, col=RED)
    bubble(ctx, 270, 760, 330, 170, (250, 950), hit, grawlix)
    spaced(ctx, "FERRARI", 230, 1440, 34, col=rgba(FER, appear(t, w(s_hook, "Ferrari"), 0.4)), anchor="center")
    spaced(ctx, "LAMBORGHINI", 800, 1500, 34, col=rgba(LAMBO, appear(t, w(s_hook, "Lamborghini"), 0.4)), anchor="center")


def s_tractors(ctx, t):
    clip_bg(ctx, photo("escena-02.jpg"), t, dim=0.0)
    rich_ = ease_in_out(clamp((t - w(s_tractors, "rico") + 0.1) / 0.8))
    light_up(ctx, photo("escena-02.jpg"), t, 640, 1250, 560, 0.35 * rich_)  # la luz dorada sube con «rico»
    ptag(ctx, "1948 · TRACTORES", 360, 1330, 390, 900, appear(t, w(s_tractors, "tractores"), 0.4), col=SKY)
    ptag(ctx, "FERRUCCIO LAMBORGHINI", 868, 1265, 780, 1080, appear(t, w(s_tractors, "creador"), 0.4), col=WHITE)


def s_cars(ctx, t):
    clip_bg(ctx, photo("escena-03.jpg"), t, dim=0.45)  # garaje en penumbra: cada coche se enciende al nombrarlo
    for (x, y), word in zip(CARS3, ("dinero", "cuantos", "Ferrari")):
        p = appear(t, w(s_cars, word), 0.4)
        light_up(ctx, photo("escena-03.jpg"), t, x, y, 240, 0.9 * p)
        if p > 0:
            glow(ctx, x, y + 30, 200, FER, 0.25 * p, add=True)
    ptag(ctx, "FERRARI 250 GT", 800, 990, 640, 1300, appear(t, w(s_cars, "Ferrari") + 0.2, 0.4), col=WHITE)


def s_clutch(ctx, t):
    clip_bg(ctx, photo("escena-04.jpg"), t, dim=0.0)
    fail = appear(t, w(s_clutch, "fallaba"), 0.4)
    light_up(ctx, photo("escena-04.jpg"), t, 760, 1400, 400, 0.5 * fail * (0.8 + 0.2 * math.sin(t * 9)))  # más humo
    zoom = appear(t, w(s_clutch, "embrague"), 0.45)
    if zoom > 0:  # lupa sobre el embrague
        k = ease_out_back(zoom)
        stroke(ctx, [(330, 930), (420, 1340)], rgba(WHITE, 0.5 * zoom), 3)
        disc(ctx, 300, 760, 175 * k, (0.05, 0.05, 0.07, 0.92))
        ctx.save()
        ctx.new_sub_path()
        ctx.arc(300, 760, 170 * k, 0, 2 * math.pi)
        ctx.clip()
        clutch(ctx, 300, 760, 135 * k, t, broken=fail)
        ctx.restore()
        ctx.new_sub_path()
        ctx.arc(300, 760, 175 * k, 0, 2 * math.pi)
        source(ctx, rgba(WHITE, 0.6 * zoom))
        ctx.set_line_width(5)
        ctx.stroke()
        ptag(ctx, "EMBRAGUE", 420, 640, 600, 540, zoom, col=WHITE)
    for word, (x, y) in (("una", (640, 640)), ("otra", (920, 1000)), ("vez", (150, 1150))):
        warning(ctx, x, y, 0.9, appear(t, w(s_clutch, word), 0.3))


def s_complain(ctx, t):
    clip_bg(ctx, photo("escena-05.jpg"), t, dim=0.0)
    ptag(ctx, "MARANELLO", 700, 760, 560, 560, appear(t, w(s_complain, "fábrica"), 0.4), col=FER)

    def angry(c):
        clutch(c, -60, 0, 52, t, broken=1.0)
        text(c, "!!", 60, 0, 90, col=RED)
    bubble(ctx, 600, 1080, 300, 180, (838, 1310), appear(t, w(s_complain, "quejarse"), 0.4), angry)
    pill(ctx, "SEGÚN CONTABA ÉL EN 1991", 540, 1585, a=appear(t, w(s_complain, "contaba"), 0.4))


def s_reply(ctx, t):
    clip_bg(ctx, photo("escena-06.jpg"), t, dim=0.0)
    pill(ctx, "RECREACIÓN", 230, 520, size=24, col=(1, 1, 1, 0.9), a=appear(t, 0.05, 0.3))
    mad = appear(t, w(s_reply, "enfadado"), 0.4)
    if mad > 0:
        glow(ctx, 320, 1010, 230, RED, 0.35 * mad * (0.8 + 0.2 * math.sin(t * 12)), add=True)
    ptag(ctx, "FERRUCCIO", 800, 830, 760, 560, appear(t, 0.1, 0.4), col=LAMBO)
    ptag(ctx, "ENZO FERRARI", 300, 1080, 330, 1520, appear(t, w(s_reply, "dueño"), 0.4), col=FER)
    yes = appear(t, w(s_reply, "tractor"), 0.4)
    no = appear(t, w(s_reply, "nunca"), 0.4)

    def answer(c):
        tractor(c, -105, 45, 0.28, t)
        badge(c, -105, -62, yes, ok=True, r=30)
        car(c, 115, 35, 0.3, FER, t)
        badge(c, 115, -62, no, ok=False, r=30)
    bubble(ctx, 330, 720, 420, 220, (330, 950), appear(t, w(s_reply, "contestó"), 0.4), answer)


def s_perfect(ctx, t):
    rev = appear(t, w(s_perfect, "perfecto") - 0.3, 0.6)
    clip_bg(ctx, photo("escena-07.jpg"), t, dim=0.55 * (1 - rev))  # en penumbra hasta «perfecto»
    light_up(ctx, photo("escena-07.jpg"), t, 545, 1370, 470, 0.45 * (1 - rev))  # primero, los planos
    light_up(ctx, photo("escena-07.jpg"), t, 545, 980, 520, 0.4 * rev)  # luego, el coche bajo el foco
    for j in range(8):
        u = (t * 0.7 + j / 8) % 1
        if rev > 0:
            disc(ctx, 200 + 680 * ((j * 0.37) % 1), 1150 - 420 * u, 5, (1, 1, 0.85, rev * (1 - u)))
    panel(ctx, 580, 470, "NACE LAMBORGHINI", "1963", "", appear(t, w(s_perfect, "decidió"), 0.4), col=LAMBO, wdt=400)


def s_bull(ctx, t):
    bull = appear(t, w(s_bull, "toro"), 0.5)
    sign = appear(t, w(s_bull, "Tauro"), 0.5)
    source(ctx, BULL_TOP)
    ctx.paint()
    clip_bg(ctx, photo("escena-08.jpg"), t, dim=0.3 * (1 - bull), dy=BULL_DY)
    fade_top(ctx, BULL_TOP, BULL_DY - 10, BULL_DY + 160)
    light_up(ctx, photo("escena-08.jpg"), t, 548, 1350, 560, 0.4 * bull, dy=BULL_DY)  # el toro se ilumina
    if sign > 0:  # y luego su constelación
        light_up(ctx, photo("escena-08.jpg"), t, 540, 340 + BULL_DY, 440, 1.1 * sign * (0.85 + 0.15 * math.sin(t * 7)), dy=BULL_DY)
        glow(ctx, *ALDEBARAN, 120, GOLD, 0.6 * sign, add=True)
    ptag(ctx, "TAURO", *ALDEBARAN, 760, 780, sign, col=YELLOW)
    pill(ctx, "NACIÓ UN 28 DE ABRIL DE 1916", 540, 1585, col=GOLD, a=sign)


def s_ask(ctx, t):
    f = appear(t, w(s_ask, "Ferrari"), 0.4)
    lb = appear(t, w(s_ask, "Lamborghini"), 0.4)
    clip_bg(ctx, photo("escena-09.jpg"), t, dim=0.3)
    for (x, y), col, name, on, ny in (((330, 1100), FER, "FERRARI", f, 880), ((760, 1100), LAMBO, "LAMBORGHINI", lb, 900)):
        light_up(ctx, photo("escena-09.jpg"), t, x, y, 330, 0.6 * on)
        if on > 0:
            glow(ctx, x, y, 300, col, 0.3 * on, add=True)
        spaced(ctx, name, x, ny, 40, col=rgba(col if on > 0.5 else WHITE, 0.55 + 0.45 * on), anchor="center")
    text(ctx, "VS", 548, 760, 64, col=(1, 1, 1, 0.9), outline=(0, 0, 0, 0.6), ow=10)


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
