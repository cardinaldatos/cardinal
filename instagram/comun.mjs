// Compartido entre generar.mjs y generar-carrusel.mjs.

export const FUENTES =
  "https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap";

export const coma = (v, decimales = 2) =>
  Number(v).toLocaleString("es", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  });

/* --------------------------------------------------------------------
   MINI-RANKING — los diez países, uno resaltado

   Filas más compactas que en la primera versión: esa se probó solo en el
   carrusel y desbordaba el feed, que además lleva el pie de cita completo
   y por eso tiene menos aire disponible. Estos valores dejan margen en
   los dos formatos, no solo en el que se probó primero — la lección de
   hoy es que "cabe en una plantilla" no significa "cabe en todas".
   -------------------------------------------------------------------- */

export const CSS_MINI_RANKING = `
  .mini-ranking { margin-top: 4px; }

  .mini-titulo {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 19px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--pizarra);
    margin-bottom: 14px;
  }

  .mini-fila {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 6px;
  }

  .mini-pais {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 17px;
    color: #B9BEC1;
    width: 56px;
    flex-shrink: 0;
  }

  .mini-pais.activo { color: var(--papel); font-weight: 600; }

  .mini-pista {
    flex: 1;
    height: 10px;
    background: #2E363D;
  }

  .mini-relleno { height: 100%; background: var(--pizarra); }
  .mini-relleno.activo { background: var(--rojo); }

  .mini-valor {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 15px;
    color: #B9BEC1;
    width: 48px;
    text-align: right;
    flex-shrink: 0;
  }

  .mini-valor.activo { color: var(--papel); font-weight: 600; }
`;

/**
 * @param {Array} paises  con_dato de limpio.json, ya viene ordenado de
 *   mayor a menor costo_pct.
 * @param {string} isoDestacado  ISO3 del país que resalta esta tarjeta.
 *
 * Nota: aquí se redondea a 1 decimal por espacio (p. ej. "3,6 %"), aunque
 * el dato grande de la tarjeta muestre 2 decimales ("3,57 %"). Es el mismo
 * número con distinta precisión de presentación, no una segunda cifra.
 */
export function renderMiniRanking(paises, isoDestacado) {
  const max = paises[0].costo_pct;

  const filas = paises
    .map((p) => {
      const activo = p.iso3 === isoDestacado;
      const clase = activo ? " activo" : "";
      const ancho = (p.costo_pct / max) * 100;
      return `
      <div class="mini-fila">
        <span class="mini-pais${clase}">${p.iso3}</span>
        <div class="mini-pista"><div class="mini-relleno${clase}" style="width:${ancho}%"></div></div>
        <span class="mini-valor${clase}">${coma(p.costo_pct, 1)}%</span>
      </div>`;
    })
    .join("");

  return `<div class="mini-ranking"><p class="mini-titulo">Los diez países</p>${filas}</div>`;
}
