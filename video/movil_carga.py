"""Vídeo: ¿Por qué el móvil carga volando hasta el 80% y luego va a paso de tortuga?

Formato de los vídeos virales de la cuenta de referencia: objeto que tienes en la mano, mito
desmentido al principio, frases cortas en segunda persona, dibujo técnico en corte con etiquetas
y cada elemento aparece cuando la voz lo nombra.

Datos: la carga rápida empuja corriente alta (fase de corriente constante) hasta ~70-80 % y luego
pasa a voltaje constante y baja la corriente para evitar que el litio se deposite como metal en el
ánodo (lithium plating) y que la batería se caliente. Por eso el último tramo es mucho más lento
y por eso los móviles ofrecen limitar la carga al 80 %.

Uso: python3 video/movil_carga.py [--voz santa|dora|alex] [--sin-voz]  ->  video/out/movil-carga/
     python3 video/movil_carga.py --preview [png]
"""
import math
import os
import random
import sys

import cairo

from engine import H, W, clamp, ease_in_out, ease_out_back, prog
from rich import (YELLOW, Scene, badge, cta_button, disc, fill_rr, glow, label, linear, mix, mul, path, poly,
                  preview, radial, render, rgba, rr, soft_ellipse, source, stroke, text, word_time)

BG = (0.031, 0.035, 0.045)
CYAN = (0.25, 0.85, 1.0)
GREEN = (0.30, 0.95, 0.55)
RED = (1.0, 0.32, 0.26)
ORANGE = (1.0, 0.55, 0.15)
WHITE = (1, 1, 1)


def scene_of(fn):
    return next(s for s in SCENES if s.draw is fn)


def dur(fn):
    return scene_of(fn).duration


def w(fn, needle):
    """Segundo en que la voz dice esa palabra en la escena de fn."""
    return word_time(scene_of(fn), needle)


# ---------- fondo y etiquetas ----------

def tech_bg(ctx, t):
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(radial(W / 2, 760, 1150, [(0, (0.08, 0.09, 0.13)), (1, BG)]))
    ctx.fill()
    ctx.set_line_width(1.5)
    source(ctx, (1, 1, 1, 0.035))
    for x in range(0, W + 1, 60):
        ctx.move_to(x, 0)
        ctx.line_to(x, H)
    for y in range(0, H + 1, 60):
        ctx.move_to(0, y)
        ctx.line_to(W, y)
    ctx.stroke()
    for i in range(7):
        off = ((i * 380 + t * 50) % 2700) - 900
        stroke(ctx, [(off, 0), (off + 900, H)], (0.4, 0.8, 1.0, 0.035), 3)


def tag(ctx, s, ax, ay, lx, ly, p, col=WHITE, size=34):
    """Etiqueta técnica: punto en el objeto, línea y texto en mayúsculas."""
    if p <= 0:
        return
    a, e = clamp(p * 1.5), ease_in_out(p)
    glow(ctx, ax, ay, 30, col, 0.5 * a, add=True)
    disc(ctx, ax, ay, 8, rgba(col, a))
    stroke(ctx, [(ax, ay), (ax + (lx - ax) * e, ay + (ly - ay) * e)], rgba(col, 0.75 * a), 3)
    if p > 0.6:
        b = clamp((p - 0.6) / 0.4)
        right = lx >= ax
        text(ctx, s, lx + (14 if right else -14), ly, size, col=rgba(col, b), anchor="left" if right else "right",
             outline=(0, 0, 0, 0.7 * b), ow=7)


def appear(t, at, d=0.35):
    return prog(t, at - 0.05, d)


# ---------- el móvil ----------

def bolt(ctx, x, y, s, col):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    poly(ctx, [(12, -60), (-34, 8), (-6, 8), (-14, 60), (34, -10), (6, -10)], col)
    ctx.restore()


