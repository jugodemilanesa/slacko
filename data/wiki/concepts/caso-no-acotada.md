---
name: caso-no-acotada
title: Solución no acotada
category: casos-particulares
aliases:
- solucion no acotada
- no acotada
- no acotado
- espacio no acotado
- region no acotada
- unbounded
related:
- region-factible
- solucion-optima
- caso-no-factible
- caso-optimos-alternativos
sources: []
updated: '2026-05-21'
summary: El espacio de soluciones no está acotado en la dirección de mejora, por lo que la función objetivo puede crecer (o decrecer) indefinidamente.
---

# Solución no acotada

Una **solución no acotada** aparece cuando el **espacio de soluciones factibles no está acotado** en la dirección de mejora de la función objetivo.

En ese caso, una de las variables puede crecer **sin romper ninguna restricción**, y la función objetivo puede aumentar (o disminuir) **indefinidamente** sin alcanzar nunca un máximo (o mínimo) finito.

**En la práctica** este caso suele indicar que **al modelo le falta una restricción**: en la realidad ningún recurso es infinito, así que cuando un solver devuelve "no acotada" conviene revisar si se omitió alguna limitación del problema.
