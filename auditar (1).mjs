#!/usr/bin/env node
/* ==========================================================================
   Cardinal Datos — auditoría del repositorio

   Responde a una sola pregunta: ¿hace falta tocar algo?

   Verde quiere decir que no. Rojo quiere decir que pasó algo concreto, y
   el mensaje dice cuál. Sin esto, cada duda obliga a abrir archivos y
   mirar a mano — que es lo que hicimos durante toda una sesión de
   auditoría y lo que este archivo existe para no repetir.

   POR QUÉ ESTÁ EN NODE Y NO EN pipeline/*.py
   piezas.js y correcciones.js son módulos ES. Node los importa y obtiene
   los valores de verdad. Python tendría que leerlos con expresiones
   regulares, y correcciones.js ya arma un campo concatenando cadenas con
   «+»: una regex lo lee mal y se calla. Un import no.

   POR QUÉ NO TIENE DEPENDENCIAS
   Para no meter un tercer ecosistema npm en dependabot.yml. Todo lo que
   usa viene con Node. No hace falta package.json: la extensión .mjs ya
   declara que es un módulo.

   DOS SEVERIDADES
   - ERROR: incumple una regla del proyecto sin ambigüedad. Tumba la
     ejecución. No debería tener falsos positivos nunca.
   - AVISO: algo que parece sospechoso pero que puede ser legítimo. Se
     informa y no tumba nada.

   El chequeo de la regla de oro nace como AVISO a propósito. Un chequeo
   que ladra sin razón se termina desactivando, y un chequeo desactivado
   no audita nada. Cuando los casos legítimos estén anotados con el
   marcador «auditoria-ok:», se pasa a ERROR con la bandera --estricto y
   se añade esa bandera al workflow.

   Se corre solo:  node auditoria/auditar.mjs [--estricto]
   ========================================================================== */

import { readFile, readdir, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const ESTRICTO = process.argv.includes("--estricto");

const errores = [];
const avisos = [];

const error = (chequeo, mensaje) => errores.push({ chequeo, mensaje });
const aviso = (chequeo, mensaje) =>
  (ESTRICTO ? errores : avisos).push({ chequeo, mensaje });

const enRaiz = (...p) => path.join(RAIZ, ...p);

async function existe(ruta) {
  try {
    await stat(ruta);
    return true;
  } catch {
    return false;
  }
}

async function leerJson(ruta) {
  return JSON.parse(await readFile(ruta, "utf-8"));
}

/* Importa un módulo ES del repositorio por ruta absoluta. En Windows un
   path suelto no vale como especificador de import; pathToFileURL sí. */
async function importar(rel) {
  return import(pathToFileURL(enRaiz(rel)).href);
}

/* ==========================================================================
   1. REGISTROS: piezas, páginas y carpetas de datos
   ========================================================================== */

async function auditarPiezas(piezas) {
  const slugs = piezas.map((p) => p.slug);

  const repetidos = slugs.filter((s, i) => slugs.indexOf(s) !== i);
  for (const s of new Set(repetidos)) {
    error("piezas", `el slug «${s}» aparece más de una vez en piezas.js`);
  }

  const hoy = new Date().toISOString().slice(0, 10);

  for (const p of piezas) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(p.publicado)) {
      error("piezas", `«${p.slug}» tiene una fecha mal formada: ${p.publicado}`);
    } else if (p.publicado > hoy) {
      error("piezas", `«${p.slug}» dice publicarse el ${p.publicado}, que es futuro`);
    }

    const pagina = enRaiz("sitio", "src", "pages", `${p.slug}.astro`);
    if (!(await existe(pagina))) {
      error("piezas", `«${p.slug}» no tiene página en sitio/src/pages/${p.slug}.astro`);
    }

    // metodo: null es válido. EDITORIAL permite publicar una pieza
    // declarada como incompleta; tratarlo como fallo pondría al código a
    // contradecir la línea editorial.
    if (!p.metodo) {
      avisos.push({
        chequeo: "piezas",
        mensaje: `«${p.slug}» está declarada sin método reproducible (metodo: null)`,
      });
      continue;
    }

    for (const archivo of ["crudo.json", "limpio.json", "metodo.md"]) {
      const ruta = enRaiz("data", p.metodo, archivo);
      if (!(await existe(ruta))) {
        error("piezas", `falta data/${p.metodo}/${archivo}, que necesita «${p.slug}»`);
      }
    }
  }

  return slugs;
}

/* Al revés: carpetas de data/ que ninguna pieza reclama. Es la que se
   rompe sola con el tiempo, cuando se abandona una pieza y su carpeta
   queda ocupando sitio y aparentando ser material publicado. */
