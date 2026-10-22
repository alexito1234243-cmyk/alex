"""Imagen de referencia del estilo de los vídeos (sin texto), para subirla a Flow como @{estilo} y que las
imágenes generadas parezcan hechas con el motor: fondo azul noche con rejilla, formas planas con degradados
suaves, sombras blandas, brillos y acentos rojo, amarillo y cian.

Uso: python3 estilo_referencia.py [salida.png]   (por defecto, assets/estilo-referencia.png de la skill)
"""
import math
import os
import sys

import cairo

from _comun import use_video


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "assets", "estilo-referencia.png")
    use_video()
    import lamborghini_ferrari as lf
    import ojos_colores as oc
    from piezas import bolt, tech_bg
    from rich import YELLOW, fill_rr, glow, linear, stroke

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1080, 1920)
    ctx = cairo.Context(surf)
    t = 1.2
    tech_bg(ctx, t)
    # carretera con los dos coches morro con morro
    fill_rr(ctx, -20, 770, 1120, 150, 0, linear(0, 770, 0, 920, [(0, (0.12, 0.12, 0.14)), (1, (0.05, 0.05, 0.06))]))
    for k in range(7):
        fill_rr(ctx, 20 + 160 * k, 840, 90, 12, 6, (1, 1, 1, 0.5))
    glow(ctx, 540, 690, 200, YELLOW, 0.45, add=True)
    lf.car(ctx, 290, 780, 0.62, lf.FER, t)
    lf.car(ctx, 790, 780, 0.62, lf.LAMBO, t, kind="wedge", flip=True)
    bolt(ctx, 540, 690, 1.2, YELLOW)
    # pieza técnica y corte por dentro
    glow(ctx, 290, 1230, 230, (0.25, 0.85, 1.0), 0.25, add=True)
    lf.clutch(ctx, 290, 1230, 150, t)
    oc.eye_section(ctx, 760, 1230, 0.55, t, press=0.6, lit=0.7, strain=0.8)
    # tractor en el campo
    fill_rr(ctx, -20, 1650, 1120, 300, 0, linear(0, 1650, 0, 1920, [(0, (0.30, 0.22, 0.13)), (1, (0.10, 0.07, 0.05))]))
    for k in range(5):
        stroke(ctx, [(0, 1680 + k * k * 12), (1080, 1680 + k * k * 12)], (0, 0, 0, 0.25), 3 + k)
    lf.tractor(ctx, 540, 1660, 0.8, t)
    for k in range(6):  # destellos sueltos
        a = k * 1.1
        glow(ctx, 540 + 420 * math.cos(a), 1080 + 300 * math.sin(a), 40, YELLOW, 0.35, add=True)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    surf.write_to_png(out)
    print("referencia:", os.path.abspath(out))


if __name__ == "__main__":
    main()
