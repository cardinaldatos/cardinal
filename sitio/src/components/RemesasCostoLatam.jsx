import { useState } from "react";

/* ------------------------------------------------------------------
   DATOS REALES — Banco Mundial, World Development Indicators, serie
   SI.RMT.COST.IB.ZS. Llegan como prop desde remesas-costo-latam.astro,
   que los lee de data/remesas-costo-latam/limpio.json — el mismo
   archivo que genera pipeline/remesas.py y que usan las imágenes de
   Instagram. Un solo origen para las tres superficies.
------------------------------------------------------------------ */

const coma = (v, decimales = 2) =>
  Number(v).toLocaleString("es", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  });

const NOMBRES_SIN_DATO = { VEN: "Venezuela", ARG: "Argentina", CHL: "Chile" };

export default function RemesasCostoLatam({ datos }) {
  const paises = datos.con_dato; // ya viene ordenado de mayor a menor costo_pct
  const [iso, setIso] = useState(paises[0].iso3); // arranca en el más caro

  const pais = paises.find((p) => p.iso3 === iso);
  const monto = datos.monto_referencia_usd;
  const llega = monto - pais.sobre_200_usd;
  const maxCosto = paises[0].costo_pct;

  const sinDato = datos.sin_dato.map((c) => NOMBRES_SIN_DATO[c] ?? c);

  return (
    <div className="pieza" data-fondo="oscuro" style={{ "--acento": "var(--verde)" }}>
      <div className="marco">
        <p className="cejilla">
          BANCO MUNDIAL · {pais.anio}
        </p>

        <h1 className="titular">
          Cuánto se <em>queda en el camino</em>
        </h1>

        <p className="bajada">
          Enviar dinero a América Latina tiene un costo que casi nunca se ve
          antes de mandar. Elige un país y mira cuánto se queda antes de
          llegar.
        </p>

        <div className="campo">
          <span className="etiqueta" id="lbl-pais">País de destino</span>
          <div className="fichas" role="group" aria-labelledby="lbl-pais">
            {paises.map((p) => (
              <button
                key={p.iso3}
                className="ficha"
                aria-pressed={p.iso3 === iso}
                onClick={() => setIso(p.iso3)}
              >
                {p.pais}
              </button>
            ))}
          </div>
        </div>

        {/* ---------------- RECIBO ---------------- */}
        <div className="recibo">
          <div className="recibo-cab">
            <strong>CARDINAL DATOS</strong>
            <span>ENVÍO A {pais.pais.toUpperCase()}</span>
          </div>

          <div className="linea">
            <span>Envías</span>
            <span className="pts" />
            <span className="val">${coma(monto, 0)}</span>
          </div>

          <div className="linea resta">
            <span>Costo de transacción ({coma(pais.costo_pct)} %)</span>
            <span className="pts" />
            <span className="val">−${coma(pais.sobre_200_usd)}</span>
          </div>
          <p className="nota-linea">
            Promedio entre los proveedores rastreados hacia {pais.pais}, {pais.anio}.
          </p>

          <div className="linea total">
            <span>Llega</span>
            <span className="pts" />
            <span className="val">${coma(llega)}</span>
          </div>

          <div className="sello">
            <p className="s-eti">Se queda en el camino</p>
            <p className="s-num">${coma(pais.sobre_200_usd)}</p>
            <p className="s-pie">{coma(pais.costo_pct)} % del envío</p>
          </div>
        </div>

        {/* ---------------- COMPARATIVA ---------------- */}
        <div className="bloque">
          <h2>Los diez países</h2>
          <p className="intro">
            Mismo envío de {coma(monto, 0)} dólares, diez destinos distintos.
            {" "}{pais.pais} está resaltado.
          </p>

          {paises.map((p) => {
            const activo = p.iso3 === iso;
            return (
              <div className={"barra-fila" + (activo ? " fila-activa" : "")} key={p.iso3}>
                <div className="barra-cab">
                  <span>{p.pais}</span>
                  <span className="n">{coma(p.costo_pct)} %</span>
                </div>
                <div className="pista">
                  <div
                    className={"relleno" + (activo ? " central" : "")}
                    style={{ width: (p.costo_pct / maxCosto) * 100 + "%" }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* ---------------- HALLAZGO ---------------- */}
        <div className="bloque">
          <h2>Tres países no están aquí</h2>
          <p className="detalle">
            {sinDato.join(", ")} no tienen datos suficientes en esta serie
            para {paises[0].anio}. No es que enviarles cueste cero — es que
            el Banco Mundial no lo mide, o no encontró suficientes
            proveedores para calcular un promedio.
          </p>
        </div>

        <div className="pie">
          <b>Fuente:</b> Banco Mundial, World Development Indicators, serie
          SI.RMT.COST.IB.ZS (costo promedio de enviar remesas hacia un
          país), con datos de origen de Remittance Prices Worldwide. El
          monto de {coma(monto, 0)} dólares es el propio monto de referencia
          sobre el que está definido el indicador, no una elección
          editorial. Cifras anuales, no trimestrales: el año más reciente
          disponible es {paises[0].anio}. El detalle por proveedor,
          comisión y tipo de cambio no está en esta serie — solo el
          promedio total de transacción.
        </div>
      </div>
    </div>
  );
}
