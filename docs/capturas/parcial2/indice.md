# Capturas · Parcial 2 (presentación y demostración)

Ordenadas según el diagrama de Gantt. Solo se incluyen las fases que, de acuerdo con la línea base, ya iniciaron al 25 oct 2026 (P1 → M4). D1 Dashboard (inicia el 02 nov), T1 y C1 todavía no tienen pantallas.

Datos: ejemplos del proyecto (objetivos del wireframe A3 y de la Práctica 4) cargados en una base de prueba temporal. Usuario de la demostración: `hector`.

## E2 · Calendario y registro (A5, A6) · línea base 23 sep – 12 oct

| Archivo | Qué muestra |
| --- | --- |
| `E2_A5_01_calendario_mes.png` | Calendario FullCalendar, vista mensual, con las actividades de todos los objetivos |
| `E2_A5_02_calendario_semana.png` | Vista semanal con horario de cada actividad |
| `E2_A6_01_modal_nueva_actividad.png` | Formulario de nueva actividad (modal) |

## M1 · Autenticación (A15) · línea base 13 – 29 oct

| Archivo | Qué muestra |
| --- | --- |
| `M1_A15_01_login.png` | Inicio de sesión; al entrar sin sesión a cualquier página se redirige aquí |
| `M1_A15_02_login_error.png` | Mensaje al escribir una contraseña incorrecta |
| `M1_A15_03_registro.png` | Alta de cuenta |
| `M1_A15_04_registro_validaciones.png` | Validación: las contraseñas no coinciden |

## M2 · Categorías y objetivos (A16 – A19) · línea base 13 – 29 oct

| Archivo | Qué muestra |
| --- | --- |
| `M2_A16_01_lista_categorias.png` | Lista de categorías con el número de objetivos de cada una |
| `M2_A16_02_nueva_categoria.png` | Formulario de nueva categoría |
| `M2_A17_01_modal_nuevo_objetivo.png` | Formulario de nuevo objetivo (modal) |
| `M2_A18_01_lista_objetivos.png` | Lista de objetivos con actividades pendientes, completadas y vencidas |
| `M2_A18_02_objetivos_filtro_activos_salud.png` | Filtros combinados: estado "Activos" y categoría "Salud" |
| `M2_A18_03_objetivos_orden_prioridad.png` | Orden por prioridad (alta → media → baja) |
| `M2_A18_04_detalle_objetivo.png` | Detalle del objetivo: conteos, gráfica esperado vs obtenido y actividades con su estado y calificación |
| `M2_A18_05_detalle_objetivo_vencidas.png` | Pestaña "Vencidas" del detalle |
| `M2_A19_01_lista_actividades.png` | Lista global de actividades con paginación |

## M3 · Registro de rendimiento (A20) · línea base 13 – 29 oct

| Archivo | Qué muestra |
| --- | --- |
| `M3_A20_01_registro_rendimiento.png` | Registro de rendimiento de una actividad: indicador, esperado, obtenido y calificación |
| `M3_A20_02_actividad_completada_en_detalle.png` | La actividad queda completada y aparece en la gráfica como sesión S6 |

## Sin captura (todavía no implementado)

- E3/E4: A8 (restricción al 30 nov), A9 (filtros del calendario), A10 (popover y panel del día).
- M4: A36 – A38 (módulo de ahorro).
- M2: editar y eliminar objetivos y categorías.
- `/estadisticas/` es solo una pantalla base; corresponde a D1 (02 – 10 nov).

Para volver a generarlas: `docs/capturas/capturas.py` (Playwright + base de prueba temporal).
