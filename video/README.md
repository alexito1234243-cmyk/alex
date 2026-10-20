# Vídeos de curiosidades

Vídeos verticales (1080x1920) con dibujos animados a mano y subtítulos palabra a palabra.

- `engine.py`: motor de render (cairo + ffmpeg).
- `boli_bic.py`: vídeo de prueba. `python3 video/boli_bic.py` → `video/out/boli-bic/` (vídeo, portada y texto del post).

Requisitos: `ffmpeg`, `pip install pycairo numpy`.

Pendiente: voz en off. Ahora las duraciones salen de la longitud del texto; con voz, saldrán de la duración del audio de cada frase.
