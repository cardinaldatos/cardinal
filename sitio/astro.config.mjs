import { defineConfig } from "astro/config";
import react from "@astrojs/react";

// Salida totalmente estática. Las islas de React se renderizan a HTML en la
// compilación y se hidratan en el navegador: no hay servidor, así que no
// hace falta adaptador de Cloudflare.
export default defineConfig({
  site: "https://cardinaldatos.workers.dev",
  output: "static",
  trailingSlash: "always",
  integrations: [react()],
});
