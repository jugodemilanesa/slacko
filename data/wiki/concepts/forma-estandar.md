---
name: forma-estandar
title: Forma estándar
category: formas
aliases:
- forma estandar
- que es la forma estandar
- modelo en forma estandar
related:
- forma-canonica
- conversion-canonica-estandar
- variable-holgura
- variable-excedente
- variable-artificial
sources: []
updated: '2026-05-21'
summary: Todas las restricciones son ecuaciones, todas las variables son no negativas y todos los bᵢ son no negativos.
---

# Forma estándar

Un problema de PL está en **forma estándar** cuando se cumplen **todas** estas condiciones:

1. Todas las restricciones son **ecuaciones** (igualdades).
2. Todas las variables son **no negativas** (xⱼ ≥ 0).
3. Los términos independientes son **no negativos** (bᵢ ≥ 0).

La forma estándar es **necesaria para aplicar el método Simplex**, que opera sobre sistemas de ecuaciones lineales.

Para llegar a forma estándar desde la forma canónica se introducen **variables de holgura** (en restricciones ≤), **variables de excedente** (en ≥) y, cuando hace falta, **variables artificiales** para iniciar el procedimiento.
