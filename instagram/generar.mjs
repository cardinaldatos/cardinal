// Genera las imágenes de Instagram a partir de los datos ya limpios del
// pipeline. No inventa cifras: lee data/<slug>/limpio.json y arma el HTML
// con lo que ya pasó por comun.py.
//
// Formatos del plan: feed 1080×1350, historias 1080×1920. Hoy solo se monta
// el feed; historias y carrusel entran cuando este primero se valide.
//
// Estructura fija, la del plan: fuente arriba, titular, dato en rojo,
// atribución abajo.

import { chromium } from "playwright";
import { readFile, mkdir } from "node:fs/promises";
import path from "node:path";

const RAIZ = path.resolve(import.meta.dirname, "..");
const SALIDA = path.join(import.meta.dirname, "salida");

const FUENTES =
  "https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap";

// Coma decimal: el manual dice que las cifras hablan español.
const coma = (v, decimales = 2) =>
  Number(v).toLocaleString("es", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  });

/* --------------------------------------------------------------------
   PLANTILLA — formato feed, 1080×1350

   Ritmo vertical: la cejilla y el bloque central llevan una separación
   fija, y un espaciador con flex:1 absorbe el resto antes del pie. Así
   el hueco entre cejilla y titular no cambia según lo corto o largo que
   sea el texto — con space-between puro, un titular corto dejaba un
   salto enorme y descentraba la pieza.
   -------------------------------------------------------------------- */

function plantillaFeed({ fuente, anio, titular, moneda, datoValor, datoNota, pie }) {
  return `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="${FUENTES}" />
<style>
  :root {
    --tinta: #14181C;
    --rojo: #C0392F;
    --papel: #F1F2EF;
    --verde: #0E5A57;
    --ambar: #E0A02E;
    --pizarra: #5C6B72;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    width: 1080px;
    height: 1350px;
    background: var(--tinta);
    color: var(--papel);
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
    display: flex;
    flex-direction: column;
    padding: 84px 90px 76px;
  }

  .cejilla {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 26px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--pizarra);
    margin-bottom: 96px;
  }

  .marca {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 22px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--pizarra);
    margin-top: 20px;
  }

  .titular {
    font-family: 'Archivo', sans-serif;
    font-weight: 700;
    font-size: 64px;
    line-height: 1.12;
    letter-spacing: -0.01em;
    max-width: 15ch;
    margin-bottom: 44px;
  }

  /* El símbolo de moneda va pegado al número, más pequeño, alineado
     arriba — como un precio, no como una cifra suelta al lado. */
  .dato {
    display: flex;
    align-items: flex-start;
    gap: 4px;
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-weight: 500;
    color: var(--rojo);
    line-height: 1;
    font-size: 220px;
    margin-bottom: 28px;
  }

  .dato .moneda {
    font-size: 0.32em;
    margin-top: 0.2em;
  }

  .dato-nota {
    font-size: 30px;
    line-height: 1.5;
    color: #B9BEC1;
    max-width: 34ch;
  }

  /* Absorbe el espacio sobrante entre el bloque central y el pie. El
     bloque central ya no se estira: mantiene su tamaño natural pase lo
     que pase con la longitud del titular. */
  .espaciador {
    flex: 1;
  }

  .pie {
    font-size: 22px;
    line-height: 1.6;
    color: var(--pizarra);
    max-width: 46ch;
    border-top: 1px solid #2E363D;
    padding-top: 28px;
  }
</style>
</head>
<body>
  <p class="cejilla">${fuente} · ${anio}</p>

  <div class="centro">
    <p class="titular">${titular}</p>
    <p class="dato"><span class="moneda">${moneda}</span>${datoValor}</p>
    <p class="dato-nota">${datoNota}</p>
  </div>

  <div class="espaciador"></div>

  <div>
    <p class="pie">${pie}</p>
    <p class="marca">Cardinal Datos</p>
  </div>
</body>
</html>`;
}

/* --------------------------------------------------------------------
   PIEZAS A GENERAR
   Hoy: una del país más caro y una del más barato, de la pieza de
   remesas. Cuando haya más piezas publicadas, esta lista crece.
   -------------------------------------------------------------------- */

async function construirPiezasRemesas() {
  const rutaDatos = path.join(RAIZ, "data", "remesas-costo-latam", "limpio.json");
  const crudo = await readFile(rutaDatos, "utf-8");
  const datos = JSON.parse(crudo);

  const [masCaro] = datos.con_dato; // ya viene ordenado de mayor a menor
  const masBarato = datos.con_dato[datos.con_dato.length - 1];

  const piezaDe = (pais) => ({
    archivo: `remesas-${pais.iso3.toLowerCase()}.png`,
    fuente: "BANCO MUNDIAL",
    anio: pais.anio,
    titular: `Mandar ${coma(datos.monto_referencia_usd, 0)} dólares a ${pais.pais} cuesta`,
    moneda: "$",
    datoValor: coma(pais.sobre_200_usd),
    datoNota: `${coma(pais.costo_pct)} % del monto enviado — el costo promedio de transacción`,
    pie: `Costo promedio de enviar remesas, según el Banco Mundial (World Development Indicators). Cardinal Datos, ${pais.anio}.`,
  });

  return [piezaDe(masCaro), piezaDe(masBarato)];
}

/* --------------------------------------------------------------------
   RENDERIZADO
   -------------------------------------------------------------------- */

async function main() {
  await mkdir(SALIDA, { recursive: true });

  const piezas = await construirPiezasRemesas();

  const navegador = await chromium.launch();
  const pagina = await navegador.newPage({
    viewport: { width: 1080, height: 1350 },
    // deviceScaleFactor 1: renderizamos ya al tamaño final. Escalar aquí
    // solo generaría un PNG más grande que Instagram recortaría igual.
    deviceScaleFactor: 1,
  });

  for (const pieza of piezas) {
    const html = plantillaFeed(pieza);
    await pagina.setContent(html, { waitUntil: "networkidle" });

    const destino = path.join(SALIDA, pieza.archivo);
    await pagina.screenshot({ path: destino });
    console.log(`  generado: ${pieza.archivo}`);
  }

  await navegador.close();
  console.log(`\nListo. ${piezas.length} imagen(es) en ${SALIDA}`);
}

main().catch((e) => {
  console.error("FALLO:", e);
  process.exit(1);
});
