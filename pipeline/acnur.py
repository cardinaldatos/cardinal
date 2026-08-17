"""Categorías del desplazamiento venezolano — ACNUR (Refugee Data Finder).

Patrón: descargar → crudo.json → limpiar → limpio.json → metodo.md

La hipótesis que sostiene la pieza quedó confirmada en la exploración: de
las personas venezolanas contabilizadas por ACNUR, la mayoría no está
contada como refugiada. En 2025 la categoría mayoritaria era «otras
personas que necesitan protección internacional».

Pero el hallazgo no es el porcentaje. Es que esas mismas personas han sido
contadas bajo tres etiquetas distintas en seis años, y que la serie se
reescribió hacia atrás cada vez. Según la tabla de versiones de ACNUR:

  - hasta junio de 2020 estaban dentro de «otras personas de interés»
  - en junio de 2020 se introdujo el tipo «venezolanos desplazados en el
    exterior» y salieron de ahí
  - en octubre de 2022 ese tipo desapareció dentro de «otras personas que
    necesitan protección internacional», retroactivamente desde 2018, y
    ACNUR declaró que el término anterior ya no se usaría

Por eso la serie arranca en 2018 y no antes: es el año desde el que la
categoría actual está aplicada. Cualquier cifra publicada por terceros
antes de octubre de 2022 se refiere a una clasificación que ya no existe.

## Cuatro trampas de este API, todas descubiertas y todas evitadas aquí

1. **Omitir `coa` no da error: agrega.** Una consulta sin `coa_all`
   devuelve una sola fila con el destino escrito como «-», o sea el total.
   Quien no lo sepa publica un total creyendo publicar un desglose. Aquí
   se pide `coa_all` siempre y se descarta cualquier fila agregada.

2. **La ausencia se escribe como cadena vacía**, no como nulo ni como
   cero, y solo en algunas columnas. Se traduce a `motivo`, no a cero.

3. **Un cero puede no ser un cero.** ACNUR redondea los números menores
   que cinco al múltiplo de cinco más cercano antes de publicar, por
   confidencialidad. Un cero publicado significa entre cero y dos
   personas. Por eso hay dos motivos distintos para un cero, y la
   diferencia se deduce de los datos, no de una lista escrita a mano.

4. **`/years/` va por delante del dato.** Es el catálogo de años del API,
   llega hasta más allá del último año con dato, y encima cambió de valor
   entre dos ejecuciones del mismo día. El año de referencia se toma del
   dato que vuelve, nunca de ese catálogo.

## Qué NO entra en el denominador

Las nueve columnas de `population` no son nueve tipos de población. Siete
son existencias —los tipos— y dos son soluciones: `returned_refugees` es
el código RET y `returned_idps` es RDP. Las soluciones son flujos anuales
y meterlas en un denominador de existencias mezcla dos cosas distintas.
Para Venezuela las dos están en cero, así que el porcentaje saldría igual;
se excluyen de todos modos, porque la aritmética tiene que estar bien por
razones y no por casualidad.

Córrelo:  cd pipeline && python acnur.py
"""

from comun import escribir_metodo, guardar, pedir

SLUG = "desplazamiento-venezolano"
BASE = "https://api.unhcr.org/population/v1"

PAIS = "VEN"

# 2018 es el año desde el que ACNUR aplicó retroactivamente la categoría
# actual, y también el primer año en que el tipo existe según su matriz de
# disponibilidad. Antes de esa fecha la serie habla de otra clasificación.
ANIO_INICIO = 2018

LIMITE = 1000
MAX_PAGINAS = 20

# Marca con la que el API escribe una fila agregada. Si aparece, la fila
# es un total y no un destino: se descarta.
MARCA_AGREGADA = {"-", "", None}

# Las siete columnas que SÍ son tipos de población, con el nombre que usa
# ACNUR en español. No son traducciones propias: son los términos de sus
# publicaciones en español. Inventar un nombre para una categoría oficial
# sería inventar una definición.
#
# El orden importa: es el que conserva limpio.json y el que usa la web.
CATEGORIAS = [
    ("refugees", "Personas refugiadas"),
    ("asylum_seekers", "Solicitantes de asilo"),
    ("oip", "Otras personas que necesitan protección internacional"),
    ("ooc", "Otras personas de interés"),
    ("stateless", "Personas apátridas"),
    ("idps", "Personas desplazadas internas"),
    ("hst", "Comunidad de acogida"),
]

