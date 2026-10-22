"""Vídeo: ¿sabías que Lamborghini nació por un insulto de Ferrari? — versión con imágenes en el estilo de los dibujos.

Mismo guion, voz, efectos y fuentes que lamborghini_ferrari.py (la versión con fotos), para comparar cuál
retiene más. Las imágenes son de Flow (Nano Banana), pedidas con la referencia de estilo de la skill
(.claude/skills/videos-curiosidades/assets/estilo-referencia.png) y están en
video/assets/lamborghini-ferrari-estilo/. La animación sale de encender zonas de cada imagen al ritmo de la voz
(light_up), de la sacudida del gancho y de las etiquetas.

Ojo con la escena 3: el tercer coche del garaje es un Lamborghini Miura, que no pinta nada entre «unos cuantos
Ferrari», así que se queda en penumbra y solo se encienden los dos primeros.

Uso: python3 video/lamborghini_estilo.py [--voz santa|dora|alex|eleven] [--sin-voz]  ->  video/out/lamborghini-ferrari-estilo/
     python3 video/lamborghini_estilo.py --preview [png]
"""
import functools
import math
import os
import sys

import lamborghini_ferrari as lf
from engine import clamp
from lamborghini_ferrari import FER, GOLD, LAMBO, RED, SKY, bubble, pill, ptag
from piezas import WHITE, appear, panel, spaced
from rich import TOP_SHORT, YELLOW, Scene, Still, clip_bg, glow, light_up, preview, render, rgba, source, text, word_time

OUT = "lamborghini-ferrari-estilo"
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", OUT)
BG = (0.049, 0.054, 0.074)  # fondo de las imágenes
# gancho: la imagen tiene los coches arriba y pequeños; se acerca 1,25 veces y la chispa baja de y=700 a y=1100
HOOK_K, HOOK_FROM, HOOK_TO = 1.25, (540, 700), (540, 1100)


def scene_of(fn):
    return next(s for s in SCENES if s.draw is fn)


def w(fn, needle):
    return word_time(scene_of(fn), needle)


@functools.lru_cache(maxsize=None)
def img(n):
    return Still(os.path.join(ASSETS, f"escena-{n:02d}.jpg"))


def bg(ctx, n, t, dim=0.0):
    clip_bg(ctx, img(n), t, dim=dim)


def lit(ctx, n, t, x, y, r, k):
    light_up(ctx, img(n), t, x, y, r, k)


def pulse(t, f=7.0):
    return 0.8 + 0.2 * math.sin(t * f)


# ---------- escenas (posiciones medidas sobre cada imagen, en coordenadas de pantalla) ----------

def s_hook(ctx, t):
    hit = appear(t, w(s_hook, "insulto"), 0.35)
    jolt = hit * (1 - clamp((t - w(s_hook, "insulto")) / 0.6))
    source(ctx, BG)
    ctx.paint()
    ctx.save()  # acercar la imagen y sacudirla con el insulto
    ctx.translate(HOOK_TO[0] + 12 * jolt * math.sin(t * 70), HOOK_TO[1] + 7 * jolt * math.cos(t * 55))
    ctx.scale(HOOK_K, HOOK_K)
    ctx.translate(-HOOK_FROM[0], -HOOK_FROM[1])
    bg(ctx, 1, t)
    flick = 0.5 + 0.5 * math.sin(t * 31) * math.sin(t * 17)
    lit(ctx, 1, t, *HOOK_FROM, 140, 0.35 + 0.35 * flick + 0.7 * hit)  # la chispa está viva
    ctx.restore()
    if hit > 0:
        glow(ctx, *HOOK_TO, 300, YELLOW, 0.55 * hit, add=True)

    def grawlix(c):
        text(c, "#@%!", 0, 0, 74, col=RED)
    bubble(ctx, 270, 850, 330, 170, (250, 1040), hit, grawlix)
    spaced(ctx, "FERRARI", 240, 1440, 34, col=rgba(FER, appear(t, w(s_hook, "Ferrari"), 0.4)), anchor="center")
    spaced(ctx, "LAMBORGHINI", 820, 1440, 34, col=rgba(LAMBO, appear(t, w(s_hook, "Lamborghini"), 0.4)), anchor="center")


def s_tractors(ctx, t):
    bg(ctx, 2, t)
    rich_ = clamp((t - w(s_tractors, "rico") + 0.1) / 0.6)
    lit(ctx, 2, t, 948, 1390, 230, 0.8 * rich_ * pulse(t, 9))  # las monedas brillan con «rico»
    ptag(ctx, "1948 · TRACTORES", 200, 1150, 240, 900, appear(t, w(s_tractors, "tractores"), 0.4), col=SKY)
    ptag(ctx, "FERRUCCIO LAMBORGHINI", 808, 1245, 760, 1010, appear(t, w(s_tractors, "creador"), 0.4), col=WHITE)


def s_cars(ctx, t):
    bg(ctx, 3, t, dim=0.55)  # garaje en penumbra; el tercero (un Miura) no se enciende
    for (x, y), word in (((220, 1250), "dinero"), ((520, 1250), "cuantos")):
        p = appear(t, w(s_cars, word), 0.4)
        lit(ctx, 3, t, x, y - 120, 300, 1.0 * p)
        if p > 0:
            glow(ctx, x, y, 190, FER, 0.25 * p, add=True)
    f = appear(t, w(s_cars, "Ferrari"), 0.4)
    lit(ctx, 3, t, 370, 840, 360, 0.5 * f)  # se encienden las lámparas
    ptag(ctx, "FERRARI 250 GT", 520, 1215, 560, 1480, appear(t, w(s_cars, "Ferrari") + 0.2, 0.4), col=WHITE)


