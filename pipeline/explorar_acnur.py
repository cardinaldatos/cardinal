"""Descubre la forma del API de ACNUR — Refugee Data Finder.

No produce datos para publicar. Produce el mapa que necesita el script
real de la pieza sobre desplazamiento venezolano: qué series expone el
API, qué dimensiones exige cada consulta, hasta qué año llega, cómo
representa la ausencia de dato, y bajo qué licencia se puede reusar.

Es el equivalente a explorar_rpw.py y a explorar_eurostat.py: primero se
pregunta la forma, después se pide el dato.

## La hipótesis que hay que confirmar o desmentir

La pieza parte de que la mayoría de las personas venezolanas desplazadas
NO están contadas como refugiadas, sino bajo otras categorías de
protección. Si el API lo desmiente, mejor saberlo antes de construir
nada encima: la sección [6] de este informe existe para eso y para nada
más. Se responde con aritmética sobre las columnas que devuelva el API,
no con lo que se espera encontrar.

## Lo que este script NO da por sabido

Los nombres de las rutas y de las columnas de este API son hipótesis, no
certezas: están escritos abajo como listas de candidatas y el script las
prueba una por una. Lo que responda queda en el log y en los JSON. Si
una ruta falla, eso es parte del hallazgo, no un error del script.

Tampoco da por sabido cómo se llama la columna que cuenta a las personas
venezolanas desplazadas fuera. En vez de buscarla por nombre, el script
imprime TODAS las columnas numéricas que devuelva y sus totales. Buscar
por nombre esperado es la forma de encontrar lo que uno ya creía.

Córrelo:  cd pipeline && python explorar_acnur.py
"""

from datetime import date

import requests

from comun import CABECERAS, guardar
from explorar_comun import (
    apartado,
    cierre,
    clasificar,
    encabezado,
    extra,
    intentar,
    pregunta,
    preparacion,
    responde,
    rezago_en_meses,
    sin_responder,
)

FUENTE = "ACNUR"
ID_FUENTE = "acnur"
ORGANISMO = "UNHCR Refugee Data Finder — API v1"
BASE = "https://api.unhcr.org/population/v1"
SLUG = "acnur-descubrimiento"

PAIS = "VEN"          # código de país de origen que se explora
ANIO_TOPE = date.today().year

# Rutas de referencia: catálogos, no datos. Sirven para saber contra qué
# lista completa se compara después la ausencia de un país.
RUTAS_REFERENCIA = ["countries", "years", "regions", "population-types"]

# Rutas de datos. Cada una es una serie distinta y solo algunas tocan
# migración o diáspora. Cuáles responden es parte de la pregunta 1.
RUTAS_DATOS = [
    "population",
    "asylum-applications",
    "asylum-decisions",
    "solutions",
    "demographics",
    "footnotes",
    "idmc",
    "unrwa",
]

# Columnas que NO son medidas: identifican la fila. Todo lo demás que
# venga numérico se trata como medida candidata.
COLUMNAS_DE_IDENTIDAD = {
    "year", "coo", "coo_iso", "coo_name", "coo_id",
    "coa", "coa_iso", "coa_name", "coa_id",
    "id", "region", "subregion",
}

LIMITE = 1000
MAX_PAGINAS = 20


def filas(js):
    """Saca la lista de filas del envoltorio que devuelva el API.

    No se asume la forma del envoltorio: se prueban las dos que se han
    visto —lista pelada y objeto con `items`— y si no es ninguna, se dice
    en vez de devolver una lista vacía silenciosa.
    """
    if js is None:
        return []
    if isinstance(js, list):
        return js
    if isinstance(js, dict):
        for clave in ("items", "data", "results"):
            if isinstance(js.get(clave), list):
                return js[clave]
    return []