# Columnas de la misma respuesta que son soluciones, no existencias. Se
# conservan en limpio.json por transparencia y quedan fuera del total.
SOLUCIONES = [
    ("returned_refugees", "Personas refugiadas retornadas"),
    ("returned_idps", "Personas desplazadas internas retornadas"),
]

# La columna cuyo peso responde la pregunta de la pieza.
CATEGORIA_REFUGIO = "refugees"

# La traducción vive en el pipeline, no en cada superficie. El nombre
# original de ACNUR se conserva en limpio.json como pais_fuente.
#
# Esta lista NO pretende cubrir el mundo: cubre los destinos que aparecen
# en la serie de Venezuela. Si aparece uno nuevo, revisar() lo grita y no
# se publica en inglés a escondidas.
NOMBRES_ES = {
    "ABW": "Aruba", "ARG": "Argentina", "ATG": "Antigua y Barbuda",
    "AUS": "Australia", "AUT": "Austria", "BEL": "Bélgica",
    "BLZ": "Belice", "BOL": "Bolivia", "BRA": "Brasil", "BRB": "Barbados",
    "CAN": "Canadá", "CHE": "Suiza", "CHL": "Chile", "COL": "Colombia",
    "CRI": "Costa Rica", "CUB": "Cuba", "CUW": "Curazao",
    "CYM": "Islas Caimán", "CZE": "Chequia", "DEU": "Alemania",
    "DNK": "Dinamarca", "DOM": "República Dominicana", "ECU": "Ecuador",
    "ESP": "España", "EST": "Estonia", "FIN": "Finlandia",
    "FRA": "Francia", "GBR": "Reino Unido", "GRC": "Grecia",
    "GUY": "Guyana", "HND": "Honduras", "HRV": "Croacia",
    "HUN": "Hungría", "IRL": "Irlanda", "ISL": "Islandia",
    "ISR": "Israel", "ITA": "Italia", "JPN": "Japón",
    "KOR": "República de Corea", "LIE": "Liechtenstein",
    "LTU": "Lituania", "LUX": "Luxemburgo", "LVA": "Letonia",
    "MEX": "México", "MLT": "Malta", "NLD": "Países Bajos",
    "NOR": "Noruega", "NZL": "Nueva Zelanda", "PAN": "Panamá",
    "PER": "Perú", "POL": "Polonia", "PRT": "Portugal",
    "PRY": "Paraguay", "ROU": "Rumanía", "SLV": "El Salvador",
    "SVK": "Eslovaquia", "SVN": "Eslovenia", "SWE": "Suecia",
    "TTO": "Trinidad y Tobago", "TUR": "Türkiye", "URY": "Uruguay",
    "USA": "Estados Unidos", "ZAF": "Sudáfrica",
    # ACNUR usa dos códigos que no son países. Se traducen igual, porque
    # si aparecen tienen que aparecer legibles y no como sigla cruda.
    "UNK": "Varios o desconocido",
}


# ---------------------------------------------------------------------------
# Descarga
# ---------------------------------------------------------------------------

def filas(js):
    """Saca las filas del envoltorio de este API."""
    if isinstance(js, dict) and isinstance(js.get("items"), list):
        return js["items"]
    if isinstance(js, list):
        return js
    raise ValueError("respuesta con una forma que no se reconoce")


def paginar(ruta, params):
    """Recorre las páginas de una consulta y devuelve todas las filas."""
    acumuladas, pagina = [], 1
    while pagina <= MAX_PAGINAS:
        consulta = dict(params, limit=LIMITE, page=pagina)
        js = pedir(f"{BASE}/{ruta}", consulta)
        lote = filas(js)
        acumuladas.extend(lote)
        total = js.get("maxPages") if isinstance(js, dict) else None
        if not lote or (total is not None and pagina >= total):
            break
        if total is None and len(lote) < LIMITE:
            break
        pagina += 1
    else:
        raise RuntimeError(
            f"la consulta a {ruta} pasó de {MAX_PAGINAS} páginas. Hay más "
            f"dato del que se está recogiendo y publicar así sería publicar "
            f"un recorte silencioso."
        )
    return acumuladas


