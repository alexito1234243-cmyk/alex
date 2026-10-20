"""Vídeo de prueba: ¿Por qué la tapa del boli BIC tiene un agujero?

Uso: python3 video/boli_bic.py  ->  salida en video/out/boli-bic/
"""
import math
import os

from engine import (BLUE, GREEN, INK, PAPER, PINK, RED, WHITE, Canvas, Scene,
                    ease_out_back, ellipse, prog, render, rrect)

DARK_BLUE = (0.13, 0.33, 0.70)
LIGHT_BLUE = (0.45, 0.62, 0.95)
GLASS = (0.78, 0.86, 0.95)
FACET = (0.62, 0.72, 0.86)
BRASS = (0.80, 0.68, 0.38)
CAP_HOLE = (0, -226)   # agujero de la tapa (coordenadas de la tapa)
PEN_HOLE = (10, -150)  # agujerito del cuerpo (coordenadas del boli)


# ---------- piezas reutilizables (proporciones del BIC Cristal) ----------

def cap(c: Canvas, t, start=0.0, key=10):
    """Tapa vertical: estrecha, punta redondeada con agujero arriba y clip a la izquierda."""
    body = [(-32, 230), (-32, -140), (-26, -200), (-14, -226), (0, -232), (14, -226),
            (26, -200), (32, -140), (32, 230), (-32, 230)]
    clip = [(-18, -208), (-50, -182), (-50, 95), (-56, 112), (-44, 124), (-36, 108),
            (-36, -160), (-22, -185), (-18, -208)]
    c.shape(body, prog(t, start, 0.7), fill=BLUE, width=7, key=key)
    c.line([(14, -170), (14, 180)], prog(t, start + 0.4, 0.4), color=LIGHT_BLUE, width=8, key=key + 1)
    c.line([(-29, 196), (29, 196)], prog(t, start + 0.5, 0.3), width=5, key=key + 2)
    c.shape(clip, prog(t, start + 0.35, 0.5), fill=DARK_BLUE, width=7, key=key + 3)
    hp = ease_out_back(prog(t, start + 0.8, 0.3))
    if hp > 0:
        c.dot(*CAP_HOLE, 12 * hp, PAPER)
        c.dot(*CAP_HOLE, 8 * hp, INK)


def pen(c: Canvas, t, start=0.0, ink_end=370, key=40, capped=False):
    """Boli vertical con la punta arriba: cuerpo hexagonal transparente, tinta, punta y tapón."""
    p = prog(t, start, 0.8)
    c.line([(0, -372), (0, ink_end)], prog(t, start + 0.3, 0.5), color=BLUE, width=12, key=key)
    barrel = [(-26, -300), (-10, -372), (10, -372), (26, -300), (26, 370), (-26, 370), (-26, -300)]
    c.shape(barrel, p, fill=GLASS, fill_alpha=0.5, width=7, key=key + 1)
    c.line([(-9, -300), (-9, 368)], prog(t, start + 0.4, 0.5), color=FACET, width=3, key=key + 2)
    c.line([(9, -300), (9, 368)], prog(t, start + 0.4, 0.5), color=FACET, width=3, key=key + 3)
    c.shape([(-8, -372), (-3, -396), (3, -396), (8, -372), (-8, -372)], prog(t, start + 0.5, 0.3),
            fill=BRASS, width=5, key=key + 4)
    c.shape(rrect(-22, 364, 44, 48, 8), prog(t, start + 0.5, 0.4), fill=BLUE, width=7, key=key + 5)
    hp = ease_out_back(prog(t, start + 0.8, 0.3))
    if hp > 0:
        c.dot(-0.5, -399, 4 * hp, INK)
        c.dot(*PEN_HOLE, 7 * hp, INK)
    # logo impreso a lo largo del cuerpo
    lp = prog(t, start + 0.9, 0.3)
    if lp > 0:
        c.push(0, 170, rot=-math.pi / 2)
        c.text("BIC", 0, 0, 42, color=INK, alpha=lp)
        c.pop()
    if capped:
        c.push(0, -330)
        cap(c, t, start + 0.5, key=key + 10)
        c.pop()


def throat(c: Canvas, t, start=0.0, key=70):
    def side(x0, phase):
        return [(x0 + 18 * math.sin(y / 90 + phase), y) for y in range(-420, 421, 20)]
    left, right = side(-120, 0), side(120, 1.3)
    p = prog(t, start, 0.7)
    c.shape(left + right[::-1], p, fill=PINK, stroke=None, key=key)
    c.line(left, p, key=key + 1)
    c.line(right, p, key=key + 2)


def check(c: Canvas, x, y, p, r=56):
    s = ease_out_back(p)
    if s <= 0:
        return
    c.push(x, y, scale=s)
    c.shape(ellipse(0, 0, r, r), 1, fill=GREEN, key=900 + int(x))
    c.line([(-r * 0.45, 0), (-r * 0.1, r * 0.35), (r * 0.5, -r * 0.35)], 1, color=WHITE, width=14, key=901)
    c.pop()


