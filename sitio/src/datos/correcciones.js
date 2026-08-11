/* ==========================================================================
   Cardinal Datos — registro público de correcciones

   Este archivo es el único origen de verdad sobre QUÉ se ha corregido.
   Lo lee src/pages/correcciones.astro, que cuenta el registro: la página
   no escribe a mano ni una fecha ni un número.

   REGLA: este archivo solo crece. No se edita una entrada para suavizarla
   ni se borra una para que la lista se vea limpia. El historial del
   repositorio deja rastro de cualquier cambio, así que reescribir aquí no
   esconde nada: solo cuesta credibilidad.

   CÓMO SE CORRIGE UNA CIFRA
   Casi ninguna cifra publicada está escrita en el HTML: sale de
   data/<slug>/limpio.json, que produce un script del pipeline. Corregir
   una cifra significa arreglar el script y volver a correrlo, no editar
   la página. Si el error estaba en el texto que rodea al dato, entonces
   sí se edita la pieza. Anota en `por_que` cuál de los dos casos fue.

   CAMPOS
     fecha    día en que se publicó la corrección, AAAA-MM-DD. Es la
              fecha de la corrección, no la del error.
     pieza    slug de la pieza afectada, tal como aparece en piezas.js.
              null si el error estaba en una página que no es una pieza.
     nivel    una de las claves de NIVELES (abajo).
     decia    lo que la pieza afirmaba antes, en una frase.
     dice     lo que afirma ahora, en una frase.
     por_que  de dónde salió el error y qué se cambió para arreglarlo.
              Es el campo que más vale: explica el fallo, no lo excusa.
     aviso    quién avisó, si pidió aparecer. Por defecto va null: no se
              publica el nombre de nadie sin que lo haya pedido.

   EJEMPLO (no borrar: es la plantilla para la primera entrada real)

     {
       fecha: "2026-09-14",
       pieza: "remesas-costo-latam",
       nivel: "correccion",
       decia: "Enviar 200 dólares a Perú costaba 3,57 dólares.",
       dice: "Enviar 200 dólares a Perú cuesta 7,14 dólares.",
       por_que:
         "El script confundía el porcentaje con el monto en dólares y no " +
         "multiplicaba por el monto de referencia. Se arregló en " +
         "pipeline/remesas.py y se volvió a generar limpio.json; la página " +
         "no se tocó.",
       aviso: null,
     },
   ========================================================================== */

export const CORRECCIONES = [
  {
    fecha: "2026-08-11",
    pieza: null,
    nivel: "incidencia",
    decia:
      "El sitio no respondía: cardinaldatos.org no resolvía a ninguna dirección.",
    dice:
      "Responde con normalidad. Ningún dato, cifra ni texto cambió.",
    por_que:
      "El sitio lo sirve un Worker de Cloudflare, y el dominio se le " +
      "asigna aparte, en el panel. El Worker se llamaba «www», y ese " +
      "nombre se confundió con el dominio: no tiene relación con él, solo " +
      "decide el subdominio de pruebas. Al intentar corregirlo cambiándole " +
      "el nombre, Cloudflare no movió el Worker existente sino que creó " +
      "uno nuevo, y quedaron dos. Al borrar el sobrante se fue con él el " +
      "registro DNS del dominio, que un dominio asignado a un Worker crea " +
      "y elimina junto con ese Worker. Sin registro DNS el nombre deja de " +
      "existir para internet: no es que el sitio devolviera un error, es " +
      "que no había a dónde llamar. Se volvió a desplegar y a asignar el " +
      "dominio. Los registros de correo quedaron intactos, así que los " +
      "avisos enviados a correcciones@ durante la caída sí llegaron. " +
      "Queda anotado en sitio/wrangler.jsonc qué decide y qué no decide " +
      "el nombre de un Worker, que es el malentendido de origen.",
    aviso: null,
  },
  {
    fecha: "2026-08-10",
    pieza: "titulo-no-cruza",
    nivel: "actualizacion",
    decia:
      "La tasa de sobrecualificación de 2024 era 39,6 % para los ciudadanos de fuera de la UE y 30,3 % para los de otro país de la UE.",
    dice:
      "Es 39,8 % y 30,2 %, que son los valores vigentes de Eurostat.",
    por_que:
      "Eurostat revisó sus cifras de 2024 después de que las copiáramos. " +
      "La pieza las llevaba escritas a mano dentro del componente desde " +
      "julio de 2025: eran correctas el día que se copiaron y falsas un " +
      "año después, sin que nada avisara. Los valores de 2014 no cambiaron. " +
      "El arreglo de fondo no fue reescribir los números sino quitarlos: " +
      "pipeline/sobrecualificacion.py descarga la serie y la pieza la lee " +
      "de data/sobrecualificacion-ue/limpio.json en cada compilación, así " +
      "que la próxima revisión de la fuente entra sola. Esta pieza era la " +
      "única que quedaba fuera de la regla de oro.",
    aviso: null,
  },
  {
    fecha: "2026-08-10",
    pieza: null,
    nivel: "correccion",
    decia:
      "La página de método decía publicar el archivo de método de cada pieza, tal como lo escribe el pipeline.",
    dice:
      "Los publica. Antes no aparecía ninguno: la página solo mostraba el procedimiento general y el registro de fuentes.",
    por_que:
      "El código de sitio/src/pages/metodo.astro sí leía cada " +
      "data/<slug>/metodo.md y lo convertía a HTML en cada compilación, " +
      "pero la plantilla nunca dibujaba ese resultado: faltaba el bloque " +
      "que recorre las fichas. El trabajo se hacía y se descartaba. Se " +
      "añadió el bloque. Ningún dato cambió — lo que faltaba era " +
      "publicarlo, que es justo lo que esa página existe para hacer.",
    aviso: null,
  },
  {
    fecha: "2026-08-10",
    pieza: null,
    nivel: "correccion",
    decia:
      "El registro contaba tres fuentes sosteniendo piezas publicadas.",
    dice:
      "Cuenta dos: el Banco Mundial y Eurostat.",
    por_que:
      "SSB, la oficina estadística de Noruega, estaba marcada «en uso», " +
      "estado que el propio registro define como sostener al menos una " +
      "pieza publicada. Ninguna se apoya en ella todavía. Se reclasificó " +
      "como «sondeada» en data/fuentes.json. La página no se tocó: cuenta " +
      "el registro, así que la cifra se corrigió sola.",
    aviso: null,
  },
];

/* Los tres tipos de cambio que se registran. La página los publica desde
   aquí: si mañana se añade un cuarto, aparece solo. */
export const NIVELES = {
  correccion: {
    etiqueta: "Corrección",
    descripcion:
      "Una cifra o un hecho estaban equivocados. Cambia lo que la pieza afirma.",
  },
  aclaracion: {
    etiqueta: "Aclaración",
    descripcion:
      "El dato era correcto, pero estaba explicado de forma confusa o incompleta. La cifra no cambia.",
  },
  incidencia: {
    etiqueta: "Interrupción",
    descripcion:
      "El sitio dejó de estar disponible. Ningún dato cambia: lo que falló fue el acceso, y queda registrado porque un lector que no pudo leer una pieza merece saber por qué.",
  },
  actualizacion: {
    etiqueta: "Actualización de la fuente",
    descripcion:
      "El organismo revisó su propio dato. La pieza se rehízo con la versión nueva y aquí queda constancia de cuál era la anterior.",
  },
};

/** Las correcciones ordenadas de más reciente a más antigua. */
export function correccionesPorFecha() {
  return [...CORRECCIONES].sort((a, b) => b.fecha.localeCompare(a.fecha));
}
