---
name: videos-curiosidades
description: Produce de principio a fin los vídeos verticales de curiosidades de la cuenta @poresoesasi23 («Por eso es así | Curiosidades») para Instagram Reels, TikTok, YouTube Shorts y Facebook. Cubre tema y datos con fuentes, tres ganchos, guion de 25-35 s, escenas animadas con el motor de video/ (rich.py, piezas.py), voz en off «santa» de Kokoro comprobada con Whisper, render MP4, portada, guion.md y texto del post. Úsala siempre que el usuario pida un vídeo, reel, short o tiktok de curiosidades; «haz otro vídeo»; «el tema N del lote»; un vídeo «como los de @resultaaquee»; cambiar la voz, los subtítulos, las transiciones o los sonidos de estos vídeos; meter imágenes de Flow o preparar sus prompts; o rehacer la portada o el texto de un vídeo, aunque no diga «skill» ni nombre el motor.
---

# Vídeos de curiosidades («Por eso es así»)

Vídeos faceless de UNA curiosidad cotidiana, con dibujos animados por código, la voz «santa» y subtítulos arriba de 1-3 palabras. El motor está en `video/` del repo. Esta skill recoge cómo se hicieron los vídeos que ya existen (`video/ojos_colores.py` es el más completo) y los errores que costaron tiempo.

**Entregables de cada vídeo** (en `video/out/<carpeta>/`): `<carpeta>.mp4`, `portada.jpg`, `texto-del-post.txt` y `guion.md`. Además, el script `video/<slug>.py`, una línea en `video/README.md`, un commit y el push.

## Antes de empezar

- **El motor.** Si no existe `video/rich.py` en el directorio de trabajo, el motor está en el repo de GitHub `alexito1234243-cmyk/alex`. Mientras no se fusione con `main`, está en la rama `claude/pensive-planck-dc80jt`.
- **Dependencias.** Instala con `pip install pycairo numpy sherpa-onnx`. Hacen falta `ffmpeg` y `convert` (ImageMagick, para las portadas).
- **Modelos de voz.** `sh video/get_voices.sh --check` baja Kokoro y Whisper base de las releases de GitHub de sherpa-onnx. Hugging Face suele estar bloqueado en la nube; no pierdas tiempo con él. Los modelos van a `video/models/`, que está en `.gitignore`.
- **Bancos de temas.** `video/lote-temas.md` tiene el lote de temas y la guía de estilo de Flow; `video/prompt-maestro.md`, las reglas editoriales. Si el usuario dice «el 12», es el tema 12 del lote.
- **Referencias del motor.** Lee `references/motor.md` antes de escribir escenas. Lee `references/flow.md` solo si hay imágenes de Flow de por medio.

## Flujo

### 1. Tema y datos

Elige un tema que el 100 % de la gente haya vivido sin entenderlo (avión, coche, cocina, cuerpo, casa, móvil) y que tenga un giro. Evita como tema principal los componentes por dentro que nadie ha visto (chips, sensores): rindieron poco.

**Marcas famosas** (lote 2 de `video/lote-temas.md`):
- Encajan mejor los «¿por qué [algo que has visto de esa marca]?» que las historias de origen.
- Las anécdotas sin fuente oficial se cuentan como «según contaba…».
- No copies logos ni anuncios: dibuja el producto o insinúalo.
- Si te llega un banco de temas de otro asistente, verifícalo entero. El primero que llegó traía un dato falso y otro engañoso, y sus puntuaciones no salían de ningún dato.

Verifica cada afirmación con una búsqueda web antes de escribir el guion y apunta la fuente. Lo que no puedas confirmar va marcado como [VERIFICAR] o fuera del guion. Si una fecha o una cifra se discute, no la digas. Las barras y los contadores «ilustrativos» van sin números: un número en pantalla se lee como un dato.

### 2. Tres ganchos

Escribe tres y recomienda uno, diciendo por qué. Fórmulas que funcionan:
- «¿Por qué [algo que todos han visto]?». Es la del vídeo del avión, el único que ha funcionado.
- «¿Sabías que [algo que suena imposible y es cierto]?».
- Una paradoja: «quitan el ruido añadiendo más ruido».

No gastes el dato más fuerte en el gancho: es el premio del segundo 25.

### 3. Guion: 80-110 palabras, 25-35 s

- **0-2 s:** el gancho.
- **2-6 s:** el giro («no es lo que crees»).
- **6-25 s:** el mecanismo en 3-4 pasos, con un dato concreto por paso.
- **25-30 s:** el dato wow o la consecuencia práctica.
- **30-35 s:** la pregunta final, DICHA POR LA VOZ y fácil de contestar («¿Qué ves tú: puntos, rayas o colores?»).

Escribe una escena por frase y frases cortas. Nunca pongas «sígueme para crear vídeos como estos» ni nada que venda.

