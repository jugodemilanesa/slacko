Flujo de modo tutor determinístico:  
**CONCEPTOS:**

¿Qué es la programación lineal?

La Programación Lineal (PL) es una técnica matemática y algorítmica de optimización. Su objetivo principal es asignar de manera eficiente recursos limitados (como tiempo, dinero, materiales o ancho de banda) entre actividades que compiten por ellos. El resultado busca siempre maximizar un beneficio o minimizar un costo.

Por qué es lineal?

El término "lineal" indica que todas las funciones matemáticas del modelo (tanto la función a optimizar como las restricciones) deben ser funciones lineales. 

Por qué programación?

El término "programación" no se refiere a la codificación en computadoras, sino a la planificación o formulación de un programa de acción.

Que es un modelo de Programación Lineal?

Es la representación matemática de un problema de optimización donde tanto la función objetivo como las restricciones son lineales.

¿Cuáles son los supuestos del modelo de Programación Lineal?  
Son 6:

* **Proporcionalidad:** La contribución de cada variable a la función objetivo y a cada restricción es proporcional a su valor.  
* **Aditividad:** La contribución total es la suma de las contribuciones individuales; no hay interacciones entre variables.  
* **Divisibilidad:** Las variables pueden tomar cualquier valor real no negativo (incluidos fraccionarios).  
* **Certidumbre:** Todos los parámetros (cⱼ, aᵢⱼ, bᵢ) son conocidos con certeza.  
* **Objetivo único:** Existe una sola función objetivo.  
* **No negatividad:** Todas las variables deben ser mayores o iguales a cero.

¿Cuáles son los componentes básicos de la programación Lineal?  
Los componentes básicos son:

* **Variables de decisión**. Representan aquello que se va a determinar matemáticamente (por ejemplo, cantidad de un producto a fabricar o dinero a invertir), representadas generalmente como x1, x2, ..., xn.  
* **Función objetivo**. Es la meta a optimizar (Maximizando ganancias o minimizando costos). Se compone por **coeficientes objetivo**, representados por c1, c2, ..., cn y multiplicados por las variables de decisión. Representa una expresión **lineal** en función de las variables de decisión: z(x1, x2, ..., xn) con la forma c1x1+c2x2+...+cnxn.  
* **Restricciones**. Son limitaciones operativas del problema (tiempo disponible, dinero, demandas o recursos físicos), es decir, pueden ser tanto físicas como de contexto. Se formulan como un sistema de igualdades o desigualdades integradas por **coeficientes tecnológicos** y **coeficientes de recurso.**  
  * **∑ aᵢⱼ xⱼ ≤ (o ≥ o \=) bᵢ**

Que son las condiciones técnicas? En que consiste la no negatividad?

* **Condiciones técnicas (No negatividad)**. Todo modelo general requiere que las variables de decisión tomen valores mayores o iguales a cero (xj=0).  
* **Condición de no negatividad:** xⱼ ≥ 0 para todo j. Las variables no pueden tomar valores negativos (no se puede producir una cantidad negativa).

Que son los coeficientes tecnológicos? 

* **Coeficientes tecnológicos (aᵢⱼ):** Cantidad de recurso i consumida por cada unidad de la actividad j.

Que representa bi? Que representan los términos independientes?

* **Términos independientes (bᵢ):** Cantidad disponible (o requerida) de cada recurso i.

Que es la region/cuerpo factible?

* **Región factible (conjunto de soluciones factibles):** Es el conjunto de todos los puntos que satisfacen simultáneamente todas las restricciones y las condiciones de no negatividad. Geométricamente es un poliedro convexo.

Cual es la solución óptima?

* **Solución óptima:** Es el punto (o puntos) de la región factible donde la función objetivo alcanza su valor máximo (o mínimo). Si existe y es finita, se encuentra en un vértice (punto extremo) del poliedro.

* **Punto extremo (vértice):** Un punto de un conjunto convexo que no puede expresarse como combinación convexa de otros dos puntos distintos del conjunto.

Cuales son las formas de representar un modelo de programación lineal?

Forma Canónica y Forma Estándar

