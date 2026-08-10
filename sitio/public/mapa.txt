"""Genera MAPA.md: el índice de enlaces a todos los archivos del repositorio.

Existe por una razón concreta. Cuando le pides ayuda a un asistente que no
tiene acceso al repositorio, este trabaja sobre lo que le pegaste — y si el
repositorio cambió desde entonces, sus propuestas revierten trabajo sin que
nadie lo note. Un índice de enlaces siempre al día convierte eso en algo
comprobable: cada archivo se puede abrir y leer antes de reescribirlo.

Lo corre .github/workflows/mapa.yml en cada push a main. No hay que
ejecutarlo a mano, pero se puede:  cd pipeline && python mapa.py

No lleva fecha de generación a propósito. Con una fecha dentro, el archivo
cambiaría en cada ejecución y ensuciaría el historial con commits que no
dicen nada — y peor: ese commit dispararía otra vez el workflow, que
volvería a cambiar la fecha, en bucle. Sin ella, solo hay commit cuando de
verdad se añadió, movió o borró un archivo.

Pero el mapa sí necesita poder fecharse de algún modo, porque el problema
que resuelve es exactamente ese: saber si lo que estás leyendo es la
versión de ahora. La solución es fecharlo por CONTENIDO en vez de por
reloj. Cada archivo lleva su tamaño exacto en bytes y los ocho primeros
dígitos de su SHA-256, y la cabecera lleva una huella del árbol completo.
Todo eso es determinista: dos ejecuciones sobre el mismo árbol producen
un archivo idéntico, así que la propiedad de no ensuciar el historial se
mantiene intacta.

Por qué bytes exactos y no «11 KB». Porque el redondeo esconde justo lo
que importa. Un archivo cacheado por GitHub que difiera en 300 bytes se
declara «11 KB» igual que el bueno, y quien lo lea no se entera. Con el
byte exacto y la huella, cualquier discrepancia salta al primer cotejo.

SEGUNDA SALIDA: sitio/public/mapa.txt

GitHub sirve páginas de archivo desde una caché que puede tener días de
retraso, y no hay parámetro que la salte. El mismo mapa se escribe en
sitio/public/, así que se despliega con el sitio y queda accesible en
https://cardinaldatos.org/mapa.txt — otra infraestructura, otra caché, y
una que sí controlamos. Esa copia es la de referencia cuando la de GitHub
resulte sospechosa.
"""

import hashlib
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Carpetas que no se indexan: son dependencias, compilados o salidas
# generadas. Los enlaces a esas rutas no sirven de referencia y, en el caso
# de node_modules, serían decenas de miles.
CARPETAS_FUERA = {
    ".git",
    ".github/workflows/__pycache__",
    "node_modules",
    "dist",
    ".astro",
    ".wrangler",
    ".venv",
    "__pycache__",
    "salida",          # imágenes generadas de Instagram
}

ARCHIVOS_FUERA = {".DS_Store", ".gitkeep"}

# El propio mapa no se indexa a sí mismo.
NOMBRE_SALIDA = "MAPA.md"

# Copia servida por el sitio. Tampoco se indexa: su contenido es el propio
# mapa, así que indexarla haría que su tamaño y su huella dependieran de sí
# mismos. No hay valor que satisfaga esa ecuación.
COPIA_SITIO = Path("sitio") / "public" / "mapa.txt"

CABECERA = """# Mapa del repositorio

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

"""


def repositorio():
    """Devuelve 'usuario/repo'. En Actions viene dado; fuera, se asume."""
    return os.environ.get("GITHUB_REPOSITORY", "cardinaldatos/cardinal")


def rama():
    return os.environ.get("GITHUB_REF_NAME", "main")


def dentro_de_carpeta_excluida(ruta_rel):
    partes = set(ruta_rel.parts)
    return bool(partes & CARPETAS_FUERA)


