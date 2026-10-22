# Imágenes de Flow en los vídeos

## Lo que hay que saber del MCP de Flow del usuario (srz-google-flow-mcp)

- **Solo funciona en su ordenador.** Maneja su propio Chrome con su sesión de Google en flow.google.com.
- **En la nube no hay forma de usarlo.** El dominio está bloqueado por la red y no se puede iniciar sesión en un navegador remoto. Tampoco pidas cookies, sesiones ni claves de su cuenta.
- **Genera imágenes** (Nano Banana Pro, 2 o 2 Lite), **no vídeos**. Sus herramientas son `flow_generate_image` (prompt, aspect `9:16`, count 1-4 y model `pro`) y `flow_upload_file`, para subir fotos de referencia.
- **Las peticiones van en cola**, una detrás de otra (lo bloquea su propio código). El «modo agente» no las acelera. Lo único que va en paralelo es pedir hasta 4 versiones de un mismo prompt.

## Qué escenas merecen una imagen

| Sí | No |
|---|---|
| El gancho con una persona real haciendo lo que todos hacen (frotarse los ojos, mirar por la ventanilla) | Mecanismos por dentro: cortes, capas, piezas, circuitos. La IA se inventa la anatomía y la técnica |
| Objetos y lugares reales (una cabina, una cocina, una calle) | Escenas cuya animación va sincronizada con la voz (etiquetas que aparecen palabra a palabra, datos en directo) |
| Personajes históricos en cuadro, como el retrato de Newton | Gráficos, comparaciones y esquemas «A = B» |
| | Personas reales del siglo XX de las que hay fotos (Enzo Ferrari): una «foto» generada sería falsa. Mejor siluetas |
| | Productos de marca: la IA pone escudos y logos inventados |
| Ambientes abstractos que acompañan una idea (los fosfenos) | Cualquier cosa que lleve texto |

Lo normal es que 3-5 escenas de 9 lleven imagen. Si el usuario pide imágenes para todas, explícale por qué no conviene y dale las que sí.

## Cómo escribir los prompts

- **Idioma:** en inglés.
- **Composición:** vertical 9:16, con el sujeto en el centro (de la cuarta parte de arriba hasta un poco por encima del final). La parte de arriba debe quedar oscura y vacía, porque ahí van los subtítulos.
- **Prohibido el texto.** Termina siempre con: `no text, no letters, no logos, no watermark`. Si la imagen tiene un papel o un libro, pide además `the handwriting blurred and unreadable`.
- **Un estilo común** para las imágenes de «3D explicativo»: `clean 3D explainer render, dark navy background, soft studio rim light, subtle cyan accent light`. Para las fotos de personas: `photorealistic, cinematic, shallow depth of field, dark navy tones, subtle cyan rim light`.
- **Describe lo que debe verse con exactitud.** Para el cuaderno de Newton había que pedir «entre el ojo y el hueso». La primera versión clavaba la aguja en la pupila y hubo que descartarla.

Dáselo al usuario como UN bloque listo para pegar en su agente:

```
Genera estas imágenes con flow_generate_image. Formato 9:16, modelo pro, 2 versiones de cada una (count 2). Guárdalas en una carpeta llamada "<tema>" y renómbralas con el nombre que pongo delante de cada prompt, añadiendo -a y -b a cada versión (por ejemplo escena-01-a.png). No cambies los prompts y genéralas una detrás de otra.

escena-01: <prompt>
escena-05: <prompt>
```

Pídele los archivos originales (no capturas de pantalla) y en un mensaje normal.

## Cuando llegan las imágenes

1. **Dónde están.** Las imágenes de un mensaje normal se guardan en `/tmp/claude-0/<sesión>/images/N.jpg`. Las que llegan mientras estás trabajando a veces solo se ven y no se guardan: si no están en disco, pide que las reenvíe.
2. **Tamaño.** Mira el tamaño con `identify`. Las de Nano Banana Pro salen a 1116×2000, suficiente para 1080×1920.
3. **Revísalas contra el guion**, una por una, y elige la mejor versión. Descarta las que:
   - contradigan lo que dice la voz;
   - tengan letras casi legibles;
   - corten objetos en el borde;
   - tengan bandas de relleno que no se puedan tapar.
   Di cuál descartas y por qué.
4. **Cópialas al repo** como `video/assets/<carpeta>/escena-NN-nombre.jpg`.
5. **Móntalas** con `Still` y `clip_bg` (ver `motor.md`, apartado 5). Ajusta `dy` si la imagen pisa los subtítulos y mide sobre la foto lo que haya que alinear.
6. **Saca fotogramas** de las escenas con foto y míralos antes del render final.
7. **Apúntalo en `guion.md`**: qué imagen va en cada escena y qué se descartó.
