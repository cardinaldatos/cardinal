"""Sobrecualificación de personas migrantes en la UE — Eurostat (EU-LFS).

Patrón: descargar → crudo.json → limpiar → limpio.json → metodo.md

Cierra la deuda de «El título no cruza», cuyas cifras estaban escritas a
mano en el componente de React desde julio de 2025.

POR QUÉ HIZO FALTA ESTE SCRIPT, aunque aquellas cifras se copiaran bien:
la exploración con explorar_eurostat.py encontró que los valores de 2014
coinciden exactamente con los transcritos (45,9 % y 34,0 %), pero los de
2024 no: la pieza decía 39,6 % y 30,3 %, y el API devuelve 39,8 % y 30,2 %.
Que 2014 cuadre y 2024 no es la firma de una revisión de la serie por parte
de Eurostat, no de un error de transcripción. Es decir: las cifras eran
correctas el día que se copiaron y hoy son falsas. Ningún cuidado al
transcribir lo habría evitado. Solo volver a preguntar.

FRANJA DE EDAD: Y20-64. La exploración mostró que Y15-64 e Y20-64 dan
valores idénticos —casi nadie tiene título universitario antes de los 20—
y que Y25-64, Y20-34, Y25-34 e Y_GE15 dan cifras distintas. Se fija
Y20-64 y se declara, porque elegir otra franja daría números parecidos
pero distintos sin que nadie lo notara.

Córrelo:  cd pipeline && python sobrecualificacion.py
"""

from comun import pedir, guardar, escribir_metodo, jsonstat_a_filas

SLUG = "sobrecualificacion-ue"
CONJUNTO = "lfsa_eoqgan"
BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

EDAD = "Y20-64"
AGREGADO = "EU27_2020"
ANIOS = ["2014", "2024"]

# Los tres grupos de ciudadanía que compara la pieza. El orden importa: es
# el que se conserva en limpio.json y el que usa la web.
GRUPOS = [
    ("NAT", "Nacionales", "Ciudadanos del país donde viven"),
    ("EU27_2020_FOR", "De otro país de la UE", "Ciudadanos de otro Estado miembro"),
    ("NEU27_2020_FOR", "De fuera de la UE", "Ciudadanos de un país no comunitario"),
]

# Los 27 de la UE, en códigos de Eurostat. Hace falta la lista explícita
# porque el conjunto también devuelve países de la AELC y candidatos:
# Islandia aparecía en el descubrimiento con 49,1 %, y colarla en un
# ranking titulado «de la UE» sería un error de bulto.
# EL es Grecia; Eurostat no usa GR.
UE27 = [
    "BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "HR",
    "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT",
    "RO", "SI", "SK", "FI", "SE",
]

# La traducción vive en el pipeline, no en cada superficie: el nombre
# original de Eurostat se conserva en limpio.json como pais_fuente.
NOMBRES_ES = {
    "BE": "Bélgica", "BG": "Bulgaria", "CZ": "Chequia", "DK": "Dinamarca",
    "DE": "Alemania", "EE": "Estonia", "IE": "Irlanda", "EL": "Grecia",
    "ES": "España", "FR": "Francia", "HR": "Croacia", "IT": "Italia",
    "CY": "Chipre", "LV": "Letonia", "LT": "Lituania", "LU": "Luxemburgo",
    "HU": "Hungría", "MT": "Malta", "NL": "Países Bajos", "AT": "Austria",
    "PL": "Polonia", "PT": "Portugal", "RO": "Rumanía", "SI": "Eslovenia",
    "SK": "Eslovaquia", "FI": "Finlandia", "SE": "Suecia",
}


def descargar():
    """Dos consultas: el agregado UE por década, y los países en 2024."""
    crudo = []

    print("  pidiendo: agregado UE, 2014 y 2024")
    params_ue = {
        "format": "JSON", "lang": "EN",
        "geo": AGREGADO, "sex": "T", "unit": "PC",
        "age": EDAD, "time": ANIOS,
    }
    crudo.append({
        "consulta": "agregado_ue",
        "url": f"{BASE}/{CONJUNTO}",
        "params": params_ue,
        "respuesta": pedir(f"{BASE}/{CONJUNTO}", params_ue),
    })

    print("  pidiendo: todos los países, 2024")
    params_paises = {
        "format": "JSON", "lang": "EN",
        "sex": "T", "unit": "PC",
        "age": EDAD, "time": "2024",
    }
    crudo.append({
        "consulta": "paises_2024",
        "url": f"{BASE}/{CONJUNTO}",
        "params": params_paises,
        "respuesta": pedir(f"{BASE}/{CONJUNTO}", params_paises),
    })

    return crudo


def indexar(filas):
    """{(citizen, geo, time): valor} a partir de las filas de JSON-stat."""
    return {
        (f.get("citizen"), f.get("geo"), f.get("time")): f["valor"]
        for f in filas
        if f.get("citizen") and f.get("geo") and f.get("time")
    }


