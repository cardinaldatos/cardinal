"""Comprueba que las fuentes del registro responden, que los parsers
funcionan y que los datos siguen frescos.

Responder no basta: la tabla 03013 de SSB siguió respondiendo durante meses
después de dejar de actualizarse, y esta comprobación salía en verde sobre
una fuente congelada. Por eso cada sonda declara cuántos meses de
antigüedad tolera.

CAMBIO DE HOY: la lista de fuentes ya no vive aquí. Está en
data/fuentes.json, que es el mismo archivo que publica la página de método.
Antes había que editar este script, el README, el workflow y la web para
añadir una fuente, y hasta que se editaran los cuatro, tres de ellos
mentían. Ahora este script no sabe cuántas fuentes hay: las cuenta.

Una fuente sin sonda no es un fallo. Es una candidata: nos interesa pero
todavía no hemos descubierto su forma. Se listan al final para que no se
olviden.

Córrelo antes de construir nada encima:  python pipeline/verificar.py
"""

import json
import re
import sys
from datetime import date

from comun import RAIZ, pedir, jsonstat_a_filas

REGISTRO = RAIZ / "data" / "fuentes.json"


def cargar_registro():
    """Lee data/fuentes.json y separa las que tienen sonda de las que no."""
    datos = json.loads(REGISTRO.read_text(encoding="utf-8"))
    fuentes = datos["fuentes"]
    con_sonda = [f for f in fuentes if f.get("sonda")]
    sin_sonda = [f for f in fuentes if not f.get("sonda")]
    return fuentes, con_sonda, sin_sonda


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


def sondear(fuente):
    """Pide una fuente y devuelve (periodo, resumen). Lanza si algo falla."""
    sonda = fuente["sonda"]
    js = pedir(sonda["url"], sonda.get("params"))

    if sonda["tipo"] == "jsonstat":
        filas = jsonstat_a_filas(js)
        if not filas:
            raise ValueError("respuesta sin filas")
        return periodo_jsonstat(js, filas), f"{len(filas)} filas", filas[0]

    if sonda["tipo"] == "banco_mundial":
        datos = js[1] if len(js) > 1 and js[1] else []
        if not datos:
            raise ValueError("respuesta sin registros")
        return datos[0].get("date"), f"{len(datos)} registros", datos[0]

    raise ValueError(f"tipo de sonda desconocido: {sonda['tipo']!r}")


def main():
    fuentes, con_sonda, sin_sonda = cargar_registro()

    print(f"Registro: {len(fuentes)} fuentes declaradas, "
          f"{len(con_sonda)} con sonda.")
    print("=" * 60)

    fallos = 0
    avisos = 0

    for fuente in con_sonda:
        nombre = fuente["nombre"]
        meses_max = fuente["sonda"].get("meses_tolerados")

        try:
            periodo, resumen, ejemplo = sondear(fuente)
            print(f"OK     {nombre}: {resumen}")
            print(f"       ejemplo: {ejemplo}")

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

    if sin_sonda:
        print()
        print(f"Sin sonda todavía ({len(sin_sonda)}):")
        for f in sin_sonda:
            print(f"  {f['nombre']} — {f['estado']}: {f['cubre']}")
        print("  No se comprueban porque aún no sabemos qué forma tienen.")
        print("  El siguiente paso de cada una es un script de exploración.")

    print()
    if fallos:
        print(f"{fallos} de {len(con_sonda)} fuentes sondeadas fallaron. "
              f"Arréglalo antes de seguir.")
        sys.exit(1)
    if avisos:
        print(f"Todas las fuentes sondeadas responden, pero hay "
              f"{avisos} aviso(s) de frescura.")
        print("Revisa si la tabla sigue viva antes de construir una pieza encima.")
        sys.exit(1)
    print("Todas las fuentes sondeadas responden y sus datos están frescos. "
          "El pipeline está vivo.")


if __name__ == "__main__":
    main()
