# Cardinal Datos

**Datos que no se traducen solos**

Recogemos estadísticas públicas sobre migración y diáspora que existen, pero
casi nadie puede leer. Las volvemos comprensibles, en español.

Sitio: https://cardinaldatos.org · Método y fuentes: https://cardinaldatos.org/metodo/

---

## Estructura

```
pipeline/     scripts que descargan y limpian los datos
data/         un subdirectorio por tema: crudo.json, limpio.json, metodo.md
data/fuentes.json   el registro de fuentes: qué usamos y qué queremos usar
sitio/        la web (Astro, desplegada en Cloudflare)
instagram/    genera las imágenes del feed a partir de los mismos datos
MAPA.md       índice de todos los archivos, regenerado solo en cada push
```

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

## Verificación de frescura

`pipeline/verificar.py` corre cada semana (y a mano cuando haga falta) y no se
limita a comprobar que cada fuente responde: comprueba que sus datos siguen
frescos. Responder no basta —una tabla puede seguir contestando meses después
de dejar de actualizarse—, así que cada sonda declara cuántos meses de
antigüedad tolera antes de dar aviso.

## Publicación

El sitio es estático y se despliega en Cloudflare con activos estáticos; el
contenido de `sitio/` es lo que se sube. Cada `push` a `main` que toque
`sitio/**` dispara el despliegue. Las dependencias están fijadas con lockfiles
y se instalan con `npm ci`, de modo que cada compilación es reproducible.

## Licencia

El código de este repositorio y el trabajo editorial de Cardinal Datos se
publican para su reuso con atribución. **Los datos de origen no son nuestros:**
pertenecen a los organismos que los publican y conservan cada uno su propia
licencia, indicada en `data/fuentes.json`. Consúltala antes de republicarlos.
