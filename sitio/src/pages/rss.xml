/* ==========================================================================
   Cardinal Datos — feed RSS

   Un archivo dentro de src/pages/ que NO termina en .astro sino en .js es
   lo que Astro llama un "endpoint": en vez de una página HTML, devuelve el
   texto que tú le digas. Este devuelve XML, y por llamarse rss.xml.js
   acaba publicado en https://cardinaldatos.workers.dev/rss.xml

   Se ejecuta una sola vez, durante `npm run build`. El resultado es un
   archivo estático más dentro de dist/. No hay servidor detrás.

   Escribimos el XML a mano, sin librería, por dos razones: no añade una
   dependencia que luego haya que mantener, y el formato es lo bastante
   corto como para leerlo entero y entender qué se publica.
   ========================================================================== */

import { piezasPorFecha } from "../datos/piezas.js";

const SITIO = "https://cardinaldatos.workers.dev";

const TITULO = "Cardinal Datos";
const DESCRIPCION =
  "Estadísticas públicas sobre migración y diáspora, en español. Cada pieza declara su fuente, su año y su método.";

/* En XML estos cinco caracteres tienen significado propio. Si aparecen sin
   escapar dentro de un texto, el feed queda malformado y los lectores lo
   rechazan entero, no solo esa pieza. El orden importa: & va primero, o
   acabaría escapando los & que acabamos de introducir. */
function escapar(texto) {
  return String(texto)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

/* RSS exige fechas en formato RFC 822 ("Fri, 07 Aug 2026 00:00:00 GMT"),
   no el AAAA-MM-DD que usamos nosotros. toUTCString() lo da exacto. */
function fechaRss(iso) {
  return new Date(`${iso}T00:00:00Z`).toUTCString();
}

export function GET() {
  const piezas = piezasPorFecha();

  const items = piezas
    .map((p) => {
      const enlace = `${SITIO}/${p.slug}/`;
      return `    <item>
      <title>${escapar(p.titulo)}</title>
      <link>${escapar(enlace)}</link>
      <guid isPermaLink="true">${escapar(enlace)}</guid>
      <pubDate>${fechaRss(p.publicado)}</pubDate>
      <description>${escapar(p.resumen)}</description>
      <category>${escapar(p.fuente)}</category>
    </item>`;
    })
    .join("\n");

  /* lastBuildDate es cuándo se compiló; pubDate del canal es la fecha de
     la pieza más reciente. Son cosas distintas a propósito. */
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${escapar(TITULO)}</title>
    <link>${SITIO}/</link>
    <description>${escapar(DESCRIPCION)}</description>
    <language>es</language>
    <atom:link href="${SITIO}/rss.xml" rel="self" type="application/rss+xml" />
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
${piezas.length ? `    <pubDate>${fechaRss(piezas[0].publicado)}</pubDate>\n` : ""}${items}
  </channel>
</rss>
`;

  return new Response(xml, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  });
}