def recolectar():
    """Todas las rutas relativas indexables, ordenadas."""
    rutas = []
    for actual, carpetas, archivos in os.walk(RAIZ):
        actual = Path(actual)

        # Poda: no descender en las carpetas excluidas.
        carpetas[:] = [c for c in carpetas if c not in CARPETAS_FUERA]

        for archivo in archivos:
            if archivo in ARCHIVOS_FUERA or archivo == NOMBRE_SALIDA:
                continue
            ruta_rel = (actual / archivo).relative_to(RAIZ)
            if dentro_de_carpeta_excluida(ruta_rel):
                continue
            if ruta_rel == COPIA_SITIO:
                continue
            rutas.append(ruta_rel)

    return sorted(rutas, key=lambda r: (str(r.parent) != ".", str(r).lower()))


def agrupar(rutas):
    """Agrupa por carpeta, con la raíz primero."""
    grupos = {}
    for r in rutas:
        grupos.setdefault(str(r.parent), []).append(r)

    orden = sorted(grupos, key=lambda c: (c != ".", c.lower()))
    return [(c, grupos[c]) for c in orden]


def medir(ruta):
    """Tamaño exacto en bytes y SHA-256 del archivo.

    Se lee por bloques porque sitio/package-lock.json pasa de 160 KB y no
    hay razón para cargarlo entero en memoria.
    """
    h = hashlib.sha256()
    tamano = 0
    with open(RAIZ / ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
            tamano += len(bloque)
    return tamano, h.hexdigest()


def huella_del_arbol(fichas):
    """Huella de todo el repositorio, a partir de rutas y huellas.

    Se alimenta de la ruta Y del contenido de cada archivo, en orden fijo,
    con separadores que no pueden aparecer en una ruta. Así, mover un
    archivo sin tocarlo también cambia la huella: la estructura es parte
    de lo que se está fechando.
    """
    h = hashlib.sha256()
    for ruta in sorted(fichas, key=lambda r: r.as_posix()):
        h.update(ruta.as_posix().encode("utf-8"))
        h.update(b"\x00")
        h.update(fichas[ruta][1].encode("ascii"))
        h.update(b"\x00")
    return h.hexdigest()[:16]


def construir():
    rutas = recolectar()
    fichas = {r: medir(r) for r in rutas}
    base = f"https://github.com/{repositorio()}/blob/{rama()}"

    total_bytes = sum(t for t, _ in fichas.values())

    lineas = [CABECERA]
    lineas.append(f"**{len(rutas)} archivos indexados, {total_bytes} bytes en total.**\n")
    lineas.append(f"**Huella del repositorio: `{huella_del_arbol(fichas)}`**\n")

    for carpeta, archivos in agrupar(rutas):
        titulo = "Raíz" if carpeta == "." else f"`{carpeta}/`"
        lineas.append(f"\n## {titulo}\n")
        for r in archivos:
            tamano, digest = fichas[r]
            lineas.append(
                f"- [{r.name}]({base}/{r.as_posix()}) — {tamano} B · `{digest[:8]}`"
            )

    return "\n".join(lineas) + "\n"


def main():
    contenido = construir()

    destino = RAIZ / NOMBRE_SALIDA
    destino.write_text(contenido, encoding="utf-8")
    print(f"Escrito: {NOMBRE_SALIDA}")

    # La copia del sitio solo se escribe si la carpeta existe. Si algún día
    # sitio/public/ se mueve, esto avisa en el registro del workflow en vez
    # de reventar la ejecución entera.
    copia = RAIZ / COPIA_SITIO
    if copia.parent.is_dir():
        copia.write_text(contenido, encoding="utf-8")
        print(f"Escrito: {COPIA_SITIO.as_posix()}")
    else:
        print(f"AVISO: no existe {COPIA_SITIO.parent.as_posix()}, no se escribió la copia del sitio")

    print(contenido.count("\n- "), "enlaces")


if __name__ == "__main__":
    main()
