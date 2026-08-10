"""Descubre la forma de lfsa_eoqgan — sobrecualificación por ciudadanía.

No produce datos para publicar. Produce el mapa que necesita el script real
de la pieza «El título no cruza», cuyas cifras hoy están escritas a mano en
el componente de React y por eso la pieza está declarada en construcción.

El artículo de Eurostat del que salieron esas cifras dice 45,9 % → 39,6 %
para ciudadanos de fuera de la UE entre 2014 y 2024. Lo que NO dice en el
titular es sobre qué franja de edad está calculado: el conjunto tiene siete
(15-64, 20-64, 25-64, 20-34, 25-34, 35-64, 15 y más). Elegir la equivocada
daría cifras parecidas pero distintas, y nadie lo notaría hasta que alguien
cuestionara la pieza.

Por eso este script no asume: pide todas las combinaciones y busca cuál
reproduce las cifras publicadas. Lo que encuentre queda escrito en el JSON
guardado, y de ahí sale el parámetro del script definitivo.

Es el equivalente a explorar_rpw.py: primero se pregunta la forma, después
se pide el dato.

Córrelo:  cd pipeline && python explorar_eurostat.py
"""

from comun import pedir, guardar, jsonstat_a_filas

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
CONJUNTO = "lfsa_eoqgan"
SLUG = "eurostat-descubrimiento"

# Las cifras que hoy afirma la pieza, tal como están escritas a mano en
# sitio/src/components/TituloNoCruza.jsx. Son la referencia contra la que
# se comprueba: si ninguna combinación las reproduce, la pieza está mal y
# hay que corregirla, no forzar el script hasta que cuadre.
AFIRMADO = {
    ("NEU27_2020_FOR", "2014"): 45.9,
    ("NEU27_2020_FOR", "2024"): 39.6,
    ("EU27_2020_FOR", "2014"): 34.0,
    ("EU27_2020_FOR", "2024"): 30.3,
    # Nacionales: la pieza dice 21 en ambos años, redondeado. Eurostat lo
    # describe "estable entre 20 % y 21 %", así que aquí se admite margen.
    ("NAT", "2014"): 21.0,
    ("NAT", "2024"): 21.0,
}

TOLERANCIA = 0.05   # coincidencia exacta al primer decimal
TOLERANCIA_NAT = 1.0  # los nacionales van redondeados en la pieza


def paso_1_agregado_ue():
    """Todas las edades y ciudadanías para el agregado UE, 2014 y 2024."""
    print("\n[1] Agregado UE — todas las edades y ciudadanías")

    params = {
        "format": "JSON",
        "lang": "EN",
        "geo": "EU27_2020",
        "sex": "T",
        "unit": "PC",
        "time": ["2014", "2024"],
    }

    js = pedir(f"{BASE}/{CONJUNTO}", params)
    guardar(SLUG, "01_agregado_ue.json", js)

    filas = jsonstat_a_filas(js)
    print(f"  {len(filas)} celdas con valor")

    dims = js.get("id", [])
    print(f"  dimensiones: {', '.join(dims)}")
    for d in dims:
        cat = js["dimension"][d]["category"]
        codigos = list(cat.get("index", {}))
        if len(codigos) <= 12:
            print(f"    {d}: {', '.join(codigos)}")
        else:
            print(f"    {d}: {len(codigos)} categorías")

    return filas


def paso_2_localizar_edad(filas):
    """Busca qué franja de edad reproduce las cifras que afirma la pieza."""
    print("\n[2] Qué franja de edad reproduce las cifras publicadas")

    if not filas:
        print("  Sin filas: no se puede comprobar.")
        return None

    # Agrupa por edad: {edad: {(ciudadania, anio): valor}}
    por_edad = {}
    for f in filas:
        edad = f.get("age")
        ciud = f.get("citizen")
        anio = f.get("time")
        if edad is None or ciud is None or anio is None:
            continue
        por_edad.setdefault(edad, {})[(ciud, anio)] = f["valor"]

    resultados = []

    for edad, valores in sorted(por_edad.items()):
        aciertos, fallos, ausentes = 0, [], 0

        for clave, esperado in AFIRMADO.items():
            obtenido = valores.get(clave)
            if obtenido is None:
                ausentes += 1
                continue
            margen = TOLERANCIA_NAT if clave[0] == "NAT" else TOLERANCIA
            if abs(round(obtenido, 1) - esperado) <= margen:
                aciertos += 1
            else:
                fallos.append((clave, esperado, round(obtenido, 1)))

        resultados.append((aciertos, edad, fallos, ausentes))

        marca = "  <-- COINCIDE" if aciertos == len(AFIRMADO) else ""
        print(f"  {edad:<10} {aciertos}/{len(AFIRMADO)} coincidencias{marca}")
        for clave, esperado, obtenido in fallos:
            print(f"             {clave[0]} {clave[1]}: pieza {esperado} / API {obtenido}")

    resultados.sort(reverse=True)
    mejor = resultados[0] if resultados else None

    print()
    if mejor and mejor[0] == len(AFIRMADO):
        print(f"  Franja localizada: age={mejor[1]}")
        print("  Ese es el parámetro que debe usar el script definitivo.")
        return mejor[1]

    print("  NINGUNA franja reproduce todas las cifras de la pieza.")
    print("  Puede significar tres cosas, y hay que averiguar cuál:")
    print("    a) el artículo usa 'country of birth' (lfsa_eoqgac) y no ciudadanía")
    print("    b) Eurostat revisó la serie desde que se transcribieron las cifras")
    print("    c) las cifras de la pieza se copiaron mal")
    print("  En los tres casos, la pieza no debe publicarse como está.")
    return mejor[1] if mejor else None


def paso_3_por_pais(edad):
    """Datos por país para 2024. Sirve para el bloque «Dónde se nota más»."""
    print(f"\n[3] Por país, 2024 (age={edad or 'sin fijar'})")

    params = {
        "format": "JSON",
        "lang": "EN",
        "sex": "T",
        "unit": "PC",
        "time": "2024",
        "citizen": "NEU27_2020_FOR",
    }
    if edad:
        params["age"] = edad

    try:
        js = pedir(f"{BASE}/{CONJUNTO}", params)
    except Exception as e:
        print(f"  FALLO: {type(e).__name__} — {e}")
        return

    guardar(SLUG, "02_por_pais_2024.json", js)
    filas = jsonstat_a_filas(js)

    ordenadas = sorted(filas, key=lambda f: f["valor"], reverse=True)
    print(f"  {len(ordenadas)} países con dato. Los diez más altos:")
    for f in ordenadas[:10]:
        etiqueta = f.get("geo_etiqueta", f.get("geo"))
        print(f"    {etiqueta:<28} {round(f['valor'], 1)} %")

    print()
    print("  La pieza afirma que Grecia tiene la tasa más alta de la UE.")
    print("  Compáralo con esta lista antes de dar la pieza por buena.")


def main():
    print("Descubrimiento Eurostat — sobrecualificación por ciudadanía")
    print("=" * 60)
    print(f"Conjunto: {CONJUNTO}")

    filas = paso_1_agregado_ue()
    edad = paso_2_localizar_edad(filas)
    paso_3_por_pais(edad)

    print("\n" + "=" * 60)
    print(f"Listo. Los JSON están en data/{SLUG}/")
    print("\nCon esto se decide:")
    print("  a) qué franja de edad usa el artículo original")
    print("  b) si las cifras escritas a mano en la pieza son correctas")
    print("  c) si los casos por país que afirma la pieza se sostienen")
    print("\nSolo después se escribe pipeline/sobrecualificacion.py.")


if __name__ == "__main__":
    main()
