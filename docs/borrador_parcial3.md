# Borrador · Parcial 3. Presentación y demostración de prácticas

Rúbrica: `entregas/Parcial3_Enunciado.pdf` (F-ACA-10, 35 pts). Entrega: 23 nov 2026, se presenta al inicio de la clase.
Los puntos marcados **[CONFIRMAR]** necesitan un dato del alumno antes de generar el Word.

---

## Portada (criterio Presentación, punto 1)

- Universidad Tecnológica del Norte de Coahuila
- **Parcial 3 · Presentación y demostración de prácticas**
- Matriz de riesgos, factibilidad del proyecto y penúltimo avance
- Proyecto: Sistema de gestión de rendimiento
- Alumno: Hector Alfredo Zamora Guerra
- Programa educativo: ITIID · 7mo cuatrimestre, grupo 7A
- Materia: Formulación de Proyectos de Tecnología · Unidad: Factibilidad del proyecto
- Docente: Ing. Domingo Fraga Hernández · Cuatrimestre: Septiembre - Diciembre 2026
- Nava, Coahuila, 23 de noviembre de 2026

---

## 1. Prácticas realizadas (criterio Presentación, punto 2)

| Entrega | Fecha | Resultado |
| --- | --- | --- |
| Presentación inicial del proyecto | Inicio del cuatrimestre | Problema y solución, tecnologías y su justificación, modelo entidad-relación de 5 entidades e impacto esperado. |
| Práctica 4. Seguimiento y validación de objetivos | 06 oct 2026 | Objetivos O1–O6 con SMART; avance real de 43 % contra 47 % planeado; validación funcional y 2 pruebas automáticas aprobadas. |
| Investigación 8. Técnicas de estimación, Gantt y PERT | 12 oct 2026 | Técnicas de estimación, elementos del Gantt y del PERT, y herramientas gratuitas para elaborarlos. |
| Práctica 6. Gestión de recursos del proyecto | 22 oct 2026 | 150 h estimadas en 7 roles; $19,950 MXN estimados sin gasto en efectivo; identificación, asignación y seguimiento de recursos. |
| Parcial 2. Presentación y demostración de prácticas | 25 oct 2026 | Descarte de A7, A9–A11 (36 actividades vigentes); avance de 57 % contra 68 %; ahorro en mínimo funcional; nueva ruta crítica de 82.6 días. |
| **[CONFIRMAR]** ¿Prácticas entregadas entre el 25 oct y el 23 nov? | | |

Capturas (una por entrega): portada de la presentación inicial, tabla de objetivos de la Práctica 4, técnicas de estimación de la Investigación 8, recursos de la Práctica 6 y Gantt actualizado del Parcial 2 (imágenes ya existentes en `capturas/practicas-anteriores/` e `img/`).

---

## 2. Matriz de riesgos del proyecto

**Escala.** Probabilidad (P) e impacto (I) de 1 a 3 (bajo, medio, alto). Nivel = P × I: 1–2 bajo, 3–4 medio, 6–9 alto.

### 2.1 Riesgos que se presentaron

| ID | Riesgo | Cuándo | Impacto que tuvo | Medida aplicada | Resultado |
| --- | --- | --- | --- | --- | --- |
| R1 | Atraso de un módulo en la ruta crítica (ahorro: A35, A36–A38) | Octubre | No se inició en su ventana (13–29 oct); al corte del Parcial 2 el avance quedó 11 puntos abajo (57 % contra 68 %) y la holgura bajó a 1.4 días. | Se redujo el ahorro a su mínimo funcional y se re-estimó por tres puntos (4.2 días). | Ahorro terminado el 13 nov. |
| R2 | Alcance mayor al necesario en el calendario | Octubre | A7, A9, A10 y A11 repetían en el calendario funciones que ya existían en la lista y el detalle de objetivos; consumían 2 fases de la ruta crítica. | Se descartaron y se ajustó el criterio de éxito de O2; la línea base no cambió. | 36 actividades vigentes en lugar de 40. |
| R3 | Falla de seguridad: datos compartidos entre usuarios | Detectado el 09 nov | Las altas se guardaban a nombre del primer usuario de la base y cualquier usuario con sesión podía ver, editar y borrar los datos de todos. | Se ligaron categorías y objetivos al usuario de Django, todas las vistas filtran por el usuario con sesión y se agregaron 7 pruebas. | Corregido el 11 nov, antes de liberar. |
| R4 | Errores de interfaz que las pruebas unitarias no detectan | Detectado el 13 nov | En la lista de objetivos, los filtros y el formulario de alta repetían identificadores; las etiquetas del formulario apuntaban al campo equivocado. | Se agregaron 8 pruebas de punta a punta con Playwright, grabadas en video. | Corregido el mismo día, con prueba de regresión. |

