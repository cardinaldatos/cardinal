import { useState } from "react";

/* ------------------------------------------------------------------
   DATOS REALES — ACNUR, Refugee Data Finder, población de fin de año
   por país de origen y de acogida. Llegan como prop desde
   desplazamiento-venezolano.astro, que los lee de
   data/desplazamiento-venezolano/limpio.json — el archivo que genera
   pipeline/acnur.py.

   Este componente no contiene ninguna cifra. Los totales, los pesos de
   cada categoría, el número de destinos y el de países sin fila se leen
   del archivo en cada compilación.

   TRES REGLAS QUE ESTA PIEZA NO PUEDE ROMPER

   1. Un hueco no se dibuja como un cero. ACNUR escribe la ausencia de
      tres maneras distintas y limpio.json las separa en el campo
      «motivos»: una columna que no se recoge para ese país, un cero que
      es relleno del esquema, y un cero redactado por confidencialidad
      que significa entre cero y dos personas. Solo el último es un
      número, y ni siquiera es exacto. Ninguno se pinta como barra.

   2. Los países que no aparecen no se publican como países sin dato. El
      API no devuelve fila para un par origen-destino ausente, así que no
      distingue «no se midió» de «no había nadie». Listarlos les
      atribuiría un significado que el dato no tiene.

   3. El peso de la categoría de refugio no es una tasa de exclusión.
      ACNUR sigue contando a estas personas en sus totales globales; lo
      que cambia es bajo qué etiqueta. La pieza lo dice donde aparece el
      porcentaje, no en una nota al final: sin esa frase el número se lee
      como si a esas personas no las contara nadie.
------------------------------------------------------------------ */

/* Separador de miles en español. Regla del manual: las cifras hablan
   español, y un total de siete dígitos sin separar no se lee. */
const miles = (v) => Number(v).toLocaleString("es");

const coma = (v, decimales = 1) =>
  Number(v).toLocaleString("es", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  });

/* Un porcentaje que existe no se escribe como cero. Colombia contabiliza
   más de mil personas en la categoría de refugio, y sobre un total de
   millones eso redondea a 0,0 %: escrito así se lee como «ninguna», que
   es justo lo que la pieza no puede decir de un valor medido. Por debajo
   del último decimal que se muestra se declara el umbral en lugar de la
   cifra redondeada. */
const porcentaje = (v, decimales = 1) => {
  const minimo = 1 / 10 ** decimales;
  if (v > 0 && v < minimo) return `menos de ${coma(minimo, decimales)} %`;
  return `${coma(v, decimales)} %`;
};