def descargar():
    """Dos consultas: la serie por destino, y las notas al pie de la fuente.

    Una sola consulta cubre todos los años. No se pide año por año ni se
    pregunta cuál es el último: se piden todos desde ANIO_INICIO y el
    último con dato se deduce de lo que vuelve. El catálogo de años de
    este API no es de fiar para eso.
    """
    crudo = []

    print(f"  pidiendo: población por destino, {PAIS}, desde {ANIO_INICIO}")
    params_pob = {
        "coo": PAIS,
        "coa_all": "true",
        "yearFrom": ANIO_INICIO,
    }
    crudo.append({
        "consulta": "poblacion_por_destino",
        "url": f"{BASE}/population/",
        "params": params_pob,
        "respuesta": {"items": paginar("population/", params_pob)},
    })

    print(f"  pidiendo: notas al pie, {PAIS}, desde {ANIO_INICIO}")
    params_pie = {"coo": PAIS, "yearFrom": ANIO_INICIO}
    crudo.append({
        "consulta": "notas_al_pie",
        "url": f"{BASE}/footnotes/",
        "params": params_pie,
        "respuesta": {"items": paginar("footnotes/", params_pie)},
    })

    print("  pidiendo: catálogo de países")
    crudo.append({
        "consulta": "catalogo_paises",
        "url": f"{BASE}/countries/",
        "params": {},
        "respuesta": pedir(f"{BASE}/countries/"),
    })

    return crudo


# ---------------------------------------------------------------------------
# Limpieza
# ---------------------------------------------------------------------------

def numero(valor):
    """Convierte una celda a número, o a None si no hay dato.

    Tres cosas distintas llegan aquí y no se pueden aplanar: un número,
    una cadena vacía —que es como este API escribe la ausencia— y un
    nulo. Solo la primera se convierte.
    """
    if valor is None:
        return None
    if isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float)):
        return valor
    texto = str(valor).strip()
    if texto in {"", "-", "n/a", "N/A"}:
        return None
    try:
        return float(texto.replace(",", "."))
    except ValueError:
        return None


def columnas_de_relleno(filas_anio, claves):
    """Columnas que están en cero en TODAS las filas de un año.

    Es la regla que separa los dos tipos de cero, y se deduce de los datos
    en vez de escribirse a mano. Una columna que vale cero en las
    cincuenta y cinco filas del año no está midiendo: es relleno del
    esquema. Para un desglose por país de acogida, «personas desplazadas
    internas» no puede tener otro valor.

    Una columna que en cambio tiene valores en unas filas y cero en otras
    sí está midiendo, y ahí el cero significa lo que significa en esta
    fuente: entre cero y dos personas, por el redondeo de confidencialidad.
    """
    relleno = set()
    for clave in claves:
        presentes = [
            v for v in (numero(f.get(clave)) for f in filas_anio)
            if v is not None
        ]
        # Una columna sin ningún valor legible NO es relleno: es una
        # columna sin recoger, y ese es otro motivo. Confundirlas volvería
        # a aplanar la distinción que este campo existe para mantener.
        if presentes and all(v == 0 for v in presentes):
            relleno.add(clave)
    return relleno


def motivo_de(valor, clave, relleno):
    """Por qué esta celda no tiene una cifra utilizable. None si la tiene.

    Cuatro motivos, no uno. El campo existe justamente porque «no hay
    dato» significa cosas distintas y pintarlas todas como cero es el
    error que la pieza tiene que no cometer.
    """
    crudo = valor
    if crudo is None:
        return "nulo"
    if isinstance(crudo, str) and crudo.strip() in {"", "-", "n/a", "N/A"}:
        return "no_recogido"
    n = numero(crudo)
    if n is None:
        return "ilegible"
    if n == 0:
        return "cero_de_esquema" if clave in relleno else "cero_redactado"
    return None


