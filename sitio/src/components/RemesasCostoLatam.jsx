import { useState } from "react";

/* ------------------------------------------------------------------
   DATOS REALES — Banco Mundial, World Development Indicators, serie
   SI.RMT.COST.IB.ZS. Llegan como prop desde remesas-costo-latam.astro,
   que los lee de data/remesas-costo-latam/limpio.json — el mismo
   archivo que genera pipeline/remesas.py y que usan las imágenes de
   Instagram. Un solo origen para las tres superficies.

   Los nombres de país vienen ya en español desde el pipeline. Antes
   había aquí un diccionario propio para los países sin dato; se quitó
   para no tener dos listas que se desincronicen.

   Este componente no contiene ninguna cifra. Los recuentos —cuántos
   países con dato, cuántos sin él— se cuentan del arreglo en vez de
   escribirse en el texto: decían «diez» y «tres» a mano, y el día que
   el Banco Mundial publique un país más lo habrían seguido diciendo.
------------------------------------------------------------------ */

const coma = (v, decimales = 2) =>
  Number(v).toLocaleString("es", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  });

export default function RemesasCostoLatam({ datos }) {
  const paises = datos.con_dato; // ya viene ordenado de mayor a menor costo_pct
  const [iso, setIso] = useState(paises[0].iso3); // arranca en el más caro

  const pais = paises.find((p) => p.iso3 === iso);
  const monto = datos.monto_referencia_usd;
  const llega = monto - pais.sobre_200_usd;
  const maxCosto = paises[0].costo_pct;
  const sinDato = datos.sin_dato.map((p) => p.pais);

  // El año de la serie, no el del país que esté seleccionado. Se toma del
  // nivel superior de limpio.json; si algún día no estuviera, cae al del
  // primer país en lugar de imprimir «undefined».
  const anioSerie = datos.anio ?? paises[0].anio;

  return (
    <div className="pieza" data-fondo="oscuro" style={{ "--acento": "var(--verde)" }}>
      <div className="marco">
        <p className="cejilla">
          BANCO MUNDIAL · {anioSerie}
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
              <button key={p.iso3} className="ficha" aria-pressed={p.iso3 === iso} onClick={() => setIso(p.iso3)}>
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
            El monto se calcula sobre el porcentaje sin redondear, así que puede
            diferir en un céntimo del que resulta de multiplicar el porcentaje
            que se muestra. Redondear al final y no antes es lo correcto, pero
            conviene decirlo para que nadie crea que la cuenta está mal.
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
          <h2>Los {paises.length} países con dato</h2>
          <p className="intro">
            Mismo envío de {coma(monto, 0)} dólares, {paises.length} destinos
            distintos.{" "}{pais.pais} está resaltado.
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
                  <div className={"relleno" + (activo ? " central" : "")} style={{ width: (p.costo_pct / maxCosto) * 100 + "%" }} />
                </div>
              </div>
            );
          })}
        </div>

        {/* ---------------- HALLAZGO ---------------- */}
        {sinDato.length > 0 && (
          <div className="bloque">
            <h2>{sinDato.length} países no están aquí</h2>
            <p className="detalle">
              {sinDato.join(", ")} no tienen valor en esta serie para {anioSerie}.
              No es que enviarles cueste cero. La serie del Banco Mundial se
              construye a partir de los proveedores que rastrea Remittance
              Prices Worldwide, y un país queda fuera cuando no hay suficientes
              para calcular un promedio, o cuando directamente no se le hace
              seguimiento. La ausencia se declara aquí en lugar de rellenarse.
            </p>
          </div>
        )}

        <div className="pie">
          <b>Fuente:</b> Banco Mundial, World Development Indicators, serie
          SI.RMT.COST.IB.ZS (costo promedio de enviar remesas hacia un
          país), con datos de origen de Remittance Prices Worldwide. El
          monto de {coma(monto, 0)} dólares es el propio monto de referencia
          sobre el que está definido el indicador, no una elección
          editorial. Cifras anuales, no trimestrales: el año más reciente
          disponible es {anioSerie}. El detalle por proveedor, comisión y
          tipo de cambio no está en esta serie — solo el promedio total de
          transacción. Los nombres de país están traducidos por nosotros; el
          original de la fuente queda en el <a href="/metodo/">método</a>, con
          la consulta exacta y los límites declarados.
        </div>
      </div>
    </div>
  );
}
