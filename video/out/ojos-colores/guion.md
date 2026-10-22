# ¿Por qué ves colores al frotarte los ojos?

**Título interno:** fosfenos de presión · tema 12 del lote
**Duración:** 31,6 s · **Guion:** 88 palabras · **Voz:** Kokoro «santa» a 1,04 · **Subtítulos:** arriba, 1-3 palabras con la palabra clave en amarillo · **Cámara:** siempre en movimiento, transiciones que atraviesan la imagen.
**Estructura:** gancho → giro («no es luz») → mecanismo en 4 pasos → dato wow (Newton) → pregunta fácil dicha por la voz.

## Ganchos

1. **«¿Por qué ves colores al frotarte los ojos?»** ← recomendado. Es algo que el 100 % ha hecho y tiene el mismo formato «¿Por qué…?» que tu vídeo del avión, el único que ha funcionado.
2. «Tus ojos pueden ver luz que no existe.» Más misterio, pero no dice de qué va: se pierde a quien no se siente identificado en 1 s.
3. «Newton se metió un punzón junto al ojo para entender esto.» Es el que más impacta, pero gasta el dato wow en el segundo 0 y deja el final sin sorpresa.

## Guion con tiempos

| Tiempo | Voz (y subtítulo) | Palabra clave | Plano | Etiquetas y datos |
|---|---|---|---|---|
| 0,0-2,9 | ¿Por qué ves colores al frotarte los ojos? | colores | **Foto (Flow):** primer plano de un ojo cerrado apretado con el dedo y, encima, humo de colores. Los colores de la foto giran despacio, con chispas, y se encienden en «colores». | — |
| 2,9-6,8 | No es luz: pasa igual en una habitación a oscuras. | luz | Corte del ojo con una bombilla cuya luz llega a la retina. En «luz», una X roja corta los rayos; en «oscuras» se apaga la bombilla, todo se oscurece… y la retina se enciende de colores igual. | LUZ QUE ENTRA 0 % |
| 6,8-10,3 | Cuando aprietas, el ojo se deforma y estira la retina. | retina | El dedo baja y hunde el globo ocular; flechas de estiramiento en la retina, que se ilumina donde más se estira. | PRESIÓN · RETINA |
| 10,3-13,4 | Sus neuronas se disparan como si les llegara luz. | disparan | Zoom a las capas de la retina: fotorreceptores, bipolares y ganglionares. El tejido se estira y las ganglionares se disparan cada vez más rápido (con su «clic»); los impulsos salen por sus fibras. | NEURONAS · SEÑAL DE LA RETINA (barra que se llena) |
| 13,4-16,9 | Luego mandan la señal por el nervio óptico al cerebro. | nervio | **Foto (Flow):** cabeza translúcida de perfil con el cerebro rosa. Los impulsos recorren el nervio amarillo de la foto y la parte de atrás del cerebro se enciende. | NERVIO ÓPTICO · CEREBRO |
| 16,9-20,6 | Para tu cerebro, todo lo que llega por ese nervio es luz. | luz | Dos filas iguales: bombilla → ojo → impulsos → cerebro, y dedo → ojo → los mismos impulsos → cerebro. «=» entre ellas; las dos acaban en «LUZ». | LUZ DE VERDAD · PRESIÓN · LUZ = LUZ |
| 20,6-23,5 | Ves luz que no existe: se llaman fosfenos. | fosfenos | Fosfenos a pantalla completa. | LUZ REAL: 0 · FOSFENOS · DEL GRIEGO «LUZ» + «MOSTRAR» |
| 23,5-27,4 | Newton se metió un punzón entre el ojo y el hueso para verlos. | punzón | **Foto (Flow):** retrato de Newton hasta «punzón»; se acerca, se funde y deja paso al cuaderno dibujado (el ojo y el borde de la órbita a tinta, el punzón entrando entre los dos y, en «verlos», anillos de colores). | ISAAC NEWTON · CUADERNO DE NEWTON · PUNZÓN |
| 27,4-31,6 | Cuéntame: ¿qué ves tú, puntos, rayas o colores? | colores | Tres círculos (puntos, rayas, manchas de color) que se encienden al nombrarlos. | PUNTOS · RAYAS · COLORES |

Comprobado con Whisper sobre el audio final: se entiende todo. Dos avisos: Whisper escribe «Tus neuronas» (el whoosh del corte tapa un poco la «s»; el subtítulo dice «Sus») y «posfenos» (no conoce la palabra; en la frase suelta la transcribe bien).

## Imágenes de Flow (Nano Banana)