def phone(ctx, x, y, s=1.0, screen=None, t=0.0, cable=True):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    w_, h_ = 420, 860
    if cable:
        stroke(ctx, [(0, h_ / 2 + 40), (0, h_ / 2 + 700)], (0.82, 0.83, 0.88), 26)
        fill_rr(ctx, -34, h_ / 2 - 6, 68, 74, 14, linear(-34, 0, 34, 0, [(0, (0.70, 0.71, 0.76)), (0.5, (0.96, 0.96, 0.98)), (1, (0.66, 0.67, 0.72))]))
    soft_ellipse(ctx, 0, 40, w_ * 0.8, h_ * 0.62, (0, 0, 0), 0.55)
    fill_rr(ctx, -w_ / 2, -h_ / 2, w_, h_, 70, linear(-w_ / 2, 0, w_ / 2, 0, [(0, (0.28, 0.29, 0.33)), (0.5, (0.64, 0.65, 0.70)), (1, (0.26, 0.27, 0.31))]))
    fill_rr(ctx, -w_ / 2 + 10, -h_ / 2 + 10, w_ - 20, h_ - 20, 62, (0.02, 0.02, 0.03))
    for bx, by, bh in [(w_ / 2 - 2, -h_ / 2 + 210, 120), (-w_ / 2 - 6, -h_ / 2 + 170, 70), (-w_ / 2 - 6, -h_ / 2 + 260, 70)]:
        fill_rr(ctx, bx, by, 8, bh, 4, (0.45, 0.46, 0.50))
    rr(ctx, -w_ / 2 + 22, -h_ / 2 + 22, w_ - 44, h_ - 44, 52)
    ctx.save()
    ctx.clip()
    ctx.rectangle(-w_ / 2, -h_ / 2, w_, h_)
    ctx.set_source(linear(0, -h_ / 2, 0, h_ / 2, [(0, (0.04, 0.06, 0.10)), (1, (0.01, 0.02, 0.04))]))
    ctx.fill()
    if screen:
        screen(ctx, t)
    poly(ctx, [(-w_ / 2, -h_ / 2), (-w_ / 2 + 190, -h_ / 2), (-w_ / 2, -h_ / 2 + 420)], (1, 1, 1, 0.05))
    ctx.restore()
    fill_rr(ctx, -62, -h_ / 2 + 40, 124, 34, 17, (0, 0, 0))
    ctx.restore()


def charge_screen(pct, slow=0.0):
    def draw(ctx, t):
        bw, bh, by = 170, 330, -70
        col = mix(GREEN, ORANGE, slow)
        glow(ctx, 0, by, 260, col, 0.25, add=True)
        rr(ctx, -bw / 2, by - bh / 2, bw, bh, 34)
        source(ctx, (1, 1, 1, 0.55))
        ctx.set_line_width(6)
        ctx.stroke()
        fill_rr(ctx, -32, by - bh / 2 - 24, 64, 20, 8, (1, 1, 1, 0.55))
        fh = (bh - 28) * pct / 100
        if fh > 1:
            fill_rr(ctx, -bw / 2 + 14, by + bh / 2 - 14 - fh, bw - 28, fh, 22, linear(0, by + bh / 2, 0, by - bh / 2, [(0, mul(col, 0.7)), (1, col)]))
        pulse = 0.75 + 0.25 * math.sin(t * (4 if slow < 0.5 else 1.5))
        bolt(ctx, 0, by, 1.15, (1, 1, 1, pulse))
        text(ctx, f"{int(pct)} %", 0, 205, 104)
        text(ctx, "Carga lenta" if slow > 0.5 else "Carga rápida", 0, 290, 34, col=rgba(col, 0.95))
    return draw


def hook_pct(t):
    return 80 * ease_in_out(min(1, t / 1.9)) ** 0.8 if t < 1.9 else 80 + (t - 1.9) * 0.9


# ---------- la batería por dentro ----------

