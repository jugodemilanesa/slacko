---
name: conversion-canonica-estandar
title: Conversión de canónica a estándar
category: formas
aliases:
- conversion canonica a estandar
- como convertir canonica a estandar
- pasar de canonica a estandar
- convertir forma canonica
- como pasar a forma estandar
related:
- forma-canonica
- forma-estandar
- variable-holgura
- variable-excedente
- variable-artificial
sources: []
updated: '2026-05-21'
summary: Se introducen variables de holgura en restricciones ≤ y de excedente en ≥ para transformar inecuaciones en igualdades.
---

# Conversión de canónica a estándar

Para convertir un modelo de **forma canónica a forma estándar** hay que transformar cada inecuación en una igualdad agregando una variable auxiliar.

**Restricción ≤** — se le suma una **variable de holgura (slack)** que absorbe la diferencia entre el recurso usado y el disponible:

    6x₁ + 4x₂ ≤ 24    →    6x₁ + 4x₂ + s₁ = 24,    s₁ ≥ 0

**Restricción ≥** — se le resta una **variable de excedente (surplus)** que representa cuánto se sobrepasa el mínimo exigido:

    3x₁ + x₂ ≥ 12    →    3x₁ + x₂ − e₁ = 12,    e₁ ≥ 0

**Restricción =** — queda como está, pero si se necesita un punto inicial factible para el Simplex se agrega una **variable artificial** penalizada en la función objetivo.