### 2.2 Riesgos que pueden ocurrir

| ID | Riesgo | P | I | Nivel | Medida |
| --- | --- | --- | --- | --- | --- |
| R5 | Pérdida de código: el trabajo del 09 al 13 nov (CRUD, dashboard, datos por usuario, ahorro, pruebas E2E) no está en el repositorio de GitHub; el último commit es del 23 oct. | 2 | 3 | Alto (6) | Subir los cambios al repositorio de inmediato y hacer commit al terminar cada actividad; respaldar la base con `dumpdata`. |
| R6 | No terminar el manual y el despliegue (C1) al 30 nov: la holgura es casi nula. | 2 | 3 | Alto (6) | Adelantar el `Dockerfile` mientras corren las pruebas; reutilizar las capturas de las pruebas E2E en el manual. |
| R7 | Falla de la demostración en vivo (base de datos apagada, VM o equipo). | 2 | 3 | Alto (6) | Probar `docker compose up` y cargar datos de ejemplo el día anterior; tener los videos de las pruebas E2E como respaldo. |
| R8 | Sin internet, el calendario (FullCalendar) y las gráficas (Chart.js) no cargan, porque vienen de un CDN. | 2 | 2 | Medio (4) | Servir ambas librerías como archivos estáticos del proyecto. |
| R9 | Sobrecarga del único responsable, que cubre 7 roles (150 h). | 2 | 2 | Medio (4) | Priorizar la ruta crítica, mantener alcances mínimos funcionales y apoyarse en las pruebas automáticas para no repetir trabajo. |
| R10 | Cambios de requerimientos en la recta final. | 1 | 2 | Bajo (2) | Registrar cada cambio contra la línea base en el plan y evaluar su impacto en la ruta crítica antes de aceptarlo. |

### 2.3 Matriz de riesgos

| Probabilidad \ Impacto | Bajo (1) | Medio (2) | Alto (3) |
| --- | --- | --- | --- |
| **Alta (3)** | | | R1 |
| **Media (2)** | | R2, R4, R8, R9 | R3, R5, R6, R7 |
| **Baja (1)** | | R10 | |

R1 a R4 ya se presentaron y están controlados; los de nivel alto pendientes (R5, R6, R7) tienen su medida antes de la demostración o del cierre.

---

## 3. Factibilidad del proyecto

### 3.1 Justificación

Muchas personas se proponen metas personales (ejercicio, ahorro, estudio) pero no les dan seguimiento real: terminan con listas de tareas sueltas que no muestran si avanzan ni qué tan bien. El sistema permite planificar objetivos, dividirlos en actividades con fecha y registrar resultados medibles (valor esperado contra obtenido), para ver con datos qué tan seguido se cumple lo planeado y en qué áreas se es más constante.

### 3.2 Factibilidad por tipo

| Tipo | Evaluación | Evidencia |
| --- | --- | --- |
| **Técnica** | Factible | El sistema funciona con 4 módulos (usuarios, gestión de objetivos y actividades, estadísticas y ahorro); 38 pruebas unitarias y 8 flujos de punta a punta aprobados; corre en una computadora personal con PostgreSQL en Docker. |
| **Económica** | Factible | Costo estimado de $19,950 MXN (Práctica 6), casi todo mano de obra propia (150 h × $100/h); sin gasto en efectivo porque todo el software es libre. Chart.js y Playwright, agregados después, también son gratuitos. |
| **Operativa** | Factible | Se usa desde el navegador, en español y con la hora local; cada usuario ve solo sus datos; los flujos principales se validaron como lo haría un usuario real. |
| **De tiempo** | Factible con holgura mínima | Avance real de 89 % contra 92 % planeado (3 puntos abajo, dentro del umbral de 5); cierre estimado el 30 nov. Ver riesgos R5–R7. |
| **Legal** | Factible | Todas las dependencias tienen licencias libres que permiten su uso (Django y Django REST Framework: BSD; PostgreSQL: PostgreSQL License; FullCalendar y Chart.js: MIT; psycopg: LGPL; Playwright: Apache 2.0). Los datos son personales y cada usuario solo accede a los suyos. |

