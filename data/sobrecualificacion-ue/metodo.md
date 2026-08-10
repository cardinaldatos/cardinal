# Método — sobrecualificacion-ue

**Fuente:** Eurostat, Encuesta de Población Activa de la UE (EU-LFS), conjunto lfsa_eoqgan (tasas de sobrecualificación por ciudadanía).
**Consulta:** `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/lfsa_eoqgan?format=JSON&age=Y20-64&sex=T&unit=PC`
**Fecha de extracción:** 2026-08-10

## Definición
Tasa de sobrecualificación: proporción de personas empleadas con estudios superiores (ISCED 5-8) que trabajan en ocupaciones de baja o media cualificación (ISCO, grupos 4-9).

Las personas se clasifican por ciudadanía, no por país de nacimiento: nacionales del país donde residen, ciudadanos de otro Estado miembro de la UE, y ciudadanos de un país no comunitario. Eurostat publica una serie paralela por país de nacimiento (lfsa_eoqgac) cuyos valores no son intercambiables con estos.

Franja de edad: Y20-64 (de 20 a 64 años).

## Límites declarados
1. La franja de edad es una elección declarada, no un dato neutro. El conjunto ofrece siete (Y20-64 entre ellas) y cada una da cifras distintas: en 2024, los ciudadanos de fuera de la UE aparecen al 39,8 % en Y20-64 y al 33,0 % en 25-34 años. Comparar cifras de franjas distintas no tiene sentido.

2. Los valores de la serie se revisan. Las cifras de 2024 que esta pieza publicó por primera vez en julio de 2025 (39,6 % y 30,3 %) ya no son las que devuelve el API (39,8 % y 30,2 %). Por eso la pieza se reconstruye desde la fuente en cada ejecución y no conserva cifras transcritas.

3. El ranking por país incluye solo los 27 Estados miembros. El conjunto también devuelve países de la AELC y candidatos —Islandia aparece con una tasa alta—, que quedan fuera porque el ranking se presenta como europeo comunitario.

4. No todos los países tienen dato cada año. Los que faltan se listan en limpio.json como sin_dato; no se estiman ni se rellenan con el año anterior.

5. Es una encuesta por muestreo, no un censo. En países pequeños o con pocas personas migrantes con título universitario, la muestra es reducida y el valor puede saltar de un año a otro sin que cambie la realidad. Eurostat marca esos casos con banderas de fiabilidad que esta consulta no recoge todavía.

6. La tasa mide desajuste entre título y ocupación. No mide reconocimiento de títulos, ni discriminación, ni idioma: son causas posibles que el indicador no separa.
