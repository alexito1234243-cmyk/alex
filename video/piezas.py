"""Piezas comunes de los vídeos de estilo técnico: fondo con rejilla, etiquetas tipo plano,
el móvil y la palabra a la que va sincronizada cada animación."""
import math

import cairo

from engine import H, W, clamp, ease_in_out, ease_out_back, prog
from rich import disc, fill_rr, glow, linear, mix, poly, radial, rgba, rr, soft_ellipse, source, stroke, text

BG = (0.031, 0.035, 0.045)
CYAN = (0.25, 0.85, 1.0)
GREEN = (0.30, 0.95, 0.55)
RED = (1.0, 0.32, 0.26)
ORANGE = (1.0, 0.55, 0.15)
WHITE = (1, 1, 1)


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


def spaced(ctx, s, x, y, size, col=WHITE, spacing=0.18, anchor="left"):
    """Mayúsculas con letras separadas (etiquetas de plano técnico)."""
    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    adv = [ctx.text_extents(ch).x_advance + size * spacing for ch in s]
    width = sum(adv) - size * spacing
    x0 = x - (width if anchor == "right" else width / 2 if anchor == "center" else 0)
    source(ctx, (0, 0, 0, 0.6 * (col[3] if len(col) > 3 else 1)))
    for ch, a in zip(s, adv):
        ctx.move_to(x0 + 1, y + size * 0.36 + 2)
        ctx.show_text(ch)
        x0 += a
    x0 = x - (width if anchor == "right" else width / 2 if anchor == "center" else 0)
    source(ctx, col)
    for ch, a in zip(s, adv):
        ctx.move_to(x0, y + size * 0.36)
        ctx.show_text(ch)
        x0 += a


def mini_tag(ctx, s, ax, ay, lx, ly, p, col=WHITE, size=30):
    """Etiqueta discreta: punto pequeño, línea fina y texto espaciado."""
    if p <= 0:
        return
    a, e = clamp(p * 1.5), ease_in_out(p)
    disc(ctx, ax, ay, 6, rgba(col, a))
    stroke(ctx, [(ax, ay), (ax + (lx - ax) * e, ay + (ly - ay) * e)], rgba(col, 0.7 * a), 2)
    if p > 0.5:
        b = clamp((p - 0.5) / 0.5)
        right = lx >= ax
        spaced(ctx, s, lx + (10 if right else -10), ly, size, col=rgba(col, b), anchor="left" if right else "right")


def panel(ctx, x, y, title, value, unit, a=1.0, col=WHITE, wdt=380):
    """Panel con un título pequeño y un valor grande (y su unidad en amarillo)."""
    if a <= 0:
        return
    fill_rr(ctx, x, y, wdt, 132, 22, (0.02, 0.03, 0.08, 0.72 * a))
    rr(ctx, x, y, wdt, 132, 22)
    source(ctx, (1, 1, 1, 0.14 * a))
    ctx.set_line_width(2)
    ctx.stroke()
    spaced(ctx, title, x + 24, y + 30, 22, col=(0.65, 0.78, 1.0, a))
    ctx.select_font_face("DejaVu Sans Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(54)
    ext = ctx.text_extents(value)
    source(ctx, rgba(col, a))
    ctx.move_to(x + 24, y + 104)
    ctx.show_text(value)
    if unit:
        text(ctx, unit, x + 36 + ext.x_advance, y + 88, 26, col=(1.0, 0.80, 0.24, a), anchor="left")


def readout(ctx, x, y, rows, a=1.0, title=None, unit=""):
    """Panel de datos en directo con números de ancho fijo: rows = [(nombre, valor, color)]."""
    if a <= 0:
        return
    h = 64 * len(rows) + (54 if title else 26)
    fill_rr(ctx, x, y, 360, h, 22, (0.02, 0.03, 0.08, 0.72 * a))
    rr(ctx, x, y, 360, h, 22)
    source(ctx, (1, 1, 1, 0.14 * a))
    ctx.set_line_width(2)
    ctx.stroke()
    yy = y + 22
    if title:
        spaced(ctx, title, x + 24, yy + 10, 22, col=(0.65, 0.78, 1.0, a))
        yy += 34
    for name, val, col in rows:
        spaced(ctx, name, x + 24, yy + 26, 26, col=rgba(col, a))
        ctx.select_font_face("DejaVu Sans Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(44)
        s = f"{val:+.2f}".replace(".", ",")
        ext = ctx.text_extents(s)
        source(ctx, (1, 1, 1, a))
        ctx.move_to(x + 360 - 24 - ext.x_advance - (70 if unit else 0), yy + 42)
        ctx.show_text(s)
        if unit:
            text(ctx, unit, x + 360 - 20, yy + 30, 22, col=(1.0, 0.80, 0.24, a), anchor="right")
        yy += 64


# ---------- personas y pantallas ----------

def person(ctx, x, y, s=1.0, look=1):
    """Silueta sencilla de cabeza y hombros."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    fill_rr(ctx, -150, 120, 300, 260, 130, linear(0, 120, 0, 380, [(0, (0.30, 0.36, 0.55)), (1, (0.14, 0.17, 0.28))]))
    disc(ctx, 0, 0, 110, radial(-30, -40, 150, [(0, (0.92, 0.70, 0.58)), (1, (0.70, 0.48, 0.38))]))
    ctx.new_sub_path()
    ctx.arc(0, -10, 114, math.pi * 1.02, math.pi * 1.98)
    ctx.close_path()
    source(ctx, (0.16, 0.11, 0.08))
    ctx.fill()
    disc(ctx, 40 * look, 10, 11, (0.10, 0.08, 0.08))
    ctx.restore()


def share_screen(picked, badge_p, sent, follow, thumb=None, badge=None):
    """Pantalla de compartir: se elige a un amigo (con un icono encima) y el botón pasa a «Enviado»."""
    def draw(c, tt):
        if thumb:
            c.save()
            c.translate(0, -230)
            thumb(c, tt)
            c.restore()
        if follow > 0:
            fill_rr(c, -95, -330, 190, 56, 28, rgba((0.95, 0.25, 0.30), follow))
            text(c, "SEGUIR", 0, -302, 28, col=(1, 1, 1, follow))
        fill_rr(c, -190, -20, 380, 420, 36, (0.10, 0.11, 0.16))
        text(c, "Enviar a", -160, 30, 28, col=(1, 1, 1, 0.8), anchor="left")
        for k, (name, col) in enumerate([("Lucía", (0.85, 0.45, 0.55)), ("Dani", (0.35, 0.60, 0.95)), ("Marta", (0.40, 0.75, 0.50)), ("Leo", (0.90, 0.70, 0.30))]):
            ax = -135 + 90 * k
            disc(c, ax, 120, 34, col)
            text(c, name[0], ax, 120, 32)
            text(c, name, ax, 182, 20, col=(1, 1, 1, 0.75))
            if k == 1 and picked > 0:
                c.arc(ax, 120, 42, 0, 2 * math.pi)
                source(c, rgba(CYAN, picked))
                c.set_line_width(6)
                c.stroke()
                if badge and badge_p > 0:
                    badge(c, ax + 34, 80, ease_out_back(badge_p))
        fill_rr(c, -160, 260, 320, 70, 35, mix((0.25, 0.45, 0.95), GREEN, sent))
        text(c, "Enviado ✓" if sent > 0.5 else "Enviar", 0, 295, 30)
    return draw