**Conclusión:** el proyecto es factible; el único factor ajustado es el tiempo, que se controla con las medidas de la matriz de riesgos.

### 3.3 Por qué las tecnologías seleccionadas

| Tecnología | Por qué |
| --- | --- |
| Django (Python) | El ORM modela la cadena usuario → objetivo → actividad → registro sin SQL a mano; trae autenticación, administración y protección de formularios listas; permitió agregar módulos como apps independientes (estadísticas, ahorro). |
| Django REST Framework | Entrega las actividades al calendario en formato JSON con permisos por usuario. |
| PostgreSQL | Integridad referencial entre tablas relacionadas y consultas agregadas para las estadísticas (cumplimiento, sumas de ahorro). |
| Docker y Docker Compose | Levantan la base de datos (y en el cierre, todo el sistema) igual en cualquier equipo con un solo comando. |
| FullCalendar | Vistas de mes, semana y día listas, en español. |
| Chart.js | Gráficas de esperado contra obtenido y del dashboard sin desarrollar dibujo propio; gratuito. |
| Playwright | Prueba los flujos en un navegador real y graba videos que sirven como evidencia. |

### 3.4 Impactos por ámbito

| Ámbito | Impacto | Por qué |
| --- | --- | --- |
| Personal | Mejor organización y seguimiento de metas. | Cada objetivo se divide en actividades con fecha y se ve su avance y vencimiento. |
| Educativo | Fomenta el hábito de estudio y la planeación académica. | Permite planear materias, cursos o proyectos y medir la constancia con rachas. |
| Toma de decisiones | Decisiones basadas en datos sobre el uso del tiempo y del dinero. | El dashboard muestra cumplimiento por semana y por categoría, esperado contra obtenido y avance del ahorro. |
| Económico | Ayuda a ahorrar y no genera costo para el usuario. | Metas de ahorro con depósitos y retiros; todo el software es libre, sin licencias. |

---

## 4. Penúltimo avance

### 4.1 Estado de los objetivos al 19 nov 2026

| ID | Objetivo | Fecha límite | Estado |
| --- | --- | --- | --- |
| O1 | Planificación y diseño | 09 oct (reprogramada) | Cumplido: 13 de 13 actividades (A35 el 13 nov). |
| O2 | Calendario con actividades y fechas válidas | 12 oct | 3 de 4: falta A8 (tope del 30 nov). **[CONFIRMAR]** si se hace antes del 23 nov. |
| O3 | Módulos de gestión y registro de rendimiento | 29 oct | Cumplido el 13 nov: autenticación con datos por usuario, categorías, objetivos y actividades con alta, edición y eliminación, rendimiento y ahorro. |
| O4 | Dashboard de estadísticas | 10 nov | Cumplido el 09 nov. |
| O5 | Validar el sistema con pruebas | 23 nov | En curso: 38 pruebas unitarias y 8 flujos E2E aprobados; 1 error encontrado y corregido. |
| O6 | Manual y despliegue en Docker | 30 nov | Por iniciar (24–30 nov). |

**Avance:** 31 de 36 actividades completas y 2 en curso. Con el mismo cálculo de la Práctica 4 ((completas + ½ en curso) ÷ total), el avance real es de **89 %** contra **92 %** planeado.

### 4.2 Guion de la demostración

| Paso | Qué se muestra | Requerimientos | Respaldo en video |
| --- | --- | --- | --- |
| 1 | Registro, inicio de sesión y redirección sin sesión | RF1 | `01_registro_e_inicio_de_sesion.webm` |
| 2 | Alta de categoría, objetivo y actividad; la actividad en el calendario | RF3, RF5, RF8, RF12 | `02_categoria_objetivo_y_actividad.webm` |
| 3 | Registro de rendimiento y gráfica del objetivo | RF10, RF13, RF14 | `03_registro_de_rendimiento.webm` |
| 4 | Editar y eliminar con aviso de borrado en cascada | RF4, RF6, RF9 | `04_editar_y_eliminar.webm` |
| 5 | Objetivo vencido y su filtro | RF7 | `06_vencimiento_de_objetivos.webm` |
| 6 | Meta de ahorro, depósito y retiro rechazado | RF16 | `07_ahorro.webm` |
| 7 | Dashboard de estadísticas | RF15 | `08_dashboard_de_estadisticas.webm` |
| 8 | Pruebas automáticas en terminal (`python manage.py test`) | O5 | — |

Capturas para el documento: las imágenes finales de los flujos E2E (`evidencias/e2e/*.png`).
