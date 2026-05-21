---
name: restricciones
title: Restricciones
category: componentes
aliases:
- restricciones
- que son las restricciones
- restriccion
- limitaciones
- inecuaciones
- sistema de restricciones
related:
- componentes-pl
- coeficientes-tecnologicos
- terminos-independientes
- no-negatividad
sources: []
updated: '2026-05-21'
summary: Limitaciones del problema expresadas como inecuaciones o ecuaciones lineales sobre las variables.
---

# Restricciones

Las **restricciones** representan las **limitaciones operativas** del problema: tiempo disponible, dinero, demandas, capacidades, recursos físicos. Pueden ser **físicas** (capacidad de una máquina) o **de contexto** (demanda mínima, mezcla regulada).

Se formulan como un **sistema de inecuaciones o igualdades** lineales en las variables de decisión:

    Σⱼ aᵢⱼ · xⱼ  ≤  (o ≥ o =)  bᵢ

donde:

- **aᵢⱼ** son los **coeficientes tecnológicos** (cuánto recurso i consume cada unidad de la actividad j),
- **bᵢ** es el **término independiente** o disponibilidad del recurso i.
