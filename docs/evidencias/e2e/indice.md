# Evidencia de pruebas E2E (flujos completos)

Ejecución: 13 nov 2026 · `python manage.py test e2e` · **8 de 8 flujos aprobados** (56 s).

Cada flujo corre en Chromium (Playwright) contra el sistema levantado por Django sobre una base de prueba vacía, como un usuario real: entra con usuario y contraseña, llena formularios y hace clic. Los datos previos que no son parte del flujo se crean directamente en la base. Se grabó un video por flujo (`.webm`, 1280×800, con pausa de 0.3 s entre acciones) y una captura del estado final (`.png`).

Código: `sistema_rendimiento/e2e/test_flujos.py`.

| # | Flujo | Requerimientos | Qué se comprueba | Resultado | Archivos |
| --- | --- | --- | --- | --- | --- |
| 01 | Registro e inicio de sesión | RF1 | Sin sesión se redirige al login; alta de cuenta; cierre de sesión; contraseña incorrecta muestra error; entrada correcta | Aprobado | `01_registro_e_inicio_de_sesion.webm` / `.png` |
| 02 | Categoría, objetivo y actividad | RF3, RF5, RF8, RF12 | Alta de categoría, objetivo (modal) y actividad (modal); la actividad aparece en el calendario | Aprobado | `02_categoria_objetivo_y_actividad.webm` / `.png` |
| 03 | Registro de rendimiento | RF10, RF13, RF14 | Registrar esperado, obtenido y calificación completa la actividad; el detalle del objetivo muestra el registro y la gráfica | Aprobado | `03_registro_de_rendimiento.webm` / `.png` |
| 04 | Editar y eliminar | RF4, RF6, RF9 | Editar el título del objetivo; eliminar una actividad con confirmación; eliminar una categoría con aviso de borrado en cascada | Aprobado | `04_editar_y_eliminar.webm` / `.png` |
| 05 | Datos por usuario | RF2 | Un usuario no ve el objetivo de otro en su lista y al abrirlo por URL recibe 404 | Aprobado | `05_datos_por_usuario.webm` / `.png` |
| 06 | Vencimiento de objetivos | RF7 | Un objetivo pendiente con fecha meta pasada aparece como "Vencido" y en el filtro "Vencidos" | Aprobado | `06_vencimiento_de_objetivos.webm` / `.png` |
| 07 | Ahorro | RF16 | Alta de meta; depósito; retiro mayor a lo ahorrado rechazado con mensaje; retiro válido; avance y faltante actualizados | Aprobado | `07_ahorro.webm` / `.png` |
| 08 | Dashboard de estadísticas | RF15 | Cumplimiento 67 %, 2 de 3 completadas, mejor racha de 2 días, ahorro 25 %, gráfica semanal, logro por indicador y vista de tabla | Aprobado | `08_dashboard_de_estadisticas.webm` / `.png` |

## Hallazgos y correcciones (A29)

| Fecha | Flujo | Hallazgo | Corrección |
| --- | --- | --- | --- |
| 13 nov | 02 | En la lista de objetivos, los filtros y el formulario del modal repetían los `id` `id_estado` e `id_categoria`; las etiquetas "Estado" y "Categoria" del modal apuntaban a los filtros. | El formulario del modal usa el prefijo `nuevo` (`core/views/objetivos.py`, `objetivo-modal.js`) y una prueba unitaria verifica que la página no repita `id`. |

## Cómo repetirla

```
pip install -r requirements-dev.txt
python -m playwright install chromium
cd sistema_rendimiento
python manage.py test e2e
```

Los archivos de esta carpeta se reemplazan en cada ejecución.