def limpiar(crudo):
    """Arma el agregado por década y el ranking de países de 2024."""
    idx_ue = indexar(jsonstat_a_filas(crudo[0]["respuesta"]))
    idx_paises = indexar(jsonstat_a_filas(crudo[1]["respuesta"]))

    # --- Agregado UE: los tres grupos en los dos años -------------------
    grupos = []
    for codigo, corto, largo in GRUPOS:
        v2014 = idx_ue.get((codigo, AGREGADO, "2014"))
        v2024 = idx_ue.get((codigo, AGREGADO, "2024"))
        if v2014 is None or v2024 is None:
            print(f"  AVISO: faltan datos del grupo {codigo}. No se inventa.")
        grupos.append({
            "id": codigo,
            "corto": corto,
            "largo": largo,
            "v2014": round(v2014, 1) if v2014 is not None else None,
            "v2024": round(v2024, 1) if v2024 is not None else None,
        })

    # --- Países en 2024 -------------------------------------------------
    # Solo los 27 de la UE: el conjunto trae también AELC y candidatos, y
    # el ranking se publica como «de la UE».
    paises, sin_dato = [], []

    for geo in UE27:
        extra = idx_paises.get(("NEU27_2020_FOR", geo, "2024"))
        nat = idx_paises.get(("NAT", geo, "2024"))
        ue = idx_paises.get(("EU27_2020_FOR", geo, "2024"))

        if extra is None:
            sin_dato.append({"geo": geo, "pais": NOMBRES_ES.get(geo, geo)})
            continue

        fila = {
            "geo": geo,
            "pais": NOMBRES_ES.get(geo, geo),
            "pais_fuente": geo,
            "extra_ue": round(extra, 1),
            "nacionales": round(nat, 1) if nat is not None else None,
            "otros_ue": round(ue, 1) if ue is not None else None,
        }
        # La brecha es el hallazgo: no cuánto es la tasa, sino cuánto más
        # alta es que la de los nacionales del mismo país.
        fila["brecha"] = (
            round(extra - nat, 1) if nat is not None else None
        )
        paises.append(fila)

    paises.sort(key=lambda p: p["extra_ue"], reverse=True)

    return {
        "conjunto": CONJUNTO,
        "edad": EDAD,
        "anios": ANIOS,
        "agregado": AGREGADO,
        "grupos": grupos,
        "paises_2024": paises,
        "sin_dato": sin_dato,
    }


def revisar(limpio):
    """Avisos que no deben pasar desapercibidos al publicar."""
    for g in limpio["grupos"]:
        if g["v2014"] is None or g["v2024"] is None:
            print(f"  AVISO: el grupo {g['id']} tiene años incompletos.")

    n = len(limpio["paises_2024"])
    print(f"  {n} de {len(UE27)} países de la UE con dato en 2024.")
    if limpio["sin_dato"]:
        nombres = ", ".join(p["pais"] for p in limpio["sin_dato"])
        print(f"  Sin dato: {nombres}")
        print("         Se registran en limpio.json: el hueco se declara.")

    if limpio["paises_2024"]:
        alto = limpio["paises_2024"][0]
        print(f"  Tasa más alta: {alto['pais']} ({alto['extra_ue']} %)")


def main():
    print(f"Sobrecualificación en la UE — Eurostat ({CONJUNTO}, {EDAD})")
    print("=" * 60)

    crudo = descargar()
    guardar(SLUG, "crudo.json", crudo)

    limpio = limpiar(crudo)
    guardar(SLUG, "limpio.json", limpio)

    print()
    revisar(limpio)

    escribir_metodo(
        SLUG,
        fuente="Eurostat, Encuesta de Población Activa de la UE (EU-LFS), "
               "conjunto lfsa_eoqgan (tasas de sobrecualificación por "
               "ciudadanía).",
        url=f"{BASE}/{CONJUNTO}?format=JSON&age={EDAD}&sex=T&unit=PC",
        definicion=(
            "Tasa de sobrecualificación: proporción de personas empleadas con "
            "estudios superiores (ISCED 5-8) que trabajan en ocupaciones de "
            "baja o media cualificación (ISCO, grupos 4-9).\n\n"
            "Las personas se clasifican por ciudadanía, no por país de "
            "nacimiento: nacionales del país donde residen, ciudadanos de "
            "otro Estado miembro de la UE, y ciudadanos de un país no "
            "comunitario. Eurostat publica una serie paralela por país de "
            "nacimiento (lfsa_eoqgac) cuyos valores no son intercambiables "
            f"con estos.\n\n"
            f"Franja de edad: {EDAD} (de 20 a 64 años)."
        ),
        limites=(
            f"1. La franja de edad es una elección declarada, no un dato "
            f"neutro. El conjunto ofrece siete ({EDAD} entre ellas) y cada "
            f"una da cifras distintas: en 2024, los ciudadanos de fuera de "
            f"la UE aparecen al 39,8 % en {EDAD} y al 33,0 % en 25-34 años. "
            f"Comparar cifras de franjas distintas no tiene sentido.\n\n"
            "2. Los valores de la serie se revisan. Las cifras de 2024 que "
            "esta pieza publicó por primera vez en julio de 2025 (39,6 % y "
            "30,3 %) ya no son las que devuelve el API (39,8 % y 30,2 %). "
            "Por eso la pieza se reconstruye desde la fuente en cada "
            "ejecución y no conserva cifras transcritas.\n\n"
            "3. El ranking por país incluye solo los 27 Estados miembros. El "
            "conjunto también devuelve países de la AELC y candidatos "
            "—Islandia aparece con una tasa alta—, que quedan fuera porque "
            "el ranking se presenta como europeo comunitario.\n\n"
            "4. No todos los países tienen dato cada año. Los que faltan se "
            "listan en limpio.json como sin_dato; no se estiman ni se "
            "rellenan con el año anterior.\n\n"
            "5. Es una encuesta por muestreo, no un censo. En países "
            "pequeños o con pocas personas migrantes con título "
            "universitario, la muestra es reducida y el valor puede saltar "
            "de un año a otro sin que cambie la realidad. Eurostat marca "
            "esos casos con banderas de fiabilidad que esta consulta no "
            "recoge todavía.\n\n"
            "6. La tasa mide desajuste entre título y ocupación. No mide "
            "reconocimiento de títulos, ni discriminación, ni idioma: son "
            "causas posibles que el indicador no separa."
        ),
    )

    print("\nListo.")


if __name__ == "__main__":
    main()