BX0, BX1, BY0, BY1 = 90, 990, 440, 1170
LAYERS = [470 + 106 * k for k in range(7)]
SLOTS = sorted([(662 + 38 * c, LAYERS[g] + 53) for g in range(6) for c in range(8)], key=lambda p: (p[0], p[1]))
N_ION = len(SLOTS)
CATH = [(178 + 40 * (i % 6), 512 + 82 * (i // 6)) for i in range(N_ION)]
OXIDE = [(158 + 40 * c, 492 + 41 * r) for r in range(16) for c in range(7)]
_rng = random.Random(5)
JIT = [(_rng.uniform(0, 6.3), _rng.uniform(0.6, 1.4)) for _ in range(N_ION + 20)]


def ion_pos(i, q, t):
    (x0, y0), (x2, y2) = CATH[i], SLOTS[i]
    x1, y1 = 540, (y0 + y2) / 2 + 60 * math.sin(i)
    q = ease_in_out(q)
    x = (1 - q) ** 2 * x0 + 2 * (1 - q) * q * x1 + q * q * x2
    y = (1 - q) ** 2 * y0 + 2 * (1 - q) * q * y1 + q * q * y2
    ph, sp = JIT[i]
    wob = 3 * (1 - q * (1 - q) * 4) * 0 + 2.5 * math.sin(t * 3 * sp + ph)
    return x + wob, y + wob * 0.6


def ion(ctx, x, y, a=1.0, col=CYAN):
    glow(ctx, x, y, 32, col, 0.7 * a, add=True)
    disc(ctx, x, y, 11, rgba(mix(col, WHITE, 0.45), a))


def battery(ctx, t, fill, current=1.0, parking=0.0, queue=0.0, plating=0.0, heat=0.0, labels=None):
    labels = labels or {}
    # circuito exterior con electrones
    wire = [(130, BY0 + 6), (130, 330), (950, 330), (950, BY0 + 6)]
    stroke(ctx, wire, (0.55, 0.58, 0.66), 8)
    seg = [(wire[k], wire[k + 1]) for k in range(3)]
    lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in seg]
    total = sum(lens)
    for k in range(16):
        d = ((k / 16) + t * 0.22 * current) % 1 * total
        for (a, b), L in zip(seg, lens):
            if d <= L:
                x, y = a[0] + (b[0] - a[0]) * d / L, a[1] + (b[1] - a[1]) * d / L
                glow(ctx, x, y, 18, YELLOW, 0.5 * current, add=True)
                disc(ctx, x, y, 5, YELLOW)
                break
            d -= L
    disc(ctx, 540, 330, 50, radial(540, 330, 50, [(0, (0.20, 0.22, 0.28)), (1, (0.10, 0.11, 0.15))]))
    ctx.arc(540, 330, 50, 0, 2 * math.pi)
    source(ctx, (1, 1, 1, 0.3))
    ctx.set_line_width(3)
    ctx.stroke()
    bolt(ctx, 540, 330, 0.55, YELLOW)
    # carcasa (se hincha un poco con el calor)
    sw = 1 + 0.015 * heat * (1 + math.sin(t * 5)) / 2
    ctx.save()
    ctx.translate(540, (BY0 + BY1) / 2)
    ctx.scale(sw, sw)
    ctx.translate(-540, -(BY0 + BY1) / 2)
    soft_ellipse(ctx, 540, BY1 - 20, 520, 80, (0, 0, 0), 0.6)
    fill_rr(ctx, BX0, BY0, BX1 - BX0, BY1 - BY0, 46, linear(0, BY0, 0, BY1, [(0, (0.70, 0.72, 0.78)), (1, (0.38, 0.40, 0.46))]))
    fill_rr(ctx, BX0 + 14, BY0 + 14, BX1 - BX0 - 28, BY1 - BY0 - 28, 36, linear(0, BY0, 0, BY1, [(0, (0.06, 0.12, 0.20)), (1, (0.03, 0.06, 0.11))]))
    # colectores: aluminio y cobre
    fill_rr(ctx, 116, 470, 16, 670, 6, (0.80, 0.82, 0.86))
    fill_rr(ctx, 948, 470, 16, 670, 6, (0.85, 0.52, 0.32))
    # cátodo: red de óxido
    for k, (x, y) in enumerate(OXIDE):
        disc(ctx, x, y, 10, (0.45, 0.18, 0.25) if (k + k // 7) % 2 else (0.58, 0.30, 0.17))
    # separador poroso
    ctx.save()
    ctx.set_dash([18, 12], 0)
    for x in (526, 554):
        stroke(ctx, [(x, 470), (x, 1140)], (0.85, 0.88, 0.95, 0.55), 4)
    ctx.restore()
    # ánodo: capas de grafito
    for y in LAYERS:
        fill_rr(ctx, 640, y - 12, 300, 24, 8, linear(0, y - 12, 0, y + 12, [(0, (0.52, 0.54, 0.60)), (1, (0.24, 0.25, 0.30))]))
        for hx in range(650, 935, 26):
            ctx.save()
            ctx.translate(hx, y)
            path(ctx, [(9 * math.cos(a * math.pi / 3), 9 * math.sin(a * math.pi / 3)) for a in range(6)])
            source(ctx, (1, 1, 1, 0.12))
            ctx.set_line_width(2)
            ctx.stroke()
            ctx.restore()
    # plazas de parking entre capas
    if parking > 0:
        ctx.save()
        ctx.set_dash([10, 8], 0)
        for g in range(6):
            yc = LAYERS[g] + 53
            for c in range(9):
                x = 643 + 38 * c
                stroke(ctx, [(x, yc - 30), (x, yc + 30)], (1, 1, 1, 0.45 * parking), 3)
        ctx.restore()
        s = ease_out_back(parking)
        ctx.save()
        ctx.translate(880, 395)
        ctx.scale(s, s)
        fill_rr(ctx, -40, -40, 80, 80, 14, (0.15, 0.40, 0.95))
        text(ctx, "P", 0, 0, 62)
        ctx.restore()
    # iones
    parked = fill * N_ION
    for i in range(N_ION):
        q = clamp(parked - i + 1)
        x, y = ion_pos(i, q, t)
        ion(ctx, x, y)
    # cola en la entrada cuando quedan pocas plazas
    if queue > 0:
        for k in range(10):
            ph, sp = JIT[N_ION + k]
            x = 590 + 22 * (k % 3) + 6 * math.sin(t * 4 * sp + ph)
            y = 560 + 60 * k + 8 * math.cos(t * 3 * sp + ph)
            ion(ctx, x, y, a=queue, col=mix(CYAN, RED, queue * 0.7))
    # litio metálico: dendritas que crecen desde el ánodo
    if plating > 0:
        for k, y0 in enumerate((560, 700, 860, 1010)):
            rnd = random.Random(k)
            pts, x, y = [(640, y0)], 640.0, float(y0)
            for j in range(9):
                x -= 9 * plating
                y += rnd.uniform(-10, 10) * plating
                pts.append((x, y))
            stroke(ctx, pts, (0.85, 0.88, 0.95), 7)
            for (px, py) in pts[2::2]:
                stroke(ctx, [(px, py), (px - 14 * plating, py + rnd.choice((-1, 1)) * 16 * plating)], (0.85, 0.88, 0.95), 4)
            glow(ctx, x, y, 30, (0.85, 0.9, 1.0), 0.5 * plating, add=True)
    if heat > 0:
        glow(ctx, 540, 805, 620, (1.0, 0.30, 0.10), 0.45 * heat * (0.85 + 0.15 * math.sin(t * 6)), add=True)
    ctx.restore()
    for key, (s, ax, ay, lx, ly, col) in {
        "cathode": ("CÁTODO", 300, 470, 300, 395, WHITE),
        "anode": ("GRAFITO", 800, 470, 760, 395, WHITE),
        "ion": ("IONES DE LITIO", *ion_pos(3, clamp(parked - 3 + 1), t), 420, 1235, CYAN),
        "free": ("QUEDAN POCAS PLAZAS", 926, SLOTS[-1][1], 640, 1235, GREEN),
        "plating": ("LITIO METÁLICO", 590, 700, 420, 1235, (0.85, 0.9, 1.0)),
    }.items():
        if key in labels:
            tag(ctx, s, ax, ay, lx, ly, labels[key], col=col)


def hud(ctx, title, value, unit, x, y, a=1.0, col=WHITE):
    if a <= 0:
        return
    fill_rr(ctx, x, y, 380, 128, 26, (0.02, 0.03, 0.08, 0.7 * a))
    rr(ctx, x, y, 380, 128, 26)
    source(ctx, (1, 1, 1, 0.16 * a))
    ctx.set_line_width(3)
    ctx.stroke()
    text(ctx, title, x + 26, y + 36, 26, col=(0.65, 0.78, 1.0, a), anchor="left")
    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(58)
    vw = ctx.text_extents(value).x_advance
    text(ctx, value, x + 26, y + 88, 58, col=rgba(col, a), anchor="left")
    text(ctx, unit, x + 38 + vw, y + 92, 30, col=(1.0, 0.80, 0.24, a), anchor="left")


# ---------- escenas ----------

def s_hook(ctx, t):
    tech_bg(ctx, t)
    pct = hook_pct(t)
    slow = prog(t, 1.9, 0.4)
    z = 1 + 0.06 * ease_in_out(t / dur(s_hook))
    ctx.translate(540, 760)
    ctx.scale(z, z)
    ctx.translate(-540, -760)
    if t < 1.9:  # chispas de carga rápida
        for k in range(10):
            ph = (t * 2.2 + k / 10) % 1
            a = k * 0.63
            r = 260 + 260 * ph
            glow(ctx, 540 + r * math.cos(a), 760 + r * math.sin(a) * 1.3, 16, GREEN, 0.6 * (1 - ph), add=True)
    phone(ctx, 540, 760, 1.0, charge_screen(min(pct, 100), slow), t)
    tag(ctx, "¿Y AHORA?", 640, 980, 800, 1200, prog(t, 2.3, 0.4), col=ORANGE, size=46)


def charger(ctx, x, y, s, t):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.move_to(0, 150)
    ctx.curve_to(0, 330, 330, 260, 380, 520)
    source(ctx, (0.85, 0.86, 0.90))
    ctx.set_line_width(26)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    soft_ellipse(ctx, 0, 40, 260, 230, (0, 0, 0), 0.55)
    fill_rr(ctx, -170, -170, 340, 340, 56, linear(-170, -170, 170, 170, [(0, (0.98, 0.98, 1.0)), (1, (0.70, 0.71, 0.76))]))
    fill_rr(ctx, -170, -170, 340, 120, 56, linear(0, -170, 0, -50, [(0, (1, 1, 1, 0.5)), (1, (1, 1, 1, 0))]))
    fill_rr(ctx, -52, 108, 104, 30, 15, (0.10, 0.10, 0.13))
    bolt(ctx, 0, -10, 1.0, (0.72, 0.73, 0.78))
    ctx.restore()


def s_not_broken(ctx, t):
    tech_bg(ctx, t)
    charger(ctx, 540, 660, 1.2, t)
    crack = appear(t, w(s_not_broken, "roto"), 0.25) * (1 - appear(t, w(s_not_broken, "propósito"), 0.3))
    if crack > 0:
        for pts in ([(470, 500), (520, 580), (500, 640), (560, 720)], [(520, 580), (600, 590)], [(500, 640), (430, 700)]):
            stroke(ctx, pts, rgba(RED, crack), 9)
        text(ctx, "¿ROTO?", 540, 1130, 76, col=rgba(RED, crack), outline=(0, 0, 0, crack), ow=8)
    p = appear(t, w(s_not_broken, "propósito"), 0.4)
    badge(ctx, 720, 480, p, ok=True, r=74)
    if p > 0:
        text(ctx, "A PROPÓSITO", 540, 1130, 80, col=rgba(GREEN, clamp(p)), outline=(0, 0, 0, clamp(p)), ow=9)


def s_inside(ctx, t):
    tech_bg(ctx, t)
    fill = 0.22 * ease_in_out(t / dur(s_inside))
    battery(ctx, t, fill, current=0.6, labels={
        "cathode": appear(t, 0.2), "anode": appear(t, 0.5), "ion": appear(t, w(s_inside, "iones"), 0.5)})


def s_parking(ctx, t):
    tech_bg(ctx, t)
    fill = 0.22 + 0.10 * ease_in_out(t / dur(s_parking))
    battery(ctx, t, fill, current=0.6, parking=appear(t, w(s_parking, "parking"), 0.5),
            labels={"cathode": 1, "anode": appear(t, w(s_parking, "grafito"), 0.4) * 0 + 1})
    p = appear(t, w(s_parking, "grafito"), 0.4)
    if p > 0:
        glow(ctx, 790, 800, 330, (0.6, 0.65, 0.8), 0.25 * (1 - abs(1 - 2 * clamp(p))), add=True)


def s_fast(ctx, t):
    tech_bg(ctx, t)
    f = 0.32 + 0.48 * ease_in_out(prog(t, 0.2, dur(s_fast) - 0.5))
    battery(ctx, t, f, current=1.6, parking=1, labels={"cathode": 1, "anode": 1})
    hud(ctx, "CARGA", f"{int(f * 100)}", "%", 610, 170, a=appear(t, 0.1), col=GREEN)
    hud(ctx, "CORRIENTE", "ALTA", "", 90, 170, a=appear(t, 0.3), col=YELLOW)


def s_few(ctx, t):
    tech_bg(ctx, t)
    f = 0.80 + 0.03 * ease_in_out(t / dur(s_few))
    q = appear(t, w(s_few, "bruto"), 0.5)
    battery(ctx, t, f, current=1.2, parking=1, queue=q, labels={"anode": 1, "free": appear(t, w(s_few, "plazas"), 0.5)})
    hud(ctx, "CARGA", f"{int(f * 100)}", "%", 610, 170, col=GREEN)
    warn = appear(t, w(s_few, "peligroso"), 0.35)
    if warn > 0:
        hud(ctx, "RIESGO", "ALTO", "", 90, 170, a=warn, col=RED)


def s_damage(ctx, t):
    tech_bg(ctx, t)
    pl = ease_in_out(prog(t, w(s_damage, "amontonan") - 0.1, 1.4))
    ht = ease_in_out(prog(t, w(s_damage, "calienta") - 0.1, 0.8))
    battery(ctx, t, 0.83, current=1.0, parking=1, queue=1 - 0.3 * pl, plating=pl, heat=ht,
            labels={"plating": appear(t, w(s_damage, "amontonan") + 0.4, 0.5)})
    hud(ctx, "TEMPERATURA", f"{int(28 + 17 * ht)}", "°C", 610, 170, col=mix(WHITE, RED, ht))
    hud(ctx, "SALUD", f"{int(100 - 9 * appear(t, w(s_damage, 'estropea'), 0.8))}", "%", 90, 170, col=mix(WHITE, RED, appear(t, w(s_damage, "estropea"), 0.8)))


def s_graph(ctx, t):
    tech_bg(ctx, t)
    ox, oy, gw, gh = 150, 1180, 820, 720
    stroke(ctx, [(ox, oy - gh - 20), (ox, oy), (ox + gw + 20, oy)], (1, 1, 1, 0.6), 4)
    text(ctx, "TIEMPO", ox + gw, oy + 42, 28, col=(1, 1, 1, 0.6), anchor="right")
    for v in (50, 100):
        y = oy - gh * v / 100
        stroke(ctx, [(ox, y), (ox + gw, y)], (1, 1, 1, 0.08), 2)
        text(ctx, f"{v}", ox - 20, y, 28, col=(1, 1, 1, 0.5), anchor="right")
    draw_to = ease_in_out(prog(t, 0.2, dur(s_graph) - 0.6))
    u80 = 0.45

    def charge(u):
        return 80 * (u / u80) ** 0.9 if u < u80 else 80 + 20 * (1 - math.exp(-(u - u80) * 5.5)) / (1 - math.exp(-(1 - u80) * 5.5))

    def current(u):
        return 95 if u < u80 else 95 * math.exp(-(u - u80) * 5.0)

    n = max(2, int(140 * draw_to))
    us = [draw_to * k / (n - 1) for k in range(n)]
    cpts = [(ox + gw * u, oy - gh * charge(u) / 100) for u in us]
    poly(ctx, [(ox, oy)] + cpts + [(cpts[-1][0], oy)], linear(0, oy - gh, 0, oy, [(0, (*GREEN, 0.35)), (1, (*GREEN, 0.0))]))
    stroke(ctx, cpts, GREEN, 8)
    ipts = [(ox + gw * u, oy - gh * current(u) / 100) for u in us]
    stroke(ctx, ipts, CYAN, 7)
    glow(ctx, *cpts[-1], 30, GREEN, 0.8, add=True)
    glow(ctx, *ipts[-1], 30, CYAN, 0.8, add=True)
    text(ctx, "CARGA", ox + 30, oy - gh - 40, 34, col=GREEN, anchor="left")
    text(ctx, "CORRIENTE", ox + 230, oy - gh - 40, 34, col=CYAN, anchor="left")
    if draw_to > u80:
        a = clamp((draw_to - u80) * 6)
        xm = ox + gw * u80
        ctx.save()
        ctx.set_dash([14, 10], 0)
        stroke(ctx, [(xm, oy), (xm, oy - gh)], (1, 0.8, 0.24, a), 4)
        ctx.restore()
        text(ctx, "80 %", xm, oy - gh * 0.8 - 50, 52, col=(1.0, 0.80, 0.24, a), outline=(0, 0, 0, a), ow=8)
    tag(ctx, "BAJA POCO A POCO", ox + gw * 0.7, oy - gh * current(0.7) / 100, ox + gw * 0.62, oy - gh * 0.25,
        appear(t, w(s_graph, "poco"), 0.5), col=CYAN, size=30)


def clock(ctx, x, y, r, t, col):
    disc(ctx, x, y, r, (0.08, 0.09, 0.13))
    ctx.arc(x, y, r, 0, 2 * math.pi)
    source(ctx, col)
    ctx.set_line_width(6)
    ctx.stroke()
    a = t * 3
    stroke(ctx, [(x, y), (x + r * 0.7 * math.sin(a), y - r * 0.7 * math.cos(a))], col, 6)
    stroke(ctx, [(x, y), (x + r * 0.45 * math.sin(a / 12), y - r * 0.45 * math.cos(a / 12))], col, 6)


def s_last(ctx, t):
    tech_bg(ctx, t)
    for k, (lab, length, col, at) in enumerate([("0 → 80 %", 640, GREEN, 0.1), ("80 → 100 %", 600, ORANGE, w(s_last, "último"))]):
        y = 560 + 330 * k
        p = ease_in_out(prog(t, at, 1.0))
        text(ctx, lab, 110, y - 80, 52, anchor="left")
        fill_rr(ctx, 110, y - 34, 700, 68, 34, (1, 1, 1, 0.08))
        if p > 0:
            fill_rr(ctx, 110, y - 34, max(68, length * p), 68, 34, linear(110, 0, 110 + length, 0, [(0, mul(col, 0.7)), (1, col)]))
            glow(ctx, 110 + length * p, y, 50, col, 0.6, add=True)
            clock(ctx, 900, y, 56, t * (1 if k == 0 else 0.3), col)
    p = ease_out_back(appear(t, w(s_last, "tanto"), 0.4))
    if p > 0:
        ctx.save()
        ctx.translate(540, 1170)
        ctx.scale(p, p)
        text(ctx, "≈ MISMO TIEMPO", 0, 0, 70, col=YELLOW, outline=(0, 0, 0), ow=9)
        ctx.restore()


def settings_screen(on, health):
    def draw(ctx, t):
        text(ctx, "Batería", -170, -300, 48, anchor="left")
        for k, (title, y) in enumerate([("Límite de carga", -180), ("Salud de la batería", 0)]):
            fill_rr(ctx, -175, y - 70, 350, 150, 26, (1, 1, 1, 0.07))
            text(ctx, title, -150, y - 30, 30, col=(1, 1, 1, 0.85), anchor="left")
        text(ctx, "80 %", -150, -132, 46, col=mix((1, 1, 1), GREEN, on), anchor="left")
        tx, ty = 95, -132
        fill_rr(ctx, tx - 50, ty - 28, 100, 56, 28, mix((0.35, 0.36, 0.40), GREEN, on))
        disc(ctx, tx - 22 + 44 * on, ty, 23, (1, 1, 1))
        fill_rr(ctx, -150, 40, 300, 22, 11, (1, 1, 1, 0.12))
        fill_rr(ctx, -150, 40, 300 * health, 22, 11, GREEN)
        text(ctx, "♥", 140, -30, 40, col=RED)
    return draw


def s_tip(ctx, t):
    tech_bg(ctx, t)
    on = ease_in_out(appear(t, w(s_tip, "limitas"), 0.4))
    health = 0.82 + 0.18 * ease_in_out(appear(t, w(s_tip, "años"), 0.9))
    phone(ctx, 540, 810, 1.1, settings_screen(on, health), t, cable=False)
    p = ease_out_back(appear(t, 0.0, 0.4))
    if p > 0:
        ctx.save()
        ctx.translate(540, 225)
        ctx.scale(p, p)
        fill_rr(ctx, -150, -46, 300, 92, 46, YELLOW)
        text(ctx, "TRUCO", 0, 0, 56, col=(0.07, 0.07, 0.10))
        ctx.restore()
    tag(ctx, "+ AÑOS DE VIDA", 700, 860, 640, 1235, appear(t, w(s_tip, "años"), 0.5), col=GREEN, size=40)


def s_cta(ctx, t):
    tech_bg(ctx, t)
    phone(ctx, 540, 620, 0.62, charge_screen(80, 0.0), t, cable=False)
    cta_button(ctx, t, 540, 1180)


SCENES = [
    Scene("¿Por qué el móvil carga volando hasta el 80%… y luego va a paso de tortuga?", s_hook,
          voice="¿Por qué el móvil carga volando hasta el ochenta por ciento, y luego va a paso de tortuga?",
          sfx=[(0.1, "riser"), (1.9, "thunk")]),
    Scene("No, tu cargador no está roto. Lo hace a propósito.", s_not_broken, sfx=[("@roto", "thunk"), ("@propósito", "pop")]),
    Scene("Tu batería está llena de iones de litio que van de un lado a otro.", s_inside, sfx=[("@iones", "pop")]),
    Scene("Cargarla es meterlos entre capas de grafito, como coches en un parking.", s_parking, sfx=[("@parking", "pop")]),
    Scene("Con el parking vacío, entran de golpe y sin problema.", s_fast, sfx=[(0.2, "riser")]),
    Scene("Pero cuando quedan pocas plazas, meterlos a lo bruto es peligroso.", s_few, sfx=[("@peligroso", "thunk")]),
    Scene("Se amontonan en la entrada, la batería se calienta y se estropea.", s_damage, sfx=[("@calienta", "boom")]),
    Scene("Por eso, a partir del 80%, el móvil baja la corriente poco a poco.", s_graph,
          voice="Por eso, a partir del ochenta por ciento, el móvil baja la corriente poco a poco."),
    Scene("Completar el último 20% puede tardar casi tanto como todo lo anterior.", s_last,
          voice="Completar el último veinte por ciento puede tardar casi tanto como todo lo anterior.",
          sfx=[("@tanto", "pop")]),
    Scene("Por cierto: si limitas la carga al 80%, tu batería durará más años.", s_tip,
          voice="Por cierto, si limitas la carga al ochenta por ciento, tu batería durará más años.",
          sfx=[(0.05, "pop"), ("@limitas", "pop")]),
    Scene("Síguenos para más curiosidades como esta.", s_cta, sfx=[(0.05, "pop"), (1.3, "pop")]),
]

POST = """¿Por qué el móvil carga volando hasta el 80 % y luego va a paso de tortuga? 🔋

No, tu cargador no está roto. Dentro de la batería, cargar es meter iones de litio entre capas de grafito, como coches en un parking. Cuando quedan pocas plazas, meterlos a lo bruto hace que se amontonen, la batería se caliente y se estropee. Por eso el móvil baja la corriente a partir del 80 %.

Truco: si limitas la carga al 80 %, tu batería durará más años.

¿Tú lo cargas al 100 %? 👇

#curiosidades #tecnologia #movil #bateria #sabiasque
"""

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "out", "movil-carga")
    os.makedirs(out, exist_ok=True)
    narrator = None
    if "--sin-voz" not in sys.argv:
        from voz import Narrator
        voice = sys.argv[sys.argv.index("--voz") + 1] if "--voz" in sys.argv else "santa"
        narrator = Narrator(voice)
    if "--preview" in sys.argv:
        i = sys.argv.index("--preview")
        dest = sys.argv[i + 1] if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith("--") else os.path.join(out, "preview.png")
        preview(SCENES, dest, narrator=narrator)
        print("preview:", dest)
    else:
        total = render(SCENES, os.path.join(out, "movil-carga.mp4"), cover_png=os.path.join(out, "fotograma.png"),
                       cover_at=(0, 1.5), narrator=narrator)
        with open(os.path.join(out, "texto-del-post.txt"), "w") as f:
            f.write(POST)
        print(f"OK: {total:.1f} s")
