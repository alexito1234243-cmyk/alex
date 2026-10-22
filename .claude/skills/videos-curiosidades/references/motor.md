# El motor de vídeo (video/)

## Índice
1. Cómo funciona un vídeo
2. Escenas, voz y sincronía
3. Zonas seguras de la pantalla
4. Piezas de dibujo
5. Fondos: clips de vídeo e imágenes
6. Sonido
7. Render, hoja de prueba y tiempos
8. Vídeos de ejemplo

## 1. Cómo funciona un vídeo

- **Formato.** Fotogramas de 1080×1920 a 30 fps dibujados con pycairo y enviados en crudo a ffmpeg: libx264 crf 21 con tope de 8 Mbit/s, y AAC a -14 LUFS, el volumen estándar de Reels y TikTok.
- **Escenas.** Un vídeo es una lista `SCENES` de `Scene` y cada escena dibuja con una función `s_xxx(ctx, t)`. `t` son los segundos desde que empieza la escena.
- **Encima de cada escena**, el motor pinta solo el oscurecido de arriba, el grano, la barra de progreso y los subtítulos.
- **Transición de 0,3 s** entre escenas, que «atraviesa» la imagen. La escena anterior sigue dibujándose con `t` mayor que su duración, así que las animaciones deben aguantar valores de `t` grandes. Con `clamp`, `appear` y `prog` ya lo hacen.
- **Cámara viva.** Cada escena se acerca un 9 % a lo largo de su duración, alrededor de (540, 960).

## 2. Escenas, voz y sincronía

```python
Scene(text, draw, duration=0.0, sfx=[], voice="", key="")
```

- **`text`** es el subtítulo, y también lo que dice la voz si no hay `voice`.
- **`voice`** es el texto hablado cuando el subtítulo lleva cifras o siglas.
- **`key`** es la palabra resaltada en amarillo. Elige la del giro o la del dato.
- **`duration`** es un MÍNIMO; la duración real la pone la voz:
  - Duración = 0,12 s + la frase + `narrator.gap` (0,22), con un mínimo de `narrator.min_scene` (1,6).
  - Úsala para dar aire a un momento visual que llega al final de la frase.
- **`sfx`** son pares `(cuándo, tipo)`. «Cuándo» puede ser:
  - un número de segundos;
  - `"@palabra"`, el momento en que se dice esa palabra;
  - `"@palabra+0.3"`, un poco después de esa palabra.

**Sincronía con palabras.** Copia de la plantilla las funciones `scene_of`, `dur(fn)` y `w(fn, "palabra")`:
- `w` devuelve el instante en que la voz dice la primera palabra que contiene ese texto.
- Es una estimación repartida por sílabas, no un alineado exacto. Cuenta con unos ±0,2 s.
- Busca por un trozo de palabra que no aparezca antes en la frase. Ojo: «un» coincide antes con «uno» que con «punzón».

**Animación.** Usa estas funciones:
- **`appear(t, at, d)`:** va de 0 a 1 entre `at` y `at + d`.
- **`prog(t, start, dur)`:** lo mismo, sin adelanto.
- **`ease_in_out` y `ease_out_back`:** suavizan el movimiento; la segunda rebota.
- **`clamp`:** limita un valor entre 0 y 1.

El patrón típico es `p = appear(t, w(s_x, "retina"), 0.4)` y dibujar algo con opacidad o escala `p`.

**Voz.** El `main` de la plantilla hace `narrator_from_args(sys.argv, speed=1.04)` con `gap = 0.22` y `min_scene = 1.6`. No aceleres Kokoro: suena más artificial.
- **Voces:** santa (por defecto), dora y alex.
- **ElevenLabs:** `--voz eleven` necesita `ELEVENLABS_API_KEY` y `ELEVENLABS_VOICE_ID` en la configuración del entorno. Nunca pidas una clave por el chat.

**Subtítulos.** Usa siempre `style=TOP_SHORT`:
- 1-3 palabras a la vista y lo ya dicho en gris.
- La palabra clave va con fondo amarillo.
- Van arriba, en y ≈ 360, fuera de la zona que tapa la interfaz de Reels.

## 3. Zonas seguras de la pantalla

| Zona | y | Uso |
|---|---|---|
| Barra de progreso y subtítulos | 0-470 | No pongas aquí nada importante. Un panel de datos cabe justo debajo (y 470-600) |
| Escenario | 480-1600 | El objeto protagonista, las etiquetas y los datos |
| Interfaz de Reels (descripción y botones) | > 1620 | Solo decoración |

- En horizontal, deja todo lo que tenga texto entre x 90 y 990. La cámara acerca un 9 % y lo que está cerca del borde se sale.
- `mini_tag` pone el texto a la derecha del punto final si `lx >= ax`, y a la izquierda si no. Para que una etiqueta no se salga por la derecha, termina la línea a la izquierda del punto.

## 4. Piezas de dibujo

**Pintura y formas** (`rich.py`):
- **Color:** `rgba(c, a)` y `mix(a, b, f)`. `mul(c, k)` aclara u oscurece.
- **Degradados:** `linear(x0, y0, x1, y1, stops)` y `radial(cx, cy, r, stops)`.
- **Formas:** `poly(ctx, pts, src)`, `fill_rr(ctx, x, y, w, h, r, src)` (rectángulo redondeado), `disc(ctx, x, y, r, src)`, `stroke(ctx, pts, col, width, close=False)` y `bezier(p0, p1, p2, p3, n)`, que devuelve puntos.
- **Luz:** `glow(ctx, x, y, r, col, a, add=True)` hace un halo; con `add` suma luz. `soft_ellipse` hace sombras suaves.
- **Texto:** `text(ctx, s, x, y, size, col, anchor, outline, ow)`.
- **Varios:** `blurred(ctx, draw_fn)` (fondo desenfocado), `badge(ctx, x, y, p, ok)` (✓ o ✗ que rebota) y `label`.