**Reglas de la voz «santa»**, aprendidas a base de transcripciones fallidas:
- No empieces una frase con una vocal suelta ni con «Y», «Así», «Está», «Va dentro» o «Dentro». Santa se las come. Usa «Cuando», «Luego», «Por cierto»…
- Escribe los números en palabras en el texto hablado. Si el subtítulo debe llevar cifras, usa `Scene(voice="...")` con la versión hablada.
- Algunas palabras se funden: «tú ves» sonó «tuve». Reordena la frase («¿qué ves tú?»).
- Al empezar frase también flojean la F, la S y la L: «Ferruccio» sonó «Perucho», «Furioso» sonó «Curioso», «Su respuesta» sonó «Tu respuesta» y «Lamborghini se picó» sonó «Amborgini». Empieza con otra palabra («Muy enfadado, …», «Con ese dinero…», «Pero…»).
- Los nombres que empiezan por vocal («Enzo») se los come también a mitad de frase. Escríbelos en pantalla y que la voz diga otra cosa («el dueño de Ferrari»).
- Los nombres extranjeros, escríbelos como suenan en `voice=` («Ferruchio»: con «Ferruccio», Santa decía «Ferruxio»).

Comprueba todas las frases ANTES de dibujar:

```sh
python3 .claude/skills/videos-curiosidades/scripts/comprobar_voz.py "Frase uno." "Frase dos."
python3 .claude/skills/videos-curiosidades/scripts/comprobar_voz.py --modulo ojos_colores   # las frases de un vídeo ya escrito
```

El script sintetiza cada frase con Santa, la transcribe con Whisper y estima la duración total. Reescribe la frase hasta que Whisper la entienda. Hay excepciones: Whisper escribe «b» por «v» y falla con palabras raras («posfenos» por «fosfenos»). Eso no es culpa de la voz.

### 4. Escenas

Copia la plantilla y renómbrala:

```sh
cp .claude/skills/videos-curiosidades/assets/plantilla.py video/<slug>.py
```

Cada escena es una función `s_xxx(ctx, t)` que dibuja el fotograma en el instante `t`. Las animaciones se enganchan a palabras con `w(s_xxx, "palabra")`, nunca a segundos fijos: la voz decide la duración. Principios que han funcionado:
- **Un objeto protagonista grande** en el centro (y 480-1600). Va cambiando: objeto → corte por dentro → zoom al detalle.
- **Que algo se mueva siempre.** Cada palabra clave dispara algo: una etiqueta, un brillo, un dato, un efecto de sonido.
- **Ninguna escena empieza vacía.** Si lo importante llega con una palabra del final, enséñalo antes en tenue (siluetas apagadas, un plano azul, una rueda que gira) y enciéndelo con la palabra. El primer fotograma del gancho tiene que llamar la atención por sí solo.
- **Etiquetas pequeñas en mayúsculas** con `mini_tag`, al menos a 90 px de los bordes: la cámara acerca un 9 % y lo empuja hacia fuera.
- **Datos en directo** con `panel` o `readout`, arriba a la derecha (x 600-980, y 470-600), debajo de los subtítulos.
- **El cierre**: la pregunta visual (opciones que se encienden al nombrarlas).

Detalles del motor, zonas seguras y sonidos: `references/motor.md`.

### 5. Hoja de prueba (sin voz, en segundos)

```sh
cd video && python3 <slug>.py --sin-voz --preview /ruta/scratch/prev.png
```

Ábrela con Read y mírala de verdad. Comprueba que:
- ninguna etiqueta queda cortada en el borde;
- nada importante cae bajo los subtítulos (y menor que 470);
- ninguna pieza dibujada contradice el guion;
- las proporciones se entienden en un móvil.

Corrige antes de poner la voz.

### 6. Render con voz y revisión

```sh
cd video && python3 <slug>.py                      # unos 10 s de cálculo por segundo de vídeo: pon un timeout de 600000 ms
python3 ../.claude/skills/videos-curiosidades/scripts/revisar.py out/<carpeta>/<carpeta>.mp4 /ruta/scratch/rejilla.png
```

`revisar.py` saca una rejilla con un fotograma por segundo y transcribe todo el audio del vídeo final, a trozos de 25 s porque Whisper solo acepta 30. Mira la rejilla con Read:
- ¿El momento clave de cada escena dura lo suficiente antes del corte? Si no, dale `duration=` (es un mínimo).
- ¿Las transiciones son limpias?
- ¿Se oye todo el texto?

Si una escena se queda corta, alárgala y renderiza otra vez. Es mejor que publicar un vídeo que no se entiende.

### 7. Portada

Añade `cover_<slug>(grain)` a `video/portadas.py`, copiando `cover_ojos`. Las reglas:
- El título va en mayúsculas, en 3-4 líneas, con la palabra clave en amarillo (`title(ctx, [(texto, resaltado)], top)`).
- Debe quedar dentro de la franja y 240-1680, que es lo que enseña la cuadrícula del perfil.
- Debajo, el objeto o la foto más llamativa del vídeo.

Ejecuta solo esa función: `python3 -c "import portadas, rich; g,k = rich.make_grain(); portadas.cover_<slug>(g)"`. El `main` de `portadas.py` rehace todas las portadas.

### 8. guion.md y texto del post

Los tiempos de cada escena salen con:

