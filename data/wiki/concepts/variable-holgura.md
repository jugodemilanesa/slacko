---
name: variable-holgura
title: Variable de holgura (slack)
category: variables-auxiliares
aliases:
- variable de holgura
- variables de holgura
- que es una variable de holgura
- slack
- variable slack
- holgura
related:
- forma-estandar
- conversion-canonica-estandar
- variable-excedente
- variable-artificial
sources: []
updated: '2026-05-21'
summary: Variable no negativa que se suma a una restricción ≤ para convertirla en igualdad. Representa el recurso no utilizado.
---

# Variable de holgura (slack)

Una **variable de holgura** (en inglés *slack*) es una **variable auxiliar no negativa** que se **suma** al lado izquierdo de una restricción de tipo **≤** para convertirla en una **igualdad**.

Representa la **cantidad de recurso que sobra**, es decir, lo que no se utilizó del lado derecho disponible.

**Ejemplo.** Si tenemos una restricción de capacidad de máquina:

    6x₁ + 4x₂ ≤ 24

agregamos s₁ ≥ 0 y queda:

    6x₁ + 4x₂ + s₁ = 24

Si en la solución óptima s₁ = 0, el recurso se usó al máximo (restricción **activa**). Si s₁ > 0, sobró ese recurso (restricción **no activa**).