Que es la forma Canónica?

## **Forma canónica**

Un problema de PL está en forma canónica cuando:

* **Para maximización:** todas las restricciones son del tipo  (menor o igual), todos los bi0 y todas las variables son no negativas.  
* **Para minimización:** todas las restricciones son del tipo  (mayor o igual), todos los bi0 y todas las variables son no negativas.

La forma canónica es útil para la interpretación geométrica y la resolución gráfica, ya que las desigualdades definen directamente los semiespacios que conforman la región factible.

Que es la forma Estándar?

## **Forma estándar**

Un problema de PL está en forma estándar cuando se cumplen todas estas condiciones:

1) Todas las restricciones son ecuaciones (igualdades).

2) Todas las variables son no negativas (xj0).  
3) Los términos independientes son no negativos (bi0).

La forma estándar es necesaria para aplicar el método Simplex.

¿Cuáles son los elementos del método gráfico? (dudoso)

1. **Restricciones:** Cada inecuación lineal define un semiespacio. En R2 es un semiplano (limitado por una recta); en R3 un semiespacio (limitado por un plano).   
2. **Región factible:** Es la intersección de todos los semiespacios. Matemáticamente genera un poliedro convexo, que es el conjunto de todas las soluciones posibles.  
3. **Función objetivo:** define una familia de hiperplanos paralelos (rectas en 2D, planos en 3D). Optimizar significa desplazar este hiperplano lo más lejos posible en la dirección de mejora sin salir de la región factible.  
4. **Teorema fundamental de la PL:** Según el Teorema Fundamental, si existe solución óptima, esta se encuentra en un punto extremo (vértice). Esto reduce la búsqueda de infinitos puntos a solo unos pocos nodos.

¿Cuáles son los pasos del método gráfico?

## **Resolución gráfica**

El método gráfico es aplicable a problemas con dos variables de decisión. Consiste en los siguientes pasos:

**Paso 1 – Plantear el modelo matemático:** Definir variables, restricciones y función objetivo.

**Paso 2 – Graficar las restricciones:** Para cada restricción, igualar a cero cada variable sucesivamente para hallar las intersecciones con los ejes y trazar la recta. El sentido de la desigualdad indica qué semiespacio es factible.

**Paso 3 – Determinar la región factible:** Es la intersección de todos los semiespacios factibles, incluyendo el primer cuadrante (no negatividad). Es un polígono convexo.

**Paso 4 – Trazar la función objetivo:** Asignar un valor arbitrario a Z y graficar la recta correspondiente. Luego, desplazar rectas paralelas en la dirección de mejora.

**Paso 5 – Encontrar la solución visual:** Identificar el último vértice de la región factible que toca la recta de la función objetivo al desplazarla. Este paso implica igualar Z a un valor arbitrario, dibujamos la recta. A medida que "empujamos" esa recta de forma paralela en la dirección de optimización, el último punto de la región factible que tocamos antes de salirnos de ella es nuestro óptimo.

* Hacia "afuera" (alejándose del origen) para maximizar.  
* Hacia "adentro" (acercándose al origen) para minimizar. El último vértice de la región factible que toque la recta antes de salir de la zona sombreada es la solución óptima.

**Paso 6 – Calcular la solución algebraica:** Resolver el sistema de ecuaciones formado por las restricciones activas (las rectas que se intersectan en el vértice óptimo) para obtener las coordenadas exactas.

Hay que tener en cuenta que este método está limitado a 3 variables (si usamos un software de graficación 3D, pero a mano es inviable) 

**¿Cómo convertimos de forma canónica a estándar?**  
Con variables de holgura. Por ejemplo, en una restricción de "menor o igual" (≤), el lado izquierdo es lo que usamos del recurso y el lado derecho es el límite disponible. La diferencia entre ambos es lo que nos sobra. Para lograr una igualdad perfecta, le sumamos al lado izquierdo una nueva variable llamada variable de holgura, que representa justamente esa cantidad de recurso no usado.  
Ejemplo:Si tenemos una restricción que dice que el uso de dos productos no puede superar las 24 horas:  
Inecuación original: 6x1 \+ 4x2 ≤ 24   
Forma estándar (ecuación): 6x1 \+ 4x2 \+ x3\= 24   
(Donde x3 es la variable de holgura que absorbe el tiempo que sobró para que la suma dé exactamente 24).