**Piezas comunes** (`piezas.py`):
- **Fondo:** `tech_bg(ctx, t)`, oscuro con rejilla y destellos lentos. Es el fondo de casi todo.
- **Etiquetas:** `mini_tag(ctx, texto, ax, ay, lx, ly, p, col)`, una etiqueta discreta (punto, línea y texto espaciado), y `tag(...)`, la versión grande.
- **Texto espaciado:** `spaced(ctx, texto, x, y, size, col, anchor)`, en mayúsculas de plano técnico.
- **Datos:** `panel(ctx, x, y, título, valor, unidad, a, col)` (un dato grande) y `readout(ctx, x, y, filas, a, título, unidad)` (varias cifras en directo).
- **Personas y móvil:** `phone(ctx, x, y, s, screen, t)` (móvil con pantalla), `person(ctx, x, y, s, look)` (silueta) y `share_screen(...)` (pantalla de compartir).
- **Colores:** `CYAN`, `GREEN`, `RED`, `ORANGE` y `WHITE`. `YELLOW` está en `rich`.

Lo que sea propio de un tema (un ojo en corte, unos auriculares, un avión) va en el script del vídeo. Si un segundo vídeo lo necesita, muévelo a `piezas.py`; así se hizo con `panel`.

## 5. Fondos: clips de vídeo e imágenes

- **`Clip(ruta)`** es un vídeo, por ejemplo de Flow. **`Still(ruta)`** es una imagen fija. Las dos se recortan a 9:16 sin deformar.
- **`clip_bg(ctx, clip, t, dim=0.25, dy=0)`** pinta el fondo:
  - `dim` lo oscurece para que se lean las etiquetas;
  - `dy` lo baja para dejar sitio arriba. Rellena antes ese hueco con el color de la parte de arriba de la imagen.
- **Pasar puntos de la imagen a la pantalla.** Usa s = max(1080/ancho, 1920/alto); entonces x' = x·s − (ancho·s − 1080)/2 e y' = y·s − (alto·s − 1920)/2 + dy.
- **Para alinear dibujos con algo de la foto**, mídelo con PIL. En `ojos_colores.py`, `NERVE_PTS` salió de buscar los píxeles amarillos del nervio.
- **Dar vida a una foto fija.** La cámara ya acerca. Además puedes:
  - repintar una zona con `OPERATOR_ADD` y una máscara radial, girándola despacio (`swirl` en `ojos_colores.py`);
  - subir el brillo al decir la palabra clave;
  - poner chispas encima.
- **Costuras y bandas de relleno** de las imágenes generadas: tápalas con un degradado del color de fondo (`fade_top` en `ojos_colores.py`).

## 6. Sonido

Se pone solo:
- un whoosh estéreo con golpe grave en cada corte entre escenas;
- un zumbido de ambiente;
- el ducking: los efectos bajan cuando habla la voz.

Efectos por escena (`sfx`):

| Tipo | Suena como | Para qué |
|---|---|---|
| `pop` | clic suave | aparece una etiqueta o un dato |
| `whoosh` | barrido | algo entra o estalla (el gancho, la palabra clave) |
| `thunk` | golpe grave | algo se apaga, cae o se corta |
| `tick` | chasquido corto | clics o disparos en serie (con `"@palabra+0.2"`) |
| `chime` | «ding-dong» de cabina de avión | serie del avión |
| `riser` | viento que crece (3 s) | tensión antes de un giro |
| `boom` | estruendo grave | impacto fuerte |

## 7. Render, hoja de prueba y tiempos

- `python3 video/<slug>.py --sin-voz --preview <png>`: un fotograma de cada escena en segundos. Con voz, quita `--sin-voz`; tarda unos 30 s más.
- `python3 video/<slug>.py`: el render completo, con unos 10 s de cálculo por segundo de vídeo. Escribe el MP4 y `texto-del-post.txt` en `video/out/<carpeta>/`.
- Los scripts de la skill (`scripts/`):
  - `comprobar_voz.py`: frases → Santa → Whisper.
  - `tiempos.py`: los tiempos de cada escena, para el guion.
  - `revisar.py`: rejilla de fotogramas y transcripción del vídeo final.

## 8. Vídeos de ejemplo (cópiales piezas)

| Script | Qué tiene de útil |
|---|---|
| `ojos_colores.py` | Corte del ojo que se deforma, capas de la retina con disparos sincronizados con clics, imágenes de Flow (`Still`, `swirl`, `fade_top`, puntos medidos sobre la foto), cambio de foto a dibujo dentro de una escena |
| `auriculares.py` | Ondas que se suman y se anulan, paneles con datos en directo, corte de un aparato con etiquetas, cierre de compartir |
| `avion_luces.py` | El que mejor ha funcionado: cielo, avión, pista y pupila que se adapta |
| `giro_movil.py` | Sensor por dentro con muelles y masa, lecturas `readout` |
| `movil_carga.py` | Móvil con pantalla animada (`phone` con `screen`) |
| `tierra_agujero.py` | Planeta en corte y caída con física |
