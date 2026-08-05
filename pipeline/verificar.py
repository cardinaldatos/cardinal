"""Comprueba que las tres APIs responden y que los parsers funcionan.

Córrelo antes de construir nada encima:  python pipeline/verificar.py
"""

import sys

from comun import pedir, jsonstat_a_filas

PRUEBAS = [
    (
        "Banco Mundial",
        "https://api.worldbank.org/v2/country/MEX/indicator/BX.TRF.PWKR.DT.GD.ZS",
        {"format": "json", "mrv": 1},
        "banco_mundial",
    ),
    (
        "Eurostat",
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/DEMO_R_D3DENS",
        {"lang": "EN", "geoLevel": "country", "time": "2023"},
        "jsonstat",
    ),
    (
        "SSB",
        "https://data.ssb.no/api/pxwebapi/v2/tables/03013/data",
        {
            "lang": "en",
            "outputFormat": "json-stat2",
            "valueCodes[Konsumgrp]": "TOTAL",
            "valueCodes[ContentsCode]": "KpiIndMnd",
            "valueCodes[Tid]": "top(2)",
        },
        "jsonstat",
    ),
]


def main():
    fallos = 0
    for nombre, url, params, tipo in PRUEBAS:
        try:
            js = pedir(url, params)
            if tipo == "jsonstat":
                filas = jsonstat_a_filas(js)
                print(f"OK     {nombre}: {len(filas)} filas")
                print(f"       ejemplo: {filas[0]}")
            else:
                datos = js[1] if len(js) > 1 and js[1] else []
                print(f"OK     {nombre}: {len(datos)} registros")
                print(f"       ejemplo: {datos[0]}")
        except Exception as e:
            fallos += 1
            print(f"FALLO  {nombre}: {type(e).__name__} — {e}")

    print()
    if fallos:
        print(f"{fallos} de {len(PRUEBAS)} fuentes fallaron. Arréglalo antes de seguir.")
        sys.exit(1)
    print("Las tres fuentes responden. El pipeline está vivo.")


if __name__ == "__main__":
    main()
