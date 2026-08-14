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
nada encima: la sección [6] existe para eso y para nada más.

## Lo que se aprendió en la ejecución del 14 de agosto de 2026

Tres cosas, y las tres están corregidas en este archivo:

1. `/years/` NO es la lista de años con dato: es el catálogo de años del
   API, y llega hasta el año en curso. La primera versión lo tomó por
   bueno, consultó 2026, recibió cero filas en todas partes y dejó tres
   preguntas sin responder por una causa que no tenía nada que ver con
   la fuente. Ahora el año se confirma pidiendo dato, no leyendo un
   catálogo, y el hueco entre los dos se publica como lo que es: una
   característica del API.

2. ACNUR escribe la ausencia como **cadena vacía**, no como nulo ni como
   cero. La primera versión descartaba una columna entera en cuanto
   traía texto, así que de las nueve medidas de `population` solo vio
   `refugees`. Se perdían las tres donde se juega la hipótesis.

3. `/population-types/` devuelve 404. Los tipos de población no tienen
   catálogo propio, pero `footnotes` trae un campo `population_type`:
   de ahí se enumeran.

## Lo que este script sigue sin dar por sabido

Los nombres de columna se imprimen todos, con sus totales. Buscar por el
nombre que uno espera es el método más fiable de encontrar lo que uno ya
creía, y aquí lo que está en juego es si la hipótesis se sostiene.

