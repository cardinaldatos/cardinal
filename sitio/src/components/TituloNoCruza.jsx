import { useState } from "react";

/* ------------------------------------------------------------------
   DATOS REALES — Eurostat, Encuesta de Población Activa de la UE,
   conjunto lfsa_eoqgan (sobrecualificación por ciudadanía). Llegan como
   prop desde titulo-no-cruza.astro, que los lee de
   data/sobrecualificacion-ue/limpio.json — el archivo que genera
   pipeline/sobrecualificacion.py.

   Este componente ya no contiene ninguna cifra. Las que tenía escritas
   a mano desde julio de 2025 resultaron estar desactualizadas: los
   valores de 2014 seguían siendo correctos, pero Eurostat había
   revisado los de 2024 (39,6 % pasó a 39,8 %; 30,3 % a 30,2 %). Eran
   correctas el día que se copiaron y falsas un año después. Por eso
   ahora se leen de la fuente en cada compilación. Queda constancia en
   el registro público de correcciones.

   Los huecos no se pintan como ceros. Si Eurostat no publica un valor,
   el componente lo dice en palabras en vez de dibujar una barra vacía
   o una cuadrícula sin marcar, que se leerían como «aquí no pasa nada».
------------------------------------------------------------------ */

/* Coma decimal, siempre. Regla del manual: las cifras hablan español. */
const coma = (v, decimales = 1) =>
  Number(v).toLocaleString("es", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  });

/* Topes de escala de las barras, no datos. Si algún valor los superara,
   la barra se desbordaría en silencio: por eso se recortan al 100 % y se
   comprueba abajo. Hoy el máximo por país es Grecia, holgadamente por
   debajo de ESCALA_PAIS. */
const ESCALA_DECADA = 50;
const ESCALA_PAIS = 80;

const ancho = (valor, escala) => Math.min((valor / escala) * 100, 100) + "%";

