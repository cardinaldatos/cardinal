# Editorial

Decisiones sobre qué publica Cardinal Datos, con qué criterio y por qué.

El `README.md` explica cómo funciona el repositorio; este archivo explica
qué se publica y con qué reglas. Se escribe aquí lo que ya está decidido,
no lo que se está pensando: si una decisión cambia, se cambia el archivo.

---

## Qué es esto

Estadísticas públicas sobre migración y diáspora —venezolana y mundial—
que existen pero casi nadie puede leer, hechas comprensibles en español.

El trabajo es **análisis original de datos públicos**, no traducción ni
resumen de artículos ajenos. Esa distinción define el proyecto y aparece
otra vez más abajo, en la sección de notas.

## Los huecos son el hallazgo

Un país sin dato, una fuente que dejó de publicar, una serie que nadie
abrió: eso no es una limitación de la pieza, es parte de lo que la pieza
cuenta. Se declara, no se rellena ni se estima.

Dos ejemplos ya publicados:

- **Remesas:** Venezuela no tiene indicador en la serie del Banco Mundial;
  Argentina y Chile aparecen con valor nulo. La pieza lo publica como
  bloque propio.
- **Sobrecualificación:** 7 de los 27 países de la UE no publican valor
  para 2024, porque la muestra de la encuesta es demasiado pequeña. La
  pieza lo publica y explica por qué.

Venezuela merece mención aparte: el país lleva años sin reportar a varios
organismos multilaterales, así que su ausencia va a repetirse en casi
cualquier serie internacional. Esa ausencia sostenida es una serie en sí
misma y es material publicable, no un obstáculo. Por eso el INE de
Venezuela está en el registro de fuentes aunque apenas publique.

## Dos tipos de contenido

**Piezas.** Interactivas, con datos. Toda cifra rastreable hasta un
archivo de `data/` descargado por un script. Sin excepciones: si no hay
script, la pieza se publica declarada como incompleta o no se publica.

**Notas.** Análisis y explicación derivados de ese trabajo. No llevan
cifras que no vengan de una pieza propia o de un archivo público citado.
Siempre enlazan a la fuente primaria.

El lector tiene que saber cuál está leyendo. Son formatos distintos con
reglas distintas, y mezclarlos diluye lo que hace creíbles a las piezas.

### De qué van las notas

De **la fuente**, no de nosotros. «Qué mide realmente el indicador de
remesas del Banco Mundial» sirve a quien nunca ha oído hablar de Cardinal
y es lo que la gente busca; «cómo leer nuestros datos» no lo busca nadie.
Se explica el indicador, y la pieza propia aparece como ejemplo.

No hay calendario. Cada nota nace de una pieza: lo que hubo que entender
para hacerla —la trampa del promedio con pocos corredores, por qué una
serie es anual y no trimestral, qué significa un valor nulo frente a un
país ausente— es la nota. Una o dos por pieza, cuando salgan.

Casi todo el material ya está escrito en los `metodo.md` y en los
comentarios del pipeline.

### Lo que no se hace

**No se parafrasean ni se traducen artículos ajenos.** Tres razones: un
parafraseo cercano sigue siendo reproducir el trabajo de otro; los
buscadores tratan el resumen derivado como contenido de relleno y rinde
mal; y rompe la regla de oro, porque las cifras vendrían del PDF de otro
y no de `data/`.

Lo que sí se puede: usar un informe extranjero como **punto de partida**.
Se va al dato original, se baja con un script, se verifica, y se escribe
análisis propio enlazando al informe. El trabajo es propio y el enlace es
cortesía.

## Fuentes

El registro vive en `data/fuentes.json`. El criterio de entrada son dos
preguntas: ¿habla de personas migrantes o de su diáspora?, ¿está el dato
encerrado en un idioma que no es el español o disperso de forma que nadie
puede leerlo?

**La región no es criterio.** Las fuentes se organizan por el papel que
cumplen —global, regional, de destino, de origen—, no por geografía.
Noruega y Colombia entran por lo mismo: son países donde vive la diáspora.
Un registro que se leyera como «Europa más un poco de América Latina»
sería un error de encuadre, no de balance.

El registro se amplía, no se cierra. Ninguna superficie del sitio nombra
una lista cerrada de fuentes ni escribe a mano cuántas hay: el código
cuenta el registro. Que una fuente esté como *candidata* significa que
nadie ha escrito aún el script que la abre, y eso se publica.

Regla de sostenibilidad: **cada pieza nueva debería mover al menos una
fuente de candidata a en uso.** Si no, el registro se convierte en lista
de deseos.

## Crecimiento

Lo que se ha decidido, en orden de rendimiento esperado:

1. **Redistribución antes que audiencia propia.** Que un periodista pueda
   citar y republicar rinde más que ganar seguidores. Eso exige licencia
   clara, método público enlazado desde cada pieza, y datos descargables.
2. **Captura por canales que no dependen de algoritmo.** El feed RSS
   existe por eso. Se publica poco y despacio, y las redes castigan ese
   ritmo; el correo y los lectores de feeds no.
3. **El pipeline es contenido.** Las decisiones técnicas —una tabla que
   siguió respondiendo meses después de morir, por qué una franja de edad
   cambia la cifra— interesan al público de periodismo de datos, que es
   quien enlaza.
4. **Ancla noticiosa.** Publicar pegado a la actualización de un organismo
   rinde mucho más que publicar un martes cualquiera.

## Dinero

No es la etapa. Cuando lo sea, la vía no será un tarro de propinas: con
una audiencia pequeña recauda casi nada, y las plataformas del estilo
Ko-fi o Buy Me a Coffee dependen de procesadores estadounidenses que no
operan con residencia en Venezuela.

Lo que sí financia proyectos así son **becas y fondos de periodismo** de
datos y de migración, que además valoran justo lo que ya existe: pipeline
reproducible, método público, licencia clara.

Si algún día entra dinero, será por un host fiscal (Open Collective) o a
través de alguien del colectivo residente fuera. Eso no es un trámite: es
una decisión sobre a quién se suma al equipo, y madura despacio.

## Autoría y seguridad

El proyecto se publica sobre migración venezolana desde Venezuela. Quién
firma y quién no es una decisión editorial con consecuencias reales, no un
detalle administrativo.

Está pendiente y hay que cerrarlo **antes de publicar la primera pieza
construida sobre cifras oficiales venezolanas**. Una ausencia de firma
declarada —explicando que la hay y por qué— pesa mucho más que una
ausencia sin explicar.

## Confianza

Señales que un lector o un editor usan para decidir si citarnos, en orden
de cuánto pesan:

- Método y datos enlazados desde cada pieza, no escondidos en el
  repositorio.
- Página de correcciones: cómo avisar de un error y qué se hace al
  confirmarlo. La confianza no es no equivocarse, es tener el mecanismo.
- Licencia explícita, o nadie sabe si puede republicar.
- Fechas visibles de publicación y de última verificación.
- Previsualización correcta al compartir un enlace: sin ella, en WhatsApp
  —que en Venezuela es *el* canal— el enlace se lee como sospechoso.
