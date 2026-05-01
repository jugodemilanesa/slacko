"""Curated theoretical concepts of Linear Programming for the deterministic tutor.

Each entry maps a single concept to its canonical answer in Spanish, plus a list of
aliases used by :mod:`apps.theory.matcher` to score user questions against concepts.

This is the deterministic source of truth: there is no LLM call here. The same data
is exposed by the REST API and serves as the seed for the future RAG pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Category:
    """A grouping of concepts by topic."""

    id: str
    title: str
    description: str


@dataclass(frozen=True)
class Concept:
    """A single theoretical concept with its canonical answer."""

    id: str
    title: str
    category: str
    aliases: tuple[str, ...]
    summary: str
    content: str
    related: tuple[str, ...] = field(default_factory=tuple)


CATEGORIES: tuple[Category, ...] = (
    Category(
        id="fundamentos",
        title="Fundamentos",
        description="¿Qué es la Programación Lineal y por qué se llama así?",
    ),
    Category(
        id="supuestos",
        title="Supuestos del modelo",
        description="Las hipótesis que tiene que cumplir un problema para modelarse como PL.",
    ),
    Category(
        id="componentes",
        title="Componentes básicos",
        description="Las piezas que conforman cualquier modelo de PL.",
    ),
    Category(
        id="geometria",
        title="Geometría de la PL",
        description="Región factible, vértices y solución óptima.",
    ),
    Category(
        id="formas",
        title="Formas de representación",
        description="Forma canónica, forma estándar y conversión entre ambas.",
    ),
    Category(
        id="variables-auxiliares",
        title="Variables auxiliares",
        description="Holgura, excedente y artificial.",
    ),
    Category(
        id="metodo-grafico",
        title="Método gráfico",
        description="Resolución geométrica de problemas de PL con dos variables.",
    ),
    Category(
        id="casos-particulares",
        title="Casos particulares",
        description="Situaciones especiales que pueden aparecer en un modelo de PL.",
    ),
)


CONCEPTS: tuple[Concept, ...] = (
    # ─── Fundamentos ──────────────────────────────────────────────────────
    Concept(
        id="programacion-lineal",
        title="Programación Lineal",
        category="fundamentos",
        aliases=(
            "programacion lineal",
            "que es la programacion lineal",
            "que es pl",
            "definicion de programacion lineal",
            "definicion de pl",
            "pl",
            "linear programming",
        ),
        summary=(
            "Técnica matemática de optimización para asignar recursos limitados "
            "entre actividades que compiten por ellos."
        ),
        content=(
            "La **Programación Lineal (PL)** es una técnica matemática y "
            "algorítmica de optimización. Su objetivo principal es asignar de "
            "manera eficiente **recursos limitados** (tiempo, dinero, "
            "materiales, mano de obra, ancho de banda, etc.) entre "
            "**actividades que compiten** por ellos.\n\n"
            "El resultado busca siempre **maximizar un beneficio** (utilidad, "
            "producción, rendimiento) o **minimizar un costo** (gasto, "
            "tiempo, desperdicio), sujeto a un conjunto de restricciones "
            "que reflejan las limitaciones del problema real."
        ),
        related=(
            "por-que-lineal",
            "por-que-programacion",
            "modelo-pl",
            "componentes-pl",
        ),
    ),
    Concept(
        id="por-que-lineal",
        title="¿Por qué se llama \"lineal\"?",
        category="fundamentos",
        aliases=(
            "por que lineal",
            "por que se llama lineal",
            "que significa lineal",
            "lineal en programacion lineal",
        ),
        summary=(
            "Porque tanto la función objetivo como las restricciones son "
            "funciones lineales de las variables de decisión."
        ),
        content=(
            "El término **\"lineal\"** indica que **todas las funciones "
            "matemáticas del modelo** —tanto la función a optimizar como "
            "las restricciones— deben ser **funciones lineales** de las "
            "variables de decisión.\n\n"
            "En la práctica, una función es lineal si las variables aparecen "
            "elevadas a la primera potencia y multiplicadas por constantes, "
            "sumadas entre sí. No se admiten productos entre variables, "
            "potencias, raíces, logaritmos, ni funciones trigonométricas."
        ),
        related=("programacion-lineal", "por-que-programacion", "supuestos-pl"),
    ),
    Concept(
        id="por-que-programacion",
        title="¿Por qué se llama \"programación\"?",
        category="fundamentos",
        aliases=(
            "por que programacion",
            "por que se llama programacion",
            "que significa programacion",
            "programacion en programacion lineal",
        ),
        summary=(
            "Porque se refiere a la planificación de un programa de acción, "
            "no a la codificación en computadoras."
        ),
        content=(
            "El término **\"programación\"** **no se refiere** a la "
            "codificación en computadoras, sino a la **planificación o "
            "formulación de un programa de acción**.\n\n"
            "Es decir, se trata de **diseñar un plan** que indique, por "
            "ejemplo, cuántas unidades de cada producto fabricar, cuánto "
            "invertir en cada actividad, o cómo distribuir un recurso "
            "escaso entre varias alternativas."
        ),
        related=("programacion-lineal", "por-que-lineal"),
    ),
    Concept(
        id="modelo-pl",
        title="Modelo de Programación Lineal",
        category="fundamentos",
        aliases=(
            "modelo de programacion lineal",
            "modelo de pl",
            "que es un modelo de pl",
            "que es un modelo de programacion lineal",
            "modelo matematico pl",
        ),
        summary=(
            "Representación matemática de un problema de optimización donde "
            "tanto la función objetivo como las restricciones son lineales."
        ),
        content=(
            "Un **modelo de Programación Lineal** es la **representación "
            "matemática** de un problema de optimización en el que **tanto "
            "la función objetivo como las restricciones son lineales**.\n\n"
            "Un modelo de PL queda completamente especificado cuando se "
            "definen:\n\n"
            "1. Las **variables de decisión** (qué se quiere determinar).\n"
            "2. La **función objetivo** (qué se quiere maximizar o minimizar).\n"
            "3. El sistema de **restricciones** (qué limitaciones existen).\n"
            "4. Las **condiciones de no negatividad** sobre las variables."
        ),
        related=(
            "programacion-lineal",
            "componentes-pl",
            "variables-decision",
            "funcion-objetivo",
            "restricciones",
        ),
    ),
    # ─── Supuestos ────────────────────────────────────────────────────────
    Concept(
        id="supuestos-pl",
        title="Supuestos del modelo de PL",
        category="supuestos",
        aliases=(
            "supuestos",
            "supuestos del modelo",
            "supuestos de pl",
            "hipotesis del modelo",
            "hipotesis de pl",
            "axiomas pl",
            "cuales son los supuestos",
        ),
        summary=(
            "Son 6: proporcionalidad, aditividad, divisibilidad, certidumbre, "
            "objetivo único y no negatividad."
        ),
        content=(
            "Para que un problema pueda modelarse como Programación Lineal "
            "deben cumplirse **seis supuestos**:\n\n"
            "1. **Proporcionalidad** — La contribución de cada variable a la "
            "función objetivo y a cada restricción es proporcional a su valor.\n"
            "2. **Aditividad** — La contribución total es la suma de las "
            "contribuciones individuales; no hay interacciones entre variables.\n"
            "3. **Divisibilidad** — Las variables pueden tomar cualquier valor "
            "real no negativo (incluidos fraccionarios).\n"
            "4. **Certidumbre** — Todos los parámetros (cⱼ, aᵢⱼ, bᵢ) son "
            "conocidos con certeza.\n"
            "5. **Objetivo único** — Existe una sola función objetivo.\n"
            "6. **No negatividad** — Todas las variables deben ser mayores o "
            "iguales a cero."
        ),
        related=(
            "proporcionalidad",
            "aditividad",
            "divisibilidad",
            "certidumbre",
            "no-negatividad",
        ),
    ),
    Concept(
        id="proporcionalidad",
        title="Proporcionalidad",
        category="supuestos",
        aliases=(
            "proporcionalidad",
            "supuesto de proporcionalidad",
            "que es la proporcionalidad",
        ),
        summary=(
            "La contribución de cada variable a la función objetivo y a cada "
            "restricción es proporcional a su valor."
        ),
        content=(
            "El supuesto de **proporcionalidad** establece que la "
            "contribución de cada variable de decisión —tanto a la función "
            "objetivo como a cada restricción— es **directamente proporcional "
            "a su valor**.\n\n"
            "Si producir una unidad de un producto genera $5 de utilidad, "
            "producir 10 unidades genera exactamente $50; no hay descuentos "
            "por volumen, economías de escala ni rendimientos decrecientes."
        ),
        related=("supuestos-pl", "aditividad"),
    ),
    Concept(
        id="aditividad",
        title="Aditividad",
        category="supuestos",
        aliases=(
            "aditividad",
            "supuesto de aditividad",
            "que es la aditividad",
        ),
        summary=(
            "La contribución total es la suma de las contribuciones "
            "individuales; no hay interacciones entre variables."
        ),
        content=(
            "El supuesto de **aditividad** establece que la contribución "
            "total a la función objetivo (o a cualquier restricción) es la "
            "**suma de las contribuciones individuales** de cada variable.\n\n"
            "**No hay interacciones entre variables**: el efecto conjunto de "
            "producir x₁ y x₂ es exactamente la suma de los efectos por "
            "separado, sin sinergias ni interferencias."
        ),
        related=("supuestos-pl", "proporcionalidad"),
    ),
    Concept(
        id="divisibilidad",
        title="Divisibilidad",
        category="supuestos",
        aliases=(
            "divisibilidad",
            "supuesto de divisibilidad",
            "que es la divisibilidad",
            "variables continuas",
        ),
        summary=(
            "Las variables pueden tomar cualquier valor real no negativo, "
            "incluidos los fraccionarios."
        ),
        content=(
            "El supuesto de **divisibilidad** establece que las variables "
            "de decisión pueden tomar **cualquier valor real no negativo**, "
            "incluyendo valores fraccionarios.\n\n"
            "Cuando este supuesto **no se cumple** —porque las variables "
            "deben ser enteras (cantidad de autos, cantidad de personas)— "
            "el problema deja de ser de PL continua y se convierte en "
            "**Programación Lineal Entera (PLE)**, que requiere métodos "
            "distintos como Branch & Bound."
        ),
        related=("supuestos-pl", "no-negatividad"),
    ),
    Concept(
        id="certidumbre",
        title="Certidumbre",
        category="supuestos",
        aliases=(
            "certidumbre",
            "supuesto de certidumbre",
            "que es la certidumbre",
            "parametros conocidos",
        ),
        summary=(
            "Todos los parámetros (coeficientes objetivo, tecnológicos y "
            "términos independientes) son conocidos con exactitud."
        ),
        content=(
            "El supuesto de **certidumbre** (o determinismo) establece que "
            "todos los parámetros del modelo son **conocidos con certeza** y "
            "**no varían**:\n\n"
            "- los coeficientes de la función objetivo (cⱼ),\n"
            "- los coeficientes tecnológicos (aᵢⱼ),\n"
            "- los términos independientes o disponibilidades (bᵢ).\n\n"
            "Cuando los parámetros son inciertos o aleatorios el modelo "
            "pasa a ser de **Programación Estocástica**, que excede el "
            "alcance de la PL clásica."
        ),
        related=(
            "supuestos-pl",
            "coeficientes-tecnologicos",
            "terminos-independientes",
        ),
    ),
    # ─── Componentes ──────────────────────────────────────────────────────
    Concept(
        id="componentes-pl",
        title="Componentes básicos de un modelo de PL",
        category="componentes",
        aliases=(
            "componentes basicos",
            "componentes de pl",
            "componentes de la programacion lineal",
            "partes de un modelo",
            "elementos de un modelo de pl",
        ),
        summary=(
            "Variables de decisión, función objetivo, restricciones y "
            "condiciones de no negatividad."
        ),
        content=(
            "Todo modelo de Programación Lineal está compuesto por **cuatro "
            "elementos** fundamentales:\n\n"
            "1. **Variables de decisión** — representan aquello que se va a "
            "determinar matemáticamente (cantidad a fabricar, dinero a "
            "invertir, horas a asignar). Se notan x₁, x₂, …, xₙ.\n"
            "2. **Función objetivo** — meta a optimizar (maximizar ganancias "
            "o minimizar costos). Tiene la forma Z = c₁x₁ + c₂x₂ + … + cₙxₙ.\n"
            "3. **Restricciones** — limitaciones operativas, físicas o de "
            "contexto. Se formulan como inecuaciones o ecuaciones lineales: "
            "Σ aᵢⱼ xⱼ ≤ (o ≥ o =) bᵢ.\n"
            "4. **Condiciones técnicas (no negatividad)** — xⱼ ≥ 0 para "
            "todo j."
        ),
        related=(
            "variables-decision",
            "funcion-objetivo",
            "restricciones",
            "no-negatividad",
        ),
    ),
    Concept(
        id="variables-decision",
        title="Variables de decisión",
        category="componentes",
        aliases=(
            "variables de decision",
            "variable de decision",
            "que son las variables",
            "que es una variable de decision",
            "xj",
            "xi",
            "x1 x2",
        ),
        summary=(
            "Lo que el modelo busca determinar: las cantidades sobre las que "
            "se decide. Se notan x₁, x₂, …, xₙ."
        ),
        content=(
            "Las **variables de decisión** representan **aquello que se va "
            "a determinar matemáticamente** al resolver el modelo: por "
            "ejemplo, la cantidad de cada producto a fabricar, los días a "
            "trabajar en cada turno, o el dinero a invertir en cada "
            "alternativa.\n\n"
            "Se notan habitualmente **x₁, x₂, …, xₙ** y, por convención de "
            "la cátedra, su definición debe incluir **la unidad de medida y "
            "el horizonte temporal** cuando aplique. Por ejemplo:\n\n"
            "*x₁: cantidad de televisores planos a producir por mes.*\n\n"
            "En el alcance de Slacko trabajamos siempre con **dos variables "
            "continuas** (x₁ y x₂)."
        ),
        related=(
            "componentes-pl",
            "funcion-objetivo",
            "restricciones",
            "no-negatividad",
        ),
    ),
    Concept(
        id="funcion-objetivo",
        title="Función objetivo",
        category="componentes",
        aliases=(
            "funcion objetivo",
            "que es la funcion objetivo",
            "z",
            "objetivo",
            "maximizar",
            "minimizar",
            "max z",
            "min z",
            "coeficientes objetivo",
            "cj",
        ),
        summary=(
            "Expresión lineal Z = c₁x₁ + c₂x₂ + … + cₙxₙ que se busca "
            "maximizar o minimizar."
        ),
        content=(
            "La **función objetivo** es la **meta del modelo**: aquello que "
            "el problema busca **maximizar** (utilidad, ingresos, "
            "producción) o **minimizar** (costos, tiempo, desperdicio).\n\n"
            "Se compone por los **coeficientes objetivo** —notados c₁, c₂, "
            "…, cₙ— multiplicados por las variables de decisión, formando "
            "una **expresión lineal**:\n\n"
            "    Z = c₁·x₁ + c₂·x₂ + … + cₙ·xₙ\n\n"
            "Cada cⱼ representa el **aporte unitario** de la variable xⱼ a "
            "la meta del modelo (por ejemplo, la ganancia por unidad "
            "vendida, o el costo por unidad producida)."
        ),
        related=("componentes-pl", "variables-decision", "solucion-optima"),
    ),
    Concept(
        id="restricciones",
        title="Restricciones",
        category="componentes",
        aliases=(
            "restricciones",
            "que son las restricciones",
            "restriccion",
            "limitaciones",
            "inecuaciones",
            "sistema de restricciones",
        ),
        summary=(
            "Limitaciones del problema expresadas como inecuaciones o "
            "ecuaciones lineales sobre las variables."
        ),
        content=(
            "Las **restricciones** representan las **limitaciones operativas** "
            "del problema: tiempo disponible, dinero, demandas, capacidades, "
            "recursos físicos. Pueden ser **físicas** (capacidad de una "
            "máquina) o **de contexto** (demanda mínima, mezcla regulada).\n\n"
            "Se formulan como un **sistema de inecuaciones o igualdades** "
            "lineales en las variables de decisión:\n\n"
            "    Σⱼ aᵢⱼ · xⱼ  ≤  (o ≥ o =)  bᵢ\n\n"
            "donde:\n\n"
            "- **aᵢⱼ** son los **coeficientes tecnológicos** (cuánto recurso "
            "i consume cada unidad de la actividad j),\n"
            "- **bᵢ** es el **término independiente** o disponibilidad del "
            "recurso i."
        ),
        related=(
            "componentes-pl",
            "coeficientes-tecnologicos",
            "terminos-independientes",
            "no-negatividad",
        ),
    ),
    Concept(
        id="coeficientes-tecnologicos",
        title="Coeficientes tecnológicos (aᵢⱼ)",
        category="componentes",
        aliases=(
            "coeficientes tecnologicos",
            "coeficiente tecnologico",
            "aij",
            "que son los coeficientes tecnologicos",
            "consumo por unidad",
        ),
        summary=(
            "Cantidad de recurso i consumida por cada unidad de la "
            "actividad j."
        ),
        content=(
            "Los **coeficientes tecnológicos**, notados **aᵢⱼ**, indican la "
            "**cantidad del recurso i** que **consume cada unidad** de la "
            "actividad j.\n\n"
            "Por ejemplo, si fabricar un televisor plano (variable x₁) "
            "requiere 4 horas de máquina A, entonces el coeficiente "
            "tecnológico para la restricción de máquina A respecto de x₁ "
            "es a₁₁ = 4. Aparecen multiplicando a las variables en el lado "
            "izquierdo de cada restricción."
        ),
        related=("restricciones", "terminos-independientes", "certidumbre"),
    ),
    Concept(
        id="terminos-independientes",
        title="Términos independientes (bᵢ)",
        category="componentes",
        aliases=(
            "terminos independientes",
            "termino independiente",
            "bi",
            "que representa bi",
            "disponibilidad de recurso",
            "lado derecho",
            "rhs",
        ),
        summary=(
            "Cantidad disponible (o requerida) de cada recurso i; aparecen "
            "en el lado derecho de las restricciones."
        ),
        content=(
            "Los **términos independientes**, notados **bᵢ**, representan "
            "la **cantidad disponible (o requerida) del recurso i**.\n\n"
            "Aparecen en el **lado derecho** de cada restricción:\n\n"
            "    aᵢ₁·x₁ + aᵢ₂·x₂ + … + aᵢₙ·xₙ  ≤  bᵢ\n\n"
            "Si la restricción es de **techo** (≤), bᵢ es la disponibilidad "
            "máxima del recurso. Si es de **piso** (≥), bᵢ es la cantidad "
            "mínima que hay que satisfacer."
        ),
        related=("restricciones", "coeficientes-tecnologicos"),
    ),
    Concept(
        id="no-negatividad",
        title="Condición de no negatividad",
        category="componentes",
        aliases=(
            "no negatividad",
            "condicion de no negatividad",
            "condiciones tecnicas",
            "xj mayor o igual a cero",
            "variables no negativas",
        ),
        summary=(
            "Todas las variables de decisión deben tomar valores mayores o "
            "iguales a cero: xⱼ ≥ 0 para todo j."
        ),
        content=(
            "La **condición de no negatividad** exige que **todas las "
            "variables de decisión** tomen valores **mayores o iguales a "
            "cero**:\n\n"
            "    xⱼ ≥ 0    para todo j\n\n"
            "Esta condición refleja la **realidad física** del problema: "
            "no se puede producir una cantidad negativa de un producto, ni "
            "trabajar un número negativo de horas, ni invertir un monto "
            "negativo.\n\n"
            "También se la conoce como **condición técnica** del modelo y "
            "es uno de los seis supuestos de la PL."
        ),
        related=("supuestos-pl", "variables-decision", "divisibilidad"),
    ),
    # ─── Geometría ────────────────────────────────────────────────────────
    Concept(
        id="region-factible",
        title="Región factible",
        category="geometria",
        aliases=(
            "region factible",
            "que es la region factible",
            "cuerpo factible",
            "que es el cuerpo factible",
            "conjunto de soluciones factibles",
            "soluciones factibles",
            "poliedro convexo",
        ),
        summary=(
            "Conjunto de todos los puntos que satisfacen simultáneamente "
            "todas las restricciones y la no negatividad."
        ),
        content=(
            "La **región factible** —también llamada **cuerpo factible** o "
            "**conjunto de soluciones factibles**— es el **conjunto de "
            "todos los puntos** que satisfacen **simultáneamente todas las "
            "restricciones** del problema y las condiciones de no "
            "negatividad.\n\n"
            "Geométricamente, en problemas de dos variables, es un "
            "**polígono convexo** sobre el primer cuadrante. En el caso "
            "general (n variables) es un **poliedro convexo**.\n\n"
            "Cualquier punto **dentro** de la región factible es una "
            "**solución factible** del problema. La **solución óptima** "
            "—si existe— se encuentra siempre en alguno de sus **vértices**."
        ),
        related=(
            "punto-extremo",
            "solucion-optima",
            "teorema-fundamental",
            "metodo-grafico-pasos",
        ),
    ),
    Concept(
        id="solucion-optima",
        title="Solución óptima",
        category="geometria",
        aliases=(
            "solucion optima",
            "cual es la solucion optima",
            "que es la solucion optima",
            "optimo",
            "punto optimo",
        ),
        summary=(
            "Punto de la región factible donde la función objetivo alcanza "
            "su valor máximo (o mínimo). Si existe y es finito, está en un "
            "vértice."
        ),
        content=(
            "La **solución óptima** es el **punto (o puntos) de la región "
            "factible** donde la **función objetivo alcanza su valor "
            "máximo** (en problemas de maximización) o **mínimo** (en "
            "problemas de minimización).\n\n"
            "Por el **Teorema Fundamental de la PL**, si la solución óptima "
            "existe y es finita, **siempre se encuentra en un vértice (punto "
            "extremo) del poliedro factible**. Esto reduce la búsqueda de "
            "infinitos puntos a evaluar la función objetivo en un número "
            "finito de vértices."
        ),
        related=(
            "punto-extremo",
            "region-factible",
            "teorema-fundamental",
            "funcion-objetivo",
        ),
    ),
    Concept(
        id="punto-extremo",
        title="Punto extremo (vértice)",
        category="geometria",
        aliases=(
            "punto extremo",
            "vertice",
            "vertices",
            "que es un vertice",
            "que es un punto extremo",
            "esquina del poligono",
        ),
        summary=(
            "Punto de un conjunto convexo que no puede expresarse como "
            "combinación convexa de otros dos puntos distintos del conjunto."
        ),
        content=(
            "Un **punto extremo** —también llamado **vértice**— es un punto "
            "de un conjunto convexo que **no puede expresarse como "
            "combinación convexa** de otros dos puntos distintos del "
            "conjunto.\n\n"
            "Intuitivamente, son las **esquinas** del polígono que define la "
            "región factible. En el método gráfico se obtienen como "
            "**intersección de dos rectas de restricción activas**.\n\n"
            "Por el Teorema Fundamental de la PL, **el óptimo de un problema "
            "de PL siempre se encuentra en un vértice** (cuando existe y es "
            "finito), por lo cual basta con evaluar la función objetivo en "
            "todos los vértices factibles para hallarlo."
        ),
        related=(
            "region-factible",
            "solucion-optima",
            "teorema-fundamental",
            "metodo-grafico-pasos",
        ),
    ),
    Concept(
        id="teorema-fundamental",
        title="Teorema Fundamental de la PL",
        category="geometria",
        aliases=(
            "teorema fundamental",
            "teorema fundamental de la pl",
            "teorema de la programacion lineal",
            "tflp",
        ),
        summary=(
            "Si existe solución óptima finita, se encuentra en al menos un "
            "vértice de la región factible."
        ),
        content=(
            "El **Teorema Fundamental de la Programación Lineal** establece "
            "que:\n\n"
            "> Si un problema de PL tiene **solución óptima finita**, "
            "entonces dicha solución se alcanza en **al menos un vértice** "
            "(punto extremo) de la región factible.\n\n"
            "**Consecuencia práctica:** la búsqueda del óptimo se reduce de "
            "infinitos puntos del poliedro a un **número finito de "
            "vértices**. Esto es lo que hace **viable** la resolución por "
            "el método gráfico (evaluando todos los vértices) y por el "
            "**método Simplex** (recorriendo vértices de forma inteligente)."
        ),
        related=(
            "punto-extremo",
            "solucion-optima",
            "region-factible",
            "metodo-grafico-elementos",
        ),
    ),
    # ─── Formas ───────────────────────────────────────────────────────────
    Concept(
        id="forma-canonica",
        title="Forma canónica",
        category="formas",
        aliases=(
            "forma canonica",
            "que es la forma canonica",
            "modelo en forma canonica",
        ),
        summary=(
            "Maximización con todas las restricciones ≤, o minimización con "
            "todas ≥; bᵢ ≥ 0 y variables no negativas."
        ),
        content=(
            "Un problema de PL está en **forma canónica** cuando:\n\n"
            "**Para maximización:**\n\n"
            "- todas las restricciones son del tipo **≤** (menor o igual),\n"
            "- todos los **bᵢ ≥ 0**,\n"
            "- todas las variables son **no negativas** (xⱼ ≥ 0).\n\n"
            "**Para minimización:**\n\n"
            "- todas las restricciones son del tipo **≥** (mayor o igual),\n"
            "- todos los **bᵢ ≥ 0**,\n"
            "- todas las variables son **no negativas** (xⱼ ≥ 0).\n\n"
            "La forma canónica es **útil para la interpretación geométrica** "
            "y la **resolución gráfica**, ya que las desigualdades definen "
            "directamente los semiespacios que conforman la región factible."
        ),
        related=(
            "forma-estandar",
            "conversion-canonica-estandar",
            "metodo-grafico-elementos",
        ),
    ),
    Concept(
        id="forma-estandar",
        title="Forma estándar",
        category="formas",
        aliases=(
            "forma estandar",
            "que es la forma estandar",
            "modelo en forma estandar",
        ),
        summary=(
            "Todas las restricciones son ecuaciones, todas las variables "
            "son no negativas y todos los bᵢ son no negativos."
        ),
        content=(
            "Un problema de PL está en **forma estándar** cuando se cumplen "
            "**todas** estas condiciones:\n\n"
            "1. Todas las restricciones son **ecuaciones** (igualdades).\n"
            "2. Todas las variables son **no negativas** (xⱼ ≥ 0).\n"
            "3. Los términos independientes son **no negativos** (bᵢ ≥ 0).\n\n"
            "La forma estándar es **necesaria para aplicar el método "
            "Simplex**, que opera sobre sistemas de ecuaciones lineales.\n\n"
            "Para llegar a forma estándar desde la forma canónica se "
            "introducen **variables de holgura** (en restricciones ≤), "
            "**variables de excedente** (en ≥) y, cuando hace falta, "
            "**variables artificiales** para iniciar el procedimiento."
        ),
        related=(
            "forma-canonica",
            "conversion-canonica-estandar",
            "variable-holgura",
            "variable-excedente",
            "variable-artificial",
        ),
    ),
    Concept(
        id="conversion-canonica-estandar",
        title="Conversión de canónica a estándar",
        category="formas",
        aliases=(
            "conversion canonica a estandar",
            "como convertir canonica a estandar",
            "pasar de canonica a estandar",
            "convertir forma canonica",
            "como pasar a forma estandar",
        ),
        summary=(
            "Se introducen variables de holgura en restricciones ≤ y de "
            "excedente en ≥ para transformar inecuaciones en igualdades."
        ),
        content=(
            "Para convertir un modelo de **forma canónica a forma estándar** "
            "hay que transformar cada inecuación en una igualdad agregando "
            "una variable auxiliar.\n\n"
            "**Restricción ≤** — se le suma una **variable de holgura "
            "(slack)** que absorbe la diferencia entre el recurso usado y "
            "el disponible:\n\n"
            "    6x₁ + 4x₂ ≤ 24    →    6x₁ + 4x₂ + s₁ = 24,    s₁ ≥ 0\n\n"
            "**Restricción ≥** — se le resta una **variable de excedente "
            "(surplus)** que representa cuánto se sobrepasa el mínimo "
            "exigido:\n\n"
            "    3x₁ + x₂ ≥ 12    →    3x₁ + x₂ − e₁ = 12,    e₁ ≥ 0\n\n"
            "**Restricción =** — queda como está, pero si se necesita un "
            "punto inicial factible para el Simplex se agrega una "
            "**variable artificial** penalizada en la función objetivo."
        ),
        related=(
            "forma-canonica",
            "forma-estandar",
            "variable-holgura",
            "variable-excedente",
            "variable-artificial",
        ),
    ),
    # ─── Variables auxiliares ─────────────────────────────────────────────
    Concept(
        id="variable-holgura",
        title="Variable de holgura (slack)",
        category="variables-auxiliares",
        aliases=(
            "variable de holgura",
            "variables de holgura",
            "que es una variable de holgura",
            "slack",
            "variable slack",
            "holgura",
        ),
        summary=(
            "Variable no negativa que se suma a una restricción ≤ para "
            "convertirla en igualdad. Representa el recurso no utilizado."
        ),
        content=(
            "Una **variable de holgura** (en inglés *slack*) es una "
            "**variable auxiliar no negativa** que se **suma** al lado "
            "izquierdo de una restricción de tipo **≤** para convertirla "
            "en una **igualdad**.\n\n"
            "Representa la **cantidad de recurso que sobra**, es decir, lo "
            "que no se utilizó del lado derecho disponible.\n\n"
            "**Ejemplo.** Si tenemos una restricción de capacidad de "
            "máquina:\n\n"
            "    6x₁ + 4x₂ ≤ 24\n\n"
            "agregamos s₁ ≥ 0 y queda:\n\n"
            "    6x₁ + 4x₂ + s₁ = 24\n\n"
            "Si en la solución óptima s₁ = 0, el recurso se usó al máximo "
            "(restricción **activa**). Si s₁ > 0, sobró ese recurso "
            "(restricción **no activa**)."
        ),
        related=(
            "forma-estandar",
            "conversion-canonica-estandar",
            "variable-excedente",
            "variable-artificial",
        ),
    ),
    Concept(
        id="variable-excedente",
        title="Variable de excedente (surplus)",
        category="variables-auxiliares",
        aliases=(
            "variable de excedente",
            "variables de excedente",
            "que es una variable de excedente",
            "surplus",
            "variable surplus",
            "excedente",
        ),
        summary=(
            "Variable no negativa que se resta a una restricción ≥ para "
            "convertirla en igualdad. Representa cuánto se supera el "
            "mínimo exigido."
        ),
        content=(
            "Una **variable de excedente** (en inglés *surplus*) es una "
            "**variable auxiliar no negativa** que se **resta** al lado "
            "izquierdo de una restricción de tipo **≥** para convertirla "
            "en una **igualdad**.\n\n"
            "Representa **cuánto se sobrepasa el mínimo exigido** por la "
            "restricción.\n\n"
            "**Ejemplo.** Si una dieta exige al menos 12 unidades de un "
            "nutriente:\n\n"
            "    3x₁ + x₂ ≥ 12\n\n"
            "restamos e₁ ≥ 0 y queda:\n\n"
            "    3x₁ + x₂ − e₁ = 12\n\n"
            "Si e₁ = 0 en la solución óptima, se cumple exactamente el "
            "mínimo. Si e₁ > 0, se está consumiendo más de lo estrictamente "
            "necesario.\n\n"
            "*Nota:* a diferencia de la holgura, la excedente **no alcanza** "
            "para iniciar el Simplex desde el origen; en general hay que "
            "acompañarla con una **variable artificial**."
        ),
        related=(
            "forma-estandar",
            "conversion-canonica-estandar",
            "variable-holgura",
            "variable-artificial",
        ),
    ),
    Concept(
        id="variable-artificial",
        title="Variable artificial",
        category="variables-auxiliares",
        aliases=(
            "variable artificial",
            "variables artificiales",
            "que es una variable artificial",
            "artificial",
            "metodo de la gran m",
            "gran m",
            "metodo de dos fases",
        ),
        summary=(
            "Variable auxiliar no negativa agregada a restricciones ≥ o = "
            "para tener un punto inicial factible en el Simplex. Se penaliza "
            "fuertemente en la función objetivo."
        ),
        content=(
            "Una **variable artificial** es una **variable auxiliar no "
            "negativa** que se agrega a las restricciones de tipo **≥** o "
            "**=** cuando se necesita un **punto inicial factible** para "
            "arrancar el método Simplex.\n\n"
            "A diferencia de la holgura y la excedente, **no tiene "
            "interpretación física**: existe solamente para que el algoritmo "
            "tenga por dónde empezar. Por eso se la **penaliza fuertemente** "
            "en la función objetivo (método de la **Gran M** o método de "
            "**Dos Fases**) para forzar al Simplex a expulsarla de la base.\n\n"
            "**Diagnóstico clave:** si en la solución óptima alguna variable "
            "artificial **permanece con valor positivo**, se concluye que "
            "el problema **no tiene solución factible**: las restricciones "
            "originales son incompatibles entre sí."
        ),
        related=(
            "forma-estandar",
            "conversion-canonica-estandar",
            "variable-holgura",
            "variable-excedente",
            "caso-no-factible",
        ),
    ),
    # ─── Método gráfico ──────────────────────────────────────────────────
    Concept(
        id="metodo-grafico-elementos",
        title="Elementos del método gráfico",
        category="metodo-grafico",
        aliases=(
            "elementos del metodo grafico",
            "metodo grafico elementos",
            "componentes del metodo grafico",
            "que tiene el metodo grafico",
        ),
        summary=(
            "Restricciones (semiespacios), región factible (intersección), "
            "función objetivo (familia de rectas paralelas) y Teorema "
            "Fundamental."
        ),
        content=(
            "El método gráfico se apoya en cuatro elementos geométricos:\n\n"
            "1. **Restricciones** — cada inecuación lineal define un "
            "**semiespacio**. En ℝ² es un **semiplano** limitado por una "
            "recta; en ℝ³ es un semiespacio limitado por un plano.\n"
            "2. **Región factible** — es la **intersección** de todos los "
            "semiespacios. Genera un **poliedro convexo**, el conjunto de "
            "todas las soluciones posibles.\n"
            "3. **Función objetivo** — define una **familia de "
            "hiperplanos paralelos** (rectas en 2D, planos en 3D). Optimizar "
            "significa **desplazar** esa recta lo más lejos posible en la "
            "dirección de mejora **sin salir** de la región factible.\n"
            "4. **Teorema Fundamental de la PL** — si existe solución "
            "óptima, esta se encuentra en un **punto extremo** (vértice). "
            "Esto reduce la búsqueda de infinitos puntos a unos pocos."
        ),
        related=(
            "metodo-grafico-pasos",
            "region-factible",
            "punto-extremo",
            "teorema-fundamental",
        ),
    ),
    Concept(
        id="metodo-grafico-pasos",
        title="Pasos del método gráfico",
        category="metodo-grafico",
        aliases=(
            "pasos del metodo grafico",
            "como resolver con metodo grafico",
            "resolucion grafica",
            "metodo grafico pasos",
            "como se resuelve graficamente",
            "resolver graficamente",
        ),
        summary=(
            "Plantear, graficar restricciones, determinar región factible, "
            "trazar la objetivo, encontrar el vértice óptimo y calcularlo "
            "algebraicamente."
        ),
        content=(
            "El método gráfico se aplica a problemas con **dos variables de "
            "decisión** y consiste en seis pasos:\n\n"
            "**Paso 1 — Plantear el modelo matemático.** Definir variables, "
            "función objetivo y restricciones.\n\n"
            "**Paso 2 — Graficar las restricciones.** Para cada restricción, "
            "igualar a cero cada variable sucesivamente para hallar las "
            "intersecciones con los ejes y trazar la recta. El sentido de "
            "la desigualdad indica qué semiespacio es factible.\n\n"
            "**Paso 3 — Determinar la región factible.** Es la intersección "
            "de todos los semiespacios factibles, incluyendo el primer "
            "cuadrante (no negatividad). Es un **polígono convexo**.\n\n"
            "**Paso 4 — Trazar la función objetivo.** Asignar un valor "
            "arbitrario a Z y graficar la recta correspondiente; luego "
            "desplazar rectas paralelas en la dirección de mejora.\n\n"
            "**Paso 5 — Encontrar la solución visual.** Identificar el "
            "**último vértice** de la región factible que toca la recta de "
            "Z al desplazarla:\n\n"
            "- *hacia afuera* (alejándose del origen) **para maximizar**,\n"
            "- *hacia adentro* (acercándose al origen) **para minimizar**.\n\n"
            "**Paso 6 — Calcular la solución algebraica.** Resolver el "
            "sistema de ecuaciones de las **restricciones activas** (las "
            "rectas que se intersectan en el vértice óptimo) para obtener "
            "las coordenadas exactas.\n\n"
            "*Alcance.* En el contexto de Slacko trabajamos siempre con "
            "**dos variables**. Con software 3D el método se extiende a "
            "tres, pero a mano es inviable."
        ),
        related=(
            "metodo-grafico-elementos",
            "region-factible",
            "punto-extremo",
            "solucion-optima",
        ),
    ),
    # ─── Casos particulares ──────────────────────────────────────────────
    Concept(
        id="caso-degeneracion",
        title="Degeneración",
        category="casos-particulares",
        aliases=(
            "degeneracion",
            "solucion degenerada",
            "caso degenerado",
            "que es la degeneracion",
        ),
        summary=(
            "Una restricción redundante genera empate en la relación mínima "
            "y al menos una variable básica vale cero en la siguiente "
            "iteración del Simplex."
        ),
        content=(
            "La **degeneración** ocurre cuando hay al menos **una "
            "restricción redundante** en el modelo, lo que produce un "
            "**empate en la relación mínima** durante el método Simplex.\n\n"
            "Como consecuencia, **al menos una variable básica toma el "
            "valor cero** en la siguiente iteración, y se dice que la "
            "solución es **degenerada**.\n\n"
            "Geométricamente, la degeneración aparece cuando **más de dos "
            "restricciones se intersectan en el mismo vértice** de la "
            "región factible. El Simplex puede ciclar entre soluciones "
            "del mismo valor objetivo, aunque en la práctica se evita con "
            "reglas de desempate (regla de Bland)."
        ),
        related=(
            "caso-optimos-alternativos",
            "caso-no-acotada",
            "caso-no-factible",
        ),
    ),
    Concept(
        id="caso-optimos-alternativos",
        title="Óptimos alternativos",
        category="casos-particulares",
        aliases=(
            "optimos alternativos",
            "infinitas soluciones",
            "soluciones alternativas",
            "multiples optimos",
            "optimo alternativo",
        ),
        summary=(
            "Hay infinitas soluciones óptimas cuando la función objetivo es "
            "paralela a una restricción activa no redundante."
        ),
        content=(
            "El caso de **óptimos alternativos** se da cuando existe una "
            "**cantidad infinita de soluciones óptimas**. Esto ocurre "
            "cuando la **función objetivo es paralela a una restricción "
            "activa no redundante**.\n\n"
            "Geométricamente, al desplazar la recta de la función objetivo "
            "en la dirección de mejora, esta no toca un único vértice antes "
            "de salir de la región factible, sino que **coincide con todo "
            "un lado del polígono**. Todos los puntos de ese segmento "
            "—incluidos los dos vértices que lo definen— son soluciones "
            "óptimas con el **mismo valor de Z**."
        ),
        related=(
            "solucion-optima",
            "punto-extremo",
            "caso-degeneracion",
            "caso-no-acotada",
        ),
    ),
    Concept(
        id="caso-no-acotada",
        title="Solución no acotada",
        category="casos-particulares",
        aliases=(
            "solucion no acotada",
            "no acotada",
            "no acotado",
            "espacio no acotado",
            "region no acotada",
            "unbounded",
        ),
        summary=(
            "El espacio de soluciones no está acotado en la dirección de "
            "mejora, por lo que la función objetivo puede crecer (o decrecer) "
            "indefinidamente."
        ),
        content=(
            "Una **solución no acotada** aparece cuando el **espacio de "
            "soluciones factibles no está acotado** en la dirección de "
            "mejora de la función objetivo.\n\n"
            "En ese caso, una de las variables puede crecer **sin romper "
            "ninguna restricción**, y la función objetivo puede aumentar "
            "(o disminuir) **indefinidamente** sin alcanzar nunca un "
            "máximo (o mínimo) finito.\n\n"
            "**En la práctica** este caso suele indicar que **al modelo le "
            "falta una restricción**: en la realidad ningún recurso es "
            "infinito, así que cuando un solver devuelve \"no acotada\" "
            "conviene revisar si se omitió alguna limitación del problema."
        ),
        related=(
            "region-factible",
            "solucion-optima",
            "caso-no-factible",
            "caso-optimos-alternativos",
        ),
    ),
    Concept(
        id="caso-no-factible",
        title="Solución no factible",
        category="casos-particulares",
        aliases=(
            "solucion no factible",
            "no factible",
            "sin solucion",
            "sin solucion factible",
            "soluciones no existentes",
            "infactible",
            "infeasible",
            "restricciones incompatibles",
        ),
        summary=(
            "Las restricciones son incompatibles entre sí: no existe ningún "
            "punto que las satisfaga simultáneamente."
        ),
        content=(
            "Un modelo de PL **no tiene solución factible** cuando sus "
            "**restricciones son incompatibles entre sí**: no existe ningún "
            "conjunto de valores de las variables que satisfaga todas las "
            "restricciones a la vez. Geométricamente, **la región factible "
            "es vacía**.\n\n"
            "Esta situación **no ocurre** si todas las restricciones son de "
            "tipo **≤** con bᵢ ≥ 0, porque en ese caso las variables de "
            "holgura proveen una solución factible obvia (el origen).\n\n"
            "Cuando hay restricciones de tipo ≥ o =, hace falta incorporar "
            "**variables artificiales penalizadas** para iniciar la "
            "resolución. **Si en la solución óptima alguna variable "
            "artificial permanece con valor positivo**, se concluye que el "
            "problema **no tiene solución factible**.\n\n"
            "**Diagnóstico habitual.** Sumas de demandas mínimas mayores a "
            "la disponibilidad total, presupuestos insuficientes para "
            "cumplir cuotas exigidas, cotas inferiores y superiores que se "
            "cruzan."
        ),
        related=(
            "variable-artificial",
            "region-factible",
            "caso-no-acotada",
            "caso-degeneracion",
        ),
    ),
)


# ─── Index helpers ────────────────────────────────────────────────────────


CONCEPTS_BY_ID: dict[str, Concept] = {c.id: c for c in CONCEPTS}
CATEGORIES_BY_ID: dict[str, Category] = {c.id: c for c in CATEGORIES}


def get_concept(concept_id: str) -> Concept | None:
    """Return the concept with that id, or ``None`` if not found."""

    return CONCEPTS_BY_ID.get(concept_id)


def list_concepts(category: str | None = None) -> list[Concept]:
    """Return all concepts, optionally filtered by category id."""

    if category is None:
        return list(CONCEPTS)
    return [c for c in CONCEPTS if c.category == category]


def list_categories() -> list[Category]:
    """Return all categories in display order."""

    return list(CATEGORIES)


def category_counts() -> dict[str, int]:
    """Return a mapping ``category_id -> number_of_concepts``."""

    counts: dict[str, int] = {c.id: 0 for c in CATEGORIES}
    for concept in CONCEPTS:
        counts[concept.category] = counts.get(concept.category, 0) + 1
    return counts
