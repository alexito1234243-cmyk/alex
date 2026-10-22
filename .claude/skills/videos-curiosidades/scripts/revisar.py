"""Revisa un vídeo ya renderizado: una rejilla con un fotograma por segundo y la transcripción de todo el
audio (a trozos de 25 s, porque Whisper solo acepta 30).

Uso: python3 revisar.py video/out/<carpeta>/<carpeta>.mp4 [rejilla.png]
     Sin rejilla.png la guarda en la carpeta temporal y dice dónde. Ábrela con Read y mírala.
"""
import math
import os
import subprocess
import sys
import tempfile

import numpy as np

from _comun import use_video


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    mp4 = sys.argv[1]
    grid = sys.argv[2] if len(sys.argv) == 3 else os.path.join(
        tempfile.gettempdir(), os.path.splitext(os.path.basename(mp4))[0] + "-rejilla.png")
    use_video()
    from voz import transcribe

    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4],
                               capture_output=True, text=True, check=True).stdout)
    size = os.path.getsize(mp4) / 1e6
    rows = math.ceil(dur / 11)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", mp4, "-vf", f"fps=1,scale=180:320,tile=11x{rows}",
                    "-frames:v", "1", grid], check=True)
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", mp4, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    step = 25 * 16000
    text = " ".join(transcribe(audio[i:i + step], 16000) for i in range(0, len(audio), step))
    print(f"duración {dur:.1f} s · {size:.1f} MB{'  ← más de 100 MB: GitHub no lo acepta' if size > 100 else ''}")
    print(f"rejilla (1 fotograma por segundo, 11 por fila): {grid}")
    print(f"se oye: {text}")


if __name__ == "__main__":
    main()
