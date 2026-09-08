// Genera el carrusel de Instagram para la pieza de remesas: cinco láminas,
// 1080×1350 cada una (misma medida que el feed — el plan no fija una
// distinta para carrusel).
//
// Narrativa: gancho → el más caro → el más barato → el hallazgo del hueco
// → cierre con llamada a la web.
//
// Los nombres de país ya vienen en español desde limpio.json. Antes había
// aquí un diccionario propio para los países sin dato; se quitó al mover
// la traducción al pipeline.
//
// Ninguna lámina escribe una cifra. El año de la serie, cuántos países
// tienen dato, cuántos no y el monto de referencia salen todos de
// limpio.json, igual que en la web. Antes estaban tecleados —«Diez
// países», «Tres países», «2023» repetido en cuatro sitios— y eran las
// únicas cifras publicadas del proyecto que ninguna comprobación miraba:
// la regla de oro solo auditaba sitio/. Una imagen no se recompila
// cuando cambian los datos, así que habrían envejecido en silencio hasta
// contradecir a la web, que sí los deriva. Las dos superficies leen ahora
// el mismo archivo y no pueden discrepar.

import { chromium } from "playwright";
import { readFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { FUENTES, coma, CSS_MINI_RANKING, renderMiniRanking } from "./comun.mjs";

const RAIZ = path.resolve(import.meta.dirname, "..");
const SALIDA = path.join(import.meta.dirname, "salida");

/* --------------------------------------------------------------------
   ARMAZÓN COMÚN A LAS CINCO LÁMINAS
   -------------------------------------------------------------------- */

function documento({ cejilla, indice, total, cuerpo, pie, cssExtra = "" }) {
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

  .encabezado {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 96px;
  }

  .cejilla {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 26px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--pizarra);
  }

  .contador {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 24px;
    letter-spacing: 0.1em;
    color: var(--pizarra);
  }

  .marca {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 22px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--pizarra);
    margin-top: 20px;
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
  ${cssExtra}
</style>
</head>
<body>
  <div class="encabezado">
    <p class="cejilla">${cejilla}</p>
    <p class="contador">${indice} · ${total}</p>
  </div>

  ${cuerpo}

  <div class="espaciador"></div>

  <div>
    ${pie ? `<p class="pie">${pie}</p>` : ""}
    <p class="marca">Cardinal Datos</p>
  </div>
</body>
</html>`;
}

/* --------------------------------------------------------------------
   LÁMINA 1 — Gancho
   -------------------------------------------------------------------- */

function laminaPortada({ total, conDato, monto }) {
  const cuerpo = `
    <p class="titular-carrusel">
      ${conDato} países.<br />Un mismo envío.<br /><em>¿Cuánto se queda</em><br /><em>en el camino?</em>
    </p>
    <p class="subida">
      ${coma(monto, 0)} dólares enviados a América Latina. Esto es lo que se
      pierde antes de llegar.
    </p>
  `;
  return documento({
    cejilla: "CARDINAL DATOS",
    indice: 1,
    total,
    cuerpo,
    pie: null,
    cssExtra: `
      .titular-carrusel {
        font-family: 'Archivo', sans-serif;
        font-weight: 700;
        font-size: 68px;
        line-height: 1.1;
        letter-spacing: -0.01em;
        margin-bottom: 32px;
      }
      .titular-carrusel em { font-style: normal; color: var(--rojo); }
      .subida {
        font-size: 30px;
        line-height: 1.55;
        color: #B9BEC1;
        max-width: 30ch;
      }
    `,
  });
}

/* --------------------------------------------------------------------
   LÁMINAS 2 y 3 — El más caro / el más barato
   Ahora con el mini-ranking de los países con dato debajo del dato.
   -------------------------------------------------------------------- */

function laminaExtremo({ indice, total, etiqueta, pais, datoValor, costoPct, todosLosPaises, anio }) {
  const cuerpo = `
    <p class="kicker">${etiqueta}</p>
    <p class="titular-extremo">${pais.pais}</p>
    <p class="dato"><span class="moneda">$</span>${datoValor}</p>
    <p class="dato-nota">${coma(costoPct)} % del monto enviado</p>
    ${renderMiniRanking(todosLosPaises, pais.iso3)}
  `;
  return documento({
    cejilla: `BANCO MUNDIAL · ${anio}`,
    indice,
    total,
    cuerpo,
    pie: null,
    cssExtra: `
      .kicker {
        font-family: 'IBM Plex Mono', ui-monospace, monospace;
        font-size: 24px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--pizarra);
        margin-bottom: 16px;
      }
      .titular-extremo {
        font-family: 'Archivo', sans-serif;
        font-weight: 700;
        font-size: 72px;
        letter-spacing: -0.01em;
        margin-bottom: 40px;
      }
      .dato {
        display: flex;
        align-items: flex-start;
        gap: 4px;
        font-family: 'IBM Plex Mono', ui-monospace, monospace;
        font-weight: 500;
        color: var(--rojo);
        line-height: 1;
        font-size: 190px;
        margin-bottom: 20px;
      }
      .dato .moneda { font-size: 0.32em; margin-top: 0.2em; }
      .dato-nota {
        font-size: 26px;
        color: #B9BEC1;
        margin-bottom: 36px;
      }
    `,
  });
}

/* --------------------------------------------------------------------
   LÁMINA 4 — El hallazgo del hueco
   -------------------------------------------------------------------- */

function laminaHallazgo({ indice, total, paises, anio }) {
  const cuerpo = `
    <p class="titular-hallazgo">${paises.length} países no<br />están en esta<br />estadística</p>
    <div class="lista-hueco">
      ${paises.map((p) => `<p class="item-hueco">${p}</p>`).join("\n")}
    </div>
    <p class="dato-nota">Sin datos suficientes en esta serie para ${anio}.</p>
  `;
  return documento({
    cejilla: `BANCO MUNDIAL · ${anio}`,
    indice,
    total,
    cuerpo,
    pie: null,
    cssExtra: `
      .titular-hallazgo {
        font-family: 'Archivo', sans-serif;
        font-weight: 700;
        font-size: 60px;
        line-height: 1.15;
        letter-spacing: -0.01em;
        margin-bottom: 44px;
      }
      .lista-hueco { margin-bottom: 24px; }
      .item-hueco {
        font-family: 'Archivo', sans-serif;
        font-weight: 700;
        font-size: 64px;
        color: var(--rojo);
        line-height: 1.3;
      }
      .dato-nota {
        font-size: 28px;
        color: #B9BEC1;
        max-width: 34ch;
      }
    `,
  });
}

/* --------------------------------------------------------------------
   LÁMINA 5 — Cierre
   -------------------------------------------------------------------- */

function laminaCierre({ total, pie }) {
  const cuerpo = `
    <p class="titular-cierre">Datos que no se<br /><em>traducen solos</em></p>
    <p class="cta">Lee la pieza completa en</p>
    <p class="enlace">cardinaldatos.org</p>
  `;
  return documento({
    cejilla: "CARDINAL DATOS",
    indice: total,
    total,
    cuerpo,
    pie,
    cssExtra: `
      .titular-cierre {
        font-family: 'Archivo', sans-serif;
        font-weight: 700;
        font-size: 64px;
        line-height: 1.1;
        letter-spacing: -0.01em;
        margin-bottom: 48px;
      }
      .titular-cierre em { font-style: normal; color: var(--rojo); }
      .cta {
        font-size: 28px;
        color: #B9BEC1;
        margin-bottom: 8px;
      }
      .enlace {
        font-family: 'IBM Plex Mono', ui-monospace, monospace;
        font-size: 32px;
        color: var(--papel);
      }
    `,
  });
}

/* --------------------------------------------------------------------
   ARMADO DE LAS CINCO LÁMINAS CON DATOS REALES
   -------------------------------------------------------------------- */

async function construirCarrusel() {
  const rutaDatos = path.join(RAIZ, "data", "remesas-costo-latam", "limpio.json");
  const crudo = await readFile(rutaDatos, "utf-8");
  const datos = JSON.parse(crudo);

  const [masCaro] = datos.con_dato;
  const masBarato = datos.con_dato[datos.con_dato.length - 1];
  const nombresSinDato = datos.sin_dato.map((p) => p.pais);

  const conDato = datos.con_dato.length;
  const monto = datos.monto_referencia_usd;

  // El año de la serie, no el del país que toque en la lámina. Se toma del
  // nivel superior de limpio.json, que es donde el pipeline lo deja cuando
  // todos los países lo comparten; si no lo comparten queda en null a
  // propósito y aquí se cae al del primer país, como hace la web. Las dos
  // superficies resuelven el año igual porque leen el mismo campo: si una
  // dijera 2023 y la otra 2024, sería un fallo y no un matiz.
  const anio = datos.anio ?? datos.con_dato[0].anio;

  const TOTAL = 5;

  const paginas = [
    {
      archivo: "carrusel-1-portada.png",
      html: laminaPortada({ total: TOTAL, conDato, monto }),
    },
    {
      archivo: "carrusel-2-mas-caro.png",
      html: laminaExtremo({
        indice: 2,
        total: TOTAL,
        etiqueta: `El más caro de los ${conDato}`,
        pais: masCaro,
        datoValor: coma(masCaro.sobre_200_usd),
        costoPct: masCaro.costo_pct,
        todosLosPaises: datos.con_dato,
        anio,
      }),
    },
    {
      archivo: "carrusel-3-mas-barato.png",
      html: laminaExtremo({
        indice: 3,
        total: TOTAL,
        etiqueta: `El más barato de los ${conDato}`,
        pais: masBarato,
        datoValor: coma(masBarato.sobre_200_usd),
        costoPct: masBarato.costo_pct,
        todosLosPaises: datos.con_dato,
        anio,
      }),
    },
    {
      archivo: "carrusel-4-hallazgo.png",
      html: laminaHallazgo({ indice: 4, total: TOTAL, paises: nombresSinDato, anio }),
    },
    {
      archivo: "carrusel-5-cierre.png",
      html: laminaCierre({
        total: TOTAL,
        pie: `Costo promedio de enviar ${coma(monto, 0)} dólares, según el Banco Mundial (World Development Indicators). Cardinal Datos, ${anio}.`,
      }),
    },
  ];

  return paginas;
}

/* --------------------------------------------------------------------
   RENDERIZADO
   -------------------------------------------------------------------- */

async function main() {
  await mkdir(SALIDA, { recursive: true });

  const paginas = await construirCarrusel();

  const navegador = await chromium.launch();
  const pagina = await navegador.newPage({
    viewport: { width: 1080, height: 1350 },
    deviceScaleFactor: 1,
  });

  for (const lamina of paginas) {
    await pagina.setContent(lamina.html, { waitUntil: "networkidle" });
    const destino = path.join(SALIDA, lamina.archivo);
    await pagina.screenshot({ path: destino });
    console.log(`  generado: ${lamina.archivo}`);
  }

  await navegador.close();
  console.log(`\nListo. ${paginas.length} láminas en ${SALIDA}`);
}

main().catch((e) => {
  console.error("FALLO:", e);
  process.exit(1);
});
