# ¿Cómo sabe tu móvil que lo has girado?

**Gancho (8 palabras):** ¿Cómo sabe tu móvil que lo has girado?
**Objeto / metáfora central:** el acelerómetro, que se transforma a lo largo del vídeo: móvil → chip de 2 mm → masa colgada de muelles → peines de silicio.
**Duración:** ~50 s · **Guion:** 153 palabras · **Voz:** Kokoro «santa» a ritmo natural · **Subtítulos:** arriba, 1-3 palabras a la vista (lo dicho en gris, la palabra clave en amarillo) · **Cámara:** siempre en movimiento, transiciones que atraviesan la imagen.
**Estructura (como el vídeo viral de referencia):** pregunta → mecanismo → datos en directo → consecuencia → giro («no sabe dónde estás tú») → ejemplo cotidiano (la cama) → cierre para compartir.

## Escenas

| # | Voz / texto en pantalla | Palabra clave | Plano visual | Etiquetas técnicas |
|---|---|---|---|---|
| 1 | ¿Cómo sabe tu móvil que lo has girado? | girado | Móvil con una foto de paisaje. En «girado» gira 90° y la foto se endereza un instante después. Flecha de giro. | — |
| 2 | Tiene una pieza que se mueve, aunque no lo notes. | pieza | Móvil en rayos X (placa, chips, batería). En «pieza» se ilumina un chip; en «mueve» el móvil vibra. | ACELERÓMETRO |
| 3 | Se esconde en un chip más pequeño que una lenteja. | lenteja | El chip a escala (1 mm = 110 px) junto a una lenteja. | 2 mm · ≈ 5 mm · LENTEJA |
| 4 | Por dentro hay una masa diminuta colgada de muelles. | muelles | Se levanta la tapa del chip: marco, anclajes, muelles en zigzag, masa perforada y peines. | MASA · MUELLES |
| 5 | La gravedad siempre tira de ella hacia abajo. | gravedad | Flecha «g» hacia abajo; la masa baja y los muelles se estiran. | g |
| 6 | Si giras el móvil, la masa se mueve menos que el grosor de un pelo. | pelo | El chip gira 60° y la masa se desplaza hacia el nuevo «abajo». Barra comparando un pelo con el desplazamiento. | PELO ≈ 70 µm · MOVIMIENTO < 1 µm |
| 7 | Pegados a ella hay peines de silicio, más finos que un pelo. | peines | Zoom a los dientes del peine (móviles y fijos), con la sección de un pelo a la misma escala. | PEINES DE SILICIO · 4 µm · PELO ≈ 70 µm |
| 8 | Cuando se mueve, cambia la distancia entre los dientes, y el chip lo mide. | distancia | Los dientes móviles oscilan; brilla el campo eléctrico donde se acercan; gráfica de señal. | DISTANCIA · SEÑAL |
| 9 | Con eso sabe, en cada eje, hacia dónde tira la gravedad. | eje | El móvil se balancea con sus ejes X, Y, Z dibujados y la flecha «g». | Panel en directo X/Y/Z en m/s² (±9,81) |
| 10 | Por eso sabe dónde está el suelo y gira la pantalla. | suelo | El móvil vuelve a vertical y la foto se endereza; flecha al suelo. | SUELO · panel X/Y/Z |
| 11 | La misma pieza cuenta tus pasos. | pasos | Huellas que aparecen al ritmo de los picos de la gráfica; contador de pasos. | ACELERÓMETRO · PASOS |
| 12 | Pero esa pieza no sabe dónde estás tú. | tú | El móvil sabe dónde está el suelo; aparece una persona con un «?». | SUELO ✓ |
| 13 | Cuando te tumbas de lado en la cama, cree que lo has girado, y gira la pantalla sin querer. | cama | Persona tumbada en la cama con el móvil; en «girado» la imagen gira sola. | SIN QUERER |
| 14 | Síguenos y mándaselo a ese amigo que siempre tiene la rotación bloqueada. | amigo | Pantalla de compartir: se elige a un amigo, aparece el icono de rotación bloqueada y «Enviado ✓». | — |

## Texto del post

¿Cómo sabe tu móvil que lo has girado? 📱

Dentro tiene una pieza que se mueve: una masa de silicio colgada de muelles, en un chip de 2 mm. La gravedad tira de ella y unos peines más finos que un pelo miden cuánto se desplaza en cada eje. Así sabe dónde está el suelo… pero no dónde estás tú. Por eso, en la cama, te gira la pantalla sin querer.

Mándaselo a ese amigo que siempre tiene la rotación bloqueada 🔒

#curiosidades #tecnologia #movil #ciencia #sabiasque

## Datos y fuentes

| Afirmación | Estado | Fuente |
|---|---|---|
| El acelerómetro va en un chip de 2 × 2 mm | Verificado | Hoja de datos Bosch BMA400 («footprint 2mm x 2mm»): https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bma400-ds000.pdf · ST LIS2DW12 (LGA-12, 2 mm): https://www.st.com/resource/en/datasheet/lis2dw12.pdf |
| Una lenteja mide ≈ 5 mm | Probable (4-8 mm según variedad) | Medida habitual; no es crítico: el chip es menor en cualquier caso |
| Dentro hay una masa colgada de muelles con dientes móviles entre electrodos fijos | Verificado | https://maketecheasier.com/how-phone-accelerometers-detect-orientation/ · https://pmc.ncbi.nlm.nih.gov/articles/PMC11434136/ |
| Los dientes miden ~4 µm de ancho y 1 µm de separación | Verificado (en un diseño publicado; varía según fabricante) | https://jksus.org/design-of-mems-capacitive-comb-accelerometer-with-perforated-proof-mass-for-seismic-applications/ |
| Un pelo humano mide 17-180 µm (~70 µm típico) | Verificado el rango; 70 µm es un valor típico | https://www.mos.org/video/microbe-vs-hair-see-size-difference |
| La masa se mueve menos que el grosor de un pelo (< 1 µm) | Verificado por deducción: no puede moverse más que la separación entre dientes (1 µm) | Misma fuente que los dientes |
| Mide el cambio de distancia entre dientes (capacidad) | Verificado | Fuentes de arriba |
| El mismo sensor gira la pantalla y cuenta los pasos | Verificado | https://www.lmlrepair.com/explain/what-is-an-accelerometer |
| Mide la aceleración en 3 ejes; en reposo marca la gravedad (≈ 9,81 m/s²) repartida entre ellos | Verificado | Hojas de datos de arriba («3-axis accelerometer») |
| Tumbado de lado, el móvil gira la pantalla aunque no quieras | Verificado: solo sabe hacia dónde tira la gravedad, no dónde están tus ojos (por eso existe el bloqueo de rotación; algunos Android usan además la cámara frontal para evitarlo) | Mismo principio de las fuentes de arriba |
