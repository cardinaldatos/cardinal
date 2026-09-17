# Método — desplazamiento-venezolano

**Fuente:** ACNUR — UNHCR Refugee Data Finder, API v1, conjunto de población de fin de año por país de origen y de acogida.
**Consulta:** `https://api.unhcr.org/population/v1/population/?coo=VEN&coa_all=true&yearFrom=2018`
**Fecha de extracción:** 2026-09-17

## Definición
Personas venezolanas contabilizadas por ACNUR fuera de Venezuela, repartidas entre los tipos de población que la propia fuente distingue. Los nombres de las categorías son los que ACNUR usa en sus publicaciones en español; no son traducciones propias.

La serie arranca en 2018 porque es el año desde el que ACNUR aplicó retroactivamente la categoría «otras personas que necesitan protección internacional», y también el primer año en que ese tipo existe en su matriz de disponibilidad.

Según la nota al pie de la propia fuente, la columna de personas refugiadas incluye a las personas en situación similar a la de refugiado.

Último año con dato: 2025. No se toma del catálogo de años del API, que llega más lejos que el dato.

## Límites declarados
1. Los números son aproximaciones por decisión de la fuente. ACNUR redondea los valores menores que cinco al múltiplo de cinco más cercano antes de publicar, por confidencialidad, y declara que los totales deben considerarse aproximados. La consecuencia práctica: un cero publicado significa entre cero y dos personas. En 2025 hay 65 celdas en ese caso, y limpio.json las marca como cero_redactado.

2. No todos los ceros dicen lo mismo. Las columnas que valen cero para todos los destinos del año no están midiendo nada: son relleno del esquema, porque el concepto no aplica a un desglose por país de acogida. En 2025 son: Comunidad de acogida, Personas desplazadas internas, Personas apátridas. Se marcan como cero_de_esquema y no se dibujan.

3. El denominador incluye solo tipos de población, no soluciones. La misma respuesta trae columnas de personas retornadas, que son flujos anuales y no existencias; sumarlas al total mezclaría dos cosas distintas. Se conservan en limpio.json y quedan fuera del porcentaje.

4. La ausencia de un país no es interpretable. De los 229 países del catálogo de ACNUR, 55 aparecen como destino. Se comprobó pidiendo pares origen-destino ausentes uno por uno: el API no devuelve fila, así que no distingue «no se midió» de «no había nadie». Por eso los que faltan no se publican como países sin dato.

5. La lista de destinos cambia de un año a otro. En el periodo cubierto hubo 30 entradas y 20 salidas de la lista. Un país que aparece o desaparece no es gente que llegó o se fue: es un país que ese año reportó o dejó de reportar.

6. La serie fue reclasificada dos veces y reescrita hacia atrás. Las personas venezolanas contadas hoy como «otras personas que necesitan protección internacional» estaban antes bajo «venezolanos desplazados en el exterior», tipo introducido en junio de 2020, y antes de eso dentro de «otras personas de interés». En octubre de 2022 ACNUR absorbió el tipo intermedio en el actual, retroactivamente desde 2018, y declaró que el término anterior dejaría de usarse. Cualquier cifra publicada por terceros antes de esa fecha se refiere a una clasificación que ya no existe y no es comparable con esta.

7. Omitir el país de acogida en la consulta no da error: el API agrega la dimensión y devuelve el total en una sola fila, con el destino escrito como un guion. Esta consulta pide el desglose explícitamente y descarta las filas agregadas que aun así lleguen; limpio.json registra cuántas fueron.
