---
name: caso-no-factible
title: Solución no factible
category: casos-particulares
aliases:
- solucion no factible
- no factible
- sin solucion
- sin solucion factible
- soluciones no existentes
- infactible
- infeasible
- restricciones incompatibles
related:
- variable-artificial
- region-factible
- caso-no-acotada
- caso-degeneracion
sources: []
updated: '2026-05-21'
summary: 'Las restricciones son incompatibles entre sí: no existe ningún punto que las satisfaga simultáneamente.'
---

# Solución no factible

Un modelo de PL **no tiene solución factible** cuando sus **restricciones son incompatibles entre sí**: no existe ningún conjunto de valores de las variables que satisfaga todas las restricciones a la vez. Geométricamente, **la región factible es vacía**.

Esta situación **no ocurre** si todas las restricciones son de tipo **≤** con bᵢ ≥ 0, porque en ese caso las variables de holgura proveen una solución factible obvia (el origen).

Cuando hay restricciones de tipo ≥ o =, hace falta incorporar **variables artificiales penalizadas** para iniciar la resolución. **Si en la solución óptima alguna variable artificial permanece con valor positivo**, se concluye que el problema **no tiene solución factible**.

**Diagnóstico habitual.** Sumas de demandas mínimas mayores a la disponibilidad total, presupuestos insuficientes para cumplir cuotas exigidas, cotas inferiores y superiores que se cruzan.
