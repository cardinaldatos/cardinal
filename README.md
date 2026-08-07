# Cardinal Datos

**Datos que no se traducen solos**

Recogemos estadísticas públicas sobre migración y diáspora que existen, pero
casi nadie puede leer. Las volvemos comprensibles, en español.

Sitio: https://cardinaldatos.org

---

## Estructura
pipeline/ scripts que descargan y limpian los datos
data/ un subdirectorio por tema: crudo.json, limpio.json, metodo.md
sitio/ la web (por ahora, una página estática)
## Regla de oro

Toda cifra publicada tiene que rastrearse hasta un archivo de `data/`
descargado por un script. Si la copiaste de un PDF, no entra.

Los nombres de país se traducen al español en el pipeline, no en cada
superficie. El nombre original de la fuente se conserva en `limpio.json`
(campo `pais_fuente`) y en `crudo.json` sin tocar.

## Puesta en marcha

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cd pipeline
python verificar.py              # comprueba que las tres APIs responden
```

## Fuentes

| Fuente | Cubre | Licencia |
|---|---|---|
| Banco Mundial, Indicators API | Remesas, migración, empleo | CC BY 4.0 |
| Eurostat, API Statistics | Datos europeos por país | Reuso con atribución |
| SSB, PxWebApi v2 | Noruega | CC BY 4.0 |

Ninguna requiere clave de acceso.

## Publicación

El sitio se despliega en Cloudflare Workers con activos estáticos.
El contenido de `sitio/` es lo que se sube.