# ---------- escenas ----------

def s_hook(c, t):
    c.push(0, 70, scale=0.78, rot=0.18)
    pen(c, t, 0.05, capped=True)
    p = prog(t, 1.6, 0.4)
    pulse = 1 + 0.1 * math.sin(t * 8) * (p >= 1)
    c.push(CAP_HOLE[0], CAP_HOLE[1] - 330, scale=pulse)
    c.shape(ellipse(0, 0, 56, 56), p, fill=None, stroke=RED, width=11, key=2)
    c.pop()
    c.pop()
    for i, (x, y, rot, at) in enumerate([(-260, -300, -0.25, 1.9), (250, -120, 0.2, 2.2)]):
        s = ease_out_back(prog(t, at, 0.3))
        if s > 0:
            c.push(x, y, scale=s, rot=rot)
            c.text("?", 0, 0, 190, color=RED)
            c.pop()



def s_not_plastic(c, t):
    c.push(scale=1.25)
    cap(c, t, -2)
    c.pop()
    c.line([(-230, -300), (230, 280)], prog(t, 0.4, 0.3), color=RED, width=22, key=5)
    c.line([(230, -300), (-230, 280)], prog(t, 0.7, 0.3), color=RED, width=22, key=6)



def s_bite(c, t):
    gulp = prog(t, 3.0, 0.5)
    iry = 150 - 70 * gulp
    c.shape(ellipse(0, 0, 310, iry + 55), prog(t, 0, 0.6), fill=RED, key=7)
    c.shape(ellipse(0, 0, 255, iry), prog(t, 0.2, 0.5), fill=INK, key=8)
    for i in range(5):
        x = -140 + i * 58
        tp = prog(t, 0.5 + i * 0.06, 0.25)
        c.shape(rrect(x, -iry + 4, 48, 52, 10), tp, fill=WHITE, width=5, key=20 + i)
        c.shape(rrect(x, iry - 56, 48, 52, 10), tp, fill=WHITE, width=5, key=30 + i)
    # la tapa entra en la boca
    move = prog(t, 0.9, 1.6)
    x = 620 - 560 * (1 - (1 - move) ** 3)
    s = 0.75 * (1 - 0.6 * gulp)
    c.push(x, 0, scale=s, rot=-math.pi / 2)
    cap(c, t, -2, key=12)
    c.pop()


def s_stuck(c, t):
    throat(c, t, 0)
    wob = 0.08 * math.sin(t * 14) * (t > 1.2)
    c.push(0, 0, scale=0.75, rot=wob)
    cap(c, t, 0.4)
    c.pop()
    s = ease_out_back(prog(t, 1.6, 0.3))
    if s > 0:
        c.push(290, -250, scale=s)
        c.shape([(0, -95), (95, 70), (-95, 70), (0, -95)], 1, fill=RED, key=90)
        c.text("!", 0, 15, 120, color=WHITE)
        c.pop()


def s_air(c, t):
    throat(c, t, -2)
    c.push(0, 0, scale=0.75)
    cap(c, t, -2)
    c.pop()
    # corrientes de aire que suben atravesando el agujero
    for i in range(6):
        y = 380 - ((t * 320 + i * 140) % 840)
        x = (-14, 0, 14)[i % 3]
        c.line([(x, y + 50), (x, y)], 1, color=WHITE, width=12, key=100 + i)
    p = prog(t, 0.6, 0.4)
    c.line([(330, -120), (170, -120)], p, color=BLUE, width=9, key=110)
    c.line([(205, -150), (170, -120), (205, -90)], prog(t, 0.9, 0.2), color=BLUE, width=9, key=111)
    if p > 0:
        c.text("AIRE", 260, -190, 64, color=BLUE, alpha=p)


def s_iso(c, t):
    side = [(200, -230)] + [(200 - 200 * (k / 10) ** 1.6, -10 + 280 * k / 10) for k in range(11)]
    shield = [(-200, -230), (0, -300)] + side + [(-x, y) for x, y in side[::-1]]
    c.shape(shield, prog(t, 0, 0.8), fill=GREEN, key=120)
    c.line([(-80, -10), (-15, 60), (100, -80)], prog(t, 0.8, 0.35), color=WHITE, width=26, key=121)
    s = ease_out_back(prog(t, 1.6, 0.35))
    if s > 0:
        c.push(0, 340, scale=s)
        c.text("ISO 11540", 0, 0, 92, color=INK)
        c.pop()


def s_barrel(c, t):
    c.push(-40, 40, scale=0.9)
    pen(c, t, 0.1)
    hx, hy = PEN_HOLE
    p = prog(t, 1.4, 0.4)
    c.shape(ellipse(hx, hy, 32, 32), p, fill=None, stroke=RED, width=8, key=130)
    lp = prog(t, 1.9, 0.5)
    c.line([(hx + 34, hy), (hx + 150, hy)], lp, color=RED, width=7, key=131)
    c.shape(ellipse(hx + 280, hy, 130, 130), lp, fill=WHITE, fill_alpha=0.85, key=132)
    c.line([(hx + 372, hy + 92), (hx + 440, hy + 180)], lp, width=24, key=133)
    if lp >= 1:
        c.dot(hx + 280, hy, 44, INK)
    c.pop()



