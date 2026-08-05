#!/usr/bin/env python3
"""
explorar_rpw.py — descubrimiento de las fuentes Remittance Prices Worldwide
en el API v2 del Banco Mundial.

No produce datos para publicar. Produce el mapa que necesita el script real:
qué fuentes RPW existen, qué series tienen, qué dimensiones exigen y hasta
qué trimestre llegan.

Equivalente al /metadata de SSB PxWebApi v2: primero se pregunta la forma,
después se pide el dato.

Uso:
    python explorar_rpw.py

Escribe todo lo que recibe en crudo/rpw_descubrimiento/ sin tocarlo.
Sin dependencias externas: solo stdlib.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://api.worldbank.org/v2"
SALIDA = Path("crudo/rpw_descubrimiento")

# El Banco Mundial devuelve 400 ante User-Agent no estandar.
# Esta cabecera debe coincidir con la que ya esta en comun.py — si alli
# la cambias, cambiala aqui tambien.
CABECERAS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

PAUSA = 0.5  # segundos entre peticiones, por cortesia


def pedir(ruta, **params):
    """GET contra el API v2, siempre en JSON. Devuelve el objeto parseado."""
    params.setdefault("format", "json")
    params.setdefault("per_page", 500)
    url = f"{BASE}/{ruta.lstrip('/')}?{urllib.parse.urlencode(params)}"
    peticion = urllib.request.Request(url, headers=CABECERAS)
    try:
        with urllib.request.urlopen(peticion, timeout=30) as r:
            cuerpo = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  ERROR {e.code} en {url}")
        return None
    except Exception as e:
        print(f"  ERROR {type(e).__name__} en {url}: {e}")
        return None
    time.sleep(PAUSA)
    return cuerpo


def guardar(nombre, objeto):
    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / f"{nombre}.json"
    destino.write_text(json.dumps(objeto, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  -> {destino}")


def cuerpo_util(respuesta):
    """El API v2 devuelve [metadatos, datos]. Devuelve la parte de datos."""
    if isinstance(respuesta, list) and len(respuesta) > 1:
        return respuesta[1]
    return respuesta


def paso_1_fuentes():
    """Localiza las fuentes RPW y devuelve sus IDs."""
    print("\n[1] Buscando fuentes que contengan 'remittance'...")
    respuesta = pedir("sources")
    if not respuesta:
        return []
    guardar("01_todas_las_fuentes", respuesta)

    fuentes = cuerpo_util(respuesta) or []
    encontradas = [
        f for f in fuentes
        if "remittance" in (f.get("name") or "").lower()
    ]
    for f in encontradas:
        print(f"  id={f['id']:>4}  {f['name']}  (actualizado: {f.get('lastupdated')})")
    if not encontradas:
        print("  Ninguna. Revisa 01_todas_las_fuentes.json a mano.")
    return [f["id"] for f in encontradas]


def paso_2_conceptos(id_fuente):
    """Dimensiones que exige la fuente. Esto es lo que rompe las consultas."""
    print(f"\n[2] Conceptos de la fuente {id_fuente}...")
    respuesta = pedir(f"sources/{id_fuente}/concepts")
    if not respuesta:
        return
    guardar(f"02_conceptos_fuente_{id_fuente}", respuesta)
    for c in cuerpo_util(respuesta) or []:
        print(f"  {c.get('id')}  {c.get('value')}")


def paso_3_series(id_fuente):
    """Series disponibles dentro de la fuente."""
    print(f"\n[3] Series de la fuente {id_fuente}...")
    respuesta = pedir("indicator", source=id_fuente)
    if not respuesta:
        return
    guardar(f"03_series_fuente_{id_fuente}", respuesta)
    series = cuerpo_util(respuesta) or []
    print(f"  {len(series)} series")
    for s in series[:25]:
        print(f"  {s.get('id')}  {s.get('name')}")
    if len(series) > 25:
        print(f"  ... y {len(series) - 25} mas (todas en el JSON)")


def paso_4_cobertura_temporal(id_fuente):
    """Hasta que periodo llega realmente la fuente.

    Este es el paso que resuelve el desfase Q1 2025 / Q3 2025. Lo que diga
    aqui el API es lo que puede sostener la pieza; el numero del informe PDF
    no cuenta como fuente reconstruible.
    """
    print(f"\n[4] Cobertura temporal declarada de la fuente {id_fuente}...")
    respuesta = pedir(f"sources/{id_fuente}")
    if not respuesta:
        return
    guardar(f"04_metadatos_fuente_{id_fuente}", respuesta)
    for f in cuerpo_util(respuesta) or []:
        print(f"  ultima actualizacion declarada: {f.get('lastupdated')}")


def main():
    print("Descubrimiento RPW — Banco Mundial API v2")
    print("=" * 50)

    ids = paso_1_fuentes()
    if not ids:
        print("\nSin fuentes RPW. Nada mas que hacer automaticamente.")
        return

    for id_fuente in ids:
        paso_2_conceptos(id_fuente)
        paso_3_series(id_fuente)
        paso_4_cobertura_temporal(id_fuente)

    print("\n" + "=" * 50)
    print("Listo. Todo el crudo esta en", SALIDA)
    print("\nSiguiente decision, con los JSON delante:")
    print("  a) que serie corresponde al costo total por corredor")
    print("  b) que dimensiones hay que fijar para pedir un corredor concreto")
    print("  c) hasta que trimestre llega — y si coincide con el prototipo")


if __name__ == "__main__":
    main()
