"""Portadas de los vídeos (1080x1920) y foto de perfil (1080x1080).

El título va dentro de la franja central 3:4 (y 240-1680), que es lo que enseña la cuadrícula del perfil.
Uso: python3 video/portadas.py  ->  video/out/<vídeo>/portada.jpg y video/out/perfil/foto-perfil.png
"""
import math
import os
import subprocess

import cairo

import avion_luces as av
import tierra_agujero as ti
from engine import FONT, H, W
from rich import YELLOW, glow, linear, make_grain, radial, text

HERE = os.path.dirname(os.path.abspath(__file__))


def finish(ctx, grain, w=W, h=H, top_shade=True):
    """Viñeta, oscurecido arriba para el título y grano, como en los vídeos."""
    ctx.rectangle(0, 0, w, h)
    ctx.set_source(radial(w / 2, h * 0.5, max(w, h) * 0.62, [(0, (0, 0, 0, 0)), (0.6, (0, 0, 0, 0)), (1, (0, 0, 0, 0.55))]))
    ctx.fill()
    if top_shade:
        ctx.rectangle(0, 0, w, h * 0.45)
        ctx.set_source(linear(0, 0, 0, h * 0.45, [(0, (0, 0, 0, 0.55)), (0.7, (0, 0, 0, 0.25)), (1, (0, 0, 0, 0))]))
        ctx.fill()
    pat = cairo.SurfacePattern(grain)
    pat.set_extend(cairo.EXTEND_REPEAT)
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT)
    ctx.set_source(pat)
    ctx.paint_with_alpha(0.28)
    ctx.restore()


def title(ctx, lines, top, max_w=960, max_size=124):
    """lines: [(texto, resaltado)]. Un solo tamaño para todas las líneas, el mayor que quepa."""
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(100)
    widest = max(ctx.text_extents(s).x_advance for s, _ in lines)
    size = min(max_size, 100 * max_w / widest)
    y = top + size / 2
    for s, hi in lines:
        text(ctx, s, W / 2, y + 6, size, col=(0, 0, 0, 0.45))
        text(ctx, s, W / 2, y, size, col=YELLOW if hi else (1, 1, 1), outline=(0.04, 0.04, 0.09), ow=14)
        y += size * 1.12


def save_jpg(surf, path):
    png = path.replace(".jpg", ".png")
    surf.write_to_png(png)
    subprocess.run(["convert", png, "-quality", "90", path], check=True)
    os.remove(png)


def cover_tierra(grain):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    t = 2.6
    ti.space(ctx, t)
    ctx.save()
    ctx.translate(0, 300)
    ti.section(ctx, t)
    ti.faller(ctx, t, 0.95)
    ctx.restore()
    finish(ctx, grain)
    title(ctx, [("¿Y SI SALTAS", False), ("POR UN AGUJERO", False), ("QUE ATRAVIESA", False), ("LA TIERRA?", True)], 270)
    save_jpg(surf, os.path.join(HERE, "out", "tierra-agujero", "portada.jpg"))


def cover_avion(grain):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    t = 1.8
    av.sky(ctx, t)
    av.clouds(ctx, t)
    av.ground(ctx, t, drift=t * 40)
    av.runway(ctx, t)
    av.plane(ctx, t, 470, 1010, s=1.02, rot=0.045)
    av.clouds(ctx, t, front=True)
    finish(ctx, grain)
    title(ctx, [("¿POR QUÉ", False), ("APAGAN LAS LUCES", True), ("AL ATERRIZAR?", False)], 300)
    save_jpg(surf, os.path.join(HERE, "out", "avion-luces", "portada.jpg"))


def avatar(grain, size=1080):
    """Interrogación amarilla cuyo punto es la Tierra: se lee incluso a 110 px."""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    ctx = cairo.Context(surf)
    c = size / 2
    ctx.rectangle(0, 0, size, size)
    ctx.set_source(radial(c, c * 0.9, size * 0.75, [(0, (0.10, 0.10, 0.28)), (1, (0.01, 0.01, 0.05))]))
    ctx.fill()
    for x, y, r, ph in ti.STARS[:90]:
        ctx.new_sub_path()
        ctx.arc(x * size / W, y * size / H, r * 0.8, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.25 + 0.4 * (0.5 + 0.5 * math.sin(ph)))
        ctx.fill()
    glow(ctx, c, c * 0.80, size * 0.46, (1.0, 0.75, 0.2), 0.40, add=True)
    # cuerpo de la interrogación
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    fs = size * 0.80
    ctx.set_font_size(fs)
    ext = ctx.text_extents("?")
    ctx.save()
    ctx.rectangle(0, 0, size, size * 0.64)  # sin el punto: lo sustituye el planeta
    ctx.clip()
    ctx.move_to(c - ext.x_advance / 2 - ext.x_bearing * 0.2, size * 0.78)
    ctx.text_path("?")
    ctx.set_source(linear(0, size * 0.18, 0, size * 0.64, [(0, (1.0, 0.93, 0.55)), (1, (1.0, 0.74, 0.16))]))
    ctx.fill_preserve()
    ctx.set_source_rgba(0.04, 0.04, 0.09, 1)
    ctx.set_line_width(size * 0.012)
    ctx.stroke()
    ctx.restore()
    ti.globe(ctx, 0.0, c + size * 0.005, size * 0.775, size * 0.10, rot=-10)
    finish(ctx, grain, size, size, top_shade=False)
    out = os.path.join(HERE, "out", "perfil")
    os.makedirs(out, exist_ok=True)
    surf.write_to_png(os.path.join(out, "foto-perfil.png"))


if __name__ == "__main__":
    grain, _keep = make_grain()
    cover_tierra(grain)
    cover_avion(grain)
    avatar(grain)
    print("OK")