def s_ink(c, t):
    # boli con la punta hacia abajo, escribiendo
    ox, oy, s = 0, -70, 0.85
    c.push(ox, oy, scale=s, rot=math.pi)
    pen(c, t, -2, ink_end=370 - 260 * prog(t, 0.6, 2.8))
    c.pop()
    hx, hy = ox - PEN_HOLE[0] * s, oy - PEN_HOLE[1] * s
    c.line([(hx - 260, hy), (hx - 40, hy)], prog(t, 0.3, 0.4), color=BLUE, width=10, key=140)
    c.line([(hx - 80, hy - 35), (hx - 40, hy), (hx - 80, hy + 35)], prog(t, 0.65, 0.2), color=BLUE, width=10, key=141)
    c.text("AIRE", hx - 170, hy - 70, 60, color=BLUE, alpha=prog(t, 0.3, 0.4))
    # la tinta sale por la punta y escribe
    tip_y = oy + 396 * s
    scrib = [(-420 + k * 14, tip_y + 40 - 26 * abs(math.sin(k * 0.45))) for k in range(31)]
    c.line(scrib, prog(t, 0.9, 2.6), color=BLUE, width=9, key=142)



def s_two(c, t):
    for i, x in enumerate((-210, 210)):
        p = prog(t, 0.1 + i * 0.25, 0.5)
        c.shape(ellipse(x, 0, 170, 170), p, fill=WHITE, key=150 + i)
    c.push(-210, 10, scale=0.55 * ease_out_back(prog(t, 0.3, 0.4)))
    cap(c, t, -2, key=160)
    c.pop()
    c.push(210, 0, scale=0.34 * ease_out_back(prog(t, 0.55, 0.4)), rot=0.6)
    pen(c, t, -2, key=170)
    c.pop()
    check(c, -90, -130, prog(t, 1.1, 0.35))
    check(c, 330, -130, prog(t, 1.5, 0.35))


def s_cta(c, t):
    press = 1 - 0.07 * math.sin(math.pi * prog(t, 1.3, 0.25))
    c.push(0, 0, scale=ease_out_back(prog(t, 0, 0.45)) * press)
    c.shape(rrect(-270, -80, 540, 160, 80), 1, fill=RED, key=180)
    c.text("SEGUIR", 0, 0, 78, color=WHITE)
    c.pop()
    rp = prog(t, 1.3, 0.8)
    if 0 < rp < 1:
        c.shape(ellipse(170, 50, 40 + 120 * rp, 40 + 120 * rp), 1, fill=None, stroke=RED, width=8 * (1 - rp) + 1, key=181)
    c.shape([(170, 50), (170, 210), (210, 170), (245, 240), (270, 228), (236, 160), (290, 160), (170, 50)],
            prog(t, 0.6, 0.6), fill=WHITE, width=8, key=182)


SCENES = [
    Scene("¿Por qué la tapa de tu boli BIC tiene un agujero?", s_hook, pops=[1.4, 1.6, 1.9, 2.2]),
    Scene("No es para ahorrar plástico.", s_not_plastic, pops=[0.45, 0.75]),
    Scene("Mucha gente las muerde… y a veces se las traga.", s_bite, pops=[0.5, 3.0]),
    Scene("Si una tapa se queda atascada en la garganta…", s_stuck, pops=[1.6]),
    Scene("…el agujero deja pasar el aire.", s_air, pops=[0.6]),
    Scene("Por eso cumple una norma de seguridad: la ISO 11540.", s_iso, pops=[0.85, 1.6]),
    Scene("Y el cuerpo del boli también tiene un agujerito.", s_barrel, pops=[1.4, 1.9]),
    Scene("Así entra aire y la tinta baja sin atascarse.", s_ink, pops=[0.3]),
    Scene("Dos agujeros diminutos. Dos problemas resueltos.", s_two, pops=[1.1, 1.5]),
    Scene("Síguenos para más curiosidades como esta.", s_cta, pops=[0.1, 1.3]),
]

POST = """¿Sabías por qué la tapa del boli BIC tiene un agujero? 🖊️

No es para ahorrar plástico: si alguien se traga la tapa y se le queda atascada, el agujero deja pasar el aire. Por eso las tapas de bolígrafo siguen la norma de seguridad ISO 11540.

Y el agujerito del cuerpo iguala la presión para que la tinta baje sin atascarse.

Síguenos para más curiosidades 👀

#curiosidades #sabiasque #ciencia #datoscuriosos #bic
"""

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "out", "boli-bic")
    os.makedirs(out, exist_ok=True)
    total = render(SCENES, os.path.join(out, "boli-bic.mp4"),
                   cover_png=os.path.join(out, "portada.png"), cover_frame_at=3.2)
    with open(os.path.join(out, "texto-del-post.txt"), "w") as f:
        f.write(POST)
    print(f"OK: {total:.1f} s")