def paginar(etiqueta, ruta, params, max_paginas=MAX_PAGINAS):
    """Recorre las páginas de una consulta y devuelve todas las filas."""
    acumuladas = []
    pagina = 1
    while pagina <= max_paginas:
        consulta = dict(params)
        consulta.update({"limit": LIMITE, "page": pagina})
        js = intentar(SLUG, f"{etiqueta}_p{pagina}", f"{BASE}/{ruta}", consulta)
        if js is None:
            break
        lote = filas(js)
        acumuladas.extend(lote)
        total_paginas = None
        if isinstance(js, dict):
            for clave in ("maxPages", "max_pages", "totalPages"):
                if isinstance(js.get(clave), int):
                    total_paginas = js[clave]
                    break
        if not lote or (total_paginas is not None and pagina >= total_paginas):
            break
        if total_paginas is None and len(lote) < LIMITE:
            break
        pagina += 1
    if pagina > max_paginas:
        print(f"    AVISO: se cortó en {max_paginas} páginas. Hay más dato.")
    return acumuladas


def columnas_numericas(muestra):
    """Columnas que se comportan como medida.

    Una columna entra si en ninguna fila trae texto: o número, o nulo. La
    parte del «o nulo» no es un detalle. Si solo se admitieran las que
    traen número en alguna fila, una columna nula en TODAS quedaría
    invisible — y ese es justamente el caso que la pregunta 4 tiene que
    ver: la medida que el organismo declara pero no llena para este país.
    """
    posibles, descartadas = [], set()
    for fila in muestra:
        if not isinstance(fila, dict):
            continue
        for clave, valor in fila.items():
            if clave in COLUMNAS_DE_IDENTIDAD or clave in descartadas:
                continue
            if valor is None:
                if clave not in posibles:
                    posibles.append(clave)
            elif isinstance(valor, (int, float)) and not isinstance(valor, bool):
                if clave not in posibles:
                    posibles.append(clave)
            else:
                descartadas.add(clave)
                if clave in posibles:
                    posibles.remove(clave)
    return posibles


# --------------------------------------------------------------------------
# [0] Preparación
# --------------------------------------------------------------------------

def paso_0_ultimo_anio():
    """Busca el año más reciente con dato, para que el resto se apoye ahí."""
    preparacion(
        "Localizar el último año con dato. Todas las consultas de abajo se "
        "apoyan en él, y la pregunta 3 lo reusa para medir el rezago."
    )

    js = intentar(SLUG, "00_anios", f"{BASE}/years/")
    anios = []
    for fila in filas(js):
        if isinstance(fila, dict):
            for clave in ("year", "id", "value"):
                if isinstance(fila.get(clave), int):
                    anios.append(fila[clave])
                    break
                if isinstance(fila.get(clave), str) and fila[clave].isdigit():
                    anios.append(int(fila[clave]))
                    break
        elif isinstance(fila, int):
            anios.append(fila)
        elif isinstance(fila, str) and fila.isdigit():
            anios.append(int(fila))

    if anios:
        ultimo = max(a for a in anios if a <= ANIO_TOPE)
        print(f"    El catálogo de años declara hasta {ultimo}.")
        return ultimo

    print("    El catálogo de años no respondió o no se entendió su forma.")
    print("    Se baja año por año desde el actual hasta encontrar dato.")
    for anio in range(ANIO_TOPE, ANIO_TOPE - 6, -1):
        js = intentar(
            SLUG, f"00_sondeo_{anio}", f"{BASE}/population/",
            {"year": anio, "coo": PAIS, "limit": 1},
        )
        if filas(js):
            print(f"    Primer año con dato encontrado: {anio}.")
            return anio

    print("    Ningún año de los últimos seis devolvió dato para " + PAIS + ".")
    return None


# --------------------------------------------------------------------------
# [1] Qué series existen
# --------------------------------------------------------------------------

