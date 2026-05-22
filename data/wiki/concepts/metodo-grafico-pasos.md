---
name: metodo-grafico-pasos
title: Pasos del método gráfico
category: metodo-grafico
aliases:
- pasos del metodo grafico
- como resolver con metodo grafico
- resolucion grafica
- metodo grafico pasos
- como se resuelve graficamente
- resolver graficamente
related:
- metodo-grafico-elementos
- region-factible
- punto-extremo
- solucion-optima
sources: []
updated: '2026-05-21'
summary: Plantear, graficar restricciones, determinar región factible, trazar la objetivo, encontrar el vértice óptimo y calcularlo algebraicamente.
---

# Pasos del método gráfico

El método gráfico se aplica a problemas con **dos variables de decisión** y consiste en seis pasos:

**Paso 1 — Plantear el modelo matemático.** Definir variables, función objetivo y restricciones.

**Paso 2 — Graficar las restricciones.** Para cada restricción, igualar a cero cada variable sucesivamente para hallar las intersecciones con los ejes y trazar la recta. El sentido de la desigualdad indica qué semiespacio es factible.

**Paso 3 — Determinar la región factible.** Es la intersección de todos los semiespacios factibles, incluyendo el primer cuadrante (no negatividad). Es un **polígono convexo**.

**Paso 4 — Trazar la función objetivo.** Asignar un valor arbitrario a Z y graficar la recta correspondiente; luego desplazar rectas paralelas en la dirección de mejora.

**Paso 5 — Encontrar la solución visual.** Identificar el **último vértice** de la región factible que toca la recta de Z al desplazarla:

- *hacia afuera* (alejándose del origen) **para maximizar**,
- *hacia adentro* (acercándose al origen) **para minimizar**.

**Paso 6 — Calcular la solución algebraica.** Resolver el sistema de ecuaciones de las **restricciones activas** (las rectas que se intersectan en el vértice óptimo) para obtener las coordenadas exactas.

*Alcance.* En el contexto de Slacko trabajamos siempre con **dos variables**. Con software 3D el método se extiende a tres, pero a mano es inviable.
