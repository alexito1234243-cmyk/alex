"""Comprueba frases con la voz: las sintetiza, las transcribe con Whisper y estima la duración del vídeo.

Uso:
  python3 comprobar_voz.py "Frase uno." "Frase dos."
  python3 comprobar_voz.py --modulo ojos_colores     # las frases de las escenas de un vídeo (su voice= si lo tienen)
  python3 comprobar_voz.py --voz dora "Frase."

Las líneas marcadas con ≠ son las que Whisper no ha entendido igual: escúchalas o reescríbelas.
Whisper confunde b/v (eso ya no se marca) y falla con palabras raras; eso no es culpa de la voz.
Necesita los modelos: sh video/get_voices.sh --check
"""
import argparse
import importlib

from _comun import LEAD, narrador, norm, to16k, use_video


def main():
    ap = argparse.ArgumentParser(description="Comprueba la pronunciación de frases con Kokoro + Whisper.")
    ap.add_argument("frases", nargs="*")
    ap.add_argument("--modulo", help="nombre del script del vídeo en video/, sin .py")
    ap.add_argument("--voz", default="santa")
    args = ap.parse_args()
    use_video()
    from voz import transcribe

    frases = list(args.frases)
    if args.modulo:
        frases += [s.voice or s.text for s in importlib.import_module(args.modulo).SCENES]
    if not frases:
        ap.error("pasa frases o --modulo")
    n = narrador(args.voz)
    total = 0.0
    for f in frases:
        audio = n.say(f)
        d = len(audio) / 44100
        total += max(LEAD + d + n.gap, n.min_scene)
        heard = transcribe(to16k(audio), 16000)
        mark = "  " if norm(heard) == norm(f) else "≠ "
        print(f"{mark}{d:4.2f} s | {f}\n           oye: {heard}")
    words = sum(len(f.split()) for f in frases)
    print(f"\n{len(frases)} frases, {words} palabras, unos {total:.1f} s de vídeo (objetivo: 80-110 palabras, 25-35 s)")


if __name__ == "__main__":
    main()
