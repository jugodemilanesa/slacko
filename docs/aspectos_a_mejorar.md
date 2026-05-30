# Reporte de Aspectos a Mejorar - Feedback de Testeo

A continuación se presentan los aspectos a mejorar identificados durante las pruebas del sistema, detallando el comportamiento observado y las sugerencias para su optimización.

| Aspecto a mejorar | Detalle observado | Sugerencia |
| :--- | :--- | :--- |
| **Persistencia de datos** | Al recargar la página, se pierde todo el progreso realizado y no se retoma desde donde el usuario quedó. Adicionalmente, el flujo oculta la información de pasos anteriores. | Implementar el almacenamiento del estado de la sesión y mantener un panel visible con el historial de datos ingresados. |
| **Funcionalidad “editar”** | Al hacer clic en “editar” una restricción, el sistema elimina las restricciones cargadas previamente, obligando al usuario a iniciar desde 0. | Modificar la lógica del botón para que recupere y pueble el formulario con los datos existentes en lugar de resetear el estado completo. |
| **Utilidad del input inicial** | El sistema solicita un escenario o enunciado inicial, pero este input no tiene ningún impacto en el flujo posterior; el sistema continúa aunque se ingresen datos sin sentido. | Si el sistema no va a procesar el texto del escenario, se sugiere omitir este paso para no generar falsas expectativas. |
| **Diseño conversacional** | La herramienta simula un chat, pero la interacción es exclusivamente mediante envíos de formularios preestablecidos y respuestas fijas. | Diseñar la interfaz para que quede claro que es un formulario guiado, no un chat libre. |
| **Sección teórica** | La sección teórica simula ser un chat que analiza una pregunta y en base a esta responde dando la documentación correspondiente, lo cual en realidad es un buscador por palabras clave. | Presentarlo por lo que es. En vez de que el usuario haga una pregunta, es mejor indicarle que busque términos asociados. |
| **Separación de funcionalidades** | - | - |
