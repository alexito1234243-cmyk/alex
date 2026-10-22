"""Vídeo: <la pregunta del gancho>

<Una línea con la estructura: gancho → giro → mecanismo → dato wow → pregunta.>

Datos y fuentes:
- <Afirmación del guion>: <URL de la fuente>
- <Afirmación del guion>: <URL de la fuente>

Uso: python3 video/<slug>.py [--voz santa|dora|alex|eleven] [--sin-voz]  ->  video/out/<carpeta>/
     python3 video/<slug>.py --preview [png]
"""
import math
import os
import sys

from engine import clamp, ease_in_out, ease_out_back
from piezas import CYAN, WHITE, appear, mini_tag, panel, spaced, tech_bg
from rich import TOP_SHORT, YELLOW, Scene, disc, glow, preview, render, word_time

OUT = "nuevo-video"  # carpeta en video/out/ y nombre del .mp4


def scene_of(fn):
    return next(s for s in SCENES if s.draw is fn)


def dur(fn):
    return scene_of(fn).duration


def w(fn, needle):
    """Instante (s) en que la voz dice la primera palabra de la escena que contiene `needle`."""
    return word_time(scene_of(fn), needle)


# ---------- piezas de este vídeo (el objeto protagonista, sus cortes, sus detalles) ----------

def objeto(ctx, x, y, s, t, lit=0.0):
    """Sustituye esto por el objeto protagonista dibujado en (x, y) a escala s."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    glow(ctx, 0, 0, 320, CYAN, 0.35 + 0.4 * lit, add=True)
    disc(ctx, 0, 0, 180 + 8 * math.sin(t * 3), CYAN)
    ctx.restore()


# ---------- escenas: una por frase; las animaciones se enganchan a palabras con w() ----------

def s_hook(ctx, t):
    tech_bg(ctx, t)
    p = ease_out_back(appear(t, w(s_hook, "gancho"), 0.5))
    objeto(ctx, 540, 1000, 1 + 0.1 * p, t, lit=p)


def s_giro(ctx, t):
    tech_bg(ctx, t)
    objeto(ctx, 540, 1000, 1.0, t)
    mini_tag(ctx, "ETIQUETA", 640, 900, 820, 700, appear(t, w(s_giro, "giro"), 0.4), col=YELLOW)


def s_dato(ctx, t):
    tech_bg(ctx, t)
    objeto(ctx, 540, 1050, 0.8, t, lit=ease_in_out(clamp(t / 1.5)))
    panel(ctx, 600, 470, "DATO", "42", "%", appear(t, w(s_dato, "dato"), 0.3), col=WHITE)


def s_pregunta(ctx, t):
    tech_bg(ctx, t)
    for k, word in enumerate(("primera", "segunda")):
        on = appear(t, w(s_pregunta, word), 0.4)
        spaced(ctx, word.upper(), 540, 900 + 220 * k, 56, col=YELLOW if on > 0.5 else (1, 1, 1, 0.5), anchor="center")


SCENES = [
    Scene("Aquí va el gancho con una pregunta.", s_hook, key="gancho", sfx=[("@gancho", "whoosh")]),
    Scene("Luego viene el giro que nadie espera.", s_giro, key="giro", sfx=[("@giro", "pop")]),
    Scene("Por cierto, este es el dato.", s_dato, key="dato", sfx=[("@dato", "pop")]),
    Scene("Cuéntame: ¿la primera o la segunda?", s_pregunta, key="segunda", duration=3.6,
          sfx=[("@primera", "pop"), ("@segunda", "pop")]),
]

POST = """<El gancho> <un emoji>
<La misma pregunta del cierre>
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
