"""Andamiaje compartido por los scripts de exploración de fuentes.

Un script de exploración no publica: descubre. Su producto son dos cosas,
el informe que imprime en el log y los JSON crudos que quedan como
artifact descargable. Ninguno escribe nada que llegue a `main`: el
workflow que los lanza corre con permiso de solo lectura.

Los tres exploradores —ACNUR, CEPAL, INE España— responden las mismas
cinco preguntas y en el mismo orden, para que sus informes se puedan leer
uno al lado del otro y comparar:

  1. Qué series existen y cuáles tocan migración o diáspora.
  2. Qué dimensiones exige la consulta y cuáles admite omitir. Ojo con
     las que se agregan solas al total y las que no.
  3. Hasta qué periodo llega y con cuánto rezago publica.
  4. Cómo representa la ausencia: valor nulo, cero, o el país no aparece.
     Es la más importante de las cinco. Sin ella no se puede distinguir
     «no se midió» de «se midió y dio cero», y sin esa distinción no hay
     campo `motivo` ni hay pieza.
  5. Cuál es la licencia, comprobada en la fuente y no en su portada.

Este módulo no sabe nada de ninguna fuente en concreto. Solo pone el
formato del informe, el pedir-sin-reventar y el cálculo del rezago.

Va aparte de `comun.py` a propósito. `comun.py` son los parsers de los
scripts de producción: lo que sostiene una pieza publicada. No conviene
que una pieza dependa de código que solo existe para descubrir, ni que un
cambio hecho para desatascar una exploración toque el archivo del que
cuelgan las cifras que ya están en el sitio.

Este archivo no se corre solo. Lo importan los tres exploradores.
"""

from datetime import date

from comun import guardar, pedir

ANCHO = 68

PREGUNTAS = {
    1: "Qué series existen y cuáles tocan migración o diáspora",
    2: "Qué dimensiones exige la consulta y cuáles admite omitir",
    3: "Hasta qué periodo llega y con cuánto rezago publica",
    4: "Cómo representa la ausencia: nulo, cero, o el país no aparece",
    5: "Licencia, comprobada en la fuente y no en su portada",
}

# Qué preguntas quedaron respondidas. Lo llena cada script con responde()
# y lo lee cierre() al final. Es estado de módulo a propósito: cada
# ejecución explora una sola fuente, así que no hay dos informes vivos a
# la vez y pasarlo de mano en mano solo alargaría cada llamada.
_RESPUESTAS = {}


def encabezado(fuente, organismo, slug):
    """Abre el informe y deja dicho qué produce y qué no."""
    print(f"Descubrimiento {fuente} — {organismo}")
    print("=" * ANCHO)
    print(f"Ejecutado el {date.today().isoformat()}")
    print(f"Los JSON crudos quedan en data/{slug}/ y suben como artifact.")
    print("Este script no confirma nada al repositorio.")


def preparacion(texto):
    """Sección previa a las cinco preguntas, para lo que hay que averiguar
    antes de poder preguntar nada. No es una de las cinco: se numera 0
    justamente para que no se confunda con ellas."""
    print()
    print("-" * ANCHO)
    print("[0] Preparación (no es una de las cinco)")
    print(f"    {texto}")
    print("-" * ANCHO)


def pregunta(n, detalle=""):
    """Abre la sección de una de las cinco preguntas."""
    print()
    print("-" * ANCHO)
    print(f"[{n}] {PREGUNTAS[n]}")
    if detalle:
        print(f"    {detalle}")
    print("-" * ANCHO)


def extra(n, titulo):
    """Sección propia de una fuente, fuera de las cinco comunes."""
    print()
    print("-" * ANCHO)
    print(f"[{n}] {titulo}")
    print("-" * ANCHO)


def apartado(texto):
    print()
    print(f"  · {texto}")


def responde(n, resumen):
    """Deja constancia de que una pregunta quedó respondida, y con qué.

    El resumen se reimprime al final. La idea es que el cierre del log se
    pueda copiar tal cual a la nota de data/fuentes.json sin volver a
    leer las trescientas líneas de arriba.
    """
    _RESPUESTAS[n] = resumen
    print(f"  => RESPUESTA {n}: {resumen}")