## **¿Cuáles son los casos particulares?**

1. **Degeneración**: Sucede cuando hay por lo menos una restricción redundante; implica que hay un empate por la relación mínima. En el método simplex, al menos una variable básica será cero en la siguiente iteración, y se dice que la nueva solución está degenerada.  
2. **Óptimos alternativos**: Puede presentarse que haya una cantidad infinita de “soluciones” óptimas cuando la función objetivo es paralela a una restricción obligatoria que no es redundante.   
3. **Soluciones no acotadas**: En algunos modelos, puede suceder que el espacio de soluciones es *no acotado,* provocando que una de las variables pueda tomar valores sin romper ninguna de las restricciones.  
4. **Soluciones no existentes (o no factibles)**: Un modelo de programación lineal no tiene solución factible cuando sus restricciones son incompatibles entre sí, es decir, no existe ningún conjunto de valores que las satisfaga simultáneamente.   
   Esta situación no ocurre si todas las restricciones son de \<= con lados derechos no negativos porque las holguras proporcionan una solución factible obvia.    
   En cambio, cuando existen restricciones de otro tipo, es necesario incorporar variables artificiales penalizadas para poder iniciar el procedimiento de resolución. Si en la solución óptima al menos una variable artificial permanece con valor positivo, se concluye que el problema no tiene solución factible.   
     
   Que es una variable slack(de holgura)?  
     
   Que es una variable artificial?  
   

   ### **Diccionario de Patrones NLP para Slacko: "Lector de Escenarios"**

   #### **1\. Identificadores de Variables de Decisión (Xi)**

Slacko debe buscar la pregunta final o la declaración de acción para saber qué entidades se van a cuantificar.

* **Patrones de texto:**  
  * "¿Cuál tiene que ser la distribución de la inversión...?" (Ej. 2\)  
  * "¿Cuántos días debe trabajar cada mina...?" (Ej. 3\)  
  * "Calcular cuántos de cada tipo hay que utilizar..." (Ej. 4\)  
  * "Calcule las cantidades óptimas de \[Entidad A\] y \[Entidad B\] que debe producir..." (Ej. 5\)  
* **Acción de Slacko:** Extraer los sustantivos asociados (Acciones tipo A/B, Días Mina A/B, Autocares Grandes/Pequeños, Solución A/B). Definirlos como X1, X2, …, Xn.  
* **Regla de la cátedra:** Slacko siempre debe declarar la variable definiendo su unidad de medida temporal si existe (ej. X1: Cantidad de TV plana a producir **por año**).

  #### **2\. Identificadores de Función Objetivo (Z)**

Busca la meta del modelo, prestando especial atención a si los coeficientes ($C\_j$) se dan directos o si Slacko debe calcularlos.

* **Patrones de Maximización (Beneficios/Rendimientos):**  
  * "...obtener el máximo interés..." (Ej. 2\) $\\rightarrow$ Buscar porcentajes o tasas ("rinden el 10%").  
  * "...maximizar sus utilidades." (Ej. 5 y 9\)  
  * **Regla de Cálculo (Clave en Ej. 9):** Si el texto dice "El costo... es de \[Monto 1\]" y "se vende a \[Monto 2\]", Slacko debe calcular el coeficiente restando: $C\_j \= \\text{Monto 2} \- \\text{Monto 1}$. En el Ej. 9: Utilidad TV Plana \= 3000 \- 1400 \= 1600\.  
* **Patrones de Minimización (Costos/Gastos):**  
  * "...para que el coste sea mínimo." (Ej. 3\)  
  * "...resulte lo más económica posible..." (Ej. 4\) $\\rightarrow$ Buscar precios de alquiler o uso ("cuesta 80 euros").

  #### **3\. Identificadores de Restricciones de Disponibilidad Máxima ($\\le$)**

Son los "techos" de los recursos.