def paso_1_series():
    pregunta(
        1,
        "Se prueban las rutas candidatas una por una. Una que falle no es "
        "un error: dice que esa vía no existe o cambió de nombre.",
    )

    vivas, muertas = [], []

    apartado("Rutas de referencia (catálogos)")
    for ruta in RUTAS_REFERENCIA:
        js = intentar(SLUG, f"01_ref_{ruta.replace('-', '_')}", f"{BASE}/{ruta}/")
        lote = filas(js)
        if js is not None:
            vivas.append(ruta)
            print(f"    {ruta:24} responde — {len(lote)} entradas")
            if lote and isinstance(lote[0], dict):
                print(f"      campos: {', '.join(sorted(lote[0]))}")
        else:
            muertas.append(ruta)

    apartado("Rutas de datos (series)")
    for ruta in RUTAS_DATOS:
        js = intentar(
            SLUG, f"01_serie_{ruta.replace('-', '_')}", f"{BASE}/{ruta}/",
            {"limit": 5},
        )
        lote = filas(js)
        if js is not None:
            vivas.append(ruta)
            print(f"    {ruta:24} responde — muestra de {len(lote)} filas")
            if lote and isinstance(lote[0], dict):
                print(f"      campos: {', '.join(sorted(lote[0]))}")
                medidas = columnas_numericas(lote)
                if medidas:
                    print(f"      medidas: {', '.join(sorted(medidas))}")
        else:
            muertas.append(ruta)

    apartado("Cuáles tocan migración o diáspora")
    print("    Esto no lo decide el script: lo decide quien lea los campos")
    print("    de arriba. Lo que el script sí puede decir es cuáles de esas")
    print("    rutas admiten filtrar por país de origen, que es la condición")
    print("    para que una serie sirva a una pieza sobre la diáspora.")

    admiten_origen = []
    for ruta in [r for r in RUTAS_DATOS if r in vivas]:
        js = intentar(
            SLUG, f"01_origen_{ruta.replace('-', '_')}", f"{BASE}/{ruta}/",
            {"coo": PAIS, "limit": 5},
        )
        lote = filas(js)
        if lote:
            admiten_origen.append(ruta)
            print(f"    {ruta:24} SÍ filtra por coo={PAIS} ({len(lote)} filas)")
        else:
            print(f"    {ruta:24} no devolvió filas con coo={PAIS}")

    if vivas:
        responde(
            1,
            f"{len(vivas)} rutas responden; {len(admiten_origen)} admiten "
            f"filtrar por país de origen: {', '.join(admiten_origen) or 'ninguna'}",
        )
    else:
        sin_responder(1, "ninguna ruta candidata respondió; el API cambió de forma")

    return admiten_origen


# --------------------------------------------------------------------------
# [2] Dimensiones
# --------------------------------------------------------------------------

