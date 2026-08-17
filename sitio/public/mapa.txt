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


**77 archivos indexados, 830224 bytes en total.**

**Huella del repositorio: `499645552befbca1`**


## Raíz

- [EDITORIAL.md](https://github.com/cardinaldatos/cardinal/blob/main/EDITORIAL.md) — 10119 B · `e6b3e01b`
- [LICENCIA.md](https://github.com/cardinaldatos/cardinal/blob/main/LICENCIA.md) — 3265 B · `98ca8a34`
- [LICENSE](https://github.com/cardinaldatos/cardinal/blob/main/LICENSE) — 1071 B · `e1eb27d6`
- [README.md](https://github.com/cardinaldatos/cardinal/blob/main/README.md) — 10742 B · `af1851c8`
- [requirements.txt](https://github.com/cardinaldatos/cardinal/blob/main/requirements.txt) — 1225 B · `dab11b7b`

## `.github/`

- [dependabot.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/dependabot.yml) — 1161 B · `c85acf93`

## `.github/workflows/`

- [acnur.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/acnur.yml) — 2257 B · `9bca0abb`
- [auditar.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/auditar.yml) — 914 B · `d2777324`
- [datos.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/datos.yml) — 711 B · `81fce6a0`
- [desplegar.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/desplegar.yml) — 3505 B · `370b58cd`
- [explorar-acnur.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/explorar-acnur.yml) — 1508 B · `f442a4bc`
- [explorar-eurostat.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/explorar-eurostat.yml) — 1211 B · `4307763c`
- [explorar-rpw.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/explorar-rpw.yml) — 1405 B · `7cf29f41`
- [generar-lockfiles.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/generar-lockfiles.yml) — 1810 B · `b72b52c7`
- [instagram.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/instagram.yml) — 1254 B · `bc4211cd`
- [mapa.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/mapa.yml) — 1691 B · `571b93a4`
- [sobrecualificacion.yml](https://github.com/cardinaldatos/cardinal/blob/main/.github/workflows/sobrecualificacion.yml) — 1466 B · `1581c3f5`

## `auditoria/`

- [auditar.mjs](https://github.com/cardinaldatos/cardinal/blob/main/auditoria/auditar.mjs) — 18160 B · `966a51ed`

## `data/`

- [fuentes.json](https://github.com/cardinaldatos/cardinal/blob/main/data/fuentes.json) — 13050 B · `f2f32246`

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

- [acnur.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/acnur.py) — 28967 B · `1e8222d2`
- [comun.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/comun.py) — 2844 B · `32449e7b`
- [explorar_acnur.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/explorar_acnur.py) — 32207 B · `8ec66e71`
- [explorar_comun.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/explorar_comun.py) — 11786 B · `5231a2e7`
- [explorar_eurostat.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/explorar_eurostat.py) — 6983 B · `b1addaa8`
- [explorar_rpw.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/explorar_rpw.py) — 3701 B · `d736855d`
- [mapa.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/mapa.py) — 8623 B · `15b7827a`
- [og.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/og.py) — 7466 B · `df95f895`
- [remesas.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/remesas.py) — 12369 B · `0cb4090d`
- [sobrecualificacion.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/sobrecualificacion.py) — 10439 B · `fbce478a`
- [verificar.py](https://github.com/cardinaldatos/cardinal/blob/main/pipeline/verificar.py) — 6281 B · `671ecae9`

## `sitio/`

- [.gitignore](https://github.com/cardinaldatos/cardinal/blob/main/sitio/.gitignore) — 51 B · `239f7736`
- [astro.config.mjs](https://github.com/cardinaldatos/cardinal/blob/main/sitio/astro.config.mjs) — 1924 B · `bb64dcd4`
- [package-lock.json](https://github.com/cardinaldatos/cardinal/blob/main/sitio/package-lock.json) — 170831 B · `fdb93016`
- [package.json](https://github.com/cardinaldatos/cardinal/blob/main/sitio/package.json) — 304 B · `b25f2971`
- [wrangler.jsonc](https://github.com/cardinaldatos/cardinal/blob/main/sitio/wrangler.jsonc) — 1602 B · `c5165c4d`

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
- [og.png](https://github.com/cardinaldatos/cardinal/blob/main/sitio/public/og.png) — 76353 B · `1e4fa6ff`

## `sitio/src/components/`

- [RemesasCostoLatam.jsx](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/components/RemesasCostoLatam.jsx) — 6982 B · `9cffe0d5`
- [TituloNoCruza.jsx](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/components/TituloNoCruza.jsx) — 12866 B · `e52ca96d`

## `sitio/src/datos/`

- [correcciones.js](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/datos/correcciones.js) — 7424 B · `d8315b96`
- [notas.js](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/datos/notas.js) — 3060 B · `311a0d62`
- [piezas.js](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/datos/piezas.js) — 2394 B · `40de157e`

## `sitio/src/layouts/`

- [Base.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/layouts/Base.astro) — 16840 B · `1affcb71`

## `sitio/src/pages/`

- [404.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/404.astro) — 703 B · `447837d4`
- [correcciones.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/correcciones.astro) — 10089 B · `cb2076c3`
- [ia.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/ia.astro) — 12660 B · `35749ba2`
- [index.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/index.astro) — 2915 B · `2eae7121`
- [licencia.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/licencia.astro) — 9549 B · `7b0d4a5f`
- [metodo.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/metodo.astro) — 16837 B · `2a8de10e`
- [remesas-costo-latam.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/remesas-costo-latam.astro) — 1504 B · `ac1b74da`
- [rss.xml.js](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/rss.xml.js) — 5155 B · `5bb4ffbe`
- [titulo-no-cruza.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/titulo-no-cruza.astro) — 2884 B · `cb97e016`

## `sitio/src/pages/notas/`

- [index.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/notas/index.astro) — 4283 B · `3a57b638`
- [misma-estadistica-dos-cifras.astro](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/pages/notas/misma-estadistica-dos-cifras.astro) — 6853 B · `5ff76493`

## `sitio/src/styles/`

- [sistema.css](https://github.com/cardinaldatos/cardinal/blob/main/sitio/src/styles/sistema.css) — 13868 B · `0093224e`
