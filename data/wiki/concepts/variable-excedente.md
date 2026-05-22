---
name: variable-excedente
title: Variable de excedente (surplus)
category: variables-auxiliares
aliases:
- variable de excedente
- variables de excedente
- que es una variable de excedente
- surplus
- variable surplus
- excedente
related:
- forma-estandar
- conversion-canonica-estandar
- variable-holgura
- variable-artificial
sources: []
updated: '2026-05-21'
summary: Variable no negativa que se resta a una restricción ≥ para convertirla en igualdad. Representa cuánto se supera el mínimo exigido.
---

# Variable de excedente (surplus)

Una **variable de excedente** (en inglés *surplus*) es una **variable auxiliar no negativa** que se **resta** al lado izquierdo de una restricción de tipo **≥** para convertirla en una **igualdad**.

Representa **cuánto se sobrepasa el mínimo exigido** por la restricción.

**Ejemplo.** Si una dieta exige al menos 12 unidades de un nutriente:

    3x₁ + x₂ ≥ 12

restamos e₁ ≥ 0 y queda:

    3x₁ + x₂ − e₁ = 12

Si e₁ = 0 en la solución óptima, se cumple exactamente el mínimo. Si e₁ > 0, se está consumiendo más de lo estrictamente necesario.

*Nota:* a diferencia de la holgura, la excedente **no alcanza** para iniciar el Simplex desde el origen; en general hay que acompañarla con una **variable artificial**.
