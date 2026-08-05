"""Parsers compartidos: JSON-stat 2.0 (Eurostat y SSB) y API del Banco Mundial."""

import json
from datetime import date
from itertools import product
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
CABECERAS = {
    "User-Agent": "Mozilla/5.0 (compatible; cardinal-datos/1.0; +https://cardinaldatos.workers.dev)",
    "Accept": "application/json",
}


def pedir(url, params=None, timeout=60):
    """GET con errores explícitos, incluido el cuerpo de la respuesta."""
    r = requests.get(url, params=params, headers=CABECERAS, timeout=timeout)
    if not r.ok:
        raise RuntimeError(
            f"HTTP {r.status_code} en {r.url}\nRespuesta: {r.text[:600]}"
        )
    return r.json()


def jsonstat_a_filas(js):
    """Convierte JSON-stat 2.0 en lista de diccionarios.

    Sirve igual para Eurostat y para SSB: ambas usan el mismo formato.
    """
    dims = js["id"]
    tam = js["size"]

    codigos_por_dim, etiquetas_por_dim = [], []
    for d in dims:
        cat = js["dimension"][d]["category"]
        indice = cat["index"]
        orden = sorted(indice, key=indice.get) if isinstance(indice, dict) else list(indice)
        codigos_por_dim.append(orden)
        etiquetas_por_dim.append(cat.get("label", {}))

    valores = js["value"]
    filas = []

    for pos, combo in enumerate(product(*[range(t) for t in tam])):
        v = valores.get(str(pos)) if isinstance(valores, dict) else valores[pos]
        if v is None:
            continue  # celda vacía: no la inventes

        fila = {"valor": v}
        for i, d in enumerate(dims):
            codigo = codigos_por_dim[i][combo[i]]
            fila[d] = codigo
            fila[d + "_etiqueta"] = etiquetas_por_dim[i].get(codigo, codigo)
        filas.append(fila)

    return filas


def guardar(slug, nombre, contenido):
    """Escribe en data/<slug>/<nombre>."""
    carpeta = RAIZ / "data" / slug
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / nombre
    if isinstance(contenido, str):
        ruta.write_text(contenido, encoding="utf-8")
    else:
        ruta.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  escrito: {ruta.relative_to(RAIZ)}")
    return ruta


def escribir_metodo(slug, fuente, url, definicion, limites):
    """El archivo que te salva cuando alguien cuestione una cifra."""
    texto = f"""# Método — {slug}

**Fuente:** {fuente}
**Consulta:** `{url}`
**Fecha de extracción:** {date.today().isoformat()}

## Definición
{definicion}

## Límites declarados
{limites}
"""
    return guardar(slug, "metodo.md", texto)
