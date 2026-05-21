---
name: caso-degeneracion
title: Degeneración
category: casos-particulares
aliases:
- degeneracion
- solucion degenerada
- caso degenerado
- que es la degeneracion
related:
- caso-optimos-alternativos
- caso-no-acotada
- caso-no-factible
sources: []
updated: '2026-05-21'
summary: Una restricción redundante genera empate en la relación mínima y al menos una variable básica vale cero en la siguiente iteración del Simplex.
---

# Degeneración

La **degeneración** ocurre cuando hay al menos **una restricción redundante** en el modelo, lo que produce un **empate en la relación mínima** durante el método Simplex.

Como consecuencia, **al menos una variable básica toma el valor cero** en la siguiente iteración, y se dice que la solución es **degenerada**.

Geométricamente, la degeneración aparece cuando **más de dos restricciones se intersectan en el mismo vértice** de la región factible. El Simplex puede ciclar entre soluciones del mismo valor objetivo, aunque en la práctica se evita con reglas de desempate (regla de Bland).
