// Compartido entre generar.mjs y generar-carrusel.mjs. Nace hoy porque el
// mini-ranking de los diez países lo necesitan los dos — la misma regla que
// se usa en sistema.css: se promueve a compartido en el segundo uso
// comprobado, no antes.

export const FUENTES =
  "https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap";

export const coma = (v, decimales = 2) =>
  Number(v).toLocaleString("es", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  });

/* --------------------------------------------------------------------
   MINI-RANKING — los diez países, uno resaltado
   Llena el hueco que dejaba la tarjeta de un solo país con algo real:
   dónde queda ese país entre los otros nueve. Ancho de barra proporcional
   al más caro de los diez, así que el resaltado en rojo siempre se lee
   respecto al conjunto, no de forma aislada.
   -------------------------------------------------------------------- */

export const CSS_MINI_RANKING = `
  .mini-ranking { margin-top: 4px; }

  .mini-titulo {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 19px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--pizarra);
    margin-bottom: 18px;
  }

  .mini-fila {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }

  .mini-pais {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 18px;
    color: #B9BEC1;
    width: 58px;
    flex-shrink: 0;
  }

  .mini-pais.activo { color: var(--papel); font-weight: 600; }

  .mini-pista {
    flex: 1;
    height: 12px;
    background: #2E363D;
  }

  .mini-relleno { height: 100%; background: var(--pizarra); }
  .mini-relleno.activo { background: var(--rojo); }

  .mini-valor {
    font-family: 'IBM Plex Mono', ui-monospace, monospace;
    font-size: 16px;
    color: #B9BEC1;
    width: 50px;
    text-align: right;
    flex-shrink: 0;
  }

  .mini-valor.activo { color: var(--papel); font-weight: 600; }
`;

/**
 * @param {Array} paises  con_dato de limpio.json, ya viene ordenado de
 *   mayor a menor costo_pct.
 * @param {string} isoDestacado  ISO3 del país que resalta esta tarjeta.
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