export default function TituloNoCruza({ datos }) {
  const GRUPOS = datos.grupos;
  const PAISES = datos.paises_2024;
  const SIN_DATO = datos.sin_dato;

  const [anioReciente, anioAntiguo] = [
    datos.anios[datos.anios.length - 1],
    datos.anios[0],
  ];
  const lapso = anioReciente - anioAntiguo;

  const [grupoId, setGrupoId] = useState(GRUPOS[0].id);
  const [anio, setAnio] = useState(anioReciente);
  const [orden, setOrden] = useState("brecha");

  const grupo = GRUPOS.find((g) => g.id === grupoId) ?? GRUPOS[0];
  const tasa = anio === anioReciente ? grupo.v2024 : grupo.v2014;
  const hayTasa = tasa !== null && tasa !== undefined;
  const marcados = hayTasa ? Math.round(tasa) : 0;

  // El orden no es un detalle de presentación: cambia qué historia se
  // lee. Por tasa, arriba salen los países donde la sobrecualificación
  // es alta para todo el mundo. Por brecha, los países donde le pasa
  // específicamente a quien viene de fuera.
  const paisesOrdenados = [...PAISES].sort((a, b) =>
    orden === "brecha"
      ? (b.brecha ?? -Infinity) - (a.brecha ?? -Infinity)
      : b.extra_ue - a.extra_ue
  );

  const conBrecha = PAISES.filter((p) => p.brecha !== null);
  const mayorBrecha = [...conBrecha].sort((a, b) => b.brecha - a.brecha)[0];
  const mayorTasa = [...PAISES].sort((a, b) => b.extra_ue - a.extra_ue)[0];

  return (
    <div className="pieza" data-fondo="claro" style={{ "--acento": "var(--ambar)" }}>
      <div className="marco">
        <p className="cejilla">
          Eurostat · Encuesta de Población Activa · {anioReciente}
        </p>

        <h1 className="titular">
          El título<br />
          <em>no cruza</em>
        </h1>

        <p className="bajada">
          Terminaste la universidad. Migraste. Y acabaste en un trabajo que no
          pide tu carrera. Eurostat le puso nombre y número a eso:
          sobrecualificación.
        </p>

        <div className="campo">
          <span className="etiqueta" id="lbl-grupo">Quién trabaja</span>
          <div className="fichas" role="group" aria-labelledby="lbl-grupo">
            {GRUPOS.map((g) => (
              <button key={g.id} className="ficha" aria-pressed={g.id === grupoId} onClick={() => setGrupoId(g.id)}>
                {g.corto}
              </button>
            ))}
          </div>
        </div>

        <div className="campo">
          <span className="etiqueta" id="lbl-anio">Año</span>
          <div className="fichas" role="group" aria-labelledby="lbl-anio">
            {datos.anios.map((a) => (
              <button key={a} className="ficha" aria-pressed={anio === a} onClick={() => setAnio(a)}>
                {a}
              </button>
            ))}
          </div>
        </div>

        {/* ---------------- CUADRÍCULA ---------------- */}
        <div className="tarjeta">
          {hayTasa ? (
            <>
              <p className="lectura">
                <b className="dato-central">{marcados} de cada 100</b>
                {grupo.largo.toLowerCase()} con título universitario trabajaban en{" "}
                {anio} en un puesto que no exige estudios superiores.
              </p>

              <div className="rejilla" role="img" aria-label={`Cuadrícula de 100 unidades: ${marcados} marcadas como sobrecualificadas`}>
                {Array.from({ length: 100 }, (_, i) => (
                  <div key={i} className={"unidad" + (i < marcados ? " marcada" : "")} />
                ))}
              </div>

              <div className="leyenda">
                <span>
                  <i className="marcada" />
                  Trabaja por debajo de su título
                </span>
                <span>
                  <i />
                  Trabaja acorde a su título
                </span>
              </div>

              <p className="detalle">
                Tasa exacta: {coma(tasa)} % del total de personas empleadas de
                este grupo con estudios superiores, en el conjunto de la UE.
              </p>
            </>
          ) : (
            <p className="detalle">
              Eurostat no publica valor para {grupo.largo.toLowerCase()} en{" "}
              {anio}. El hueco se declara en lugar de dibujarse como un cero:
              una cuadrícula sin marcar diría que la sobrecualificación es
              nula, y lo que ocurre es que no hay medición.
            </p>
          )}
        </div>

        {/* ---------------- DÉCADA ---------------- */}
        <div className="bloque">
          <h2>{lapso} años después, la brecha sigue</h2>
          <p className="intro">
            La barra tenue es {anioAntiguo}; la de color, {anioReciente}. Las
            tasas de los migrantes bajaron, pero ninguna se acercó a la de los
            nacionales.
          </p>

          {GRUPOS.map((g) => {
            const completo = g.v2014 !== null && g.v2024 !== null;
            return (
              <div className="barra-fila decada" key={g.id}>
                <div className="barra-cab">
                  <span>{g.corto}</span>
                  <span className="n">
                    {completo ? `${coma(g.v2014)} % → ${coma(g.v2024)} %` : "Sin serie completa"}
                  </span>
                </div>
                {completo && (
                  <div className="pista">
                    <div className="relleno tenue" style={{ width: ancho(g.v2014, ESCALA_DECADA) }} />
                    <div className="relleno acento encima" style={{ width: ancho(g.v2024, ESCALA_DECADA) }} />
                  </div>
                )}
                <p className="barra-pie">
                  {!completo
                    ? `Eurostat no publica uno de los dos años para este grupo, así que la comparación no se puede hacer.`
                    : Math.abs(g.v2014 - g.v2024) < 0.05
                      ? "Sin cambio apreciable"
                      : g.v2024 < g.v2014
                        ? `Bajó ${coma(g.v2014 - g.v2024)} puntos en ${lapso} años`
                        : `Subió ${coma(g.v2024 - g.v2014)} puntos en ${lapso} años`}
                </p>
              </div>
            );
          })}
        </div>

        {/* ---------------- PAÍSES ---------------- */}
        <div className="bloque">
          <h2>Dónde se nota más</h2>
          <p className="intro">
            La media europea esconde diferencias grandes. Cambia el orden y
            cambia la historia: por tasa salen arriba los países donde el
            desajuste es alto para todo el mundo; por brecha, aquellos donde le
            ocurre sobre todo a quien viene de fuera.
          </p>

          <div className="campo">
            <span className="etiqueta" id="lbl-orden">Ordenar por</span>
            <div className="fichas" role="group" aria-labelledby="lbl-orden">
              <button className="ficha" aria-pressed={orden === "brecha"} onClick={() => setOrden("brecha")}>
                Brecha con los nacionales
              </button>
              <button className="ficha" aria-pressed={orden === "tasa"} onClick={() => setOrden("tasa")}>
                Tasa más alta
              </button>
            </div>
          </div>

          {paisesOrdenados.map((p) => (
            <div className="barra-fila" key={p.geo}>
              <div className="barra-cab">
                <span>{p.pais}</span>
                <span className="n">{coma(p.extra_ue)} %</span>
              </div>
              <div className="pista">
                <div className="relleno tenue" style={{ width: p.nacionales === null ? 0 : ancho(p.nacionales, ESCALA_PAIS) }} />
                <div className="relleno acento encima" style={{ width: ancho(p.extra_ue, ESCALA_PAIS) }} />
              </div>
              <p className="barra-pie">
                {p.nacionales === null
                  ? "Sin dato de los nacionales para comparar"
                  : `Nacionales del mismo país: ${coma(p.nacionales)} % · ${
                      Math.abs(p.brecha) < 0.05
                        ? "sin diferencia apreciable"
                        : p.brecha > 0
                          ? `${coma(p.brecha)} puntos por encima`
                          : `${coma(Math.abs(p.brecha))} puntos por debajo: aquí son los nacionales quienes trabajan más por debajo de su título`
                    }`}
              </p>
            </div>
          ))}

          <p className="detalle">
            La barra tenue es la tasa de los nacionales de ese mismo país; la de
            color, la de los ciudadanos de fuera de la UE.{" "}
            {mayorTasa && mayorBrecha && (
              <>
                {mayorTasa.pais} registra la tasa más alta ({coma(mayorTasa.extra_ue)} %)
                {mayorTasa.geo === mayorBrecha.geo
                  ? " y también la mayor diferencia frente a sus propios nacionales."
                  : `, y ${mayorBrecha.pais} la mayor diferencia frente a sus propios nacionales (${coma(mayorBrecha.brecha)} puntos).`}
              </>
            )}
          </p>
        </div>

        {/* ---------------- HALLAZGO: LOS QUE FALTAN ---------------- */}
        {SIN_DATO.length > 0 && (
          <div className="bloque">
            <h2>
              {SIN_DATO.length} países de la UE no están en esta comparación
            </h2>
            <p className="detalle">
              {SIN_DATO.map((p) => p.pais).join(", ")} no publican valor para{" "}
              {anioReciente} en esta serie. No significa que allí no exista
              sobrecualificación: la Encuesta de Población Activa es una muestra,
              y cuando el número de personas migrantes con título universitario
              es demasiado pequeño para dar una cifra fiable, Eurostat no la
              publica. La ausencia se declara aquí en lugar de rellenarse.
            </p>
          </div>
        )}

        <div className="pie">
          <b>Fuente:</b> Eurostat, Encuesta de Población Activa de la UE
          (EU-LFS), conjunto {datos.conjunto}. Se considera sobrecualificada a
          la persona empleada con estudios superiores que ocupa un puesto de
          baja o media cualificación. Franja de edad {datos.edad}.
          {/* auditoria-ok: ISCED e ISCO son códigos de clasificación de Eurostat y los años de la franja los declara datos.edad; no son cifras nuestras */}
          <span> Los códigos exactos son ISCED 5–8 para el nivel de estudios e ISCO 4–9 para el tipo de puesto, en la franja de 20 a 64 años.</span>{" "}
          Otras franjas dan cifras distintas y no son comparables entre sí. La
          clasificación es por ciudadanía, no por país de nacimiento; Eurostat
          publica una serie paralela por país de nacimiento cuyos valores no son
          intercambiables con estos. Los nombres de país están traducidos por
          nosotros; el código original de la fuente y los límites declarados
          quedan en el <a href="/metodo/">método</a>.
        </div>
      </div>
    </div>
  );
}
