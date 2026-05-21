---
name: variable-artificial
title: Variable artificial
category: variables-auxiliares
aliases:
- variable artificial
- variables artificiales
- que es una variable artificial
- artificial
- metodo de la gran m
- gran m
- metodo de dos fases
related:
- forma-estandar
- conversion-canonica-estandar
- variable-holgura
- variable-excedente
- caso-no-factible
sources: []
updated: '2026-05-21'
summary: Variable auxiliar no negativa agregada a restricciones ≥ o = para tener un punto inicial factible en el Simplex. Se penaliza fuertemente en la función objetivo.
---

# Variable artificial

Una **variable artificial** es una **variable auxiliar no negativa** que se agrega a las restricciones de tipo **≥** o **=** cuando se necesita un **punto inicial factible** para arrancar el método Simplex.

A diferencia de la holgura y la excedente, **no tiene interpretación física**: existe solamente para que el algoritmo tenga por dónde empezar. Por eso se la **penaliza fuertemente** en la función objetivo (método de la **Gran M** o método de **Dos Fases**) para forzar al Simplex a expulsarla de la base.

**Diagnóstico clave:** si en la solución óptima alguna variable artificial **permanece con valor positivo**, se concluye que el problema **no tiene solución factible**: las restricciones originales son incompatibles entre sí.
