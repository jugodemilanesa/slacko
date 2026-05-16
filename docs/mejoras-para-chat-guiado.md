# Plan de Mejoras - Aplicación Slacko

## 1. Interfaz e Ingreso de Datos (Carga del Modelo)
* [cite_start]**Consejos en selección de objetivo**: Agregar una sección de consejos para el usuario cuando se le pregunta si el problema busca Maximizar o Minimizar[cite: 1, 2].
* [cite_start]**Formato de función objetivo**: Mostrar la función objetivo (ej. Max Z = 2x1 + 4x2) utilizando formato LaTeX[cite: 14, 15].
* [cite_start]**Botón de edición**: Añadir un botón de editar junto a la opción de quitar en la lista de restricciones[cite: 31].
* [cite_start]**Especificación de decimales**: Indicar de forma explícita cómo ingresar los valores decimales en el formulario[cite: 46].
* [cite_start]**Corrección del flujo de edición**: Arreglar la función de editar para que permita modificar una restricción en particular en lugar de forzar a cargar todos los datos de nuevo [cite: 70][cite_start], asegurando que devuelva al usuario al apartado de quitar-editar[cite: 71].

## 2. Forma Estándar y Métodos de Resolución
* [cite_start]**Interactividad en forma estándar**: Permitir que el usuario intente plantear la forma estándar por sí mismo antes de dar el paso por hecho, o preguntarle si prefiere una transformación automática[cite: 72].
* [cite_start]**Manejo de artificiales**: Evitar que el sistema choque innecesariamente con las variables artificiales en esta fase de interacción[cite: 72].
* [cite_start]**Lógica del método gráfico**: Revisar la resolución gráfica para que calcule basándose únicamente en las intersecciones de las rectas, evitando que parezca que usa Simplex por el despliegue de variables artificiales en esta vista[cite: 89].

## 3. Visualización, Gráficos y Resultados
* [cite_start]**Tutorial interactivo previo**: Añadir un tutorial para el estudiante sobre cómo realizar el método gráfico y el análisis de vértices antes de mostrar el gráfico final[cite: 73].
* [cite_start]**Validación con IA**: Utilizar la resolución hecha por la IA exclusivamente para validar las respuestas y pasos del estudiante[cite: 73].
* [cite_start]**Persistencia de componentes**: Mantener el cuadro de vértices y el gráfico visibles en el chat al pasar al siguiente paso, evitando que desaparezcan de la pantalla[cite: 92].
* [cite_start]**Interpretación de variables de holgura**: Incorporar la explicación de las variables slack y surplus en el análisis final, detallando cuánto recurso quedó ocioso o sobrante[cite: 136].

## 4. Funcionalidades del "Modo Tutor Guiado"
* [cite_start]**Flujo acompañado**: Implementar un modo guiado paso a paso para que el estudiante arme el modelo por sí mismo de forma acompañada[cite: 137].
* [cite_start]**Control de avance por errores**: Frenar al usuario inmediatamente si comete un error (por ejemplo, en la definición de variables) y explicarle el concepto para evitar que arrastre la falla hasta el final[cite: 138].
* [cite_start]**Pistas teóricas contextuales**: Lanzar explicaciones teóricas breves (como qué es una variable slack o una restricción) justo en el momento exacto en que se necesitan utilizar[cite: 139].
* [cite_start]**Preguntas de análisis (hacer dudar)**: Introducir preguntas reflexivas ante enunciados confusos (por ejemplo, preguntar si un dato es diario o mensual) para que el usuario aprenda a analizar mejor el problema[cite: 140].