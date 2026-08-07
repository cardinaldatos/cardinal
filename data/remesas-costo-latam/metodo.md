# Método — remesas-costo-latam

**Fuente:** Banco Mundial, World Development Indicators, serie SI.RMT.COST.IB.ZS (costo promedio de enviar remesas hacia un país). Los datos de origen provienen de Remittance Prices Worldwide.
**Consulta:** `https://api.worldbank.org/v2/country/<ISO3>/indicator/SI.RMT.COST.IB.ZS?format=json&mrv=5`
**Fecha de extracción:** 2026-08-07

## Definición
Costo total de transacción de enviar 200 USD hacia el país, como porcentaje del monto enviado, promediado entre todos los proveedores de servicios de remesas incluidos en la base Remittance Prices Worldwide para ese destino.

La cifra en dólares de esta pieza devuelve ese porcentaje al monto sobre el que el indicador está definido: no es una extrapolación. Tampoco es la tarifa de ningún proveedor concreto — es el promedio del mercado rastreado.

## Límites declarados
1. Los valores latinoamericanos (2–3,5 %) quedan muy por debajo del promedio global del RPW (6,36 %). No es una discrepancia de método: ambos miden lo mismo, y América Latina es la región más barata del mundo para recibir remesas. Pendiente menor: contrastar contra el promedio regional del informe, no contra el global.

2. Frecuencia anual, no trimestral. El metadato del catálogo declara actualizaciones recientes, pero el último año con dato es 2023: refrescan el catálogo sin añadir años. Verificar en cada ejecución.

3. Es un promedio entre los corredores rastreados hacia cada país. En países con pocos corredores el promedio salta fuerte de un año a otro sin que cambie el mercado real. No usar la serie temporal de un país como si fuera una tendencia.

4. Venezuela no tiene indicador en esta serie. Argentina y Chile aparecen con valor nulo. Su ausencia se registra en limpio.json.

5. No hay desglose entre comisión y margen de tipo de cambio, ni por país emisor, ni por tipo de proveedor. Ese detalle solo existe en el Excel trimestral de Remittance Prices Worldwide.
