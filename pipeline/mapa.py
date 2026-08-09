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
dicen nada. Sin ella, solo hay commit cuando de verdad se añadió, movió o
borró un archivo.
"""

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
            rutas.append(ruta_rel)

    return sorted(rutas, key=lambda r: (str(r.parent) != ".", str(r).lower()))


def agrupar(rutas):
    """Agrupa por carpeta, con la raíz primero."""
    grupos = {}
    for r in rutas:
        grupos.setdefault(str(r.parent), []).append(r)

    orden = sorted(grupos, key=lambda c: (c != ".", c.lower()))
    return [(c, grupos[c]) for c in orden]


def peso(ruta):
    """Tamaño legible. Ayuda a ver de un vistazo qué archivo es enorme."""
    n = (RAIZ / ruta).stat().st_size
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def construir():
    rutas = recolectar()
    base = f"https://github.com/{repositorio()}/blob/{rama()}"

    lineas = [CABECERA]
    lineas.append(f"**{len(rutas)} archivos indexados.**\n")

    for carpeta, archivos in agrupar(rutas):
        titulo = "Raíz" if carpeta == "." else f"`{carpeta}/`"
        lineas.append(f"\n## {titulo}\n")
        for r in archivos:
            lineas.append(f"- [{r.name}]({base}/{r.as_posix()}) — {peso(r)}")

    return "\n".join(lineas) + "\n"


def main():
    contenido = construir()
    destino = RAIZ / NOMBRE_SALIDA
    destino.write_text(contenido, encoding="utf-8")
    print(f"Escrito: {NOMBRE_SALIDA}")
    print(contenido.count("\n- ") , "enlaces")


if __name__ == "__main__":
    main()
