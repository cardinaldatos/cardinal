"""Costo de enviar remesas a América Latina — Banco Mundial (WDI).

Patrón: descargar → crudo.json → limpiar → limpio.json → metodo.md

Pide los países de uno en uno por lotes de seis. El API devuelve un error 500
genérico, sin explicación, cuando la lista es más larga.

Venezuela va en la lista a propósito, aunque sabemos que no tiene dato. Su
ausencia queda registrada en limpio.json como hallazgo, no como omisión.

Córrelo:  cd pipeline && python remesas.py
"""

from comun import pedir, guardar, escribir_metodo

SLUG = "remesas-costo-latam"
SERIE = "SI.RMT.COST.IB.ZS"
BASE = "https://api.worldbank.org/v2"

# Países receptores de América Latina con diáspora significativa.
PAISES = [
    "COL", "ECU", "PER", "DOM", "MEX", "GTM",
    "HND", "SLV", "NIC", "BOL", "ARG", "CHL", "VEN",
]

LOTE = 6  # más de esto y el API devuelve 500

# 200 USD no es una elección nuestra: es el monto sobre el que el indicador
# está definido. Cambiarlo convertiría el recibo en una extrapolación.
MONTO = 200


def lotes(lista, tam):
    for i in range(0, len(lista), tam):
        yield lista[i:i + tam]


def descargar():
    """Trae cinco años por país. Devuelve las respuestas crudas, sin tocar."""
    crudo = []
    for grupo in lotes(PAISES, LOTE):
        url = f"{BASE}/country/{';'.join(grupo)}/indicator/{SERIE}"
        params = {"format": "json", "mrv": 5, "per_page": 200}
        print(f"  pidiendo: {', '.join(grupo)}")
        js = pedir(url, params)
        crudo.append({"paises": grupo, "url": url, "respuesta": js})
    return crudo


def limpiar(crudo):
    """Se queda con el año más reciente que tenga valor, por país.

    Los países sin ningún valor no se descartan: se listan aparte. El hueco
    es parte del hallazgo.
    """
    por_pais = {}

    for bloque in crudo:
        registros = bloque["respuesta"][1] if len(bloque["respuesta"]) > 1 else None
        for r in (registros or []):
            iso = r.get("countryiso3code")
            valor = r.get("value")
            anio = r.get("date")
            if valor is None:
                continue
            previo = por_pais.get(iso)
            if previo is None or anio > previo["anio"]:
                por_pais[iso] = {
                    "iso3": iso,
                    "pais": r["country"]["value"],
                    "anio": anio,
                    "costo_pct": round(valor, 2),
                    "sobre_200_usd": round(valor / 100 * MONTO, 2),
                }

    con_dato = sorted(por_pais.values(), key=lambda f: f["costo_pct"], reverse=True)
    sin_dato = [p for p in PAISES if p not in por_pais]

    return {
        "serie": SERIE,
        "monto_referencia_usd": MONTO,
        "con_dato": con_dato,
        "sin_dato": sin_dato,
    }


def revisar(limpio):
    """Avisos que no deben pasar desapercibidos al publicar."""
    anios = {f["anio"] for f in limpio["con_dato"]}
    if len(anios) > 1:
        print(f"  AVISO: los países no comparten año ({sorted(anios)}).")
        print("         Compararlos en una misma pieza exige declararlo.")
    else:
        print(f"  Todos los países en el mismo año: {anios.pop()}")

    if limpio["sin_dato"]:
        print(f"  Sin dato: {', '.join(limpio['sin_dato'])}")


def main():
    print(f"Remesas — costo de envío a América Latina ({SERIE})")
    print("=" * 55)

    crudo = descargar()
    guardar(SLUG, "crudo.json", crudo)

    limpio = limpiar(crudo)
    guardar(SLUG, "limpio.json", limpio)

    print()
    revisar(limpio)

    escribir_metodo(
        SLUG,
        fuente="Banco Mundial, World Development Indicators, serie SI.RMT.COST.IB.ZS "
               "(costo promedio de enviar remesas hacia un país). Los datos de origen "
               "provienen de Remittance Prices Worldwide.",
        url=f"{BASE}/country/<ISO3>/indicator/{SERIE}?format=json&mrv=5",
        definicion=(
            f"Costo total de transacción de enviar {MONTO} USD hacia el país, como "
            f"porcentaje del monto enviado, promediado entre todos los proveedores "
            f"de servicios de remesas incluidos en la base Remittance Prices "
            f"Worldwide para ese destino.\n\n"
            f"La cifra en dólares de esta pieza devuelve ese porcentaje al monto "
            f"sobre el que el indicador está definido: no es una extrapolación. "
            f"Tampoco es la tarifa de ningún proveedor concreto — es el promedio "
            f"del mercado rastreado."
        ),
        limites=(
            "1. Los valores latinoamericanos (2–3,5 %) quedan muy por debajo del "
            "promedio global del RPW (6,36 %). No es una discrepancia de método: "
            "ambos miden lo mismo, y América Latina es la región más barata del "
            "mundo para recibir remesas. Pendiente menor: contrastar contra el "
            "promedio regional del informe, no contra el global.\n\n"
            "2. Frecuencia anual, no trimestral. El metadato del catálogo declara "
            "actualizaciones recientes, pero el último año con dato es 2023: "
            "refrescan el catálogo sin añadir años. Verificar en cada ejecución.\n\n"
            "3. Es un promedio entre los corredores rastreados hacia cada país. En "
            "países con pocos corredores el promedio salta fuerte de un año a otro "
            "sin que cambie el mercado real. No usar la serie temporal de un país "
            "como si fuera una tendencia.\n\n"
            "4. Venezuela no tiene indicador en esta serie. Argentina y Chile "
            "aparecen con valor nulo. Su ausencia se registra en limpio.json.\n\n"
            "5. No hay desglose entre comisión y margen de tipo de cambio, ni por "
            "país emisor, ni por tipo de proveedor. Ese detalle solo existe en el "
            "Excel trimestral de Remittance Prices Worldwide."
        ),
    )

    print("\nListo.")


if __name__ == "__main__":
    main()