```sh
python3 .claude/skills/videos-curiosidades/scripts/tiempos.py <modulo>
```

Usa la misma estructura que `video/out/ojos-colores/guion.md`:
1. Título y ficha (duración, palabras, voz, estructura).
2. Los tres ganchos, con el recomendado marcado.
3. Una tabla con tiempo, voz, palabra clave, plano y etiquetas.
4. Las imágenes de Flow, si las hay, con lo usado y lo descartado y por qué.
5. El texto del post.
6. Una tabla de datos con su estado y su fuente.

Las fuentes también van en el docstring del script.

**Texto del post:** dos líneas, sin hashtags. Los hashtags no dan alcance (lo ha dicho varias veces Adam Mosseri, el jefe de Instagram), @resultaaquee no los usa y las palabras que la gente busca ya van en el gancho. Si el usuario quiere alguno, que sean 1-2 del tema, nunca una lista. La primera línea es el gancho con un emoji; la segunda, la misma pregunta del cierre. Va en `POST` dentro del script, que lo escribe en `texto-del-post.txt`.

### 9. Entregar

1. Añade una línea a `video/README.md` con el script y lo que tenga de nuevo.
2. Ejecuta `python3 -m pyflakes` sobre los .py tocados.
3. Haz `git add video/` (las imágenes de Flow van en `video/assets/<carpeta>/`). Escribe el commit en español y en imperativo («Añadir el vídeo de…»), con las líneas de atribución que pida la sesión y sin nombres de modelos.
4. Haz push a la rama de la sesión. El MP4 debe pesar menos de 100 MB: el motor ya limita el bitrate.
5. Envía al usuario el MP4, la portada, el texto del post y el guion, si tienes una herramienta para enviar archivos.
6. Dile qué hacer:
   - Publícalo con esa portada y ese texto.
   - Compártelo también en Facebook.
   - A las 48 h, pasa capturas de la retención, el tiempo medio de visualización y los compartidos.

## Lo que dicen los datos de la cuenta (actualízalo cuando lleguen métricas nuevas)

| Vídeo | Duración | Resultado |
|---|---|---|
| Por qué apagan las luces al aterrizar (`avion_luces.py`) | 29 s | 3.059 personas y 6 seguidores: el único que pasó la prueba inicial de Instagram |
| Auriculares que quitan ruido (`auriculares.py`) | 49 s | 731 |
| Cómo sabe el móvil que lo has girado (`giro_movil.py`) | 50 s | 116 |
| Agujero que atraviesa la Tierra (`tierra_agujero.py`) | 36 s | 128 en Instagram y 1.134 en Facebook |

Lecciones:
- Los vídeos cortos (25-35 s) y con gancho de pregunta sobre algo vivido rinden más. Los de 50 s, explicando componentes por dentro, se hundieron.
- Prioriza la serie «Misterios del avión» (temas 1, 3, 7 y 11 del lote).
- No ha habido compartidos ni comentarios en ningún vídeo. Por eso el cierre es una pregunta fácil, dicha por la voz.
- El perfil convierte bien (6 de 6 visitas se hicieron seguidores). El cuello de botella es el alcance, no el perfil.
- 3-4 vídeos por semana. Más volumen no compensa hasta tener datos de retención.

## Imágenes de Flow (resumen; los detalles están en `references/flow.md`)

El MCP de Flow del usuario solo funciona en su ordenador: maneja su Chrome con su sesión de Google. Desde la nube no se puede usar, y no hay que pedirle cookies ni claves.

El reparto de trabajo es este:
1. Tú le das un bloque de prompts listo para pegar en su agente.
2. Él te pasa las imágenes en un mensaje normal.
3. Tú las montas con `Still` y `clip_bg`.

Usa imágenes solo donde el realismo aporta (el gancho con una persona real, objetos reales, personajes históricos, ambientes). Los mecanismos se quedan dibujados, porque la IA se inventa la anatomía y la técnica. Rechaza cualquier imagen que contradiga el guion y explica por qué.

## Errores que ya costaron tiempo

- **Bucles de espera con `pgrep -f`/`pkill -f`.** Se encuentran a sí mismos o matan tu propia shell. Usa el truco del corchete (`[g]iro_movil.py`) o, mejor, ejecuta el render en primer plano con timeout.
- **Animaciones en segundos fijos.** Se desincronizan en cuanto cambia la voz. Usa siempre `w(fn, "palabra")` y `dur(fn)`.
- **El `main` de `portadas.py`.** Reescribe todas las portadas; ejecuta solo la función nueva.
- **Las imágenes que el usuario manda mientras trabajas.** A veces solo se ven y no llegan como archivo (busca en `/tmp/claude-0/*/images/`). Pídele que las reenvíe en un mensaje nuevo.
- **Whisper con más de 30 s.** Solo transcribe los primeros 30. `revisar.py` ya trocea el audio.
- **El tamaño del vídeo.** Un MP4 de más de 100 MB no sube a GitHub. El motor ya usa `-maxrate 8M`.
- **`__pycache__`.** No debe entrar en git: está en `.gitignore`.