def paso_2_dimensiones(anio):
    pregunta(
        2,
        "Se corre la misma consulta quitando una dimensión cada vez. Lo que "
        "importa no es si falla, sino si al omitirla el API agrega solo.",
    )

    if anio is None:
        sin_responder(2, "sin año de referencia no se puede montar la matriz")
        return

    consultas = [
        ("solo año", {"year": anio}),
        ("año + origen", {"year": anio, "coo": PAIS}),
        ("año + origen + coa_all", {"year": anio, "coo": PAIS, "coa_all": "true"}),
        ("año + origen + coo_all", {"year": anio, "coo": PAIS, "coo_all": "true"}),
        ("año + destino suelto", {"year": anio, "coa": "COL"}),
        ("origen sin año", {"coo": PAIS}),
    ]

    resultados = {}
    for etiqueta, params in consultas:
        clave = etiqueta.replace(" ", "_").replace("+", "y")
        js = intentar(
            SLUG, f"02_dim_{clave}", f"{BASE}/population/",
            {**params, "limit": 5},
        )
        lote = filas(js)
        total = None
        if isinstance(js, dict):
            for c in ("total", "totalElements", "maxPages"):
                if isinstance(js.get(c), int):
                    total = f"{c}={js[c]}"
                    break
        resultados[etiqueta] = len(lote)
        print(f"    {etiqueta:26} {len(lote)} filas en la muestra"
              + (f"  ({total})" if total else ""))
        if lote and isinstance(lote[0], dict):
            destino = lote[0].get("coa_name") or lote[0].get("coa") or "—"
            origen = lote[0].get("coo_name") or lote[0].get("coo") or "—"
            print(f"      primera fila: origen={origen} destino={destino}")

    apartado("Cuáles se agregan solas y cuáles no")
    print("    Si «año + origen» devuelve UNA fila y «año + origen + coa_all»")
    print("    devuelve muchas, el destino se agrega solo al total cuando se")
    print("    omite. Esa es la trampa: una consulta sin coa_all no da error,")
    print("    da el total, y quien no lo sepa publica un total creyendo que")
    print("    publica un desglose.")

    sin_todo = resultados.get("año + origen", 0)
    con_todo = resultados.get("año + origen + coa_all", 0)
    if sin_todo and con_todo and con_todo > sin_todo:
        veredicto = ("el destino se agrega solo al omitirlo; hay que pedir "
                     "coa_all para desglosar")
    elif sin_todo and con_todo and con_todo == sin_todo:
        veredicto = "omitir el destino no agrega: devuelve el mismo desglose"
    else:
        veredicto = "no concluyente con esta muestra; hay que mirar los JSON"

    responde(2, veredicto)


# --------------------------------------------------------------------------
# [3] Periodo y rezago
# --------------------------------------------------------------------------

def paso_3_periodo(anio):
    pregunta(
        3,
        "El rezago se mide desde el CIERRE del periodo, no desde su inicio: "
        "un anual de 2024 no lleva veinte meses de rezago en enero de 2025.",
    )

    if anio is None:
        sin_responder(3, "no se localizó ningún año con dato")
        return

    meses = rezago_en_meses(anio, mes=12)
    print(f"    Último año con dato: {anio}")
    print(f"    Hoy: {date.today().isoformat()}")
    print(f"    Rezago desde el cierre de {anio}: {meses} meses")

    apartado("Si la serie es anual, ese rezago fija el `meses_tolerados`")
    print("    de la sonda en data/fuentes.json. Conviene dejarlo por encima")
    print("    del rezago observado y no pegado a él: una fuente que publica")
    print("    con seis meses de retraso dispararía aviso cada año si el")
    print("    umbral se pone en seis.")

    responde(3, f"llega a {anio}; {meses} meses desde el cierre del periodo")


# --------------------------------------------------------------------------
# [4] La ausencia
# --------------------------------------------------------------------------

