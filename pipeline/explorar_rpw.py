"""Descubre qué hay dentro de las fuentes Remittance Prices Worldwide.

No produce datos para publicar. Produce el mapa que necesita el script real
de la pieza «El recibo invisible»: qué fuentes RPW existen en el API, qué
series tienen, qué dimensiones exigen y hasta qué periodo llegan.

Es el equivalente al /metadata de SSB: primero se pregunta la forma, después
se pide el dato.

Córrelo:  cd pipeline && python explorar_rpw.py
"""

from comun import pedir, guardar

BASE = "https://api.worldbank.org/v2"
SLUG = "rpw-descubrimiento"


def cuerpo(js):
    """El API v2 devuelve [metadatos, datos]. Devuelve la parte de datos."""
    if isinstance(js, list) and len(js) > 1 and js[1]:
        return js[1]
    return []


def intentar(etiqueta, url, params=None):
    """Pide y guarda, sin reventar el script si una ruta no existe.

    Varias de estas rutas son hipótesis. Un fallo aquí es información, no
    un error: significa que esa vía no sirve y hay que probar otra.
    """
    params = {"format": "json", "per_page": 500, **(params or {})}
    try:
        js = pedir(url, params)
    except Exception as e:
        print(f"FALLO  {etiqueta}: {type(e).__name__} — {e}")
        return None
    guardar(SLUG, f"{etiqueta}.json", js)
    return js


def paso_1_fuentes():
    """Localiza las fuentes RPW dentro del catálogo de fuentes."""
    print("\n[1] Fuentes que mencionan remesas o remittance")
    js = intentar("01_fuentes", f"{BASE}/sources")
    if not js:
        return []

    encontradas = []
    for f in cuerpo(js):
        nombre = (f.get("name") or "").lower()
        if "remittance" in nombre or "remesa" in nombre:
            encontradas.append(f)
            print(f"  id={f.get('id'):>4}  {f.get('name')}")
            print(f"           última actualización declarada: {f.get('lastupdated')}")

    if not encontradas:
        print("  Ninguna coincidencia. Revisa 01_fuentes.json a mano:")
        print("  puede que el nombre esté en otro idioma o abreviado.")
    return [f["id"] for f in encontradas]


def paso_2_conceptos(id_fuente):
    """Dimensiones que exige la fuente. Esto es lo que rompe las consultas."""
    print(f"\n[2] Dimensiones de la fuente {id_fuente}")
    js = intentar(f"02_dimensiones_{id_fuente}", f"{BASE}/sources/{id_fuente}/concepts")
    if not js:
        return
    for c in cuerpo(js):
        print(f"  {c.get('id')}  {c.get('value')}")


def paso_3_series(id_fuente):
    """Series disponibles dentro de la fuente."""
    print(f"\n[3] Series de la fuente {id_fuente}")
    js = intentar(f"03_series_{id_fuente}", f"{BASE}/indicator", {"source": id_fuente})
    if not js:
        return
    series = cuerpo(js)
    print(f"  {len(series)} series en total")
    for s in series[:30]:
        print(f"  {s.get('id')}  {s.get('name')}")
    if len(series) > 30:
        print(f"  ... y {len(series) - 30} más (todas en el JSON guardado)")


def main():
    print("Descubrimiento RPW — Banco Mundial API v2")
    print("=" * 55)

    ids = paso_1_fuentes()
    if not ids:
        print("\nSin fuentes RPW localizadas automáticamente.")
        print("El JSON de fuentes está guardado; hay que mirarlo a mano.")
        return

    for id_fuente in ids:
        paso_2_conceptos(id_fuente)
        paso_3_series(id_fuente)

    print("\n" + "=" * 55)
    print("Listo. Los JSON están en data/" + SLUG + "/")
    print("\nCon eso decidimos tres cosas:")
    print("  a) qué serie es el costo total por corredor")
    print("  b) qué dimensiones hay que fijar para pedir Noruega→Venezuela")
    print("  c) hasta qué trimestre llega, y si cuadra con el prototipo")


if __name__ == "__main__":
    main()
