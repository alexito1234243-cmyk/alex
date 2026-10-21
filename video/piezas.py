"""Piezas comunes de los vídeos de estilo técnico: fondo con rejilla, etiquetas tipo plano,
el móvil y la palabra a la que va sincronizada cada animación."""
from engine import H, W, clamp, ease_in_out, prog
from rich import disc, fill_rr, glow, linear, poly, radial, rgba, rr, soft_ellipse, source, stroke, text

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