def paso_4_ausencia(anio):
    pregunta(
        4,
        "La más importante. Tres estados distintos, no dos: país que no "
        "aparece, país que aparece con nulo, país que aparece con cero.",
    )

    if anio is None:
        sin_responder(4, "sin año de referencia no hay contra qué comparar")
        return

    apartado("Lista completa de países según el propio catálogo")
    js = intentar(SLUG, "04_catalogo_paises", f"{BASE}/countries/")
    catalogo = {}
    for fila in filas(js):
        if not isinstance(fila, dict):
            continue
        codigo = fila.get("iso") or fila.get("code") or fila.get("id")
        nombre = fila.get("name") or fila.get("label") or codigo
        if codigo:
            catalogo[str(codigo)] = nombre
    print(f"    {len(catalogo)} países en el catálogo")

    apartado(f"Filas para origen={PAIS}, año {anio}, con destino desglosado")
    datos = paginar(
        "04_ven_por_destino", "population/",
        {"year": anio, "coo": PAIS, "coa_all": "true"},
    )
    print(f"    {len(datos)} filas")

    if not datos:
        sin_responder(4, f"el API no devolvió filas para coo={PAIS} en {anio}")
        return

    presentes = set()
    for fila in datos:
        codigo = fila.get("coa_iso") or fila.get("coa")
        if codigo:
            presentes.add(str(codigo))

    medidas = columnas_numericas(datos)
    apartado("Cómo se comporta cada columna en las filas que sí existen")
    print(f"    {'columna':28} {'nulo':>6} {'cero':>6} {'valor':>6}")
    for medida in sorted(medidas):
        conteo = {"nulo": 0, "cero": 0, "con valor": 0, "no numérico": 0}
        for fila in datos:
            conteo[clasificar(fila.get(medida))] += 1
        print(f"    {medida:28} {conteo['nulo']:>6} {conteo['cero']:>6} "
              f"{conteo['con valor']:>6}")

    apartado("Países del catálogo que NO aparecen como destino")
    ausentes = sorted(set(catalogo) - presentes)
    print(f"    {len(ausentes)} de {len(catalogo)}")
    for codigo in ausentes[:15]:
        print(f"      {codigo}  {catalogo[codigo]}")
    if len(ausentes) > 15:
        print(f"      ... y {len(ausentes) - 15} más (están en los JSON)")

    apartado("Notas al pie, que es donde suele estar el porqué de un hueco")
    js_pie = intentar(
        SLUG, "04_notas_al_pie", f"{BASE}/footnotes/",
        {"year": anio, "coo": PAIS, "limit": 50},
    )
    pies = filas(js_pie)
    if pies:
        print(f"    {len(pies)} notas para {PAIS} en {anio}")
        for pie in pies[:5]:
            if isinstance(pie, dict):
                print(f"      {str(pie)[:160]}")
    else:
        print("    Sin notas al pie, o la ruta no expone esta consulta.")

    print()
    print("    LECTURA: un país ausente y un país con cero NO son lo mismo.")
    print("    El ausente dice que el organismo no midió ahí; el cero dice")
    print("    que midió y no encontró a nadie. Solo el primero habla de qué")
    print("    se decide medir. Esa distinción es el campo `motivo` de")
    print("    limpio.json, y una barra vacía no se pinta como cero.")

    hay_nulos = any(
        clasificar(f.get(m)) == "nulo" for f in datos for m in medidas
    )
    responde(
        4,
        f"{len(presentes)} países presentes, {len(ausentes)} ausentes del "
        f"catálogo; nulos explícitos en las filas: {'sí' if hay_nulos else 'no'}",
    )


# --------------------------------------------------------------------------
# [5] Licencia
# --------------------------------------------------------------------------

def paso_5_licencia():
    pregunta(
        5,
        "Un script localiza una licencia; confirmarla es trabajo humano. "
        "Aquí solo se recoge lo que declara el propio servicio.",
    )

    apartado("Cabeceras de la respuesta del API")
    encontradas = {}
    try:
        r = requests.get(
            f"{BASE}/countries/", headers=CABECERAS, timeout=60,
        )
        interesantes = [
            "license", "x-license", "link", "terms", "x-terms",
            "copyright", "server", "content-type",
        ]
        for clave, valor in r.headers.items():
            if clave.lower() in interesantes:
                encontradas[clave] = valor
                print(f"    {clave}: {valor}")
        if not encontradas:
            print("    Ninguna cabecera declara licencia ni términos.")
        guardar(SLUG, "05_cabeceras.json", dict(r.headers))
    except Exception as e:
        print(f"    FALLO al leer cabeceras: {type(e).__name__} — {e}")

    apartado("Qué hay que abrir a mano, y por qué no vale la portada")
    print("    La portada de un organismo suele decir «datos abiertos» sin")
    print("    nombrar licencia. Lo que se registra en data/fuentes.json es")
    print("    el texto que obliga, no el eslogan. Abrir estas tres:")
    print("      https://www.unhcr.org/refugee-statistics/")
    print("      https://www.unhcr.org/terms-and-conditions")
    print("      https://api.unhcr.org/docs/refugee-statistics.html")
    print()
    print("    Lo que hay que sacar de ahí, en este orden:")
    print("      a) si permite reuso comercial")
    print("      b) si permite obra derivada (una pieza lo es)")
    print("      c) qué fórmula exacta de atribución exige")
    print("    Si el texto no nombra una licencia estándar, en fuentes.json")
    print("    NO se escribe «CC BY 4.0» por parecido: se escribe lo que")
    print("    dice, aunque quede feo. Hoy la entrada declara «Reuso con")
    print("    atribución», que es una descripción, no una licencia.")

    sin_responder(
        5,
        "requiere lectura humana de los términos; el script solo dejó las "
        "cabeceras guardadas y las tres URL que hay que abrir",
    )


