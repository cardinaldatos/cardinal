# Cardinal Datos

**Datos que no se traducen solos**

Recogemos estadísticas públicas sobre migración y diáspora que existen, pero
casi nadie puede leer. Las volvemos comprensibles, en español.

Sitio: https://cardinaldatos.org · Método y fuentes: https://cardinaldatos.org/metodo/

---

## Estructura

```
pipeline/     scripts que descargan y limpian los datos
data/         salida del pipeline: un subdirectorio por tema con
              crudo.json, limpio.json y metodo.md
data/fuentes.json   el registro de fuentes: qué usamos y qué queremos usar
sitio/        la web (Astro, desplegada en Cloudflare)
sitio/src/datos/    lo que se mantiene a mano: el registro de piezas y el
                    de correcciones
instagram/    genera las imágenes del feed a partir de los mismos datos
auditoria/    comprueba que todo lo anterior siga cuadrando
MAPA.md       índice de todos los archivos, regenerado solo en cada push
```

`data/` y `sitio/src/datos/` se parecen y no son lo mismo. `data/` lo escriben
los scripts y no se edita a mano; `sitio/src/datos/` es al revés. Un archivo
escrito a mano no va en `data/`, aunque compile igual.

## Regla de oro

Toda cifra publicada tiene que rastrearse hasta un archivo de `data/`
descargado por un script. Si la copiaste de un PDF, no entra.

Los nombres de país se traducen al español **en el pipeline**, no en cada
superficie. El nombre original de la fuente se conserva en `limpio.json`
(campo `pais_fuente`) y en `crudo.json` sin tocar. Así la web, las imágenes
de Instagram y cualquier otra superficie leen el mismo `limpio.json`: un solo
origen, sin diccionarios de traducción repetidos que se desincronizan.

## Un dato, tres superficies

El mismo `data/<tema>/limpio.json` alimenta la web, las imágenes de Instagram
y el método público. Si dos superficies mostraran cifras distintas, sería un
fallo, no un matiz. Los huecos —países sin dato, series que faltan— no se
rellenan ni se estiman: se conservan y se declaran, porque la ausencia es
parte del hallazgo.

Los huecos tampoco son todos iguales. Que un organismo no publique una serie
para un país y que la publique sin obtener valor son dos cosas distintas, y
solo la primera dice algo sobre qué se decide medir. Donde la fuente permite
distinguirlas, `limpio.json` lo hace.

## Inteligencia artificial

Este proyecto se construye con asistencia de inteligencia artificial: el
código del pipeline, la exploración de las APIs que nadie ha abierto todavía,
la lectura de documentación en inglés y en noruego, la auditoría del propio
trabajo y la redacción de los textos. Se declara en una página pública,
https://cardinaldatos.org/ia/, y en el pie de cada página del sitio.

**Ninguna cifra publicada la escribe un modelo.** Lo garantiza la regla de oro
de más arriba, y no como promesa de buena conducta: es una restricción del
método que `auditoria/auditar.mjs` comprueba en cada push, incluidos los
números escritos con letra. Tampoco se le pide a un modelo que rellene un
hueco con una estimación —los huecos son el hallazgo—, ni que invente fuentes
o citas, ni que genere imágenes de personas.

Las herramientas concretas no se nombran, a propósito. Cambian de nombre y de
versión cada pocos meses, así que una lista de marcas envejecería igual que
una cifra escrita a mano, y nombrarlas se lee como respaldo comercial. Lo que
se declara son las tareas y los límites.

Aprender a trabajar con APIs públicas, análisis de datos y auditoría de datos
con esta clase de herramientas fue parte del origen del proyecto y sigue ahí,
pero en segundo plano: ninguna decisión editorial se toma para que el
experimento quede mejor. Lo que dejó sí es reutilizable, y está aquí entero.

Lo que hace comprobable todo lo anterior no es esta declaración: es que el
código, los datos y el método estén abiertos y sean reproducibles. Una
afirmación sobre cómo se hizo algo vale lo que valga la posibilidad de
revisarla. El razonamiento completo está en `EDITORIAL.md`.

