# Mapa del repositorio

Índice de todos los archivos del proyecto, con enlace directo a cada uno.
Lo genera `pipeline/mapa.py` en cada push a `main`: no se edita a mano.

## Para quien trabaje con un asistente sobre este repositorio

Un asistente no ve el repositorio por defecto. Las páginas de carpeta y de
historial de GitHub bloquean el acceso automatizado; las páginas de archivo
individual, no.

**Regla:** antes de reescribir cualquier archivo existente, hay que abrir su
enlace y leer la versión que está en `main`. Nunca partir de una copia
pegada en una conversación anterior — el repositorio cambia y esa copia
envejece sin avisar.

**Cómo comprobar que lo que leíste es la versión de ahora.** Cada archivo
lleva su tamaño exacto en bytes y los ocho primeros dígitos de su SHA-256.
GitHub declara en la cabecera de cada archivo su tamaño: si no coincide con
el que dice aquí al byte, lo que estás leyendo es una copia cacheada y no
sirve. Pídele a la persona que lo pegue.

**Y cómo comprobar que este mapa es el de ahora.** GitHub también cachea
esta página. La misma copia se publica en https://cardinaldatos.org/mapa.txt
desde otra infraestructura: si las dos huellas de repositorio no coinciden,
la buena es la del sitio.

Este archivo no lleva fecha ni número de commit. Los llevaría a costa de
cambiar en cada ejecución, y eso llenaría el historial de commits vacíos.
La huella cumple la misma función sin ese precio: depende solo del
contenido del árbol, así que dos huellas distintas son dos árboles
distintos.


**64 archivos indexados, 589660 bytes en total.**

**Huella del repositorio: `70f4d7147bb8d91e`**


## Raíz

