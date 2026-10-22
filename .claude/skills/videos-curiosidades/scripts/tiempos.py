"""Tiempos de cada escena de un vídeo con la voz real, para la tabla del guion.md.

Uso: python3 tiempos.py ojos_colores      (el nombre del script en video/, sin .py)
"""
import importlib
import sys

from _comun import narrador, use_video


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    use_video()
    from rich import narrate
    scenes = importlib.import_module(sys.argv[1]).SCENES
    narrate(scenes, narrador())
    start = 0.0
    for s in scenes:
        print(f"{start:5.1f}-{start + s.duration:5.1f} | {len(s.text.split()):2d} palabras | {s.text}")
        start += s.duration
    print(f"total {start:.1f} s, {sum(len(s.text.split()) for s in scenes)} palabras")


if __name__ == "__main__":
    main()
