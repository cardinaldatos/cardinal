"""Comprueba que las tres APIs responden, que los parsers funcionan y que
los datos siguen frescos.

Responder no basta: la tabla 03013 de SSB siguió respondiendo durante meses
después de dejar de actualizarse, y esta comprobación salía en verde sobre
una fuente congelada. Por eso ahora cada sonda declara cuántos meses de
antigüedad tolera.

Córrelo antes de construir nada encima:  python pipeline/verificar.py
"""

import re
import sys
from datetime import date

from comun import pedir, jsonstat_a_filas

# nombre, url, params, tipo, meses_tolerados
# meses_tolerados = None  ->  la sonda fija un periodo concreto, no aplica
PRUEBAS = [
    (
        "Banco Mundial",
        "https://api.worldbank.org/v2/country/MEX/indicator/BX.TRF.PWKR.DT.GD.ZS",
        {"format": "json", "mrv": 1},
        "banco_mundial",
        30,  # anual, con rezago largo de publicación
    ),
    (
        "Eurostat",
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/DEMO_R_D3DENS",
        {"lang": "EN", "geoLevel": "country", "time": "2023"},
        "jsonstat",
        None,  # la consulta pide 2023 a propósito; medir frescura no tendría sentido
    ),
    (
        "SSB",
        "https://data.ssb.no/api/pxwebapi/v2/tables/14700/data",
        {
            "lang": "en",
            "outputFormat": "json-stat2",
            "valueCodes[Tid]": "top(2)",
            # La 14700 exige ContentsCode: no admite eliminación, a diferencia
            # de VareTjenesteGrp, que se agrega sola al total.
            "valueCodes[ContentsCode]": "KpiIndMnd",
        },
        "jsonstat",
        4,  # mensual, publicada a mediados del mes siguiente
    ),
]


def antiguedad_meses(codigo):
    """Meses transcurridos desde un código de periodo. None si no lo entiende.

    Entiende '2026M06' (mensual) y '2023' (anual, contado desde diciembre).
    """
    if codigo is None:
        return None
    codigo = str(codigo).strip()
    hoy = date.today()

    m = re.fullmatch(r"(\d{4})M(\d{2})", codigo)
    if m:
        anio, mes = int(m.group(1)), int(m.group(2))
    elif re.fullmatch(r"\d{4}", codigo):
        anio, mes = int(codigo), 12
    else:
        return None

    return (hoy.year - anio) * 12 + (hoy.month - mes)


def periodo_jsonstat(js, filas):
    """Último periodo presente en la respuesta JSON-stat."""
    time_dims = (js.get("role") or {}).get("time") or []
    if not time_dims:
        return None
    dim = time_dims[0]
    periodos = [f[dim] for f in filas if dim in f]
    return max(periodos) if periodos else None


def main():
    fallos = 0
    avisos = 0

    for nombre, url, params, tipo, meses_max in PRUEBAS:
        try:
            js = pedir(url, params)

            if tipo == "jsonstat":
                filas = jsonstat_a_filas(js)
                if not filas:
                    raise ValueError("respuesta sin filas")
                periodo = periodo_jsonstat(js, filas)
                print(f"OK     {nombre}: {len(filas)} filas")
                print(f"       ejemplo: {filas[0]}")
            else:
                datos = js[1] if len(js) > 1 and js[1] else []
                if not datos:
                    raise ValueError("respuesta sin registros")
                periodo = datos[0].get("date")
                print(f"OK     {nombre}: {len(datos)} registros")
                print(f"       ejemplo: {datos[0]}")

            if meses_max is None:
                print("       frescura: no aplica (la consulta fija el periodo)")
                continue

            edad = antiguedad_meses(periodo)
            if edad is None:
                avisos += 1
                print(f"       AVISO: no supe leer el periodo '{periodo}'")
            elif edad > meses_max:
                avisos += 1
                print(f"       AVISO: último periodo {periodo}, {edad} meses de "
                      f"antigüedad (tolerado: {meses_max}).")
                print("              Responde, pero puede haber dejado de actualizarse.")
            else:
                print(f"       frescura: {periodo}, {edad} meses. Dentro de lo esperado.")

        except Exception as e:
            fallos += 1
            print(f"FALLO  {nombre}: {type(e).__name__} — {e}")

    print()
    if fallos:
        print(f"{fallos} de {len(PRUEBAS)} fuentes fallaron. Arréglalo antes de seguir.")
        sys.exit(1)
    if avisos:
        print(f"Las tres fuentes responden, pero hay {avisos} aviso(s) de frescura.")
        print("Revisa si la tabla sigue viva antes de construir una pieza encima.")
        sys.exit(1)
    print("Las tres fuentes responden y los datos están frescos. El pipeline está vivo.")


if __name__ == "__main__":
    main()