Córrelo:  cd pipeline && python explorar_acnur.py
"""

from datetime import date

import requests

from comun import CABECERAS, guardar
from explorar_comun import (
    apartado,
    aviso,
    cierre,
    clasificar,
    columnas_de_medida,
    encabezado,
    extra,
    intentar,
    pregunta,
    preparacion,
    responde,
    rezago_en_meses,
    sin_responder,
    tabla_de_ausencia,
)

FUENTE = "ACNUR"
ID_FUENTE = "acnur"
ORGANISMO = "UNHCR Refugee Data Finder — API v1"
BASE = "https://api.unhcr.org/population/v1"
SLUG = "acnur-descubrimiento"

PAIS = "VEN"          # país de origen que se explora
DESTINO_CONTROL = "COL"   # destino usado para probar la dimensión contraria
ANIO_TOPE = date.today().year
ANIOS_A_PROBAR = 6    # cuántos años se baja buscando el último con dato

# Rutas de referencia: catálogos, no datos. `population-types` dio 404 el
# 14 de agosto de 2026. Se sigue probando porque cuesta una petición y
# porque si vuelve, es la vía limpia de enumerar los tipos de población.
RUTAS_REFERENCIA = ["countries", "years", "regions", "population-types"]

# Rutas de datos. `idmc` y `unrwa` no devolvieron nada con coo=VEN, lo
# cual tiene sentido: son desplazamiento interno y población palestina.
# Se siguen probando para que el informe lo diga en vez de suponerlo.
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

# Columnas que identifican la fila. Todo lo demás es medida candidata.
COLUMNAS_DE_IDENTIDAD = {
    "year", "coo", "coo_iso", "coo_name", "coo_id",
    "coa", "coa_iso", "coa_name", "coa_id",
    "id", "region", "subregion",
    "app_type", "dec_level", "procedure_type",
    "footnote", "population_type",
}

# Columnas de `population` cuyo significado NO es evidente por el nombre
# y del que depende la hipótesis. Sin su definición no se publica ningún
# porcentaje: `ooc` y `oip` pueden ser categorías disjuntas o solaparse.
COLUMNAS_A_DEFINIR = ["ooc", "oip", "hst"]

LIMITE = 1000
MAX_PAGINAS = 20


def filas(js):
    """Saca la lista de filas del envoltorio que devuelva el API."""
    if js is None:
        return []
    if isinstance(js, list):
        return js
    if isinstance(js, dict):
        for clave in ("items", "data", "results"):
            if isinstance(js.get(clave), list):
                return js[clave]
    return []


def paginas(js):
    """Número de páginas que declara la respuesta, si lo declara."""
    if isinstance(js, dict):
        for clave in ("maxPages", "max_pages", "totalPages"):
            if isinstance(js.get(clave), int):
                return js[clave]
    return None


def medidas_de(muestra):
    return columnas_de_medida(muestra, COLUMNAS_DE_IDENTIDAD)


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
        total = paginas(js)
        if not lote or (total is not None and pagina >= total):
            break
        if total is None and len(lote) < LIMITE:
            break
        pagina += 1
    else:
        aviso(f"se cortó en {max_paginas} páginas; hay más dato del recogido")
    return acumuladas


# --------------------------------------------------------------------------
# [0] Preparación
# --------------------------------------------------------------------------

def paso_0_ultimo_anio():
    """Encuentra el último año que DEVUELVE dato, no el que el API lista.

    La distinción costó una ejecución entera. El catálogo de años llega
    hasta el año en curso, así que creerle produce consultas vacías en
    cadena y tres preguntas sin responder por una causa inventada.
    """
    preparacion(
        "Confirmar el último año con dato pidiendo dato, no leyendo el "
        "catálogo. Todo lo de abajo se apoya en él."
    )

    js = intentar(SLUG, "00_anios", f"{BASE}/years/")
    catalogados = []
    for fila in filas(js):
        valor = fila.get("year") if isinstance(fila, dict) else fila
        if isinstance(valor, int):
            catalogados.append(valor)
        elif isinstance(valor, str) and valor.isdigit():
            catalogados.append(int(valor))

    tope_catalogo = max(catalogados) if catalogados else ANIO_TOPE
    print(f"    El catálogo declara {len(catalogados)} años, hasta {tope_catalogo}.")

    for anio in range(min(tope_catalogo, ANIO_TOPE), tope_catalogo - ANIOS_A_PROBAR, -1):
        js = intentar(
            SLUG, f"00_sondeo_{anio}", f"{BASE}/population/",
            {"year": anio, "coo": PAIS, "coa_all": "true", "limit": 1},
        )
        if filas(js):
            print(f"    Último año que devuelve dato para {PAIS}: {anio}.")
            hueco = tope_catalogo - anio
            if hueco:
                print(f"    El catálogo va {hueco} año(s) por delante del dato.")
                print("    Eso NO es un error del API: es una característica que")
                print("    hay que declarar. Un script que consulte el máximo del")
                print("    catálogo recibe cero filas y no se entera de por qué.")
            return anio, tope_catalogo
        print(f"    {anio}: sin filas.")

    aviso(f"ningún año de los últimos {ANIOS_A_PROBAR} devolvió dato para {PAIS}")
    return None, tope_catalogo


# --------------------------------------------------------------------------
# [1] Qué series existen
# --------------------------------------------------------------------------

def paso_1_series():
    pregunta(
        1,
        "Se prueban las rutas candidatas una por una. Una que falle no es "
        "un error: dice que esa vía no existe o cambió de nombre.",
    )

    vivas = []

    apartado("Rutas de referencia (catálogos)")
    for ruta in RUTAS_REFERENCIA:
        js = intentar(SLUG, f"01_ref_{ruta.replace('-', '_')}", f"{BASE}/{ruta}/")
        lote = filas(js)
        if js is None:
            continue
        vivas.append(ruta)
        print(f"    {ruta:24} responde — {len(lote)} entradas")
        if lote and isinstance(lote[0], dict):
            print(f"      campos: {', '.join(sorted(lote[0]))}")

    apartado("Rutas de datos (series)")
    for ruta in RUTAS_DATOS:
        js = intentar(
            SLUG, f"01_serie_{ruta.replace('-', '_')}", f"{BASE}/{ruta}/",
            {"limit": 20},
        )
        lote = filas(js)
        if js is None:
            continue
        vivas.append(ruta)
        print(f"    {ruta:24} responde — muestra de {len(lote)} filas")
        if lote and isinstance(lote[0], dict):
            print(f"      campos:  {', '.join(sorted(lote[0]))}")
            medidas = medidas_de(lote)
            print(f"      medidas: {', '.join(medidas) or 'ninguna'}")

    apartado("Cuáles tocan migración o diáspora")
    print("    Lo decide quien lea los campos de arriba. Lo que el script sí")
    print("    puede decir es cuáles admiten filtrar por país de origen, que")
    print("    es la condición para que una serie sirva a una pieza sobre la")
    print("    diáspora.")

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
            f"filtrar por origen: {', '.join(admiten_origen) or 'ninguna'}",
        )
    else:
        sin_responder(1, "ninguna ruta candidata respondió; el API cambió de forma")

    return admiten_origen


# --------------------------------------------------------------------------
# [2] Dimensiones
# --------------------------------------------------------------------------

def sondear_dimension(etiqueta, params):
    """Pide una fila y lee cuántas páginas declara la respuesta.

    Con limit=1, el número de páginas es el número de filas totales. Sale
    mucho más barato que traerse el conjunto entero solo para contarlo.
    """
    clave = etiqueta.replace(" ", "_").replace("+", "y")
    js = intentar(
        SLUG, f"02_dim_{clave}", f"{BASE}/population/", {**params, "limit": 1},
    )
    lote = filas(js)
    total = paginas(js)
    marca = ""
    if lote and isinstance(lote[0], dict):
        origen = lote[0].get("coo_name") or lote[0].get("coo") or "—"
        destino = lote[0].get("coa_name") or lote[0].get("coa") or "—"
        marca = f"origen={origen} destino={destino}"
    print(f"    {etiqueta:30} {str(total) if total is not None else '?':>6} filas"
          + (f"   {marca}" if marca else ""))
    return total, lote


def paso_2_dimensiones(anio):
    pregunta(
        2,
        "Se corre la misma consulta quitando una dimensión cada vez. Lo que "
        "importa no es si falla, sino si al omitirla el API agrega solo.",
    )

    if anio is None:
        sin_responder(2, "sin año con dato no se puede montar la matriz")
        return

    apartado(f"Matriz de dimensiones sobre `population`, año {anio}")
    sin_destino, filas_sin = sondear_dimension(
        "año + origen (sin coa_all)", {"year": anio, "coo": PAIS})
    con_destino, _ = sondear_dimension(
        "año + origen + coa_all", {"year": anio, "coo": PAIS, "coa_all": "true"})
    sin_origen, _ = sondear_dimension(
        "año + destino (sin coo_all)", {"year": anio, "coa": DESTINO_CONTROL})
    con_origen, _ = sondear_dimension(
        "año + destino + coo_all", {"year": anio, "coa": DESTINO_CONTROL,
                                    "coo_all": "true"})
    sondear_dimension("solo año", {"year": anio})
    sondear_dimension("origen sin año", {"coo": PAIS})

    apartado("Cuáles se agregan solas y cuáles no")

    marca_agregada = None
    if filas_sin and isinstance(filas_sin[0], dict):
        marca_agregada = filas_sin[0].get("coa_name") or filas_sin[0].get("coa")
    if marca_agregada is not None:
        print(f"    Con el destino omitido, la fila lo trae como: «{marca_agregada}»")
        print("    Ese valor es la marca de fila agregada. Si un script pidiera")
        print("    sin coa_all y guardara el resultado, publicaría el total")
        print("    creyendo que publica un desglose, y sin ningún error de por")
        print("    medio que lo delatara.")

    veredictos = []
    if sin_destino and con_destino:
        if con_destino > sin_destino:
            veredictos.append("el destino se agrega solo si se omite; hay que pedir coa_all")
        else:
            veredictos.append("omitir el destino no agrega")
    if sin_origen and con_origen:
        if con_origen > sin_origen:
            veredictos.append("el origen también se agrega solo; hay que pedir coo_all")
        else:
            veredictos.append("omitir el origen no agrega")

    if veredictos:
        responde(2, "; ".join(veredictos))
    else:
        sin_responder(2, "la matriz no devolvió conteos comparables")


# --------------------------------------------------------------------------
# [3] Periodo y rezago
# --------------------------------------------------------------------------

def paso_3_periodo(anio, tope_catalogo):
    pregunta(
        3,
        "El rezago se mide desde el CIERRE del periodo, no desde su inicio: "
        "un anual de 2024 no lleva veinte meses de rezago en enero de 2025.",
    )

    if anio is None:
        sin_responder(3, "no se localizó ningún año con dato")
        return

    meses = rezago_en_meses(anio, mes=12)
    print(f"    Último año con dato:      {anio}")
    print(f"    Último año del catálogo:  {tope_catalogo}")
    print(f"    Hoy:                      {date.today().isoformat()}")
    print(f"    Rezago desde el cierre de {anio}: {meses} meses")

    if meses < 0:
        aviso("rezago negativo: el año medido todavía no ha cerrado. "
              "Es un error de método, no un dato de la fuente.")
        sin_responder(3, f"rezago negativo sobre {anio}; hay que revisar el paso 0")
        return

    apartado("Ese rezago fija el `meses_tolerados` de la sonda")
    print("    Conviene dejarlo por encima del rezago observado y no pegado a")
    print("    él: una fuente que publica con seis meses de retraso dispararía")
    print("    aviso cada año si el umbral se pone en seis.")

    responde(3, f"llega a {anio}; {meses} meses desde el cierre del periodo")


# --------------------------------------------------------------------------
# [4] La ausencia
# --------------------------------------------------------------------------

def paso_4_ausencia(anio):
    pregunta(
        4,
        "La más importante. Cuatro estados distintos: país que no aparece, "
        "celda nula, celda vacía, y cero. Solo el cero significa medición.",
    )

    if anio is None:
        sin_responder(4, "sin año con dato no hay contra qué comparar")
        return []

    apartado("Lista completa de países según el propio catálogo")
    js = intentar(SLUG, "04_catalogo_paises", f"{BASE}/countries/")
    catalogo = {}
    for fila in filas(js):
        if not isinstance(fila, dict):
            continue
        codigo = fila.get("iso") or fila.get("code") or fila.get("id")
        nombre = fila.get("name") or fila.get("nameShort") or codigo
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
        return []

    presentes = set()
    for fila in datos:
        codigo = fila.get("coa_iso") or fila.get("coa")
        if codigo:
            presentes.add(str(codigo))

    medidas = medidas_de(datos)
    apartado("Cómo se comporta cada medida en las filas que sí existen")
    conteos = tabla_de_ausencia(datos, medidas)

    apartado("Con qué escribe ACNUR la ausencia")
    total_nulo = sum(c["nulo"] for c in conteos.values())
    total_vacio = sum(c["vacío"] for c in conteos.values())
    total_cero = sum(c["cero"] for c in conteos.values())
    print(f"    nulos: {total_nulo}   vacíos: {total_vacio}   ceros: {total_cero}")
    if total_vacio and not total_nulo:
        forma = "cadena vacía (nunca null)"
    elif total_nulo and not total_vacio:
        forma = "null (nunca cadena vacía)"
    elif total_vacio and total_nulo:
        forma = "las dos: null y cadena vacía, y hay que averiguar si difieren"
    else:
        forma = "ni null ni vacío: toda celda trae número"
    print(f"    Forma de la ausencia: {forma}")

    apartado("Países del catálogo que NO aparecen como destino")
    ausentes = sorted(set(catalogo) - presentes)
    print(f"    {len(ausentes)} de {len(catalogo)}")
    for codigo in ausentes[:15]:
        print(f"      {codigo}  {catalogo[codigo]}")
    if len(ausentes) > 15:
        print(f"      ... y {len(ausentes) - 15} más (están en los JSON)")

    apartado("Tipos de población, que no tienen catálogo propio")
    print("    /population-types/ devuelve 404. Pero footnotes trae el campo")
    print("    population_type, así que los tipos se enumeran desde ahí.")
    js_pie = intentar(
        SLUG, "04_notas_al_pie", f"{BASE}/footnotes/",
        {"year": anio, "coo": PAIS, "limit": 200},
    )
    pies = filas(js_pie)
    tipos = sorted({p.get("population_type") for p in pies
                    if isinstance(p, dict) and p.get("population_type")})
    if tipos:
        print(f"    Tipos vistos en las notas de {PAIS}: {', '.join(tipos)}")
    if pies:
        print(f"    {len(pies)} notas al pie para {PAIS} en {anio}. Primeras:")
        for pie in pies[:5]:
            if isinstance(pie, dict):
                print(f"      [{pie.get('coa_iso') or '—'}] "
                      f"{str(pie.get('footnote'))[:140]}")
    else:
        print("    Sin notas al pie para este país y año.")

    print()
    print("    LECTURA: un país ausente y un país con cero NO son lo mismo.")
    print("    El ausente dice que el organismo no midió ahí; el cero dice que")
    print("    midió y no encontró a nadie. Solo el primero habla de qué se")
    print("    decide medir. Y la celda vacía es un tercer caso: la columna")
    print("    existe en el esquema pero para ese país no se recoge. Esa")
    print("    distinción es el campo `motivo` de limpio.json.")

    responde(
        4,
        f"{len(presentes)} destinos presentes, {len(ausentes)} del catálogo "
        f"sin aparecer; la ausencia se escribe como {forma}",
    )

    return datos


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
    try:
        r = requests.get(f"{BASE}/countries/", headers=CABECERAS, timeout=60)
        interesantes = ["license", "x-license", "link", "terms", "x-terms",
                        "copyright", "server", "content-type"]
        halladas = {k: v for k, v in r.headers.items()
                    if k.lower() in interesantes}
        for clave, valor in halladas.items():
            print(f"    {clave}: {valor}")
        if not any(k.lower() in {"license", "x-license", "terms", "x-terms",
                                 "copyright", "link"} for k in halladas):
            print("    Ninguna cabecera declara licencia ni términos.")
            print("    Ya se comprobó el 14 de agosto de 2026: solo Content-Type")
            print("    y Server. Por esta vía no va a venir.")
        guardar(SLUG, "05_cabeceras.json", dict(r.headers))
    except Exception as e:
        print(f"    FALLO al leer cabeceras: {type(e).__name__} — {e}")

    apartado("Qué hay que abrir a mano, y por qué no vale la portada")
    print("    La portada de un organismo suele decir «datos abiertos» sin")
    print("    nombrar licencia. Lo que se registra en data/fuentes.json es el")
    print("    texto que obliga, no el eslogan. Abrir estas tres:")
    print("      https://www.unhcr.org/refugee-statistics/")
    print("      https://www.unhcr.org/terms-and-conditions")
    print("      https://api.unhcr.org/docs/refugee-statistics.html")
    print()
    print("    Lo que hay que sacar de ahí, en este orden:")
    print("      a) si permite reuso comercial")
    print("      b) si permite obra derivada (una pieza lo es)")
    print("      c) qué fórmula exacta de atribución exige")
    print("    Si el texto no nombra una licencia estándar, en fuentes.json NO")
    print("    se escribe «CC BY 4.0» por parecido: se escribe lo que dice,")
    print("    aunque quede feo. Hoy la entrada declara «Reuso con atribución»,")
    print("    que es una descripción, no una licencia.")

    sin_responder(
        5,
        "requiere lectura humana de los términos; el API no declara licencia "
        "en cabeceras y hay tres URL que abrir",
    )


# --------------------------------------------------------------------------
# [6] La hipótesis de la pieza
# --------------------------------------------------------------------------

def paso_6_hipotesis(anio, datos):
    extra(6, "La hipótesis de la pieza (propio de ACNUR, fuera de las cinco)")

    print("    Hipótesis: la mayoría de las personas venezolanas desplazadas")
    print("    NO están contadas como refugiadas, sino bajo otras categorías")
    print("    de protección. Se comprueba sumando cada columna, sin decidir")
    print("    de antemano cuál es la que importa.")
    print()
    print("    Nota de la primera ejecución: `population` NO tiene columna de")
    print("    «venezolanos desplazados en el exterior». Si la categoría")
    print("    existe, está dentro de ooc, oip o hst.")

    if anio is None:
        print("    Sin año con dato no se puede comprobar.")
        return

    # Se reusan las filas que ya trajo el paso 4. Volver a pedirlas
    # duplicaría la descarga entera para llegar al mismo sitio.
    if not datos:
        print("    Sin filas: la hipótesis queda sin comprobar.")
        return

    medidas = medidas_de(datos)
    totales = {}
    for medida in medidas:
        suma = 0
        for fila in datos:
            valor = fila.get(medida)
            if clasificar(valor) in ("cero", "con valor"):
                suma += float(str(valor).replace(",", "."))
        totales[medida] = suma

    total_general = sum(totales.values())
    print()
    print(f"    Totales para origen={PAIS}, año {anio}:")
    for medida, suma in sorted(totales.items(), key=lambda x: -x[1]):
        parte = (suma / total_general * 100) if total_general else 0
        print(f"      {medida:24} {suma:>16,.0f}  {parte:5.1f} %")

    if not total_general:
        print("    Todos los totales en cero: la hipótesis no se puede juzgar.")
        return

    columnas_refugio = [m for m in totales if "refug" in m.lower()
                        and "returned" not in m.lower()]
    suma_refugio = sum(totales[m] for m in columnas_refugio)
    parte_refugio = suma_refugio / total_general * 100

    print()
    print(f"    Columnas contadas como refugio: "
          f"{', '.join(columnas_refugio) or 'ninguna'}")
    print(f"    Pesan {parte_refugio:.1f} % del total.")
    mayor = max(totales, key=totales.get)
    print(f"    Categoría mayoritaria: {mayor} ({totales[mayor]:,.0f})")
    print()
    if parte_refugio < 50:
        print("    LA HIPÓTESIS SE SOSTIENE con estos números. La categoría")
        print("    mayoritaria es otra, y nombrarla bien es la pieza.")
    else:
        print("    LA HIPÓTESIS NO SE SOSTIENE con estos números. Mejor saberlo")
        print("    ahora: hay que reencuadrar la pieza antes de construir nada")
        print("    encima, no después.")

    print()
    print("    LO QUE FALTA ANTES DE PUBLICAR ESTE PORCENTAJE:")
    print(f"    definir {', '.join(COLUMNAS_A_DEFINIR)} con el texto del propio")
    print("    ACNUR, en https://api.unhcr.org/docs/refugee-statistics.html")
    print("    Dos razones. Una: si alguna de esas columnas es un total y no")
    print("    una categoría, la suma cuenta a la misma persona dos veces y el")
    print("    porcentaje está mal. Dos: si la categoría mayoritaria resulta")
    print("    ser la que agrupa a las personas venezolanas, la pieza depende")
    print("    de nombrarla con la definición oficial y no con una traducción")
    print("    propia. Eso es texto de la fuente, no cifra: no lo puede sacar")
    print("    este script.")


def main():
    encabezado(FUENTE, ORGANISMO, SLUG)

    anio, tope_catalogo = paso_0_ultimo_anio()
    paso_1_series()
    paso_2_dimensiones(anio)
    paso_3_periodo(anio, tope_catalogo)
    datos = paso_4_ausencia(anio)
    paso_5_licencia()
    paso_6_hipotesis(anio, datos)

    cierre(FUENTE, ID_FUENTE)


if __name__ == "__main__":
    main()
