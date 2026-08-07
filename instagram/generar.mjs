// Genera las imágenes de Instagram a partir de los datos ya limpios del
// pipeline. No inventa cifras: lee data/<slug>/limpio.json y arma el HTML
// con lo que ya pasó por comun.py.
//
// Estructura fija, la del plan: fuente arriba, titular, dato en rojo,
// atribución abajo. Debajo del dato va el mini-ranking de los diez
// países — ver comun.mjs.

import { chromium } from "playwright";
import { readFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { FUENTES, coma, CSS_MINI_RANKING, renderMiniRanking } from "./comun.mjs";

const RAIZ = path.resolve(import.meta.dirname, "..");
const SALIDA = path.join(import.meta.dirname, "salida");

function plantillaFeed({ fuente, anio, titular, moneda, datoValor, datoNota, miniRankingHtml, pie }) {
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

  .dato .moneda { font-size: 0.32em; margin-top: 0.2em; }

  .dato-nota {
    font-size: 30px;
    line-height: 1.5;
    color: #B9BEC1;
    max-width: 34ch;
    margin-bottom: 44px;
  }

  .espaciador { flex: 1; }

  .pie {
    font-size: 22px;
    line-height: 1.6;
    color: var(--pizarra);
    max-width: 46ch;
    border-top: 1px solid #2E363D;
    padding-top: 28px;
  }

  ${CSS_MINI_RANKING}
</style>
</head>
<body>
  <p class="cejilla">${fuente} · ${anio}</p>

  <div class="centro">
    <p class="titular">${titular}</p>
    <p class="dato"><span class="moneda">${moneda}</span>${datoValor}</p>
    <p class="dato-nota">${datoNota}</p>
    ${miniRankingHtml}
  </div>

  <div class="espaciador"></div>

  <div>
    <p class="pie">${pie}</p>
    <p class="marca">Cardinal Datos</p>
  </div>
</body>
</html>`;
}

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
    miniRankingHtml: renderMiniRanking(datos.con_dato, pais.iso3),
    pie: `Costo promedio de enviar remesas, según el Banco Mundial (World Development Indicators). Cardinal Datos, ${pais.anio}.`,
  });

  return [piezaDe(masCaro), piezaDe(masBarato)];
}

async function main() {
  await mkdir(SALIDA, { recursive: true });

  const piezas = await construirPiezasRemesas();

  const navegador = await chromium.launch();
  const pagina = await navegador.newPage({
    viewport: { width: 1080, height: 1350 },
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