# --------------------------------------------------------------------------
# [6] La hipótesis de la pieza
# --------------------------------------------------------------------------

def paso_6_hipotesis(anio):
    extra(6, "La hipótesis de la pieza (propio de ACNUR, fuera de las cinco)")

    print("    Hipótesis: la mayoría de las personas venezolanas desplazadas")
    print("    NO están contadas como refugiadas, sino bajo otras categorías")
    print("    de protección. Se comprueba sumando cada columna, sin decidir")
    print("    de antemano cuál es la que importa.")

    if anio is None:
        print("    Sin año de referencia no se puede comprobar.")
        return

    datos = paginar(
        "06_hipotesis", "population/",
        {"year": anio, "coo": PAIS, "coa_all": "true"},
    )
    if not datos:
        print("    Sin filas: la hipótesis queda sin comprobar.")
        return

    medidas = columnas_numericas(datos)
    totales = {}
    for medida in medidas:
        suma = 0
        for fila in datos:
            valor = fila.get(medida)
            if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                suma += valor
        totales[medida] = suma

    total_general = sum(totales.values())
    print()
    print(f"    Totales para origen={PAIS}, año {anio}:")
    for medida, suma in sorted(totales.items(), key=lambda x: -x[1]):
        parte = (suma / total_general * 100) if total_general else 0
        print(f"      {medida:30} {suma:>14,.0f}  {parte:5.1f} %")

    print()
    columnas_refugio = [m for m in totales if "refug" in m.lower()]
    suma_refugio = sum(totales[m] for m in columnas_refugio)
    if not total_general:
        print("    Todos los totales en cero: la hipótesis no se puede juzgar.")
        return

    parte_refugio = suma_refugio / total_general * 100
    print(f"    Columnas con «refug» en el nombre: "
          f"{', '.join(columnas_refugio) or 'ninguna'}")
    print(f"    Pesan {parte_refugio:.1f} % del total.")
    print()
    if parte_refugio < 50:
        print("    LA HIPÓTESIS SE SOSTIENE con estos números. La categoría")
        print("    mayoritaria es otra, y nombrarla bien es la pieza.")
    else:
        print("    LA HIPÓTESIS NO SE SOSTIENE con estos números. Mejor")
        print("    saberlo ahora: hay que reencuadrar la pieza antes de")
        print("    construir nada encima, no después.")
    print()
    print("    OJO antes de dar esto por bueno: sumar columnas de un mismo")
    print("    conjunto puede estar contando dos veces si alguna es un total")
    print("    y no una categoría. Antes de publicar el porcentaje hay que")
    print("    comprobar en la documentación que las columnas son disjuntas.")


def main():
    encabezado(FUENTE, ORGANISMO, SLUG)

    anio = paso_0_ultimo_anio()
    paso_1_series()
    paso_2_dimensiones(anio)
    paso_3_periodo(anio)
    paso_4_ausencia(anio)
    paso_5_licencia()
    paso_6_hipotesis(anio)

    cierre(FUENTE, ID_FUENTE)


if __name__ == "__main__":
    main()
