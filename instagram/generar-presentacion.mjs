// Post de presentación — el primero de la cuenta, antes de cualquier pieza
// de datos. No sigue la estructura fija del plan (fuente/titular/dato/
// atribución) porque no reporta una cifra: presenta el proyecto.
//
// El isotipo es el archivo real de 01 — Identidad (cardinal-isotipo.svg),
// ya coloreado para fondo oscuro según el manual: brazo norte en rojo,
// los otros tres en papel, punto central en tinta. Se pega el <path> tal
// cual, sin recolorear ni rotar — el manual lo prohíbe explícitamente.
//
// La descripción larga es la misma frase del manual, palabra por palabra:
// no se redacta una nueva.

import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const SALIDA = path.join(import.meta.dirname, "salida");

const FUENTES =
  "https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap";

// Isotipo real, tal cual, en su variante de fondo oscuro
// (01 — Identidad / cardinal-isotipo.svg). Sin el <rect> de fondo: aquí
// el fondo lo pone la plantilla.
const ISOTIPO = `
<svg viewBox="0 0 100 100" width="220" height="220" role="img" aria-label="Cardinal">
  <g transform="translate(0, 2)">
    <path d="M50 12 L56 46 L50 51 L44 46 Z" fill="#C0392F"/>
    <path d="M88 51 L56 57 L50 51 L56 45 Z" fill="#F1F2EF"/>
    <path d="M50 79 L44 57 L50 51 L56 57 Z" fill="#F1F2EF"/>
    <path d="M12 51 L44 45 L50 51 L44 57 Z" fill="#F1F2EF"/>
    <circle cx="50" cy="51" r="2.4" fill="#14181C"/>
  </g>
</svg>`;

function plantillaPresentacion() {
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
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 90px;
  }

  .isotipo { margin-bottom: 44px; }

  .wordmark {
    font-family: 'Archivo', sans-serif;
    font-weight: 700;
    font-size: 88px;
    letter-spacing: -0.02em;
    margin-bottom: 28px;
  }

  .tagline {
    font-family: 'Archivo', sans-serif;
    font-weight: 700;
    font-size: 42px;
    line-height: 1.25;
    letter-spacing: -0.01em;
    margin-bottom: 40px;
  }

  .tagline em { font-style: normal; color: var(--rojo); }

  .mision {
    font-size: 26px;
    line-height: 1.6;
    color: #B9BEC1;
    max-width: 34ch;
    margin-bottom: 90px;
  }

  .pie {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 22px;
    letter-spacing: 0.08em;
    color: var(--pizarra);
    line-height: 1.8;
  }
</style>
</head>
<body>
  <div class="isotipo">${ISOTIPO}</div>

  <p class="wordmark">Cardinal</p>

  <p class="tagline">Datos que no se<br /><em>traducen solos</em></p>

  <p class="mision">
    Recogemos estadísticas públicas sobre migración y diáspora que existen,
    pero casi nadie puede leer. Las volvemos comprensibles, en español.
  </p>

  <p class="pie">
    Proyecto colectivo · método siempre declarado<br />
    cardinaldatos.org
  </p>
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

  await pagina.setContent(plantillaPresentacion(), { waitUntil: "networkidle" });
  const destino = path.join(SALIDA, "presentacion.png");
  await pagina.screenshot({ path: destino });

  await navegador.close();
  console.log(`Listo: ${destino}`);
}

main().catch((e) => {
  console.error("FALLO:", e);
  process.exit(1);
});
