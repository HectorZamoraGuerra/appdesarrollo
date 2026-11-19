# Sistema de gestión de rendimiento — documentación del proyecto

Aplicación web personal (Django 6.1, Django REST Framework, PostgreSQL 16 en Docker, FullCalendar) para planificar objetivos de mediano y largo plazo, dividirlos en actividades con fecha y registrar resultados medibles (valor esperado contra obtenido).

Proyecto de la materia **Formulación de Proyectos de Tecnología** (ITIID, 7mo cuatrimestre, grupo 7A, Universidad Tecnológica del Norte de Coahuila). Docente: Ing. Domingo Fraga Hernández. Alumno: Hector Alfredo Zamora Guerra. Cuatrimestre septiembre–diciembre 2026.

| Archivo | Contenido |
| --- | --- |
| [vision.md](vision.md) | Problema, solución, alcance, tecnologías justificadas, entidades e impacto (presentación inicial) |
| [plan.md](plan.md) | Objetivos O1–O6, fases, actividades A0–A39, estimación PERT, ruta crítica y Gantt |
| [entregas.md](entregas.md) | Prácticas e investigaciones entregadas y lo que se reportó en cada una |
| [img/](img/) | Diagrama de Gantt, diagrama PERT y modelo entidad-relación |
| [evidencias/e2e/](evidencias/e2e/indice.md) | Videos y capturas de los 8 flujos E2E con Playwright (13 nov) |
| [entregas/](entregas/) | PDF y Word de las entregas y enunciados |

## Estado del código (22 oct 2026)

| Módulo | Estado |
| --- | --- |
| Modelo de datos: Usuario, Categoria, Objetivo, Actividad, RegistroRendimiento | Hecho |
| PostgreSQL en Docker, credenciales en `.env` (python-decouple) | Hecho |
| Calendario FullCalendar alimentado por `api/actividades/` | Hecho |
| Alta de objetivos y de actividades | Hecho |
| Registro de rendimiento que marca la actividad como completada (A20) | Hecho, con 2 pruebas |
| Admin de Django para los 5 modelos | Hecho |
| Autenticación (A15) y datos por usuario (RF2): categorías y objetivos pertenecen al `User` de Django; vistas, filtros, API y dashboard filtran por `request.user` (migraciones 0002–0004; se eliminó `core.Usuario`) | Hecho (11 nov) |
| Vencimiento automático de objetivos (RF7): estado `vencido` en lugar de `cancelado`; `Objetivo.objects.marcar_vencidos()` al abrir objetivos y estadísticas | Hecho (11 nov) |
| Idioma `es-mx` y zona horaria `America/Matamoros` (RNF4) | Hecho (11 nov) |
| Editar y eliminar categorías, objetivos y actividades (A16–A19), con confirmación y aviso de borrado en cascada | Hecho (09 nov), con 7 pruebas |
| Leyenda dinámica de categorías y sidebar adaptable a pantallas angostas | Descartados (11 nov) |
| Dashboard de estadísticas (A22–A25, A39), app `estadisticas`: cumplimiento general, por semana y por categoría, rachas, satisfacción, esperado vs obtenido por indicador y objetivos por vencer | Hecho (09 nov), con 11 pruebas |
| Módulo de ahorro (A35–A38), app `ahorro`: metas con monto y fecha, depósitos y retiros (sin dejar el saldo en negativo), avance y faltante; tarjeta de ahorro en el dashboard (A21) | Hecho (13 nov), mínimo funcional, con 10 pruebas |
| Manual y despliegue con Docker Compose (A30, A31) | Pendiente |
