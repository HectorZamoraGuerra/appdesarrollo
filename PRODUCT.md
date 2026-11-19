# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Cualquier persona con metas personales de mediano o largo plazo (hacer ejercicio, ahorrar dinero, estudiar algo nuevo) a la que le cuesta darles seguimiento real. La usa una sola persona para manejar su propia información; no es una herramienta colaborativa. La usa a diario o cada semana para planear actividades en el calendario, marcarlas como hechas, registrar resultados y revisar su avance.

## Product Purpose

Gestor personal de metas con vista de calendario. El usuario planea objetivos, los divide en actividades con fecha y registra resultados medibles de cada una. Así ve con honestidad cómo avanza: qué tan seguido cumple lo que se propone, qué objetivos están por vencer y en qué áreas de su vida es más constante. Hay éxito cuando el usuario puede contestar con datos si de verdad avanza hacia sus metas.

## Positioning

Mide resultados, no solo casillas marcadas. Cada actividad registra el valor esperado contra el obtenido y una calificación de satisfacción, y el dashboard convierte eso en cumplimiento, rachas y desviaciones. Una lista de tareas o un calendario común solo dicen si algo se hizo; este sistema dice qué tan bien se hizo.

## Operating Context

- Proyecto escolar (Formulación de Proyectos de Tecnología, ITIID 7A, UTNC, septiembre–diciembre 2026). El plan, las entregas y el avance están en `docs/`.
- La aplicación corre en local con Docker Compose (Django + PostgreSQL 16).
- Flujo principal: Categoría (área de vida) → Objetivo (fechas, prioridad, estado) → Actividad (fecha y horario, aparece en el calendario) → Registro de rendimiento (indicador, valor esperado y obtenido, calificación).
- Módulo de ahorro: metas con monto y fecha, depósitos y retiros (el saldo no puede quedar en negativo), avance y faltante.

## Capabilities and Constraints

- Stack fijo: plantillas de Django, CSS y JS propios, FullCalendar 6.1.15 y Chart.js 4.4.1 (por CDN), y los archivos estáticos que ya existen en `core/static`, `estadisticas/static` y `ahorro/static`. **Nada de dependencias ni frameworks de frontend nuevos.**
- Pantallas: login y registro (`usuarios`), calendario (`/`), objetivos, actividades, categorías (CRUD con confirmación de borrado en cascada), panel de estadísticas (`/estadisticas/`) y metas de ahorro (`/ahorro/`).
- Estados: objetivo pendiente, en progreso, completado o vencido (pasa a vencido automáticamente); actividad pendiente, completada o vencida (calculado).
- **Fecha límite de entrega: 30 nov 2026** (manual y despliegue, A30–A31). Los cambios de diseño deben ser pequeños, seguros y fáciles de revertir.
- **No romper las pruebas E2E con Playwright** (`sistema_rendimiento/e2e/`, evidencias en `docs/evidencias/e2e/`): conservar textos visibles, rutas y selectores en los que se apoyan.
- Interfaz solo en español de México (`es-mx`, zona horaria `America/Matamoros`). No hace falta i18n.
- Fuera de alcance (descartado por el alumno): filtros del calendario, popover y panel del día, color por categoría en el calendario, leyenda dinámica de categorías.

## Brand Commitments

- Nombre: "Sistema de gestión de rendimiento".
- Dirección visual pedida por el usuario (obligatoria): estética de "ventana de sistema" digital tipo HUD de videojuego; fondo oscuro casi negro con azul profundo, azul eléctrico o neón brillante con resplandor (glow), marcos de interfaz con líneas luminosas, títulos en mayúsculas espaciadas y un tono de notificación. Referencia: una ventana de notificación de anime/videojuego que dio el usuario. Se toma la estética, no el contenido: no copiar nombres de personajes, textos, logotipos ni marcas de esa obra.

## Evidence on Hand

- Documentación real: `docs/vision.md`, `docs/plan.md`, `docs/entregas.md`, el modelo ER y los diagramas Gantt/PERT en `docs/img/`.
- Capturas de interfaces y videos E2E en `docs/capturas/` y `docs/evidencias/e2e/`.
- No hay usuarios reales, testimonios ni métricas de uso; no inventarlos.

## Product Principles

1. Ser honesto con el progreso: mostrar sin suavizar los vencidos, las desviaciones y el faltante.
2. Ir del dato a la acción: cada pantalla responde qué sigue o cómo voy.
3. Hacer rápida la captura diaria: registrar una actividad o un resultado debe tomar segundos.
4. Mantener la estética sin sacrificar la claridad: el estilo HUD sirve a la lectura de estados y números, nunca la estorba.
5. Hacer cambios seguros antes de la entrega: nada que ponga en riesgo la demo, las pruebas o el manual.

## Accessibility & Inclusion

Con un tema oscuro y efectos glow, el texto y los números deben mantener contraste legible (WCAG AA), y el estado nunca debe depender solo del color o del brillo. Respetar `prefers-reduced-motion` en cualquier animación de resplandor o escaneo.