* **Patrones de texto:**  
  * "Se dispone de \[Número\] \[Unidad\]..." (Ej. 2 y 5\) $\\rightarrow$ Ej: $X\_1 \+ X\_2 \\le 210000$.  
  * "Decidimos invertir un máximo de \[Número\]..." (Ej. 2\) $\\rightarrow$ Ej: $X\_1 \\le 130000$.  
  * "...solo dispone de \[Número\] \[Recurso\]" (Ej. 4\) $\\rightarrow$ Ej: $X\_1 \+ X\_2 \\le 9$ (Restricción de conductores compartidos).  
  * "...máxima de \[Número\]" (Ej. 9\) $\\rightarrow$ Límite de demanda.

  #### **4\. Identificadores de Restricciones de Requerimiento Mínimo ($\\ge$)**

Son los "pisos" obligatorios a cumplir.

* **Patrones de texto:**  
  * "...y como mínimo \[Número\] en las del tipo..." (Ej. 2\) $\\rightarrow$ Ej: $X\_2 \\ge 60000$.  
  * "La compañía necesita al menos \[Número\] toneladas..." (Ej. 3\) $\\rightarrow$ Crea restricciones de tipo $\\ge$ para cada calidad de hierro.  
  * "...debe contener por lo menos \[Número\] unidades del nutriente..." (Ej. 6).  
  * "...completar cantidad mínima de \[Número\]..." (Ej. 6\) $\\rightarrow$ Restricción de volumen total: $X\_1 \+ X\_2 \\ge 100$.

  #### **5\. Identificadores de Restricciones de Rango (Acotadas)**

Cuando una variable tiene un piso y un techo explícitos.

* **Patrones de texto:**  
  * "La demanda... está entre \[Número 1\] y \[Número 2\]..." (Ej. 5\) $\\rightarrow$ Slacko debe generar dos inecuaciones: $X\_1 \\ge 30$ y $X\_1 \\le 150$.  
  * "...producción fluctúa entre \[Número 1\] y \[Número 2\]..." (Ej. 9\) $\\rightarrow$ Generar: $X\_2 \\ge 2000$ y $X\_2 \\le 5000$.

  #### **6\. Patrones Avanzados de Modelado (Especialidad de la Cátedra)**

**A. Homogeneización de Capacidades (El uso de la conjunción "ó")**

Como se ve en el PDF de la cátedra y en el Ejercicio 9, las máquinas que procesan a distintas velocidades no suman sus unidades directamente.

* **Patrón de texto:**  
  * "\[Proceso\] puede producir \[Num 1\] \[Entidad A\] ó \[Num 2\] \[Entidad B\]" (Ej. 9: "7000 TV plana ó 5200 led").  
* **Acción de Slacko:** NO crear $X\_1 \+ X\_2 \\le 7000$. Debe aplicar la fórmula de fracción de capacidad consumida o equivalencia.  
  * *Modelo Cátedra:* $\\frac{X\_1}{7000} \+ \\frac{X\_2}{5200} \\le 1$

**B. Relaciones de Proporción y Mezcla**

Establecen vínculos directos entre las variables de decisión, sin un límite numérico externo fijo.

* **Patrón de texto:**  
  * "...que la \[Entidad A\] sea menor que el doble de la \[Entidad B\]" (Ej. 2).  
* **Acción de Slacko:** Traducir literalmente a matemática y luego estandarizar pasando todo a la izquierda.  
  * Traducción inicial: $X\_1 \< 2 X\_2$ (En PL continua se asume $\\le$).  
  * Forma canónica final: $X\_1 \- 2 X\_2 \\le 0$.

**C. Restricciones de Inventario Múltiple (Matriz de Consumo)**

Cuando un producto o entidad requiere/produce varias cosas al mismo tiempo (como las dietas o las minas).

* **Patrón de texto:**  
  * "La \[Entidad A\] produce cada día \[Num 1\] ton de \[Cualidad 1\], \[Num 2\] ton de \[Cualidad 2\]..." (Ej. 3).  
  * "Cada kg de \[Entidad A\] contiene: \[Num 1\] unid de \[Nutriente 1\], \[Num 2\] unid de \[Nutriente 2\]..." (Ej. 6).  