MOTIVOS = {
    "nulo": "La celda viene nula. No hay valor declarado.",
    "no_recogido": (
        "La columna existe en el esquema pero para este país no se recoge. "
        "El API lo escribe como cadena vacía, no como cero."
    ),
    "cero_de_esquema": (
        "Cero en una columna que está en cero para todos los destinos de "
        "ese año. No es una medición: es relleno del esquema."
    ),
    "cero_redactado": (
        "Cero en una columna que en otros destinos sí tiene valor. Por la "
        "salvaguarda de confidencialidad de ACNUR, que redondea los "
        "números menores que cinco al múltiplo de cinco más cercano, "
        "significa entre cero y dos personas. No es un cero exacto."
    ),
    "ilegible": "El valor no se pudo leer como número.",
}


def limpiar(crudo):
    """Arma la serie por año y el desglose por destino del último año."""
    todas = filas(crudo[0]["respuesta"])
    pies = filas(crudo[1]["respuesta"])
    catalogo_bruto = filas(crudo[2]["respuesta"])

    claves_pob = [c for c, _ in CATEGORIAS]
    claves_sol = [c for c, _ in SOLUCIONES]

    # --- Descartar filas agregadas y años fuera de rango ----------------
    # El filtro por año se repite aquí aunque la consulta ya lo pida: si
    # yearFrom dejara de funcionar, la serie se llenaría de años viejos
    # que hablan de otra clasificación y nadie lo notaría.
    utiles, agregadas = [], 0
    for f in todas:
        anio = f.get("year")
        if not isinstance(anio, int) or anio < ANIO_INICIO:
            continue
        destino = f.get("coa_iso") or f.get("coa")
        nombre = f.get("coa_name")
        if destino in MARCA_AGREGADA or nombre in MARCA_AGREGADA:
            agregadas += 1
            continue
        utiles.append(f)

    if not utiles:
        raise ValueError(
            "no quedó ninguna fila utilizable. O el API cambió de forma, o "
            "la consulta devolvió solo el total agregado."
        )

    anios = sorted({f["year"] for f in utiles})
    anio_ultimo = max(anios)

    # --- Serie por año --------------------------------------------------
    serie = []
    destinos_por_anio = {}
    for anio in anios:
        del_anio = [f for f in utiles if f["year"] == anio]
        relleno = columnas_de_relleno(del_anio, claves_pob)

        por_categoria = {}
        for clave, _ in CATEGORIAS:
            suma = sum(
                n for n in (numero(f.get(clave)) for f in del_anio)
                if n is not None
            )
            por_categoria[clave] = int(round(suma))

        soluciones = {}
        for clave, _ in SOLUCIONES:
            suma = sum(
                n for n in (numero(f.get(clave)) for f in del_anio)
                if n is not None
            )
            soluciones[clave] = int(round(suma))

        total = sum(por_categoria.values())
        refugio = por_categoria.get(CATEGORIA_REFUGIO, 0)

        serie.append({
            "anio": anio,
            "destinos": len(del_anio),
            "total": total,
            "por_categoria": por_categoria,
            "soluciones": soluciones,
            "parte_refugio": round(refugio / total * 100, 1) if total else None,
            "columnas_de_relleno": sorted(relleno),
        })

        destinos_por_anio[anio] = {
            str(f.get("coa_iso") or f.get("coa")) for f in del_anio
        }

    # --- Cómo cambia la lista de destinos de un año a otro ---------------
    # Un país que entra o sale de la lista no es gente que llegó o se fue:
    # es un país que ese año reportó o no reportó. Si la pieza dibuja un
    # mapa por año, esto tiene que estar declarado o el mapa miente.
    cambios = []
    for anterior, actual in zip(anios, anios[1:]):
        cambios.append({
            "de": anterior,
            "a": actual,
            "entraron": sorted(destinos_por_anio[actual] - destinos_por_anio[anterior]),
            "salieron": sorted(destinos_por_anio[anterior] - destinos_por_anio[actual]),
        })

    # --- Desglose por destino del último año ----------------------------
    del_ultimo = [f for f in utiles if f["year"] == anio_ultimo]
    relleno_ultimo = columnas_de_relleno(del_ultimo, claves_pob)

    destinos, sin_traducir = [], set()
    for f in del_ultimo:
        iso = str(f.get("coa_iso") or f.get("coa"))
        nombre_fuente = f.get("coa_name") or iso
        if iso not in NOMBRES_ES:
            sin_traducir.add((iso, nombre_fuente))

        categorias, motivos = {}, {}
        for clave, _ in CATEGORIAS:
            categorias[clave] = numero(f.get(clave))
            motivo = motivo_de(f.get(clave), clave, relleno_ultimo)
            if motivo:
                motivos[clave] = motivo

        soluciones = {c: numero(f.get(c)) for c in claves_sol}

        total = sum(v for v in categorias.values() if v)
        destinos.append({
            "coa": iso,
            "pais": NOMBRES_ES.get(iso, nombre_fuente),
            "pais_fuente": nombre_fuente,
            "total": int(round(total)),
            "categorias": {k: (int(round(v)) if v is not None else None)
                           for k, v in categorias.items()},
            "soluciones": {k: (int(round(v)) if v is not None else None)
                           for k, v in soluciones.items()},
            "motivos": motivos,
        })

    destinos.sort(key=lambda d: d["total"], reverse=True)

    # --- La ausencia de país, declarada sin interpretarla ---------------
    # Aquí NO se publica la lista de los que faltan. La exploración
    # comprobó que pedir un par origen-destino ausente no devuelve fila
    # ninguna: este API no distingue «no se midió» de «no había nadie».
    # Publicar 177 países como «sin dato» les atribuiría un significado
    # que el dato no tiene. Se declara el hueco y se declara que no es
    # interpretable, que es lo único cierto.
    codigos_catalogo = {
        str(c.get("iso")) for c in catalogo_bruto
        if isinstance(c, dict) and c.get("iso")
    }
    con_fila = {d["coa"] for d in destinos}

    ausencia = {
        "paises_en_catalogo": len(codigos_catalogo),
        "destinos_con_fila": len(con_fila),
        "sin_fila": len(codigos_catalogo - con_fila),
        "distinguible": False,
        "nota": (
            "Un país que no aparece como destino puede ser un país sin "
            "personas venezolanas contabilizadas o un país que no reporta. "
            "Se comprobó pidiendo pares origen-destino ausentes uno por "
            "uno: el API no devuelve fila, así que no distingue los dos "
            "casos. La ausencia no se interpreta."
        ),
    }

    # --- Notas al pie de la propia fuente -------------------------------
    notas = []
    vistas = set()
    for p in pies:
        if not isinstance(p, dict):
            continue
        texto = (p.get("footnote") or "").strip()
        if not texto or texto in vistas:
            continue
        vistas.add(texto)
        notas.append({
            "anio": p.get("year"),
            "destino": p.get("coa_iso") or p.get("coa"),
            "tipo_de_poblacion": p.get("population_type"),
            "texto": texto,
        })

    return {
        "fuente": "ACNUR — UNHCR Refugee Data Finder, API v1",
        "anio_inicio": ANIO_INICIO,
        "anio": anio_ultimo,
        "anios": anios,
        "categorias": [
            {"id": c, "nombre": n, "tipo": "poblacion"} for c, n in CATEGORIAS
        ] + [
            {"id": c, "nombre": n, "tipo": "solucion"} for c, n in SOLUCIONES
        ],
        "categoria_refugio": CATEGORIA_REFUGIO,
        "serie": serie,
        "cambios_de_destinos": cambios,
        "destinos": destinos,
        "ausencia": ausencia,
        "motivos": MOTIVOS,
        "filas_agregadas_descartadas": agregadas,
        "redaccion": {
            "regla": (
                "ACNUR redondea los números menores que cinco al múltiplo "
                "de cinco más cercano antes de publicar, por "
                "confidencialidad, y redondea las decisiones de asilo "
                "entre cinco y diez."
            ),
            "consecuencia": (
                "Un cero publicado significa entre cero y dos personas, y "
                "los totales son aproximaciones. Lo declara la propia "
                "fuente en su página de estructura de datos."
            ),
        },
    }


