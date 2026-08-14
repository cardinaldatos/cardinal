/* ==========================================================================
   Cardinal Datos — catálogo de notas publicadas

   Una NOTA no es una PIEZA. La distinción no es de longitud:

     Una pieza publica datos. Tiene su carpeta en data/, su script que los
     descarga, su metodo.md generado, y sus cifras salen de limpio.json en
     tiempo de compilación.

     Una nota explica algo que se aprendió haciendo esas piezas: cómo se
     mide un indicador, por qué un organismo revisa sus cifras después de
     publicarlas, qué decisión hubo detrás de una consulta. No trae datos
     nuevos. Es lo que EDITORIAL.md llama publicar el pipeline como
     contenido.

   POR QUÉ LAS NOTAS NO LLEVAN CIFRAS

   La regla de oro no distingue entre piezas y notas: toda cifra publicada
   tiene que rastrearse hasta un archivo generado por un script. Una nota
   es texto escrito a mano, así que cualquier número dentro de ella sería
   una cifra a mano — y envejecería igual que las demás. Peor: las notas
   hablan justo de indicadores que se revisan, así que envejecerían rápido.

   Por eso las notas explican la MECÁNICA y enlazan a la pieza para el
   número. «La franja de edad puede mover el resultado varios puntos» no
   caduca; «39,8 %» sí. Esto incluye los números escritos con letra: «los
   diez países» es una cifra igual que «10», y es la forma en que se cuela
   de verdad.

   Si algún día una nota necesita de verdad una cifra en el cuerpo, la vía
   no es escribirla aquí: es que su página lea limpio.json, como ya hacen
   las piezas y la página de método.

   PARA AÑADIR UNA NOTA: añade un objeto aquí y crea su página en
   src/pages/notas/<slug>.astro. El listado y el feed la recogen solos.

   CAMPOS
   slug        carpeta de la URL: /notas/<slug>/. Tiene que existir un
               src/pages/notas/<slug>.astro con ese nombre.
   titulo      el titular de la nota.
   resumen     una o dos frases. Se ve en el listado y en el feed.
   publicado   fecha real de publicación, AAAA-MM-DD. La usa el RSS para
               ordenar y para pubDate. Si te la inventas, los lectores de
               feeds muestran fechas falsas.
   pieza       slug de la pieza de la que salió esta nota, o null si no
               viene de ninguna. Sirve para enlazarlas entre sí; el
               listado comprueba contra piezas.js que el slug exista.
   ========================================================================== */

export const NOTAS = [
  {
    slug: "misma-estadistica-dos-cifras",
    titulo: "La misma estadística, dos cifras distintas",
    resumen:
      "Un titular sobre migrantes sobrecualificados puede dar cifras muy distintas sin que nadie mienta. Depende de una casilla que casi nunca se menciona: la franja de edad.",
    publicado: "2026-08-14",
    pieza: "titulo-no-cruza",
  },
];

/** Las notas ordenadas de más reciente a más antigua. */
export function notasPorFecha() {
  return [...NOTAS].sort((a, b) => b.publicado.localeCompare(a.publicado));
}
