"""Costo de enviar remesas a América Latina — Banco Mundial (WDI).

Patrón: descargar → crudo.json → limpiar → limpio.json → metodo.md

Pide los países de uno en uno por lotes de seis. El API devuelve un error 500
genérico, sin explicación, cuando la lista es más larga.

Venezuela va en la lista a propósito, aunque sabemos que no tiene dato. Su
ausencia queda registrada en limpio.json como hallazgo, no como omisión.

No todas las ausencias son iguales, y hasta ahora limpio.json las mezclaba.
Un país puede faltar porque el Banco Mundial no publica esta serie para él
—la consulta no devuelve ni un registro— o porque la publica y todos los
años vienen sin valor. La primera dice algo sobre qué se decide medir; la
segunda, sobre la cobertura de los proveedores. Ahora se distinguen en el
campo `motivo`, y el motivo se deduce de lo que respondió el API, no de lo
que creamos saber.

Los nombres de país se traducen aquí, no en cada superficie. El API los
devuelve en inglés ("Peru", "Dominican Republic") y este es un proyecto en
español: si la traducción viviera en el sitio y en los generadores de
Instagram por separado, tendríamos tres diccionarios que se desincronizan.
El nombre original de la fuente se conserva en `pais_fuente` para que la
cifra siga siendo rastreable hasta el registro crudo.

Córrelo: cd pipeline && python remesas.py
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

# Nombre publicable, en español. Cubre los trece de PAISES, tengan dato o no.
NOMBRES_ES = {
    "COL": "Colombia",
    "ECU": "Ecuador",
    "PER": "Perú",
    "DOM": "República Dominicana",
    "MEX": "México",
    "GTM": "Guatemala",
    "HND": "Honduras",
    "SLV": "El Salvador",
    "NIC": "Nicaragua",
    "BOL": "Bolivia",
    "ARG": "Argentina",
    "CHL": "Chile",
    "VEN": "Venezuela",
}

LOTE = 6  # más de esto y el API devuelve 500

# 200 USD no es una elección nuestra: es el monto sobre el que el indicador
# está definido. Cambiarlo convertiría el recibo en una extrapolación.
MONTO = 200

# Los dos motivos por los que un país puede quedar fuera. El texto es el que
# se publica, así que vive aquí y no en las superficies: si mañana cambia la
# redacción, cambia en la web y en Instagram a la vez.
MOTIVOS = {
    "sin_indicador": (
        "El Banco Mundial no publica esta serie para el país: la consulta no "
        "devuelve ningún registro."
    ),
    "valor_nulo": (
        "El Banco Mundial publica la serie para el país, pero todos los años "
        "consultados vienen sin valor."
    ),
}


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

    Los países sin ningún valor no se descartan: se listan aparte, y cada uno
    con el motivo de su ausencia. El hueco es parte del hallazgo, pero un
    hueco sin explicar no dice nada — hay que saber si el dato no existe o si
    existe vacío.
    """
    por_pais = {}

    # Países que el API devolvió, con valor o sin él. Es lo que permite
    # separar «no hay serie» de «hay serie sin valores». Se registra antes de
    # descartar los nulos, porque el descarte es justo lo que borra la pista.
    devueltos = set()

    for bloque in crudo:
        respuesta = bloque["respuesta"]
        registros = respuesta[1] if len(respuesta) > 1 else None
        for r in (registros or []):
            iso = r.get("countryiso3code")
            if iso in NOMBRES_ES:
                devueltos.add(iso)

            valor = r.get("value")
            anio = r.get("date")
            if valor is None:
                continue

            previo = por_pais.get(iso)
            if previo is None or anio > previo["anio"]:
                nombre_fuente = r["country"]["value"]
                por_pais[iso] = {
                    "iso3": iso,
                    "pais": NOMBRES_ES.get(iso, nombre_fuente),
                    "pais_fuente": nombre_fuente,
                    "anio": anio,
                    "costo_pct": round(valor, 2),
                    # Se calcula sobre el valor SIN redondear y se redondea al
                    # final. Es lo correcto, pero implica que este campo no se
                    # puede recalcular multiplicando costo_pct: los dos salen
                    # del mismo original por caminos distintos y pueden
                    # diferir en un céntimo. Está declarado en la pieza y en
                    # los límites de más abajo.
                    "sobre_200_usd": round(valor / 100 * MONTO, 2),
                }

    con_dato = sorted(por_pais.values(), key=lambda f: f["costo_pct"], reverse=True)

    sin_dato = []
    for p in PAISES:
        if p in por_pais:
            continue
        motivo = "valor_nulo" if p in devueltos else "sin_indicador"
        sin_dato.append({
            "iso3": p,
            "pais": NOMBRES_ES.get(p, p),
            "motivo": motivo,
            "motivo_texto": MOTIVOS[motivo],
        })

    # Año común de la serie, si lo hay. Las superficies lo necesitan para
    # hablar del conjunto sin tener que espiar el primer país de la lista.
    # Si los países no comparten año, queda en null a propósito: entonces no
    # existe «el año de la pieza» y decir uno sería mentir.
    anios = {f["anio"] for f in con_dato}
    anio_comun = next(iter(anios)) if len(anios) == 1 else None

    return {
        "serie": SERIE,
        "anio": anio_comun,
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
    elif anios:
        print(f"  Todos los países en el mismo año: {limpio['anio']}")

    for clave in MOTIVOS:
        cuales = [p["pais"] for p in limpio["sin_dato"] if p["motivo"] == clave]
        if cuales:
            print(f"  Sin dato ({clave}): {', '.join(cuales)}")

    # Si el API trae un país que no está en NOMBRES_ES, se publicaría con el
    # nombre en inglés sin que nadie lo note. Mejor que grite.
    faltan = [
        f["iso3"] for f in limpio["con_dato"] if f["iso3"] not in NOMBRES_ES
    ]
    if faltan:
        print(f"  AVISO: sin nombre en español para {', '.join(faltan)}.")
        print("         Se publicarán con el nombre en inglés de la fuente.")


def limite_de_ausencias(limpio):
    """Redacta el límite sobre países sin dato a partir de los datos.

    Antes esta línea nombraba a Venezuela, Argentina y Chile escritos a mano
    dentro del texto del método. Era correcta el día que se escribió y habría
    envejecido en silencio, igual que las cifras de la pieza de Eurostat. Ya
    no: la genera el script en cada ejecución.
    """
    faltantes = limpio["sin_dato"]
    if not faltantes:
        return (
            "4. Todos los países consultados tienen valor en esta serie. No hay "
            "ausencias que declarar en esta ejecución."
        )

    trozos = ["4. Ausencias, que no son todas iguales. "]

    sin_indicador = [p["pais"] for p in faltantes if p["motivo"] == "sin_indicador"]
    nulos = [p["pais"] for p in faltantes if p["motivo"] == "valor_nulo"]

    if sin_indicador:
        trozos.append(
            f"Sin serie publicada para este indicador: {', '.join(sin_indicador)} "
            f"— la consulta no devuelve ningún registro. "
        )
    if nulos:
        trozos.append(
            f"Con serie publicada pero sin valor en los años consultados: "
            f"{', '.join(nulos)}. "
        )

    trozos.append(
        "Que un organismo no mida un país y que lo mida sin obtener valor son "
        "dos cosas distintas, y solo la primera dice algo sobre qué se decide "
        "contar. La distinción queda en el campo `motivo` de cada entrada de "
        "`sin_dato` en limpio.json. Este párrafo lo genera el script a partir "
        "de la respuesta del API: no está escrito a mano."
    )
    return "".join(trozos)


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

            f"{limite_de_ausencias(limpio)}\n\n"

            "5. No hay desglose entre comisión y margen de tipo de cambio, ni por "
            "país emisor, ni por tipo de proveedor. Ese detalle solo existe en el "
            "Excel trimestral de Remittance Prices Worldwide.\n\n"

            "6. Los nombres de país se publican en español. La traducción es "
            "nuestra, no de la fuente: el API los devuelve en inglés. El nombre "
            "original queda guardado en el campo `pais_fuente` de limpio.json, y "
            "en crudo.json sin tocar. Ninguna cifra depende de esta traducción.\n\n"

            f"7. Los campos `costo_pct` y `sobre_200_usd` se redondean por separado "
            f"a partir del valor original sin redondear. Multiplicar el porcentaje "
            f"publicado por {MONTO} puede dar un céntimo de diferencia con el monto "
            f"publicado. Redondear al final y no antes es lo correcto, pero conviene "
            f"decirlo: la cuenta no está mal, está hecha en otro orden."
        ),
    )

    print("\nListo.")


if __name__ == "__main__":
    main()
