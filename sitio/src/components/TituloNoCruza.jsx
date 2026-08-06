import { useState } from "react";

/* ------------------------------------------------------------------
   DATOS REALES — Eurostat, "Migrant integration statistics –
   over-qualification". Datos extraídos el 16 de julio de 2025,
   año de referencia 2024. Encuesta de Población Activa de la UE.

   Tasa de sobrecualificación: personas empleadas con estudios
   superiores (ISCED 5–8) que trabajan en ocupaciones de baja o
   media cualificación (ISCO 4–9).

   PENDIENTE DE FASE 1: reconstruir estas cifras desde la API de
   Eurostat con un script en pipeline/, como se hizo con remesas.
   Hasta entonces, esta pieza no sale de "en construcción".
------------------------------------------------------------------ */

const GRUPOS = [
  {
    id: "nac",
    corto: "Nacionales",
    largo: "Ciudadanos del país donde viven",
    v2014: 21,
    v2024: 21,
    nota: "Se ha mantenido estable entre 20 % y 21 % durante una década.",
  },
  {
    id: "ue",
    corto: "De otro país de la UE",
    largo: "Ciudadanos de otro Estado miembro",
    v2014: 34.0,
    v2024: 30.3,
    nota: "Su título se reconoce por norma europea, y aun así el desajuste persiste.",
  },
  {
    id: "extra",
    corto: "De fuera de la UE",
    largo: "Ciudadanos de un país no comunitario",
    v2014: 45.9,
    v2024: 39.6,
    nota: "El grupo más afectado cada año desde que hay registro. Las mujeres, más que los hombres.",
  },
];

const CASOS = [
  {
    lugar: "Grecia",
    texto: "La tasa más alta de la UE para hombres y mujeres de fuera del bloque.",
  },
  {
    lugar: "Chequia y Malta",
    texto:
      "Entre los jóvenes de 20 a 34 años de fuera de la UE supera el 50 %. Entre los nacionales de la misma edad, no llega al 15 %.",
  },
  {
    lugar: "Italia, España y Grecia",
    texto:
      "Pasados los 35 años, más de la mitad de los trabajadores de fuera de la UE con título universitario siguen en empleos por debajo de su formación.",
  },
  {
    lugar: "Alemania, Irlanda y Chipre",
    texto:
      "La excepción: aquí son los ciudadanos de otros países de la UE quienes registran la tasa más alta.",
  },
];

/* Coma decimal, siempre. Regla del manual: las cifras hablan español. */
const coma = (v, decimales = 1) =>
  v.toLocaleString("es", {
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  });

const ESCALA_DECADA = 50; // % máximo de las barras de comparación

export default function TituloNoCruza() {
  const [grupoId, setGrupoId] = useState("extra");
  const [anio, setAnio] = useState(2024);

  const grupo = GRUPOS.find((g) => g.id === grupoId);
  const tasa = anio === 2024 ? grupo.v2024 : grupo.v2014;
  const marcados = Math.round(tasa);

  return (
    <div className="pieza" data-fondo="claro" style={{ "--acento": "var(--ambar)" }}>
      <div className="marco">
        <p className="cejilla">Eurostat · Encuesta de Población Activa · 2024</p>

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
              <button
                key={g.id}
                className="ficha"
                aria-pressed={g.id === grupoId}
                onClick={() => setGrupoId(g.id)}
              >
                {g.corto}
              </button>
            ))}
          </div>
        </div>

        <div className="campo">
          <span className="etiqueta" id="lbl-anio">Año</span>
          <div className="fichas" role="group" aria-labelledby="lbl-anio">
            {[2014, 2024].map((a) => (
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

        {/* ---------------- CUADRÍCULA ---------------- */}
        <div className="tarjeta">
          <p className="lectura">
            <b className="dato-central">{marcados} de cada 100</b>
            {grupo.largo.toLowerCase()} con título universitario trabajaban en{" "}
            {anio} en un puesto que no exige estudios superiores.
          </p>

          <div
            className="rejilla"
            role="img"
            aria-label={`Cuadrícula de 100 unidades: ${marcados} marcadas como sobrecualificadas`}
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
              Trabaja por debajo de su título
            </span>
            <span>
              <i />
              Trabaja acorde a su título
            </span>
          </div>

          <p className="detalle">{grupo.nota}</p>
        </div>

        {/* ---------------- DÉCADA ---------------- */}
        <div className="bloque">
          <h2>Diez años después, la brecha sigue</h2>
          <p className="intro">
            La barra tenue es 2014; la de color, 2024. Las tasas de los
            migrantes bajaron, pero ninguna se acercó a la de los nacionales.
          </p>

          {GRUPOS.map((g) => (
            <div className="barra-fila decada" key={g.id}>
              <div className="barra-cab">
                <span>{g.corto}</span>
                <span className="n">
                  {coma(g.v2014)} % → {coma(g.v2024)} %
                </span>
              </div>
              <div className="pista">
                <div
                  className="relleno tenue"
                  style={{ width: (g.v2014 / ESCALA_DECADA) * 100 + "%" }}
                />
                <div
                  className="relleno acento encima"
                  style={{ width: (g.v2024 / ESCALA_DECADA) * 100 + "%" }}
                />
              </div>
              <p className="barra-pie">
                {g.v2014 === g.v2024
                  ? "Sin cambio apreciable"
                  : `Bajó ${coma(g.v2014 - g.v2024)} puntos en diez años`}
              </p>
            </div>
          ))}
        </div>

        {/* ---------------- CASOS ---------------- */}
        <div className="bloque">
          <h2>Dónde se nota más</h2>
          <p className="intro">
            La media europea esconde diferencias grandes entre países.
          </p>
          <div>
            {CASOS.map((c) => (
              <div className="caso" key={c.lugar}>
                <strong>{c.lugar}</strong>
                <span>{c.texto}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="pie">
          <b>Fuente:</b> Eurostat, «Migrant integration statistics –
          over-qualification», datos de 2024 extraídos el 16 de julio de 2025.
          Base: Encuesta de Población Activa de la UE. Se considera
          sobrecualificada a la persona empleada con estudios superiores
          (ISCED 5–8) que ocupa un puesto de baja o media cualificación
          (ISCO 4–9). La tasa de los nacionales aparece redondeada a 21 %:
          Eurostat la describe estable entre 20 % y 21 % en toda la serie.
        </div>
      </div>
    </div>
  );
}
