import { defineConfig } from "astro/config";
import react from "@astrojs/react";

// Salida totalmente estática. Las islas de React se renderizan a HTML en la
// compilación y se hidratan en el navegador: no hay servidor, así que no
// hace falta adaptador de Cloudflare.
//
// `site` es el dominio propio, no el subdominio .workers.dev. El Worker
// sigue llamándose "www" y respondiendo también en workers.dev; esto solo
// fija la forma canónica que usan las URLs absolutas del sitio.
export default defineConfig({
  site: "https://cardinaldatos.org",
  output: "static",
  trailingSlash: "always",
  integrations: [react()],
});