async function auditarCarpetasHuerfanas(piezas) {
  const reclamadas = new Set(piezas.map((p) => p.metodo).filter(Boolean));
  const entradas = await readdir(enRaiz("data"), { withFileTypes: true });

  for (const e of entradas) {
    if (!e.isDirectory()) continue;
    if (!reclamadas.has(e.name)) {
      error("datos", `data/${e.name}/ no la reclama ninguna pieza de piezas.js`);
    }
  }
}

/* ==========================================================================
   2. CORRECCIONES
   ========================================================================== */

function auditarCorrecciones(correcciones, niveles, slugs) {
  const clavesNivel = Object.keys(niveles);

  for (const [i, c] of correcciones.entries()) {
    const donde = `entrada ${i + 1} (${c.fecha})`;

    if (!clavesNivel.includes(c.nivel)) {
      error("correcciones", `${donde} usa el nivel «${c.nivel}», que no está en NIVELES`);
    }
    if (c.pieza !== null && !slugs.includes(c.pieza)) {
      error("correcciones", `${donde} apunta a la pieza «${c.pieza}», que no existe en piezas.js`);
    }
    if (!/^\d{4}-\d{2}-\d{2}$/.test(c.fecha)) {
      error("correcciones", `${donde} tiene una fecha mal formada`);
    }
    for (const campo of ["decia", "dice", "por_que"]) {
      if (!c[campo] || !String(c[campo]).trim()) {
        error("correcciones", `${donde} tiene el campo «${campo}» vacío`);
      }
    }
  }
}

/* ==========================================================================
   3. FUENTES

   El chequeo que importa aquí no es de forma sino de coherencia: el
   registro define «en uso» como sostener al menos una pieza publicada.
   Eso es una afirmación comprobable, y la página de método la publica
   como cifra. Estuvo mal durante meses sin que nada avisara.
   ========================================================================== */

async function auditarFuentes(piezas) {
  const registro = await leerJson(enRaiz("data", "fuentes.json"));
  const fuentes = registro.fuentes ?? [];

  const ids = fuentes.map((f) => f.id);
  for (const id of new Set(ids.filter((x, i) => ids.indexOf(x) !== i))) {
    error("fuentes", `el id «${id}» aparece más de una vez`);
  }

  for (const f of fuentes) {
    if (!(f.estado in (registro._estados ?? {}))) {
      error("fuentes", `«${f.id}» tiene estado «${f.estado}», fuera del vocabulario de _estados`);
    }
    if (!(f.papel in (registro._papeles ?? {}))) {
      error("fuentes", `«${f.id}» tiene papel «${f.papel}», fuera del vocabulario de _papeles`);
    }
  }

  const fuentesDePiezas = new Set(piezas.map((p) => p.fuente));

  for (const f of fuentes) {
    if (f.estado === "en uso" && !fuentesDePiezas.has(f.nombre)) {
      error(
        "fuentes",
        `«${f.id}» está marcada «en uso» pero ninguna pieza la declara como fuente. ` +
          `El propio registro define ese estado como sostener al menos una pieza publicada.`
      );
    }
  }

  const nombresEnUso = new Set(fuentes.filter((f) => f.estado === "en uso").map((f) => f.nombre));
  for (const p of piezas) {
    if (!nombresEnUso.has(p.fuente)) {
      error(
        "fuentes",
        `«${p.slug}» declara la fuente «${p.fuente}», que no figura en fuentes.json como «en uso»`
      );
    }
  }
}

/* ==========================================================================
   4. DATOS: invariantes aritméticas dentro de cada limpio.json

   Esta sección sí conoce la forma de cada conjunto, y tiene que ser así:
   comprobar que una resta cuadra exige saber qué se resta. Cada chequeo
   va nombrado y solo corre si su carpeta existe.
   ========================================================================== */

async function auditarRemesas() {
  const ruta = enRaiz("data", "remesas-costo-latam", "limpio.json");
  if (!(await existe(ruta))) return;

  const d = await leerJson(ruta);
  const monto = d.monto_referencia_usd;

  for (const p of d.con_dato ?? []) {
    const esperado = (p.costo_pct * monto) / 100;
    // Tolerancia de dos céntimos, no igualdad exacta. El script calcula el
    // monto con el porcentaje sin redondear y guarda el porcentaje ya
    // redondeado, así que los dos campos NO se derivan uno del otro. Es
    // metodológicamente correcto y está declarado en la pieza.
    if (Math.abs(esperado - p.sobre_200_usd) > 0.02) {
      error(
        "datos",
        `remesas: ${p.pais} declara ${p.costo_pct} % y ${p.sobre_200_usd} sobre ${monto}; ` +
          `esperado ${esperado.toFixed(2)} ±0,02`
      );
    }
    if (!p.pais_fuente) {
      aviso("datos", `remesas: ${p.iso3} no conserva pais_fuente`);
    }
  }

  for (const p of d.sin_dato ?? []) {
    if (!p.iso3 || !p.pais) {
      error("datos", `remesas: una entrada de sin_dato no tiene iso3 o pais`);
    }
    if (!p.motivo) {
      aviso(
        "datos",
        `remesas: ${p.pais} está en sin_dato sin campo «motivo». No se distingue ` +
          `«no hay indicador» de «hay indicador con valor nulo», que EDITORIAL sí distingue.`
      );
    }
  }
}

