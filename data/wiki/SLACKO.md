# SLACKO Wiki — Schema y guía de mantenimiento

Este wiki es la fuente única de verdad teórica para Slacko (asistente de Programación Lineal, UTN). Inspirado en el [llm-wiki de Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): los `.md` los puede editar un humano, y el LLM se encarga de mantener consistencia.

## Alcance

- **Programación Lineal continua** con **2 variables de decisión**.
- Método gráfico, vértices, análisis de sensibilidad básico.
- Conceptos cubiertos: fundamentos, supuestos, componentes, geometría, formas, variables auxiliares, casos particulares.
- **Fuera de alcance**: simplex, programación entera/mixta, más de 2 variables, programación no lineal, estocástica.

## Estructura de archivos

```
data/wiki/
├── SLACKO.md         # este archivo
├── index.md          # catálogo autogenerado (no editar a mano)
├── log.md            # bitácora append-only de operaciones
├── concepts/         # un .md por concepto teórico
├── methods/          # procedimientos (método gráfico, conversión a estándar, etc.)
└── examples/         # ejemplos resueltos (balones-ajedrez, etc.)
```

## Frontmatter obligatorio

Cada página `.md` arranca con frontmatter YAML:

```yaml
---
name: kebab-case-slug
title: Título legible
category: fundamentos | supuestos | componentes | geometria | formas | variables-auxiliares | metodo-grafico | casos-particulares
aliases:
  - "como pregunta el alumno 1"
  - "como pregunta el alumno 2"
related:
  - otro-slug
  - otro-slug-2
sources: []   # ["taha-cap2.pdf:p12-15"] cuando provenga de bibliografía
updated: YYYY-MM-DD
summary: |
  Resumen de 1-3 oraciones que se muestra en listas y en `related`.
---
```

El cuerpo del archivo (debajo del frontmatter) es markdown libre con:
- Markdown estándar (encabezados, listas, bold, italic).
- LaTeX inline `$...$` y block `$$...$$`.
- Cross-links `[[otro-slug]]` que el frontend resuelve a enlaces.

## Categorías

Ver `index.md` para la lista vigente. Categorías estables:

| ID | Título | Descripción |
|---|---|---|
| `fundamentos` | Fundamentos | ¿Qué es la PL? |
| `supuestos` | Supuestos del modelo | Hipótesis de la PL |
| `componentes` | Componentes básicos | Variables, objetivo, restricciones |
| `geometria` | Geometría de la PL | Región factible, vértices |
| `formas` | Formas de representación | Canónica, estándar |
| `variables-auxiliares` | Variables auxiliares | Holgura, excedente, artificial |
| `metodo-grafico` | Método gráfico | Resolución gráfica |
| `casos-particulares` | Casos particulares | No acotado, infactible, múltiples óptimos |

## Operaciones que el LLM puede realizar sobre el wiki

| Operación | Cuándo | Efecto |
|---|---|---|
| `create` | Concepto no existe | Crea `.md` nuevo |
| `update` | Existe y la fuente aporta valor | Reescribe completo, mantiene aliases existentes |
| `touch` | Existe y la fuente solo confirma | Agrega entrada en `sources:` |
| `conflict` | Fuente contradice contenido actual | Marca en `log.md` y NO toca el archivo |

## Reglas duras

1. **Aliases cubren cómo pregunta el alumno**, no cómo lo expresa la cátedra. Incluí variantes con errores frecuentes ("region facible", "que es la holgura").
2. **Cross-links con `[[slug]]`** siempre que un concepto aparezca y exista página propia.
3. **Idioma**: español rioplatense neutro en cuerpo; nombres de variables (`x1`, `x2`, `s1`) y código en inglés.
4. **No inventes**: si la sección no se sustenta en fuentes o conocimiento previo, omitila.
5. **No resuelvas contradicciones**: si una fuente nueva contradice una página, emití `conflict` para revisión humana.

## Log

El archivo `log.md` registra cada operación con formato:

```
## [YYYY-MM-DD] <op> | <título>
- path: <archivo>
- source: <opcional>
```