Están en `video/assets/ojos-colores/`. Solo van en las escenas donde una imagen real aporta algo. En las del mecanismo (ojo deformado, retina, «luz = presión»), la animación va sincronizada con la voz y la IA inventaría la anatomía.

| Escena | Imagen | Decisión |
|---|---|---|
| 1 | `escena-01-ojo.jpg` | Usada. Baja 200 px para que el humo de colores no quede bajo los subtítulos; arriba se funde con su color. |
| 5 | `escena-05-cerebro.jpg` | Usada. Los impulsos recorren el nervio de la propia foto (medido sobre ella). |
| 7 | fosfenos (damero) | Pendiente: llegó solo como vista previa y no como archivo. Por ahora van mis fosfenos animados. |
| 8 | `escena-08-newton.jpg` | Usada la versión sin vela (la otra tenía la vela cortada en el borde). Arriba tiene una costura de relleno que queda tapada con un fundido. |
| 8 | cuaderno | Descartada: el punzón atraviesa la pupila y la voz dice «entre el ojo y el hueso». Además tenía letras falsas casi legibles. Se queda el cuaderno dibujado. |

Prompts usados (formato 9:16, modelo pro; terminan pidiendo «no text, no letters, no logos, no watermark» y la cuarta parte de arriba oscura y vacía):

| Escena | Prompt |
|---|---|
| 1 | Photorealistic extreme close-up of a young adult's closed eye being rubbed with an index fingertip, soft side lighting, real skin texture, very dark background. Above the eye, floating in the darkness, faint glowing swirls of colored light in magenta, cyan and yellow, like the patterns you see when you rub your eyes… |
| 5 | Side profile of a translucent human head facing left, glass-like skin, a softly glowing pink brain visible inside. A thin bright yellow nerve fiber runs from the eye backwards to the back of the brain, which glows warm yellow. Clean 3D medical illustration style… |
| 7 | Full-frame abstract image of phosphenes, the colored light patterns seen when pressing on closed eyes: a dark field with a slowly swirling checkerboard of faint colored squares arranged in concentric rings… |
| 8 | Oil painting portrait of Isaac Newton in the style of the 1689 Godfrey Kneller portrait… |

## Texto del post (2 líneas, sin hashtags, como prueba)

¿Por qué ves colores al frotarte los ojos? 👁️
Cuéntame: ¿qué ves tú, puntos, rayas o colores?

## Datos y fuentes

| Afirmación | Estado | Fuente |
|---|---|---|
| Ver luz sin que entre luz en el ojo se llama fosfeno; los más comunes son los de presión, al frotar o apretar los ojos cerrados | Verificado | Wikipedia, «Phosphene»: https://en.wikipedia.org/wiki/Phosphene |
| «Fosfeno» viene del griego phôs (luz) y phainein (mostrar) | Verificado | Wikipedia, «Phosphene» |
| Pasa igual a oscuras | Verificado: el estudio de Grüsser se hizo en total oscuridad | Grüsser et al. (1989): https://fis.uke.de/portal/en/publications/responses-of-retinal-ganglion-cells-to-eyeball-deformation-a-neurophysiological-basis-for-pressure-phosphenes(482ecb92-4ecf-41b3-bba3-db388b8573c2).html |
| Al apretar, el ojo se deforma y estira la retina, y sus neuronas (células ganglionares) se activan de forma parecida a como lo hacen con la luz | Verificado en gatos; que el estiramiento sea la causa es la hipótesis de los autores. El mecanismo molecular no está aclarado | Grüsser et al. (1989); Križaj (2016), Adv Exp Med Biol 854: https://pmc.ncbi.nlm.nih.gov/articles/PMC5111544/ |
| El cerebro lo interpreta como luz porque esas conexiones van «cableadas» a la vista (por eso no lo notas como tacto) | Verificado (explicación clásica de Morgagni y Helmholtz) | Križaj (2016) |
| Newton se metió un punzón romo («bodkin») entre el ojo y el hueso y vio círculos blancos, oscuros y de colores | Verificado. La fecha exacta se discute (hacia 1665-1666; una exposición de Cambridge dice hacia 1669); por eso no sale en el vídeo | Biblioteca de la Universidad de Cambridge: https://exhibitions.lib.cam.ac.uk/linesofthought/?p=140 |
| Al apretar un lado del ojo, el anillo de color aparece al lado contrario | Verificado (Wikipedia, citando a Newton) | Wikipedia, «Phosphene» |
| La barra «SEÑAL DE LA RETINA» y el ritmo de los disparos | Ilustrativos: no son medidas reales; por eso no llevan números | — |