* **Acción de Slacko:** Entender que la *Entidad* es la variable (columnas de la matriz) y las *Cualidades/Nutrientes* son los recursos limitantes (filas de la matriz).  
  * Nutriente A (Ej. 6): $3 X\_1 \+ 1 X\_2 \\ge 27$  
  * Nutriente B (Ej. 6): $1 X\_1 \+ 1 X\_2 \\ge 21$

  ---

  ### **¿Cómo debería Slacko procesar internamente un prompt de un alumno?**

Si un estudiante le pega a Slacko el **Ejercicio 4**, el procesamiento lógico del bot debería ser:

1. **Detecta Meta:** "lo más económica posible"MINIMIZAR.  
2. **Detecta Costos (Cj):** "autocar grande cuesta 80" (C1 \= 80), "pequeño, 60" (C2 \= 60).  Y GENERAR : Z \= 80 X1 \+ 60 X2.  
3. **Detecta Requerimiento (mayor o igual):** "excursión para 400 alumnos".  
4. **Detecta Coeficientes Tecnológicos (a{ij}):** Grande \= 50 plazas, Pequeño \= 40 plazas. Y GENERAR:  50 X1 \+ 40 X2 mayor o igual 400  
5. **Detecta Disponibilidad Múltiple (menor o igual):** "8 autocares de 40" (X2 menor o igual 8), "10 autocares de 50" (X1 menor o igual 10).  
6. **Detecta Restricción Compartida:** "solo dispone de 9 conductores". X1 \+ X2 menor o igual 9 (Asumiendo 1 conductor por autocar).

COMO RESOLVERIA EL EJERCICIO 2 DE LA TAREA A ENTREGAR:

### **🧠 Fase 1: Slacko escanea el texto (Detección de Patrones)**

1. **Detecta la Meta (Z):** *"que la factura del crudo sea lo menor posible"* **MINIMIZAR** costos.  
2. **Detecta Costos (Cj):** *"costes por barril son de 30 dólares para... Argentina y 32 para el de Venezuela"*.  
3. **Detecta Entidades (Variables):** Slacko nota que hay *Orígenes* (Argentina, Venezuela) y *Destinos/Productos* (Súper, Plus). Activa el patrón de **Doble Índice (Matriz de consumo)** que vimos en el Ejercicio 3 de tu guía.  
4. **Detecta Restricciones de Mezcla (Porcentajes):** Identifica frases como *"al menos 35% de a"*, *"como mucho un 60% de b"*. Activa la regla de reordenamiento algebraico.  
5. **Detecta Restricción de Demanda:** *"demanda semanal máxima es de 60000... que hay que satisfacer"*. La frase "hay que satisfacer" obliga a Slacko a usar un signo de igualdad (=) para garantizar que se cumpla la cuota, a pesar de la palabra "máxima" (ya que si usara $\\le$ en un problema de minimizar, el modelo produciría cero).  
6. **Detecta Límite de Recurso (menor o igual):** *"Se cuenta con 40000$ para inmovilizar..."*.  
   ---

   ### **📐 Fase 2: El Planteo Matemático de Slacko**

**1\. Variables de Decisión ($X\_{ij}$)**

Slacko define que necesita saber cuánto de cada crudo va a cada gasolina:

* $X\_{AS}$: Cantidad de barriles de crudo de Argentina para producir gasolina Súper.  
* $X\_{VS}$: Cantidad de barriles de crudo de Venezuela para producir gasolina Súper.  
* $X\_{AP}$: Cantidad de barriles de crudo de Argentina para producir gasolina Plus.  
* $X\_{VP}$: Cantidad de barriles de crudo de Venezuela para producir gasolina Plus.  
  *(Unidad de medida: barriles/semana)*

**2\. Función Objetivo**

El objetivo es minimizar la factura total (lo que se gasta en comprar ambos crudos, sin importar en qué gasolina terminen).

$$Min\~Z \= 30(X\_{AS} \+ X\_{AP}) \+ 32(X\_{VS} \+ X\_{VP})$$  
**3\. Restricciones de Demanda**

