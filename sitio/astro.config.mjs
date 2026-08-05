import { defineConfig } from "astro/config";

// Salida totalmente estática: no hace falta adaptador de Cloudflare.
// astro build deja HTML plano en dist/ y wrangler lo sube como activos
// estáticos del Worker.
//
// Cuando entren las islas de React (al migrar la primera pieza) se añade
// aquí la integración @astrojs/react. Siguen siendo estáticas: React solo
// se hidrata en el cliente.
export default defineConfig({
  site: "https://cardinaldatos.workers.dev",
  output: "static",
  trailingSlash: "always",
});