def plural(n, singular, plural_):
    """«1 salida» y no «1 salidas». El texto de metodo.md se publica."""
    return f"{n} {singular if n == 1 else plural_}"


# ---------------------------------------------------------------------------
# Revisión
# ---------------------------------------------------------------------------

def revisar(limpio):
    """Avisos que no deben pasar desapercibidos al publicar."""
    ultimo = next(s for s in limpio["serie"] if s["anio"] == limpio["anio"])

    print(f"  Serie: {limpio['anios'][0]}–{limpio['anio']} "
          f"({len(limpio['anios'])} años)")
    print(f"  Destinos en {limpio['anio']}: {ultimo['destinos']}")
    print(f"  Total contabilizado: {ultimo['total']:,}".replace(",", "."))

    nombres = {c["id"]: c["nombre"] for c in limpio["categorias"]}
    for clave, valor in sorted(ultimo["por_categoria"].items(),
                               key=lambda x: -x[1]):
        if not ultimo["total"]:
            continue
        parte = valor / ultimo["total"] * 100
        print(f"    {nombres[clave][:46]:46} {valor:>12,} {parte:5.1f} %"
              .replace(",", "."))

    print(f"  Peso de «{nombres[limpio['categoria_refugio']]}»: "
          f"{ultimo['parte_refugio']} %")

    if limpio["filas_agregadas_descartadas"]:
        print(f"  Se descartaron {limpio['filas_agregadas_descartadas']} "
              f"filas agregadas. Es lo esperado: el API las devuelve cuando "
              f"una dimensión no está desglosada.")

    if ultimo["columnas_de_relleno"]:
        cuales = ", ".join(nombres[c] for c in ultimo["columnas_de_relleno"])
        print(f"  Columnas en cero para todos los destinos: {cuales}")
        print("         Se marcan como cero_de_esquema, no como medición.")

    redactados = sum(
        1 for d in limpio["destinos"]
        for m in d["motivos"].values() if m == "cero_redactado"
    )
    if redactados:
        print(f"  {redactados} celdas con cero redactado (entre 0 y 2 "
              f"personas). NO son ceros exactos.")

    a = limpio["ausencia"]
    print(f"  {a['destinos_con_fila']} de {a['paises_en_catalogo']} países "
          f"del catálogo aparecen como destino.")
    print("         Los que faltan NO se publican como sin dato: el API no "
          "distingue ausencia de medición.")

    for c in limpio["cambios_de_destinos"]:
        if c["entraron"] or c["salieron"]:
            print(f"  {c['de']}→{c['a']}: entraron "
                  f"{len(c['entraron'])}, salieron {len(c['salieron'])}")

    # Traducciones que faltan. Esto es un aviso fuerte a propósito: sin
    # él, un destino nuevo se publicaría con su nombre en inglés y nadie
    # lo vería hasta que un lector lo señalara.
    faltan = [d for d in limpio["destinos"] if d["pais"] == d["pais_fuente"]
              and d["coa"] not in NOMBRES_ES]
    if faltan:
        print()
        print("  AVISO IMPORTANTE: hay destinos sin traducir. Se están "
              "publicando con su nombre en inglés.")
        for d in faltan:
            print(f"    {d['coa']}  {d['pais_fuente']}")
        print("  Añádelos a NOMBRES_ES en este script antes de publicar. La "
              "traducción vive en el pipeline, no en la web.")


