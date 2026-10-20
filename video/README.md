# Vídeos de curiosidades

Vídeos verticales (1080x1920) con dibujos animados a mano y subtítulos palabra a palabra.

- `engine.py`: motor de render (cairo + ffmpeg).
- `boli_bic.py`: vídeo de prueba. `python3 video/boli_bic.py` → `video/out/boli-bic/` (vídeo, portada y texto del post).
- `rich.py`: motor v2 para escenas a pantalla completa (degradados, luces, grano, fundidos, ambiente sonoro).
- `avion_luces.py`: vídeo elaborado con el motor v2. `python3 video/avion_luces.py` → `video/out/avion-luces/`;
  con `--preview <png>` saca una hoja con un fotograma por escena en 3 segundos.
- `tierra_agujero.py`: ¿qué pasaría si saltaras por un agujero que atraviesa la Tierra? → `video/out/tierra-agujero/`.

- `movil_carga.py`: ¿por qué el móvil carga lento desde el 80 %? Formato de la cuenta de referencia (mito desmentido, corte técnico con etiquetas, animaciones sincronizadas con palabras) → `video/out/movil-carga/`.
- `portadas.py`: portadas diseñadas (título dentro de la franja 3:4 del perfil) y foto de perfil → `video/out/perfil/`.

Requisitos: `ffmpeg`, `pip install pycairo numpy`.

## Voz en off

Locución local con Kokoro (sherpa-onnx), sin cuentas ni pagos por uso:

```sh
sh video/get_voices.sh            # baja el modelo (~350 MB) a video/models/ (no se sube a git)
python3 video/tierra_agujero.py   # con voz "santa" por defecto
python3 video/tierra_agujero.py --voz dora   # voces: santa, dora, alex
python3 video/tierra_agujero.py --sin-voz
```

Cada escena dura lo que su frase; los subtítulos se reparten por sílabas a lo largo del audio.
Si el subtítulo lleva números o siglas, la escena define `voice="..."` con el texto hablado.
Para comprobar la pronunciación: `sh video/get_voices.sh --check` y `python3 video/voz.py --check "frase"`.
