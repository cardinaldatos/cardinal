"""Genera sitio/public/og.png: la imagen de previsualización del sitio.

QUÉ ES Y POR QUÉ EXISTE

Cuando alguien comparte un enlace de cardinaldatos.org en WhatsApp, en
Slack o en cualquier red, el rastreador de esa plataforma lee las
etiquetas Open Graph del <head> y pinta una tarjeta. La imagen de esa
tarjeta es este archivo. Sin ella el enlace se ve pelado, y en el canal
principal de la diáspora venezolana un enlace pelado se lee como
sospechoso.

Vive en pipeline/ por el mismo motivo que mapa.py: es un script que
produce un archivo del sitio de forma determinista, no una pieza de datos.
Ni escribe en data/ ni publica cifras. La regla de «data/ es salida del
pipeline» no se toca aquí.

SIN CIFRAS, A PROPÓSITO

Esta lámina no lleva ningún número y no debe llevarlo nunca. Un dato
quemado en un PNG es una cifra escrita a mano: la auditoría no puede
leerla, no se regenera cuando el organismo revisa su serie, y se sigue
compartiendo con el valor viejo durante años. Si algún día se quieren
imágenes por pieza con su dato, se generan desde el limpio.json de esa
pieza y se regeneran con ella, no se dibujan aquí.

POR QUÉ NO USA UN NAVEGADOR

Los generadores de instagram/ arman HTML y lo fotografían con Playwright.
Aquí se dibuja directamente con Pillow. Dos razones: instalar Chromium
para una sola imagen estática es caro, y —más importante— aquellos
generadores cargan la tipografía desde Google Fonts, mientras que el sitio
la autoaloja desde que se quitó esa dependencia. Este script lee los mismos
.woff2 que sirve el sitio, así que la imagen usa exactamente la tipografía
publicada y no depende de ninguna red al generarse.

El isotipo se dibuja como polígonos con las mismas coordenadas del SVG que
está en el <header> de Base.astro y en favicon.svg. Son cuatro rectas y un
círculo: no hace falta un motor de SVG.

CÓMO SE CORRE

    cd pipeline && python og.py

Necesita Pillow, fonttools y brotli (fonttools descomprime woff2 con
brotli). Están en requirements.txt.

El resultado es determinista: dos ejecuciones sobre las mismas fuentes
producen el mismo PNG, así que no ensucia el historial si se vuelve a
correr sin cambios.
"""

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

RAIZ = Path(__file__).resolve().parent.parent
PUBLICO = RAIZ / "sitio" / "public"
SALIDA = PUBLICO / "og.png"

# 1200x630 es la medida que esperan los rastreadores de Open Graph y la
# proporción que usa Twitter para summary_large_image (1.91:1). Ir más
# grande no mejora nada y engorda el archivo; ir más chico hace que algunas
# plataformas degraden la tarjeta a formato pequeño.
ANCHO, ALTO = 1200, 630

# Se dibuja a 3x y se reduce al final. Pillow no antialiasa los polígonos
# al trazarlos, pero reducir una imagen grande sí produce bordes suaves.
ESCALA = 3

# La paleta del sistema, la misma de sistema.css y de instagram/.
TINTA = (20, 24, 28)        # #14181C
PAPEL = (241, 242, 239)     # #F1F2EF
ROJO = (192, 57, 47)        # #C0392F
PIZARRA = (92, 107, 114)    # #5C6B72
TEXTO_2 = (185, 190, 193)   # #B9BEC1
LINEA = (46, 54, 61)        # #2E363D

MARGEN = 76


def cargar_fuente(nombre, tamano):
    """Carga un .woff2 de sitio/public/ como fuente utilizable por Pillow.

    Pillow no abre woff2, así que fonttools lo reescribe a TrueType en
    memoria. No se guarda ningún .ttf en disco: sería un archivo derivado
    más que mantener y que podría desincronizarse del woff2 real.
    """
    fuente = TTFont(PUBLICO / f"{nombre}.woff2")
    fuente.flavor = None
    buffer = io.BytesIO()
    fuente.save(buffer)
    buffer.seek(0)
    return ImageFont.truetype(buffer, tamano)