## Puesta en marcha

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cd pipeline
python verificar.py              # sondea las fuentes del registro
```

## Fuentes

No hay una lista de fuentes en este archivo, a propósito. Vive en
[`data/fuentes.json`](data/fuentes.json), que es lo que sondea el script de
verificación y lo que publica la [página de método](https://cardinaldatos.org/metodo/).
Una sola lista, varios consumidores; ningún número de fuentes escrito a mano
en ninguna parte.

El registro no se organiza por región, sino por el papel que cumple cada
fuente:

- **Globales** — comparan todos los países con la misma vara (Banco Mundial, ACNUR, OIM).
- **Regionales** — comparan dentro de un bloque, entre pares (Eurostat, CEPAL, R4V).
- **De destino** — registros administrativos del país que recibe, que suelen decir lo que ninguna serie internacional recoge y casi nunca están en español (SSB, IMDi, NAV, Datos Abiertos Colombia, INE España).
- **De origen** — lo que el país emisor publica sobre su propia gente fuera (INE Venezuela).

El criterio de entrada no es dónde está el país. Son dos preguntas: ¿habla de
personas migrantes o de su diáspora?, ¿está el dato encerrado en un idioma que
no es el español o disperso de forma que nadie puede leerlo? Si las dos son
sí, entra.

Cada fuente declara además su estado: **en uso** (ya sostiene una pieza),
**sondeada** (responde y la entendemos, sin pieza todavía) o **candidata**
(nos interesa; falta el script que descubre su forma). El registro se amplía,
no se cierra: que una fuente no esté todavía solo significa que nadie ha
escrito aún el script que la abre.

### Para proponer una fuente

Abre un issue, o añade directamente un objeto a `data/fuentes.json` con estado
`candidata` y una nota de por qué te interesa. No hace falta que funcione:
proponerla ya es trabajo útil. El paso siguiente es un script de exploración
—como `pipeline/explorar_rpw.py`— que averigüe qué series tiene, qué
dimensiones exige y hasta qué periodo llega; solo después se le escribe una
sonda y se construye una pieza encima.

Preferimos fuentes sin clave de acceso, con licencia de reuso explícita y con
cobertura de más de un país. Las que exigen registro o publican en un solo
idioma no quedan excluidas —son, de hecho, buena parte del sentido del
proyecto—, pero cuestan más de mantener y hay que decirlo en su nota.

## Correcciones

Cuando una cifra publicada resulta estar mal, o cuando el organismo revisa su
propio dato después de que lo hayamos copiado, queda constancia pública en
https://cardinaldatos.org/correcciones/ — con lo que decía antes, lo que dice
ahora y de dónde salió el error.

El registro vive en `sitio/src/datos/correcciones.js` y **solo crece**. No se
edita una entrada para suavizarla ni se borra una para que la lista se vea
limpia. El historial de este repositorio deja rastro de cualquier cambio, así
que reescribir ahí no escondería nada: solo costaría credibilidad.

Corregir una cifra casi nunca significa editar una página. Como ninguna cifra
está escrita en el HTML, el arreglo es en el script que la produce, y la
página se corrige sola en la siguiente compilación.

Si ves un error: https://cardinaldatos.org/correcciones/ explica cómo avisar.

## Comprobaciones automáticas

Dos, y las dos corren solas cada semana además de a demanda.

**Frescura de las fuentes.** `pipeline/verificar.py` no se limita a comprobar
que cada fuente responde: comprueba que sus datos siguen frescos. Responder no
basta —una tabla puede seguir contestando meses después de dejar de
actualizarse—, así que cada sonda declara cuántos meses de antigüedad tolera
antes de dar aviso.

**Coherencia del repositorio.** `auditoria/auditar.mjs` comprueba lo que a un
ojo humano se le pasa: que cada pieza tenga su página y sus archivos de datos,
que ninguna carpeta de `data/` quede huérfana, que las fuentes marcadas «en
uso» sostengan de verdad una pieza publicada, que los enlaces internos lleven a
algún sitio, que las cifras derivadas cuadren con las de origen, y que no se
haya colado un número escrito a mano en el texto de una pieza —con letra o con
dígito, porque el fallo real que lo motivó fue una palabra, no un número.
Corre sin dependencias: `node auditoria/auditar.mjs`.

La segunda existe porque la primera no bastaba. Una fuente puede seguir
respondiendo perfectamente mientras la pieza que la usa lleva un año mostrando
cifras que el organismo ya revisó.

## Índice del repositorio

`MAPA.md` lista todos los archivos con su enlace, su tamaño exacto en bytes y
la huella de su contenido. Lo genera `pipeline/mapa.py` en cada push y no se
edita a mano.

Sirve para trabajar sobre este repositorio sin abrirlo entero, y sobre todo
para saber si lo que estás leyendo es la versión de ahora: si el tamaño que
declara GitHub no coincide al byte con el del mapa, estás ante una copia
cacheada. La misma copia se publica en https://cardinaldatos.org/mapa.txt,
servida desde otra infraestructura, para cuando la de GitHub resulte
sospechosa.

## Publicación

El sitio es estático y se despliega en Cloudflare con activos estáticos; el
contenido de `sitio/` es lo que se sube. Cada `push` a `main` que toque
`sitio/**` dispara el despliegue. Las dependencias están fijadas con lockfiles
y se instalan con `npm ci`, de modo que cada compilación es reproducible.

## Autoría

Cardinal Datos lo hace Mafer Córdova, venezolana. Estudié economía en
Venezuela y trabajo con datos administrativos.

No vengo del periodismo, y pesa poco acá: ninguna cifra de este sitio se
sostiene en quién firma. Cada una viene de un archivo que descargó un script
publicado en este repositorio, y una comprobación automática rechaza
cualquier número escrito a mano.

Soy también el titular del copyright que declara [`LICENSE`](LICENSE) y quien
asume la responsabilidad editorial de lo publicado. El razonamiento de por
qué se firma con nombre propio, y por qué no se publica ninguna ubicación,
está en `EDITORIAL.md`.

Los avisos de corrección se reciben en correcciones@cardinaldatos.org y los
respondo yo.

## Licencia

El código de este repositorio se publica bajo licencia MIT: ver
[`LICENSE`](LICENSE), y [`LICENCIA.md`](LICENCIA.md) para la explicación en
español de qué puedes hacer con esto. También está publicada en
https://cardinaldatos.org/licencia/.

**Los datos de origen no son nuestros:** pertenecen a los organismos que los
publican y conservan cada uno su propia licencia, indicada en
`data/fuentes.json`. Consúltala antes de republicarlos.