async function auditarSobrecualificacion() {
  const ruta = enRaiz("data", "sobrecualificacion-ue", "limpio.json");
  if (!(await existe(ruta))) return;

  const d = await leerJson(ruta);

  for (const p of d.paises_2024 ?? []) {
    if (p.nacionales === null || p.brecha === null) continue;
    const esperado = p.extra_ue - p.nacionales;
    if (Math.abs(esperado - p.brecha) > 0.05) {
      error(
        "datos",
        `sobrecualificación: ${p.pais} declara brecha ${p.brecha}; ` +
          `${p.extra_ue} − ${p.nacionales} = ${esperado.toFixed(1)}`
      );
    }
  }

  for (const p of d.sin_dato ?? []) {
    if (!p.pais) error("datos", "sobrecualificación: una entrada de sin_dato no tiene pais");
  }
}

/* ==========================================================================
   5. ENLACES INTERNOS

   Cada href="/algo/" del sitio tiene que corresponder a una página. Un
   enlace roto en la cadena que va del dato a su método es peor que no
   tenerlo: promete trazabilidad y devuelve un 404.
   ========================================================================== */

async function archivosDe(carpeta, extensiones) {
  const salida = [];
  async function recorrer(dir) {
    let entradas;
    try {
      entradas = await readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const e of entradas) {
      const completa = path.join(dir, e.name);
      if (e.isDirectory()) await recorrer(completa);
      else if (extensiones.some((x) => e.name.endsWith(x))) salida.push(completa);
    }
  }
  await recorrer(enRaiz(carpeta));
  return salida;
}

