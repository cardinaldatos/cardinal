/* ==========================================================================
   Cardinal Datos — catálogo de piezas publicadas

   Este archivo es el único origen de verdad sobre QUÉ piezas existen.
   Lo leen tres sitios distintos:

     - src/pages/index.astro   -> la lista de la portada
     - src/pages/rss.xml.js    -> el feed RSS
     - src/pages/metodo.astro  -> la página de método público

   Antes, la lista vivía dentro de index.astro. Si hubiéramos añadido el
   RSS copiándola, la segunda publicación habría quedado desincronizada:
   pieza nueva en la portada, feed viejo. Es el mismo criterio que ya
   aplica limpio.json a las tres superficies de datos.

   PARA AÑADIR UNA PIEZA: añade un objeto aquí. La portada, el feed y la
   página de método la recogen solas. No hay que tocar nada más.

   CAMPOS
   slug        carpeta de la URL: /<slug>/. Tiene que existir un
               src/pages/<slug>.astro con ese nombre.
   titulo      el titular de la pieza.
   resumen     una o dos frases. Se ve en la portada y en el feed.
   fuente      organismo. Se muestra como cejilla.
   anio        año de los DATOS, no de la publicación.
   publicado   fecha en que salió la pieza, AAAA-MM-DD. Solo la usa el
               RSS, para ordenar y para el campo pubDate. Si te la
               inventas, los lectores de feeds mostrarán fechas falsas:
               ponla real y no la cambies después.
   metodo      nombre de la carpeta dentro de data/ que contiene su
               metodo.md, o null si la pieza todavía no tiene método
               reproducible. null no es un error: se declara como tal en
               la página de método.
   ========================================================================== */

export const PIEZAS = [
  {
    slug: "remesas-costo-latam",
    titulo: "Cuánto se queda en el camino",
    resumen:
      "Lo que cuesta enviar 200 dólares a diez países de América Latina, y los tres que no aparecen en la estadística.",
    fuente: "Banco Mundial",
    anio: "2023",
    publicado: "2026-08-07",
    metodo: "remesas-costo-latam",
  },
  {
    slug: "titulo-no-cruza",
    titulo: "El título no cruza",
    resumen:
      "Cuatro de cada diez migrantes de fuera de la UE con título universitario trabajan por debajo de su formación.",
    fuente: "Eurostat",
    anio: "2024",
    publicado: "2026-07-28",
    metodo: null,
  },
];

/** Las piezas ordenadas de más reciente a más antigua. */
export function piezasPorFecha() {
  return [...PIEZAS].sort((a, b) => b.publicado.localeCompare(a.publicado));
}