def s_clutch(ctx, t):
    zoom = appear(t, w(s_clutch, "embrague"), 0.45)
    fail = appear(t, w(s_clutch, "fallaba"), 0.4)
    bg(ctx, 4, t, dim=0.45 * (1 - zoom))  # la lupa se enciende con «embrague»
    lit(ctx, 4, t, 540, 930, 330, 0.35 * zoom)
    if fail > 0:  # el embrague y el humo laten en rojo
        lit(ctx, 4, t, 540, 930, 200, 0.6 * fail * pulse(t, 14))
        glow(ctx, 540, 930, 260, RED, 0.35 * fail * pulse(t, 14), add=True)
        lit(ctx, 4, t, 700, 1500, 260, 0.4 * fail)
    for word, (x, y) in (("una", (860, 630)), ("otra", (950, 850)), ("vez", (200, 1190))):
        p = appear(t, w(s_clutch, word), 0.3)
        lit(ctx, 4, t, x, y, 90, 1.2 * p)
        if p > 0:
            glow(ctx, x, y, 110, YELLOW, 0.5 * p * (1 - clamp((t - w(s_clutch, word)) / 0.6)), add=True)
    ptag(ctx, "EMBRAGUE", 330, 720, 300, 540, zoom, col=WHITE)


def s_complain(ctx, t):
    bg(ctx, 5, t)
    f = appear(t, w(s_complain, "fábrica"), 0.4)
    lit(ctx, 5, t, 500, 1170, 330, 0.45 * f)  # se encienden las ventanas
    q = appear(t, w(s_complain, "quejarse"), 0.4)
    lit(ctx, 5, t, 898, 1040, 140, 0.8 * q * pulse(t, 10))  # su bocadillo con el embrague roto
    ptag(ctx, "MARANELLO", 330, 1000, 380, 640, f, col=FER)
    pill(ctx, "SEGÚN CONTABA ÉL EN 1991", 540, 860, a=appear(t, w(s_complain, "contaba"), 0.4))


def s_reply(ctx, t):
    bg(ctx, 6, t)
    mad = appear(t, w(s_reply, "enfadado"), 0.4)
    if mad > 0:
        glow(ctx, 290, 1160, 230, RED, 0.35 * mad * pulse(t, 12), add=True)
    yes = appear(t, w(s_reply, "tractor"), 0.4)
    no = appear(t, w(s_reply, "nunca"), 0.4)
    lit(ctx, 6, t, 335, 640, 170, 0.8 * yes)  # el tractor y su ✓
    lit(ctx, 6, t, 744, 650, 170, 0.8 * no)  # el Ferrari y su ✗
    if no > 0:
        glow(ctx, 744, 574, 120, RED, 0.5 * no * pulse(t, 12), add=True)
    pill(ctx, "RECREACIÓN", 200, 990, size=24, col=(1, 1, 1, 0.9), a=appear(t, 0.05, 0.3))
    ptag(ctx, "ENZO FERRARI", 290, 1250, 330, 1560, appear(t, w(s_reply, "dueño"), 0.4), col=FER)
    ptag(ctx, "FERRUCCIO", 840, 1080, 700, 1400, appear(t, 0.1, 0.4), col=LAMBO)


def s_perfect(ctx, t):
    rev = appear(t, w(s_perfect, "perfecto") - 0.3, 0.6)
    bg(ctx, 7, t, dim=0.5 * (1 - rev))
    lit(ctx, 7, t, 550, 1270, 470, 0.5 * (1 - rev))  # primero, el plano
    lit(ctx, 7, t, 540, 1570, 470, 0.55 * rev)  # luego, el coche
    panel(ctx, 580, 470, "NACE LAMBORGHINI", "1963", "", appear(t, w(s_perfect, "decidió"), 0.4), col=LAMBO, wdt=400)


def s_bull(ctx, t):
    bull = appear(t, w(s_bull, "toro"), 0.5)
    sign = appear(t, w(s_bull, "Tauro"), 0.5)
    bg(ctx, 8, t, dim=0.45 * (1 - bull))
    lit(ctx, 8, t, 538, 950, 330, 0.5 * bull * pulse(t, 6))
    lit(ctx, 8, t, 538, 1590, 170, 1.0 * sign * pulse(t, 8))
    if sign > 0:
        glow(ctx, 538, 1590, 200, YELLOW, 0.4 * sign, add=True)
    ptag(ctx, "TAURO", 600, 1590, 720, 1520, sign, col=YELLOW)
    pill(ctx, "NACIÓ UN 28 DE ABRIL DE 1916", 540, 1460, col=GOLD, a=sign)


def s_ask(ctx, t):
    f = appear(t, w(s_ask, "Ferrari"), 0.4)
    lb = appear(t, w(s_ask, "Lamborghini"), 0.4)
    bg(ctx, 9, t, dim=0.35)
    lit(ctx, 9, t, 540, 1080, 120, 0.6 * pulse(t, 11))  # el rayo
    for (x, y), col, name, on, ny in (((540, 790), FER, "FERRARI", f, 600), ((540, 1350), LAMBO, "LAMBORGHINI", lb, 1530)):
        lit(ctx, 9, t, x, y, 470, 0.7 * on)
        if on > 0:
            glow(ctx, x, y, 320, col, 0.3 * on, add=True)
        spaced(ctx, name, x, ny, 44, col=rgba(col if on > 0.5 else WHITE, 0.55 + 0.45 * on), anchor="center")


DRAWS = [s_hook, s_tractors, s_cars, s_clutch, s_complain, s_reply, s_perfect, s_bull, s_ask]
SCENES = [Scene(s.text, d, duration=s.min_duration, sfx=list(s.sfx), voice=s.voice, key=s.key) for s, d in zip(lf.SCENES, DRAWS)]
POST = lf.POST

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