- [EDITORIAL.md](https://github.com/cardinaldatos/cardinal/blob/main/EDITORIAL.md) — 7112 B · `97b52c5b`
- [LICENCIA.md](https://github.com/cardinaldatos/cardinal/blob/main/LICENCIA.md) — 1681 B · `d5db826d`
- [LICENSE](https://github.com/cardinaldatos/cardinal/blob/main/LICENSE) — 1071 B · `e1eb27d6`
- [README.md](https://github.com/cardinaldatos/cardinal/blob/main/README.md) — 5161 B · `cc19219a`
- [requirements.txt](https://github.com/cardinaldatos/cardinal/blob/main/requirements.txt) — 647 B · `4a8ba3b1`

## `.github/`

- [dependabot.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/dependabot.yml) — 1161 B · `c85acf93`

## `.github/workflows/`

- [datos.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/datos.yml) — 711 B · `81fce6a0`
- [desplegar.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/desplegar.yml) — 1629 B · `fcb2d13f`
- [explorar-eurostat.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/explorar-eurostat.yml) — 1211 B · `4307763c`
- [explorar-rpw.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/explorar-rpw.yml) — 1405 B · `7cf29f41`
- [generar-lockfiles.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/generar-lockfiles.yml) — 1810 B · `b72b52c7`
- [instagram.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/instagram.yml) — 1254 B · `bc4211cd`
- [mapa.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/mapa.yml) — 1278 B · `37d15a43`
- [sobrecualificacion.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/sobrecualificacion.yml) — 1466 B · `1581c3f5`

## `data/`

- [fuentes.json](https://github.com/cardinaldatos/cardinal/blob/main/data/fuentes.json) — 11357 B · `517f3e2f`

## `data/remesas-costo-latam/`

- [crudo.json](https://github.com/cardinaldatos/cardinal/blob/main/data/remesas-costo-latam/crudo.json) — 28174 B · `966aacb4`
- [limpio.json](https://github.com/cardinaldatos/cardinal/blob/main/data/remesas-costo-latam/limpio.json) — 1974 B · `fd324ade`
- [metodo.md](https://github.com/cardinaldatos/cardinal/blob/main/data/remesas-costo-latam/metodo.md) — 2241 B · `9284fa0b`

## `data/sobrecualificacion-ue/`

- [crudo.json](https://github.com/cardinaldatos/cardinal/blob/main/data/sobrecualificacion-ue/crudo.json) — 20451 B · `a0c61d4d`
- [limpio.json](https://github.com/cardinaldatos/cardinal/blob/main/data/sobrecualificacion-ue/limpio.json) — 4672 B · `9dff95fb`
- [metodo.md](https://github.com/cardinaldatos/cardinal/blob/main/data/sobrecualificacion-ue/metodo.md) — 2387 B · `231b52de`

## `instagram/`

- [comun.mjs](https://github.com/cardinaldatos/cardinal/blob/main/instagram/comun.mjs) — 3118 B · `95fe0b3a`
- [generar-carrusel.mjs](https://github.com/cardinaldatos/cardinal/blob/main/instagram/generar-carrusel.mjs) — 10682 B · `0940b19c`
- [generar-dominio.mjs](https://github.com/cardinaldatos/cardinal/blob/main/instagram/generar-dominio.mjs) — 4602 B · `23da1a6f`
- [generar-presentacion.mjs](https://github.com/cardinaldatos/cardinal/blob/main/instagram/generar-presentacion.mjs) — 4124 B · `b021af18`
- [generar.mjs](https://github.com/cardinaldatos/cardinal/blob/main/instagram/generar.mjs) — 5162 B · `96a33264`
- [package-lock.json](https://github.com/cardinaldatos/cardinal/blob/main/instagram/package-lock.json) — 1638 B · `5adb1fe1`
- [package.json](https://github.com/cardinaldatos/cardinal/blob/main/instagram/package.json) — 181 B · `4319fcbe`

## `pipeline/`

- [comun.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/comun.py) — 2844 B · `32449e7b`
- [explorar_eurostat.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/explorar_eurostat.py) — 6983 B · `b1addaa8`
- [explorar_rpw.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/explorar_rpw.py) — 3701 B · `d736855d`
- [mapa.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/mapa.py) — 8623 B · `15b7827a`
- [remesas.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/remesas.py) — 7749 B · `b16d28e8`
- [sobrecualificacion.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/sobrecualificacion.py) — 10439 B · `fbce478a`
- [verificar.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/verificar.py) — 5321 B · `75e99f59`

## `sitio/`

- [.gitignore](https://github.com/cardinaldatos/cardinal/blob/main/sitio/.gitignore) — 51 B · `239f7736`
- [astro.config.mjs](https://github.com/cardinaldatos/cardinal/blob/main/sitio/astro.config.mjs) — 1924 B · `bb64dcd4`
- [package-lock.json](https://github.com/cardinaldatos/cardinal/blob/main/sitio/package-lock.json) — 170831 B · `fdb93016`
- [package.json](https://github.com/cardinaldatos/cardinal/blob/main/sitio/package.json) — 304 B · `b25f2971`
- [wrangler.jsonc](https://github.com/cardinaldatos/cardinal/blob/main/sitio/wrangler.jsonc) — 712 B · `27f8df91`

## `sitio/public/`

- [_headers](https://github.com/cardinaldatos/cardinal/blob/main/sitio/public/_headers) — 494 B · `905caf01`
- [archivo-v25-latin-600.woff2](https://github.com/cardinaldatos/cardinal/blob/main/sitio/public/archivo-v25-latin-600.woff2) — 13820 B · `d9e8c29f`
- [archivo-v25-latin-700.woff2](https://github.com/cardinaldatos/cardinal/blob/main/sitio/public/archivo-v25-latin-700.woff2) — 14508 B · `abada6cd`
- [archivo-v25-latin-regular.woff2](https://github.com/cardinaldatos/cardinal/blob/main/sitio/public/archivo-v25-latin-regular.woff2) — 14700 B · `07f91601`
- [favicon.svg](https://github.com/cardinaldatos/cardinal/blob/main/sitio/public/favicon.svg) — 554 B · `a443f6d4`
- [ibm-plex-mono-v20-latin-500.woff2](https://github.com/cardinaldatos/cardinal/blob/main/sitio/public/ibm-plex-mono-v20-latin-500.woff2) — 14888 B · `01d28544`
- [ibm-plex-mono-v20-latin-regular.woff2](https://github.com/cardinaldatos/cardinal/blob/main/sitio/public/ibm-plex-mono-v20-latin-regular.woff2) — 14708 B · `08949f72`
- [ibm-plex-sans-v23-latin-500.woff2](https://github.com/cardinaldatos/cardinal/blob/main/sitio/public/ibm-plex-sans-v23-latin-500.woff2) — 24184 B · `0717336f`
- [ibm-plex-sans-v23-latin-600.woff2](https://github.com/cardinaldatos/cardinal/blob/main/sitio/public/ibm-plex-sans-v23-latin-600.woff2) — 24252 B · `8960851d`
- [ibm-plex-sans-v23-latin-regular.woff2](https://github.com/cardinaldatos/cardinal/blob/main/sitio/public/ibm-plex-sans-v23-latin-regular.woff2) — 22588 B · `3b646991`

## `sitio/src/components/`

- [RemesasCostoLatam.jsx](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/components/RemesasCostoLatam.jsx) — 6982 B · `9cffe0d5`
- [TituloNoCruza.jsx](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/components/TituloNoCruza.jsx) — 11566 B · `8e85acfd`

## `sitio/src/datos/`

- [correcciones.js](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/datos/correcciones.js) — 5815 B · `b95bec47`
- [piezas.js](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/datos/piezas.js) — 2394 B · `40de157e`

## `sitio/src/layouts/`

- [Base.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/layouts/Base.astro) — 10079 B · `15457e14`

## `sitio/src/pages/`

- [404.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/404.astro) — 703 B · `447837d4`
- [correcciones.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/correcciones.astro) — 10089 B · `cb2076c3`
- [index.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/index.astro) — 2915 B · `2eae7121`
- [licencia.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/licencia.astro) — 9549 B · `7b0d4a5f`
- [metodo.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/metodo.astro) — 15104 B · `a00c0e1f`
- [remesas-costo-latam.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/remesas-costo-latam.astro) — 1504 B · `ac1b74da`
- [rss.xml.js](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/rss.xml.js) — 3670 B · `563d5b71`
- [titulo-no-cruza.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/titulo-no-cruza.astro) — 2884 B · `cb97e016`

## `sitio/src/styles/`

- [sistema.css](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/styles/sistema.css) — 13868 B · `0093224e`
