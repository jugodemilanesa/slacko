# Index del wiki

_Autogenerado — no editar a mano. Regenerar con `python -m scripts.migrate_kb_to_wiki` o el lint del wiki._

## Fundamentos

_¿Qué es la Programación Lineal y por qué se llama así?_

- [Programación Lineal](concepts/programacion-lineal.md) — Técnica matemática de optimización para asignar recursos limitados entre actividades que compiten por ellos.
- [¿Por qué se llama "lineal"?](concepts/por-que-lineal.md) — Porque tanto la función objetivo como las restricciones son funciones lineales de las variables de decisión.
- [¿Por qué se llama "programación"?](concepts/por-que-programacion.md) — Porque se refiere a la planificación de un programa de acción, no a la codificación en computadoras.
- [Modelo de Programación Lineal](concepts/modelo-pl.md) — Representación matemática de un problema de optimización donde tanto la función objetivo como las restricciones son lineales.

## Supuestos del modelo

_Las hipótesis que tiene que cumplir un problema para modelarse como PL._

- [Supuestos del modelo de PL](concepts/supuestos-pl.md) — Son 6: proporcionalidad, aditividad, divisibilidad, certidumbre, objetivo único y no negatividad.
- [Proporcionalidad](concepts/proporcionalidad.md) — La contribución de cada variable a la función objetivo y a cada restricción es proporcional a su valor.
- [Aditividad](concepts/aditividad.md) — La contribución total es la suma de las contribuciones individuales; no hay interacciones entre variables.
- [Divisibilidad](concepts/divisibilidad.md) — Las variables pueden tomar cualquier valor real no negativo, incluidos los fraccionarios.
- [Certidumbre](concepts/certidumbre.md) — Todos los parámetros (coeficientes objetivo, tecnológicos y términos independientes) son conocidos con exactitud.

## Componentes básicos

_Las piezas que conforman cualquier modelo de PL._

- [Componentes básicos de un modelo de PL](concepts/componentes-pl.md) — Variables de decisión, función objetivo, restricciones y condiciones de no negatividad.
- [Variables de decisión](concepts/variables-decision.md) — Lo que el modelo busca determinar: las cantidades sobre las que se decide. Se notan x₁, x₂, …, xₙ.
- [Función objetivo](concepts/funcion-objetivo.md) — Expresión lineal Z = c₁x₁ + c₂x₂ + … + cₙxₙ que se busca maximizar o minimizar.
- [Restricciones](concepts/restricciones.md) — Limitaciones del problema expresadas como inecuaciones o ecuaciones lineales sobre las variables.
- [Coeficientes tecnológicos (aᵢⱼ)](concepts/coeficientes-tecnologicos.md) — Cantidad de recurso i consumida por cada unidad de la actividad j.
- [Términos independientes (bᵢ)](concepts/terminos-independientes.md) — Cantidad disponible (o requerida) de cada recurso i; aparecen en el lado derecho de las restricciones.
- [Condición de no negatividad](concepts/no-negatividad.md) — Todas las variables de decisión deben tomar valores mayores o iguales a cero: xⱼ ≥ 0 para todo j.

## Geometría de la PL

_Región factible, vértices y solución óptima._

- [Región factible](concepts/region-factible.md) — Conjunto de todos los puntos que satisfacen simultáneamente todas las restricciones y la no negatividad.
- [Solución óptima](concepts/solucion-optima.md) — Punto de la región factible donde la función objetivo alcanza su valor máximo (o mínimo). Si existe y es finito, está en un vértice.
- [Punto extremo (vértice)](concepts/punto-extremo.md) — Punto de un conjunto convexo que no puede expresarse como combinación convexa de otros dos puntos distintos del conjunto.
- [Teorema Fundamental de la PL](concepts/teorema-fundamental.md) — Si existe solución óptima finita, se encuentra en al menos un vértice de la región factible.

## Formas de representación

_Forma canónica, forma estándar y conversión entre ambas._

- [Forma canónica](concepts/forma-canonica.md) — Maximización con todas las restricciones ≤, o minimización con todas ≥; bᵢ ≥ 0 y variables no negativas.
- [Forma estándar](concepts/forma-estandar.md) — Todas las restricciones son ecuaciones, todas las variables son no negativas y todos los bᵢ son no negativos.
- [Conversión de canónica a estándar](concepts/conversion-canonica-estandar.md) — Se introducen variables de holgura en restricciones ≤ y de excedente en ≥ para transformar inecuaciones en igualdades.

## Variables auxiliares

_Holgura, excedente y artificial._

- [Variable de holgura (slack)](concepts/variable-holgura.md) — Variable no negativa que se suma a una restricción ≤ para convertirla en igualdad. Representa el recurso no utilizado.
- [Variable de excedente (surplus)](concepts/variable-excedente.md) — Variable no negativa que se resta a una restricción ≥ para convertirla en igualdad. Representa cuánto se supera el mínimo exigido.
- [Variable artificial](concepts/variable-artificial.md) — Variable auxiliar no negativa agregada a restricciones ≥ o = para tener un punto inicial factible en el Simplex. Se penaliza fuertemente en la función objetivo.

## Método gráfico

_Resolución geométrica de problemas de PL con dos variables._

- [Elementos del método gráfico](concepts/metodo-grafico-elementos.md) — Restricciones (semiespacios), región factible (intersección), función objetivo (familia de rectas paralelas) y Teorema Fundamental.
- [Pasos del método gráfico](concepts/metodo-grafico-pasos.md) — Plantear, graficar restricciones, determinar región factible, trazar la objetivo, encontrar el vértice óptimo y calcularlo algebraicamente.

## Casos particulares

_Situaciones especiales que pueden aparecer en un modelo de PL._

- [Degeneración](concepts/caso-degeneracion.md) — Una restricción redundante genera empate en la relación mínima y al menos una variable básica vale cero en la siguiente iteración del Simplex.
- [Óptimos alternativos](concepts/caso-optimos-alternativos.md) — Hay infinitas soluciones óptimas cuando la función objetivo es paralela a una restricción activa no redundante.
- [Solución no acotada](concepts/caso-no-acotada.md) — El espacio de soluciones no está acotado en la dirección de mejora, por lo que la función objetivo puede crecer (o decrecer) indefinidamente.
- [Solución no factible](concepts/caso-no-factible.md) — Las restricciones son incompatibles entre sí: no existe ningún punto que las satisfaga simultáneamente.