# ---------------------------------------------------------------------------

def main():
    print(f"Categorías del desplazamiento venezolano — ACNUR ({PAIS})")
    print("=" * 66)

    crudo = descargar()
    guardar(SLUG, "crudo.json", crudo)

    limpio = limpiar(crudo)
    guardar(SLUG, "limpio.json", limpio)

    print()
    revisar(limpio)

    ultimo = next(s for s in limpio["serie"] if s["anio"] == limpio["anio"])
    nombres = {c["id"]: c["nombre"] for c in limpio["categorias"]}
    a = limpio["ausencia"]
    entradas = sum(len(c["entraron"]) for c in limpio["cambios_de_destinos"])
    salidas = sum(len(c["salieron"]) for c in limpio["cambios_de_destinos"])
    redactados = sum(
        1 for d in limpio["destinos"]
        for m in d["motivos"].values() if m == "cero_redactado"
    )
    relleno = ", ".join(nombres[c] for c in ultimo["columnas_de_relleno"]) or "ninguna"

    escribir_metodo(
        SLUG,
        fuente="ACNUR — UNHCR Refugee Data Finder, API v1, conjunto de "
               "población de fin de año por país de origen y de acogida.",
        url=f"{BASE}/population/?coo={PAIS}&coa_all=true&yearFrom={ANIO_INICIO}",
        definicion=(
            "Personas venezolanas contabilizadas por ACNUR fuera de "
            "Venezuela, repartidas entre los tipos de población que la "
            "propia fuente distingue. Los nombres de las categorías son "
            "los que ACNUR usa en sus publicaciones en español; no son "
            "traducciones propias.\n\n"
            f"La serie arranca en {ANIO_INICIO} porque es el año desde el "
            "que ACNUR aplicó retroactivamente la categoría «otras "
            "personas que necesitan protección internacional», y también "
            "el primer año en que ese tipo existe en su matriz de "
            "disponibilidad.\n\n"
            "Según la nota al pie de la propia fuente, la columna de "
            "personas refugiadas incluye a las personas en situación "
            "similar a la de refugiado.\n\n"
            f"Último año con dato: {limpio['anio']}. No se toma del "
            "catálogo de años del API, que llega más lejos que el dato."
        ),
        limites=(
            "1. Los números son aproximaciones por decisión de la fuente. "
            "ACNUR redondea los valores menores que cinco al múltiplo de "
            "cinco más cercano antes de publicar, por confidencialidad, y "
            "declara que los totales deben considerarse aproximados. La "
            "consecuencia práctica: un cero publicado significa entre cero "
            f"y dos personas. En {limpio['anio']} hay "
            f"{plural(redactados, 'celda', 'celdas')} en ese caso, y "
            "limpio.json las marca como cero_redactado.\n\n"
            "2. No todos los ceros dicen lo mismo. Las columnas que valen "
            "cero para todos los destinos del año no están midiendo nada: "
            "son relleno del esquema, porque el concepto no aplica a un "
            f"desglose por país de acogida. En {limpio['anio']} son: "
            f"{relleno}. Se marcan como cero_de_esquema y no se dibujan.\n\n"
            "3. El denominador incluye solo tipos de población, no "
            "soluciones. La misma respuesta trae columnas de personas "
            "retornadas, que son flujos anuales y no existencias; "
            "sumarlas al total mezclaría dos cosas distintas. Se conservan "
            "en limpio.json y quedan fuera del porcentaje.\n\n"
            "4. La ausencia de un país no es interpretable. De los "
            f"{a['paises_en_catalogo']} países del catálogo de ACNUR, "
            f"{a['destinos_con_fila']} aparecen como destino. Se comprobó "
            "pidiendo pares origen-destino ausentes uno por uno: el API no "
            "devuelve fila, así que no distingue «no se midió» de «no "
            "había nadie». Por eso los que faltan no se publican como "
            "países sin dato.\n\n"
            "5. La lista de destinos cambia de un año a otro. En el "
            f"periodo cubierto hubo {plural(entradas, 'entrada', 'entradas')} "
            f"y {plural(salidas, 'salida', 'salidas')} "
            "de la lista. Un país que aparece o desaparece no es "
            "gente que llegó o se fue: es un país que ese año reportó o "
            "dejó de reportar.\n\n"
            "6. La serie fue reclasificada dos veces y reescrita hacia "
            "atrás. Las personas venezolanas contadas hoy como «otras "
            "personas que necesitan protección internacional» estaban "
            "antes bajo «venezolanos desplazados en el exterior», tipo "
            "introducido en junio de 2020, y antes de eso dentro de «otras "
            "personas de interés». En octubre de 2022 ACNUR absorbió el "
            "tipo intermedio en el actual, retroactivamente desde 2018, y "
            "declaró que el término anterior dejaría de usarse. Cualquier "
            "cifra publicada por terceros antes de esa fecha se refiere a "
            "una clasificación que ya no existe y no es comparable con "
            "esta.\n\n"
            "7. Omitir el país de acogida en la consulta no da error: el "
            "API agrega la dimensión y devuelve el total en una sola fila, "
            "con el destino escrito como un guion. Esta consulta pide el "
            "desglose explícitamente y descarta las filas agregadas que "
            "aun así lleguen; limpio.json registra cuántas fueron."
        ),
    )

    print("\nListo.")


if __name__ == "__main__":
    main()
