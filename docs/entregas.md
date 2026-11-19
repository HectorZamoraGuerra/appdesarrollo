# Entregas

Archivos en [entregas/](entregas/).

## Presentación inicial del proyecto

Archivo: `Presentacion_Sistema_de_gestion_de_rendimiento.pdf` (8 láminas)

Descripción general, tecnologías y justificación, elementos del proyecto, avances (modelo ER de 5 entidades) e impacto. Resumen en [vision.md](vision.md). Las láminas "Actividades y Fechas" y la segunda de "Avances" están vacías en el PDF exportado.

## Práctica 4 — Seguimiento y validación de objetivos (06 oct 2026)

Archivo: `Practica4_Seguimiento_y_Validacion.pdf`

- Objetivos O1–O6 redactados con SMART (ver [plan.md](plan.md)).
- KPI al corte: 14 de 40 actividades completas, 6 en curso; **avance real 43 % contra 47 % planeado** (4 puntos abajo, recuperable). Atraso en A33–A35, A8 y A9.
- Cambios: A33–A35 reprogramadas del 07 al 09 oct; A20 (registro de rendimiento) adelantada y terminada el 06 oct. La línea base no cambió.
- Validación funcional con datos de ejemplo ("Correr 10K antes de diciembre", "Terminar curso de inglés B2"); 2 pruebas automáticas del registro de rendimiento aprobadas.
- Pantallas base de estadísticas y categorías integradas en la navegación.

## Investigación 8 — Técnicas de estimación, Gantt y PERT (12 oct 2026)

Archivo: `Investigacion8_Estimacion_Gantt_PERT.pdf`

Técnicas de estimación (análoga, paramétrica, tres puntos/PERT, juicio de expertos, Planning Poker), elementos del Gantt y del PERT, y herramientas gratuitas (GanttProject, ClickUp, Asana; Visual Paradigm Online, Lucidchart, Creately). Base de los diagramas en [img/](img/).

## Práctica 6 — Gestión de recursos del proyecto (22 oct 2026)

Enunciado: `Practica6_Enunciado.pdf` · Entrega: `Practica6_Gestion_de_Recursos.docx`

Rúbrica (9 pts): portada (1), recursos financieros, humanos y materiales (1), proceso de identificación (2), proceso de asignación (2), seguimiento y monitoreo (2), conclusión (1).

Contenido entregado:

- Recursos humanos: el alumno cubre 7 roles; 150 h estimadas (estimación propia, no medida).
- Recursos financieros: $19,950 MXN estimados, sin gasto en efectivo (software libre, despliegue con Docker Compose). Tarifa de referencia $100/h.
- Único recurso por adquirir: Chart.js (gratuito), para D1.
- Identificación: EDT de 40 actividades / 13 fases / 6 objetivos; duración estimada con PERT (ruta crítica 80.7 días).
- Asignación por fase según dependencias y ruta crítica, con Gantt y PERT como figuras.
- Seguimiento: avance real contra línea base, cumplimiento de hitos O1–O6, ruta crítica y pruebas automáticas.

## Parcial 2 — Presentación y demostración de prácticas (corte 25 oct 2026)

Rúbrica: `F-ACA-10` (35 pts). Entrega: `Parcial2_Presentacion_Demostracion.docx`. Capturas en [capturas/parcial2/](capturas/parcial2/); Gantt y PERT nuevos en `img/gantt_actualizado.png` y `img/pert_actualizado.png`.

- Cambios de alcance: se descartan A7, A9, A10 y A11 (estado, filtros, popover y color dentro del calendario); el estado y los filtros viven en la lista y el detalle de objetivos (A18). Quedan 36 actividades. A33 y A34 terminadas. Criterio de O2 ajustado.
- KPI: **57 % real contra 68 % planeado** (11 puntos abajo, supera el umbral de 5). Atraso en A8, A35 y ahorro.
- Acción correctiva: ahorro (A36–A38) en mínimo funcional, estimado al 31 oct.
- Re-estimación PERT de lo pendiente; nueva ruta crítica: corte → A35 → M4 → D1 → T1 → C1 = **82.6 días (28 nov)**, holgura 1.4 días.

## Investigación 14 — Evaluación y medición de proyectos de TI (17 nov 2026)

Archivo: `Investigacion14_Evaluacion_y_Medicion.pdf` (7 láminas)

Qué es la evaluación de proyectos de TI; cómo se determinan las métricas al concluir (línea base, KPIs, datos post-implementación, análisis de varianza); 10 criterios de evaluación (ROI, requisitos, calidad del código, rendimiento, satisfacción, seguridad, desviación de presupuesto y cronograma, tasa de errores, documentación, impacto en procesos); y los resultados que definen continuar, cambiar o cancelar un proyecto.

## Parcial 3 — Presentación y demostración de prácticas (entrega 23 nov 2026)

Rúbrica: `Parcial3_Enunciado.pdf` (F-ACA-10, 35 pts, unidad Factibilidad del proyecto). Entrega: `Parcial3_Presentacion_Demostracion.docx`, generado con `capturas/documento_parcial3.py`; imágenes en `capturas/parcial3/` (`codigo_vscode.py` y `storyboards_e2e.py`).

- Matriz de riesgos: 5 riesgos presentados (atraso del ahorro, alcance del calendario, datos compartidos entre usuarios, errores de interfaz detectados por E2E, trabajo fuera del repositorio) y 5 posibles (C1 sin holgura, falla de la demo, CDN, sobrecarga, cambios de requerimientos).
- Factibilidad técnica, económica ($19,950 MXN estimados, sin gasto en efectivo), operativa, de tiempo y legal; justificación de tecnologías e impactos por ámbito.
- Penúltimo avance al 19 nov: **89 % real contra 92 % planeado**; O1, O3 y O4 cumplidos; falta A8 en O2; O5 en curso (38 pruebas unitarias y 8 flujos E2E aprobados); O6 por iniciar.
- Evidencia: storyboards de los 8 videos E2E, capturas con estilo de VS Code del código de pruebas, de la estructura de carpetas y de la ejecución en terminal.
