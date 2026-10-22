"""Lo que comparten los scripts de la skill: encontrar el motor (video/) y la voz con los mismos ajustes
que usan los vídeos (santa a 1,04, 0,22 s entre frases, escenas de 1,6 s como mínimo)."""
import os
import re
import sys
import unicodedata
from pathlib import Path

SPEED, GAP, MIN_SCENE, LEAD = 1.04, 0.22, 1.6, 0.12


def video_dir():
    """VIDEO_DIR si está definida; si no, la primera carpeta con rich.py y voz.py subiendo desde el
    directorio actual o desde esta skill (que vive en <repo>/.claude/skills/videos-curiosidades/)."""
    if os.environ.get("VIDEO_DIR"):
        cands = [Path(os.environ["VIDEO_DIR"])]
    else:
        cands = []
        for start in (Path.cwd(), Path(__file__).resolve().parent):
            for base in (start, *start.parents):
                cands += [base, base / "video"]
    for c in cands:
        if (c / "rich.py").exists() and (c / "voz.py").exists():
            return c
    sys.exit("No encuentro el motor (video/rich.py). Ejecuta desde el repo o define VIDEO_DIR.")


def use_video():
    """Pone video/ en sys.path para poder importar rich, voz y los vídeos."""
    d = video_dir()
    sys.path.insert(0, str(d))
    return d


def narrador(voice="santa"):
    from voz import Narrator
    n = Narrator(voice, speed=SPEED)
    n.gap, n.min_scene = GAP, MIN_SCENE
    return n


def to16k(audio, sr=44100):
    """Whisper trabaja a 16 kHz; pasarle el audio ya convertido evita el aviso de sherpa-onnx."""
    from voz import resample
    return resample(audio, sr, 16000)


def norm(s):
    """Para comparar lo escrito con lo que oye Whisper: sin tildes, signos ni la confusión b/v."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn").replace("v", "b")
    return re.sub(r"[^a-z0-9ñ ]+", " ", s).split()