La cantidad total de gasolina fabricada es la suma de los crudos que la componen:

* R1 (Demanda Súper): $X\_{AS} \+ X\_{VS} \= 60.000$  
* R2 (Demanda Plus): $X\_{AP} \+ X\_{VP} \= 40.000$

**4\. Restricciones de Calidad (Patrón de Mezcla)**

Slacko aplica la fórmula: *Atributo aportado $\\ge$ o $\\le$ Atributo exigido por el total*.

* **Para la gasolina Súper:**  
  * R3 (Mínimo 35% aditivo A): $0.20 X\_{AS} \+ 0.50 X\_{VS} \\ge 0.35 (X\_{AS} \+ X\_{VS})$  
  * R4 (Máximo 60% aditivo B): $0.70 X\_{AS} \+ 0.35 X\_{VS} \\le 0.60 (X\_{AS} \+ X\_{VS})$  
* **Para la gasolina Plus:**  
  * R5 (Mínimo 30% aditivo A): $0.20 X\_{AP} \+ 0.50 X\_{VP} \\ge 0.30 (X\_{AP} \+ X\_{VP})$  
  * R6 (Máximo 55% aditivo B): $0.70 X\_{AP} \+ 0.35 X\_{VP} \\le 0.55 (X\_{AP} \+ X\_{VP})$

**5\. Restricción Financiera**

* R7 (Límite de inventario): $30(X\_{AS} \+ X\_{AP}) \+ 32(X\_{VS} \+ X\_{VP}) \\le 40.000$

**6\. Condición de No Negatividad**

* $X\_{ij} \\ge 0$  
  ---

  ### **🔧 Fase 3: Estandarización de Slacko (Transformación para el Simplex)**

Slacko sabe que el software no entiende de paréntesis ni mezclas, así que "limpia" las inecuaciones 3 a 6 agrupando las variables:

* **R3 reordenada:** $(0.20 \- 0.35)X\_{AS} \+ (0.50 \- 0.35)X\_{VS} \\ge 0$  
  $\\rightarrow \-0.15 X\_{AS} \+ 0.15 X\_{VS} \\ge 0$  
* **R4 reordenada:** $(0.70 \- 0.60)X\_{AS} \+ (0.35 \- 0.60)X\_{VS} \\le 0$  
  $\\rightarrow 0.10 X\_{AS} \- 0.25 X\_{VS} \\le 0$  
* **R5 reordenada:** $(0.20 \- 0.30)X\_{AP} \+ (0.50 \- 0.30)X\_{VP} \\ge 0$  
  $\\rightarrow \-0.10 X\_{AP} \+ 0.20 X\_{VP} \\ge 0$  
* **R6 reordenada:** $(0.70 \- 0.55)X\_{AP} \+ (0.35 \- 0.55)X\_{VP} \\le 0$  
  $\\rightarrow 0.15 X\_{AP} \- 0.20 X\_{VP} \\le 0$  
  ---

  ### **🚨 ¡Alerta Analítica de Slacko\! (Caso Especial de la Unidad)**

Aquí es donde Slacko demuestra ser un tutor inteligente y no solo un bot de cálculo. Le diría al alumno:

*"¡Ojo aquí\! Si cargamos este modelo en el WinQSB o Solver, nos va a arrojar el caso especial de **Solución No Factible** (que vimos en los conceptos de teoría). ¿Por qué?* \>

*Fíjate en la matemática:*

* *La Demanda me exige producir $100.000$ barriles en total (R1 \+ R2).*  
* *El costo más barato de crudo es $30.*  
* *Para cumplir la demanda, necesito gastar como mínimo $100.000 \\times \\$30 \= \\$3.000.000$.*  
* *Pero la restricción financiera (R7) dice que solo tengo **$40.000** disponibles.*

*Existe una contradicción insalvable en el enunciado: no hay forma física ni matemática de comprar el crudo necesario con ese presupuesto. Para resolverlo en la práctica, el profesor o gerente deberá aumentar el presupuesto a $3.000.000, o relajar las restricciones de demanda volviéndolas de tipo 'menor o igual'."*

