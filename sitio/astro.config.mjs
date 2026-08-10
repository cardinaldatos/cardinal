import { defineConfig } from "astro/config";
import react from "@astrojs/react";

// Salida totalmente estática. Las islas de React se renderizan a HTML en la
// compilación y se hidratan en el navegador: no hay servidor, así que no
// hace falta adaptador de Cloudflare.
//
// `site` es el dominio propio, no el subdominio .workers.dev. El Worker
// sigue llamándose "www" y respondiendo también en workers.dev; esto solo
// fija la forma canónica que usan las URLs absolutas del sitio.
//
// CAMBIO: sacamos de la página el poco de JavaScript en línea que Astro
// genera para arrancar las islas de React. Por defecto ese arranque va
// incrustado en el HTML como <script> sin archivo, y un CSP estricto
// (script-src 'self') lo bloquea: sin él, las piezas interactivas —las
// fichas de país, los botones de año— dejan de responder.
//
// La alternativa habitual sería autorizar ese script por su hash sha256.
// No lo hacemos: el hash cambia cada vez que Astro se actualiza o se toca
// una isla, y habría que recapturarlo a mano cada vez o la pieza se rompe
// en silencio. Sacar el script a un archivo .js servido desde nuestro
// propio dominio lo vuelve innecesario: 'self' ya lo cubre, y no queda
// ninguna huella que mantener.
//
//   - inlineStylesheets: "never"  -> los estilos también salen a archivo,
//     no incrustados. Coherente con lo anterior y hace el CSP de estilos
//     más estricto a futuro.
//   - build.assetsInlineLimit: 0  -> nada se incrusta por ser "pequeño";
//     todo activo va a archivo. Es la regla de Vite (el empaquetador que
//     Astro usa por debajo) que evita los <script> y las imágenes en línea.
export default defineConfig({
  site: "https://cardinaldatos.org",
  output: "static",
  trailingSlash: "always",
  integrations: [react()],
  build: {
    inlineStylesheets: "never",
  },
  vite: {
    build: {
      assetsInlineLimit: 0,
    },
  },
});