export default function DesplazamientoVenezolano({ datos }) {
  const SERIE = datos.serie;
  const DESTINOS = datos.destinos;
  const AUSENCIA = datos.ausencia;

  // Las etapas de la reclasificación salen de limpio.json, no de aquí.
  // Cuántas son se cuenta del arreglo: el titular de esta pieza habla de
  // ellas, y era la última cifra que quedaba escrita a mano en el texto.
  const ETAPAS = datos.reetiquetas ?? [];
  const cambiosDeNombre = Math.max(ETAPAS.length - 1, 0);

  const nombres = Object.fromEntries(
    datos.categorias.map((c) => [c.id, c.nombre])
  );
  const soluciones = datos.categorias.filter((c) => c.tipo === "solucion");

  const [anio, setAnio] = useState(datos.anio);
  const [todos, setTodos] = useState(false);

  const delAnio = SERIE.find((s) => s.anio === anio) ?? SERIE[SERIE.length - 1];
  const hayParte = delAnio.parte_refugio !== null && delAnio.parte_refugio !== undefined;

  // Cuántas de cada cien están contadas como refugiadas, y su complemento.
  // El complemento es el número del que habla la pieza, pero solo
  // significa algo junto a la frase de que ACNUR las sigue contando.
  const marcados = hayParte ? Math.round(delAnio.parte_refugio) : 0;
  const resto = 100 - marcados;

  // Las columnas de relleno están en cero para todos los destinos de ese
  // año: el concepto no aplica a un desglose por país de acogida. No son
  // una medición y no se dibujan.
  const relleno = new Set(delAnio.columnas_de_relleno);
  const reparto = datos.categorias
    .filter((c) => c.tipo === "poblacion" && !relleno.has(c.id))
    .map((c) => ({ ...c, valor: delAnio.por_categoria[c.id] ?? 0 }))
    .sort((a, b) => b.valor - a.valor);

  const excluidas = datos.categorias.filter(
    (c) => c.tipo === "poblacion" && relleno.has(c.id)
  );

  // Movimiento de la lista de destinos en todo el periodo. Un país que
  // entra o sale no es gente que llegó o se fue: es un país que ese año
  // reportó o dejó de reportar.
  const entradas = datos.cambios_de_destinos.reduce((n, c) => n + c.entraron.length, 0);
  const salidas = datos.cambios_de_destinos.reduce((n, c) => n + c.salieron.length, 0);

  const mayorTotal = DESTINOS.length ? DESTINOS[0].total : 0;
  const visibles = todos ? DESTINOS : DESTINOS.slice(0, 12);

  const anioPrimero = datos.anios[0];

  return (
    <div className="pieza" data-fondo="claro" style={{ "--acento": "var(--verde)" }}>
      <div className="marco">
        <p className="cejilla">
          ACNUR · Refugee Data Finder · {datos.anio}
        </p>

        <h1 className="titular">
          La etiqueta que se<br />
          <em>reescribió hacia atrás</em>
        </h1>

        <p className="bajada">
          Las personas venezolanas que ACNUR contabiliza han sido contadas
          bajo {ETAPAS.length} nombres distintos desde que empezó la salida
          masiva. Y cada vez que el nombre cambió, la serie de años anteriores
          se rehízo con el nombre nuevo.
        </p>

        {/* ---------------- EL HALLAZGO: LA REETIQUETA ---------------- */}
        <div className="bloque">
          <h2>{ETAPAS.length} nombres para las mismas personas</h2>
          <p className="intro">
            No es que unas personas salieran de una categoría y otras entraran.
            Es el mismo grupo, renombrado, y con el pasado reescrito cada vez.
          </p>

          <ul className="reetiquetas">
            {ETAPAS.map((e) => (
              <li
                className={"reetiqueta" + (e.vigente ? " vigente" : "")}
                key={e.id}
              >
                <span className="cuando">{e.cuando}</span>
                <span className="como">{e.como}</span>
                <span className="que-paso">{e.que_paso}</span>
              </li>
            ))}
          </ul>

          <p className="detalle">
            La reclasificación de la última etapa se aplicó hacia atrás hasta{" "}
            {datos.anio_inicio}, que es por eso el primer año de esta serie.
            Cualquier cifra publicada antes de esa fecha se refiere a una
            clasificación que ya no existe, y no es comparable con estas.
          </p>
        </div>

        {/* ---------------- CUÁNTAS SON REFUGIADAS ---------------- */}
        <div className="bloque">
          <h2>Cuántas están contadas como refugiadas</h2>

          <div className="campo">
            <span className="etiqueta" id="lbl-anio">Año</span>
            <div className="fichas" role="group" aria-labelledby="lbl-anio">
              {datos.anios.map((a) => (
                <button
                  key={a}
                  className="ficha"
                  aria-pressed={anio === a}
                  onClick={() => setAnio(a)}
                >
                  {a}
                </button>
              ))}
            </div>
          </div>

          <div className="tarjeta">
            {hayParte ? (
              <>
                <p className="lectura">
                  <b className="dato-central">{marcados} de cada 100</b>
                  personas venezolanas contabilizadas por ACNUR en {anio}{" "}
                  estaban contadas como refugiadas.
                </p>

                <div
                  className="rejilla"
                  role="img"
                  aria-label={`Cuadrícula de 100 unidades: ${marcados} marcadas como contadas en la categoría de personas refugiadas y ${resto} bajo otras categorías del mismo recuento`}
                >
                  {Array.from({ length: 100 }, (_, i) => (
                    <div
                      key={i}
                      className={"unidad" + (i < marcados ? " marcada" : "")}
                    />
                  ))}
                </div>

                <div className="leyenda">
                  <span>
                    <i className="marcada" />
                    Contadas como refugiadas
                  </span>
                  <span>
                    <i />
                    Contadas por ACNUR bajo otra categoría
                  </span>
                </div>

                <p className="nota-fuente">
                  <b>Las otras no desaparecen del recuento.</b> ACNUR sigue
                  contando a estas personas en sus totales globales de
                  desplazamiento: lo que cambia es bajo qué etiqueta aparecen,
                  no si aparecen. Leer este número como una tasa de exclusión
                  sería leerlo al revés. Lo que mide es una recategorización,
                  y la categoría mayoritaria es la que cambió de nombre{" "}
                  {cambiosDeNombre} veces.
                </p>

                <p className="detalle">
                  Peso exacto de la categoría de {nombres[datos.categoria_refugio].toLowerCase()}
                  : {coma(delAnio.parte_refugio)} % de{" "}
                  {miles(delAnio.total)} personas contabilizadas en{" "}
                  {delAnio.destinos} destinos.
                </p>
              </>
            ) : (
              <p className="detalle">
                No hay reparto por categoría para {anio} en esta serie. El
                hueco se declara en lugar de dibujarse como un cero: una
                cuadrícula sin marcar diría que nadie está contado como
                refugiado, y lo que ocurre es que no hay medición.
              </p>
            )}
          </div>
        </div>

        {/* ---------------- REPARTO POR CATEGORÍA ---------------- */}
        <div className="bloque">
          <h2>Bajo qué categorías está contado el resto</h2>
          <p className="intro">
            El reparto de {anio}, con los nombres que usa ACNUR en sus
            publicaciones en español. No son traducciones nuestras.
          </p>

          {reparto.map((c) => (
            <div className="barra-fila reparto" key={c.id}>
              <div className="barra-cab">
                <span>{c.nombre}</span>
                <span className="n">{miles(c.valor)}</span>
              </div>
              <div className="pista">
                <div
                  className={"relleno" + (c.id === datos.categoria_refugio ? " acento" : "")}
                  style={{
                    width: delAnio.total
                      ? (c.valor / delAnio.total) * 100 + "%"
                      : 0,
                  }}
                />
              </div>
              <p className="barra-pie">
                {delAnio.total
                  ? `${porcentaje((c.valor / delAnio.total) * 100)} del total contabilizado`
                  : "Sin total con el que comparar"}
              </p>
            </div>
          ))}

          {excluidas.length > 0 && (
            <p className="detalle">
              {excluidas.map((c) => c.nombre).join(", ")}{" "}
              {excluidas.length === 1 ? "no aparece" : "no aparecen"} en este
              reparto. {excluidas.length === 1 ? "Vale" : "Valen"} cero para
              todos los destinos del año, que es lo que ocurre cuando el
              concepto no aplica a un desglose por país de acogida: es relleno
              del esquema y no una medición. Dibujarlo como una barra en cero
              diría que se midió y no había nadie.
            </p>
          )}

          <p className="detalle">
            Fuera del reparto quedan también{" "}
            {soluciones.map((c) => c.nombre.toLowerCase()).join(" y ")}. Son
            flujos de un año, no personas contabilizadas a 31 de diciembre, y
            sumarlas al total mezclaría dos cosas distintas. Se conservan en
            los datos y quedan fuera del porcentaje.
          </p>
        </div>

        {/* ---------------- DESTINOS ---------------- */}
        <div className="bloque">
          <h2>Dónde están, y cómo las cuenta cada país</h2>
          <p className="intro">
            La barra ancha es cuánta gente contabiliza ACNUR en ese destino en{" "}
            {datos.anio}. La barra fina de debajo es la composición de ese
            mismo destino: en color, el tramo contado como{" "}
            {nombres[datos.categoria_refugio].toLowerCase()}. El reconocimiento
            no depende solo de cuánta gente llega.
          </p>

          {visibles.map((d) => {
            const ref = d.categorias[datos.categoria_refugio];
            const motivoRef = d.motivos[datos.categoria_refugio];
            // Un cero redactado no es un cero: por la salvaguarda de
            // confidencialidad significa entre cero y dos personas. No se
            // dibuja tramo, y la fila lo dice.
            const refDibujable = ref !== null && ref !== undefined && ref > 0 && !motivoRef;
            const parte = d.total && refDibujable ? (ref / d.total) * 100 : 0;

            return (
              <div className="barra-fila" key={d.coa}>
                <div className="barra-cab">
                  <span>{d.pais}</span>
                  <span className="n">{miles(d.total)}</span>
                </div>
                <div className="pista">
                  <div
                    className="relleno tenue"
                    style={{ width: mayorTotal ? (d.total / mayorTotal) * 100 + "%" : 0 }}
                  />
                  {refDibujable && (
                    <div
                      className="relleno acento encima"
                      style={{
                        width: mayorTotal ? (ref / mayorTotal) * 100 + "%" : 0,
                      }}
                    />
                  )}
                </div>
                <div className="pista" style={{ marginTop: "4px", height: "7px" }}>
                  {refDibujable && (
                    <div className="relleno acento" style={{ width: parte + "%" }} />
                  )}
                </div>
                <p className="barra-pie">
                  {motivoRef
                    ? datos.motivos[motivoRef]
                    : refDibujable
                      ? `Contadas como ${nombres[datos.categoria_refugio].toLowerCase()}: ${miles(ref)} · ${porcentaje(parte)} de este destino`
                      : `Sin personas contadas como ${nombres[datos.categoria_refugio].toLowerCase()} en este destino`}
                </p>
              </div>
            );
          })}

          {DESTINOS.length > visibles.length && (
            <button className="ficha" onClick={() => setTodos(true)}>
              Ver todos los destinos
            </button>
          )}
          {todos && (
            <button className="ficha" onClick={() => setTodos(false)}>
              Ver solo los principales
            </button>
          )}

          <p className="detalle">
            La lista de destinos no es la misma todos los años: en el periodo
            cubierto hubo {entradas} entradas y {salidas} salidas. Un país que
            aparece o desaparece no es gente que llegó o se fue, es un país que
            ese año reportó o dejó de reportar.
          </p>
        </div>

        {/* ---------------- HALLAZGO: LO QUE NO SE PUEDE SABER ---------------- */}
        <div className="bloque">
          <h2>Los países que no aparecen no dicen nada</h2>
          <p className="detalle">
            De los {AUSENCIA.paises_en_catalogo} países del catálogo de ACNUR,{" "}
            {AUSENCIA.destinos_con_fila} aparecen como destino en {datos.anio}.
            Los otros {AUSENCIA.sin_fila} no están en esta pieza, y no como
            países sin dato: {AUSENCIA.nota.charAt(0).toLowerCase() + AUSENCIA.nota.slice(1)}
          </p>
          <p className="detalle">
            Por eso no hay aquí una lista de ausentes. Publicarla daría a
            entender que en esos países no hay personas venezolanas, y eso es
            justo lo que el dato no permite afirmar. El hueco se declara; lo
            que no se hace es interpretarlo.
          </p>
        </div>

        <div className="pie">
          <b>Fuente:</b> {datos.fuente}, conjunto de población de fin de año por
          país de origen y de acogida, desde {anioPrimero}. Los nombres de las
          categorías son los que usa ACNUR en español.{" "}
          <b>Los números son aproximaciones por decisión de la fuente:</b>{" "}
          {datos.redaccion.regla.charAt(0).toLowerCase() + datos.redaccion.regla.slice(1)}{" "}
          {datos.redaccion.consecuencia} En esta pieza los ceros que podrían no
          ser ceros se declaran fila por fila en lugar de dibujarse. El detalle
          de la consulta, las categorías completas y los límites declarados
          quedan en el <a href="/metodo/">método</a>; si encuentras un error,
          las <a href="/correcciones/">correcciones</a> explican cómo avisar.
        </div>
      </div>
    </div>
  );
}