def sin_responder(n, motivo):
    """Lo contrario, y es igual de valioso: una pregunta que la fuente no
    deja responder es material publicable, no un fracaso."""
    _RESPUESTAS[n] = f"SIN RESPONDER — {motivo}"
    print(f"  => SIN RESPONDER {n}: {motivo}")


def intentar(slug, etiqueta, url, params=None, timeout=60):
    """Pide y guarda, sin reventar el script si una ruta no existe.

    Varias de las rutas que prueban estos scripts son hipótesis. Un fallo
    aquí es información, no un error: significa que esa vía no sirve y
    hay que probar otra. Por eso devuelve None en vez de propagar.
    """
    try:
        js = pedir(url, params, timeout=timeout)
    except Exception as e:
        print(f"    FALLO  {etiqueta}: {type(e).__name__} — {e}")
        return None
    guardar(slug, f"{etiqueta}.json", js)
    return js


def rezago_en_meses(anio, mes=12, hoy=None):
    """Meses entre el final del último periodo publicado y hoy.

    Se cuenta desde el final del periodo, no desde su inicio: un dato
    anual de 2024 no está «rezagado veinte meses» en enero de 2025, está
    recién cerrado. Medirlo desde el inicio infla el rezago de toda serie
    anual en once meses y hace parecer lenta a una fuente que no lo es.
    """
    hoy = hoy or date.today()
    return (hoy.year - anio) * 12 + (hoy.month - mes)


def clasificar(valor):
    """Traduce una celda a la distinción que necesita el campo `motivo`.

    Tres estados, no dos. «nulo» y «cero» dicen cosas distintas sobre lo
    que el organismo decidió medir, y aplanarlos es exactamente el error
    que la pieza tiene que evitar.
    """
    if valor is None:
        return "nulo"
    if isinstance(valor, str):
        limpio = valor.strip()
        if limpio == "" or limpio in {"-", ":", "..", "...", "n/a", "N/A"}:
            return "nulo"
        try:
            valor = float(limpio.replace(",", "."))
        except ValueError:
            return "no numérico"
    if isinstance(valor, (int, float)):
        return "cero" if valor == 0 else "con valor"
    return "no numérico"


def cierre(fuente, id_fuente):
    """Cierra el informe con el estado de las cinco preguntas.

    Si alguna quedó sin responder, imprime qué escribir en la nota de
    data/fuentes.json. El límite acordado es de tres horas por fuente: si
    se cumplen sin las cinco respuestas, la fuente se queda como
    candidata y se anota qué la trancó. Una fuente pública que no se
    puede abrir es un hallazgo publicable.
    """
    print()
    print("=" * ANCHO)
    print(f"Cierre — {fuente}")
    print("=" * ANCHO)

    pendientes = []
    for n in sorted(PREGUNTAS):
        respuesta = _RESPUESTAS.get(n)
        if respuesta is None:
            respuesta = "SIN RESPONDER — el script no llegó a esta sección"
        if respuesta.startswith("SIN RESPONDER"):
            pendientes.append(n)
        print(f"  [{n}] {PREGUNTAS[n]}")
        print(f"      {respuesta}")

    print()
    if not pendientes:
        print("  Las cinco preguntas quedaron respondidas.")
        print(f"  La fuente «{id_fuente}» puede pasar de candidata a sondeada")
        print("  en data/fuentes.json, con su bloque `sonda` escrito a partir")
        print("  de la consulta que funcionó, y su `licencia` con lo que diga")
        print("  la propia fuente y no su portada.")
    else:
        faltan = ", ".join(str(n) for n in pendientes)
        print(f"  Quedan sin responder las preguntas: {faltan}.")
        print(f"  La fuente «{id_fuente}» se queda como candidata.")
        print("  Anota en su `nota` de data/fuentes.json qué fue lo que la")
        print("  trancó, con el mismo detalle con que se anotaría un hallazgo:")
        print("  eso es lo que después se publica.")
        print()
        print("  Recordatorio del límite acordado: tres horas por fuente.")
        print("  Si ya se cumplieron, se detiene aquí y se pasa a la siguiente.")