def dibujar_isotipo(lienzo, x, y, lado):
    """El cardinal, con las coordenadas del SVG de Base.astro.

    El SVG original tiene viewBox 0 0 100 100 y un translate(0, 2) sobre el
    grupo; aquí ese desplazamiento va sumado en las coordenadas.
    """
    def p(px, py):
        return (x + px / 100 * lado, y + (py + 2) / 100 * lado)

    lienzo.polygon([p(50, 12), p(56, 46), p(50, 51), p(44, 46)], fill=ROJO)
    lienzo.polygon([p(88, 51), p(56, 57), p(50, 51), p(56, 45)], fill=PAPEL)
    lienzo.polygon([p(50, 79), p(44, 57), p(50, 51), p(56, 57)], fill=PAPEL)
    lienzo.polygon([p(12, 51), p(44, 45), p(50, 51), p(44, 57)], fill=PAPEL)

    cx, cy = p(50, 51)
    r = 2.4 / 100 * lado
    lienzo.ellipse([cx - r, cy - r, cx + r, cy + r], fill=TINTA)


def texto_espaciado(lienzo, xy, texto, fuente, relleno, espaciado):
    """Dibuja texto letra a letra para poder separar los caracteres.

    Pillow no tiene letter-spacing. La cejilla en monoespaciada del sistema
    lo lleva (0.14em en las láminas de Instagram, 0.16em en la web), y sin
    él no se reconoce como el mismo elemento de la identidad.
    """
    x, y = xy
    for caracter in texto:
        lienzo.text((x, y), caracter, font=fuente, fill=relleno)
        x += lienzo.textlength(caracter, font=fuente) + espaciado
    return x


def construir():
    ancho, alto = ANCHO * ESCALA, ALTO * ESCALA
    margen = MARGEN * ESCALA

    imagen = Image.new("RGB", (ancho, alto), TINTA)
    lienzo = ImageDraw.Draw(imagen)

    titular = cargar_fuente("archivo-v25-latin-700", 82 * ESCALA)
    cuerpo = cargar_fuente("ibm-plex-sans-v23-latin-regular", 26 * ESCALA)
    mono = cargar_fuente("ibm-plex-mono-v20-latin-regular", 21 * ESCALA)

    # --- Cabecera: isotipo y marca -------------------------------------
    lado_isotipo = 66 * ESCALA
    dibujar_isotipo(lienzo, margen, margen, lado_isotipo)

    texto_espaciado(
        lienzo,
        (margen + lado_isotipo + 18 * ESCALA, margen + 23 * ESCALA),
        "CARDINAL DATOS",
        mono,
        PIZARRA,
        3 * ESCALA,
    )

    # --- Titular --------------------------------------------------------
    # El mismo de la portada y de la lámina de presentación de Instagram.
    # La segunda línea va en rojo, como el <em> del titular en el sitio.
    y = margen + 148 * ESCALA
    interlinea = 92 * ESCALA

    lienzo.text((margen, y), "Datos que no se", font=titular, fill=PAPEL)
    lienzo.text((margen, y + interlinea), "traducen solos", font=titular, fill=ROJO)

    # --- Bajada ---------------------------------------------------------
    y_bajada = y + interlinea * 2 + 34 * ESCALA
    lienzo.text(
        (margen, y_bajada),
        "Estadísticas públicas sobre migración y diáspora, en español.",
        font=cuerpo,
        fill=TEXTO_2,
    )

    # --- Pie ------------------------------------------------------------
    y_linea = alto - margen - 46 * ESCALA
    lienzo.line(
        [(margen, y_linea), (ancho - margen, y_linea)],
        fill=LINEA,
        width=max(1, ESCALA),
    )

    texto_espaciado(
        lienzo,
        (margen, y_linea + 18 * ESCALA),
        "CARDINALDATOS.ORG",
        mono,
        PIZARRA,
        3 * ESCALA,
    )

    return imagen.resize((ANCHO, ALTO), Image.LANCZOS)


def main():
    imagen = construir()

    # optimize=True recomprime buscando el menor tamaño. Importa: WhatsApp
    # descarta previsualizaciones cuya imagen pesa de más, y con una paleta
    # plana como esta el archivo debería quedarse en decenas de kilobytes.
    imagen.save(SALIDA, "PNG", optimize=True)

    print(f"Escrito: {SALIDA.relative_to(RAIZ).as_posix()}")
    print(f"{SALIDA.stat().st_size} bytes · {ANCHO}x{ALTO}")


if __name__ == "__main__":
    main()
