# Vídeos de curiosidades

Vídeos verticales (1080x1920) con dibujos animados a mano y subtítulos palabra a palabra.

- `engine.py`: motor de render (cairo + ffmpeg).
- `boli_bic.py`: vídeo de prueba. `python3 video/boli_bic.py` → `video/out/boli-bic/` (vídeo, portada y texto del post).
- `rich.py`: motor v2 para escenas a pantalla completa (degradados, luces, grano, fundidos, ambiente sonoro).
- `avion_luces.py`: vídeo elaborado con el motor v2. `python3 video/avion_luces.py` → `video/out/avion-luces/`;
  con `--preview <png>` saca una hoja con un fotograma por escena en 3 segundos.

Requisitos: `ffmpeg`, `pip install pycairo numpy`.

Pendiente: voz en off. Ahora las duraciones salen de la longitud del texto; con voz, saldrán de la duración del audio de cada frase.
