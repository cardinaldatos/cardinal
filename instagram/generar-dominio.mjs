// Post de anuncio de dominio propio. Como el de presentación, no reporta
// una cifra, así que no sigue la estructura fuente/titular/dato/atribución.
//
// Aquí el dato central es la URL nueva: por eso se lleva el rojo, y por eso
// es lo único rojo de la lámina. La anterior va tachada en pizarra — sigue
// funcionando, pero deja de ser la buena.
//
// El isotipo es el archivo real de 01 — Identidad (cardinal-isotipo.svg),
// variante de fondo oscuro. Se pega tal cual, sin recolorear ni rotar.

import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { FUENTES } from "./comun.mjs";

const SALIDA = path.join(import.meta.dirname, "salida");

const ISOTIPO = `
<svg viewBox="0 0 100 100" width="96" height="96" role="img" aria-label="Cardinal">
  <g transform="translate(0, 2)">
    <path d="M50 12 L56 46 L50 51 L44 46 Z" fill="#C0392F"/>
    <path d="M88 51 L56 57 L50 51 L56 45 Z" fill="#F1F2EF"/>
    <path d="M50 79 L44 57 L50 51 L56 57 Z" fill="#F1F2EF"/>
    <path d="M12 51 L44 45 L50 51 L44 57 Z" fill="#F1F2EF"/>
    <circle cx="50" cy="51" r="2.4" fill="#14181C"/>
  </g>
</svg>`;

function plantillaDominio() {
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
    margin-bottom: 120px;
  }

  .titular {
    font-family: 'Archivo', sans-serif;
    font-weight: 700;
    font-size: 76px;
    line-height: 1.08;
    letter-spacing: -0.015em;
    margin-bottom: 72px;
  }

  /* El dominio anterior: sigue vivo, pero ya no es el bueno. Tachado con
     una línea de 2px — no es sombra ni degradado, solo una regla. */
  .anterior {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 34px;
    color: var(--pizarra);
    text-decoration: line-through;
    text-decoration-thickness: 2px;
    margin-bottom: 26px;
  }

  .flecha {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 34px;
    color: var(--pizarra);
    margin-bottom: 26px;
  }

  /* El dato central de esta lámina. Único rojo, como manda el manual. */
  .nuevo {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-weight: 500;
    font-size: 62px;
    color: var(--rojo);
    letter-spacing: -0.01em;
    line-height: 1.1;
  }

  .espaciador { flex: 1; }

  .nota {
    font-size: 24px;
    line-height: 1.6;
    color: #B9BEC1;
    max-width: 40ch;
    border-top: 1px solid #2E363D;
    padding-top: 28px;
  }

  .cierre {
    display: flex;
    align-items: center;
    gap: 24px;
    margin-top: 40px;
  }

  .marca {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 22px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--pizarra);
  }
</style>
</head>
<body>
  <p class="cejilla">Casa nueva</p>

  <p class="titular">Cardinal Datos<br />tiene dominio<br />propio</p>

  <p class="anterior">cardinaldatos.workers.dev</p>
  <p class="flecha">↓</p>
  <p class="nuevo">cardinaldatos.org</p>

  <div class="espaciador"></div>

  <p class="nota">
    Mismas piezas, mismo método, misma regla: si un dato no se puede
    rastrear hasta un archivo público, no se publica.
  </p>

  <div class="cierre">
    ${ISOTIPO}
    <p class="marca">Cardinal Datos</p>
  </div>
</body>
</html>`;
}

async function main() {
  await mkdir(SALIDA, { recursive: true });

  const navegador = await chromium.launch();
  const pagina = await navegador.newPage({
    viewport: { width: 1080, height: 1350 },
    deviceScaleFactor: 1,
  });

  await pagina.setContent(plantillaDominio(), { waitUntil: "networkidle" });
  const destino = path.join(SALIDA, "dominio.png");
  await pagina.screenshot({ path: destino });

  await navegador.close();
  console.log(`Listo: ${destino}`);
}

main().catch((e) => {
  console.error("FALLO:", e);
  process.exit(1);
});