async function auditarEnlaces() {
  /* Las páginas se buscan RECORRIENDO subcarpetas, no solo el primer nivel.
     Antes esto usaba un readdir plano, que bastaba mientras todas las
     páginas vivían sueltas en pages/. Al aparecer pages/notas/, ese readdir
     dejaba de ver tanto /notas/ como cada /notas/<slug>/, y los marcaba a
     todos como enlaces rotos: un error de la auditoría, no del sitio. Un
     falso positivo en un chequeo de severidad «error» es especialmente
     caro, porque tumba la ejecución y enseña a desconfiar del verde.

     Astro deriva la URL de la ruta del archivo dentro de pages/, así que
     la ruta se compone igual: la carpeta más el nombre, y un index.astro
     responde en la ruta de su carpeta. */
  const rutasValidas = new Set(["/"]);
  for (const completa of await archivosDe("sitio/src/pages", [".astro"])) {
    const rel = path
      .relative(enRaiz("sitio", "src", "pages"), completa)
      .split(path.sep)
      .join("/");
    if (rel === "404.astro") continue;
    const sinExtension = rel.replace(/\.astro$/, "");
    const ruta = sinExtension.replace(/(^|\/)index$/, "");
    rutasValidas.add(ruta === "" ? "/" : `/${ruta}/`);
  }

  const fuentes = await archivosDe("sitio/src", [".astro", ".jsx", ".js"]);
  for (const archivo of fuentes) {
    const texto = await readFile(archivo, "utf-8");
    const rel = path.relative(RAIZ, archivo);
    for (const m of texto.matchAll(/href="(\/[^"#?]*)"/g)) {
      const destino = m[1];
      // Se ignoran los archivos servidos tal cual desde sitio/public/.
      if (/\.[a-z0-9]+$/i.test(destino)) continue;
      if (!rutasValidas.has(destino)) {
        error("enlaces", `${rel} enlaza a ${destino}, que no corresponde a ninguna página`);
      }
    }
  }
}

/* ==========================================================================
   6. REGLA DE ORO: cifras escritas a mano en el texto visible

   El fallo real no fue nunca un «39,8» tecleado: fue la palabra «diez» en
   «Los diez países». Por eso se buscan números escritos con letra además
   de con dígitos.

   Solo se mira el texto literal entre etiquetas — lo que no contiene
   llaves. Cualquier texto con {expresión} ya viene de los datos por
   construcción, y los atributos y el código quedan fuera.

   Para eximir un caso legítimo (una constante de la fuente, un código
   ISCED) se pone en esa línea o en la anterior un comentario con
   «auditoria-ok: la razón». La exención vive junto al número y con su
   motivo, no en una lista aparte que nadie vuelve a leer.
   ========================================================================== */

const NUMEROS_CON_LETRA = [
  "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez",
  "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete",
  "dieciocho", "diecinueve", "veinte", "treinta", "cuarenta", "cincuenta",
  "sesenta", "setenta", "ochenta", "noventa", "cien", "ciento", "mil",
];

const RE_PALABRA = new RegExp(`\\b(${NUMEROS_CON_LETRA.join("|")})\\b`, "gi");

/* Los comentarios se vacían, no se borran: se sustituye cada carácter por
   un espacio y se conservan los saltos de línea. Si se borraran, un
   comentario de varias líneas correría la numeración y el aviso señalaría
   una línea equivocada — que es peor que no avisar, porque manda a mirar
   al sitio incorrecto. */
function sinComentarios(texto) {
  return texto
    .replace(/\/\*[\s\S]*?\*\//g, (m) => m.replace(/[^\n]/g, " "))
    .replace(/^(\s*)\/\/.*$/gm, "$1");
}

async function auditarReglaDeOro(piezas) {
  const objetivos = [];
  for (const p of piezas) {
    objetivos.push(path.join("sitio", "src", "pages", `${p.slug}.astro`));
  }
  for (const c of await archivosDe("sitio/src/components", [".jsx"])) {
    objetivos.push(path.relative(RAIZ, c));
  }

  for (const rel of objetivos) {
    const completa = enRaiz(rel);
    if (!(await existe(completa))) continue;

    const original = await readFile(completa, "utf-8");
    const lineas = original.split("\n");
    const limpio = sinComentarios(original);

    // Texto literal entre etiquetas: sin < > ni llaves de por medio.
    //
    // El «>» tiene que ser el cierre de una etiqueta, no un operador: se
    // exige que lo preceda una letra, un dígito, una comilla o una barra
    // (`</b>`, `className="pie">`, `<br />`). Así quedan fuera el `=>` de
    // las funciones flecha y el `length > 0` de las comparaciones, que en
    // la primera versión se colaban como si fueran texto. Y el «<» tiene
    // que abrir etiqueta, no ser un «menor que».
    for (const m of limpio.matchAll(/(?<=[A-Za-z0-9"'/])>([^<>{}]+)<(?=[/a-zA-Z])/g)) {
      const fragmento = m[1];
      // Sin letras no es prosa: es una expresión que se coló.
      if (!/[a-záéíóúüñ]/i.test(fragmento)) continue;
      if (!/\d/.test(fragmento) && !RE_PALABRA.test(fragmento)) continue;
      RE_PALABRA.lastIndex = 0;

      const linea = limpio.slice(0, m.index).split("\n").length;
      const contexto = [lineas[linea - 2] ?? "", lineas[linea - 1] ?? ""].join("\n");
      if (contexto.includes("auditoria-ok:")) continue;

      const muestra = fragmento.trim().replace(/\s+/g, " ").slice(0, 70);
      if (!muestra) continue;
      aviso("regla-de-oro", `${rel}:${linea} — cifra en texto literal: «${muestra}»`);
    }
  }
}

/* ==========================================================================
   Salida
   ========================================================================== */

async function main() {
  const { piezasPorFecha } = await importar("sitio/src/datos/piezas.js");
  const { correccionesPorFecha, NIVELES } = await importar("sitio/src/datos/correcciones.js");

  const piezas = piezasPorFecha();

  const slugs = await auditarPiezas(piezas);
  await auditarCarpetasHuerfanas(piezas);
  auditarCorrecciones(correccionesPorFecha(), NIVELES, slugs);
  await auditarFuentes(piezas);
  await auditarRemesas();
  await auditarSobrecualificacion();
  await auditarEnlaces();
  await auditarReglaDeOro(piezas);

  console.log(`Auditoría de Cardinal Datos — ${piezas.length} piezas revisadas`);
  console.log(ESTRICTO ? "Modo estricto: los avisos cuentan como errores.\n" : "");

  if (avisos.length) {
    console.log(`AVISOS (${avisos.length}) — no tumban la ejecución:`);
    for (const a of avisos) console.log(`  · [${a.chequeo}] ${a.mensaje}`);
    console.log("");
  }

  if (errores.length) {
    console.log(`ERRORES (${errores.length}):`);
    for (const e of errores) console.log(`  ✗ [${e.chequeo}] ${e.mensaje}`);
    console.log("\nLa auditoría no pasa.");
    process.exit(1);
  }

  console.log("Sin errores. No hace falta tocar nada.");
}

main().catch((e) => {
  console.error("La auditoría falló al ejecutarse:", e);
  process.exit(1);
});
