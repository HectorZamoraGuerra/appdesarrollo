"""Word del Parcial 2: presentación y demostración de prácticas (rúbrica F-ACA-10)."""
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

IMG = sys.argv[1]          # carpeta con gantt, pert y páginas de prácticas
CAP = sys.argv[2]          # carpeta de capturas del sistema
SALIDA = sys.argv[3]

TITULO = 'Parcial 2. Presentación y demostración de prácticas'

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
for lado in ('left_margin', 'right_margin'):
    setattr(sec, lado, Inches(1))
sec.top_margin = sec.bottom_margin = Inches(0.9)

estilo = doc.styles['Normal']
estilo.font.name = 'Calibri'
estilo.font.size = Pt(11)
estilo.paragraph_format.space_after = Pt(6)
for nivel, tam in ((1, 15), (2, 12.5)):
    h = doc.styles[f'Heading {nivel}']
    h.font.name = 'Calibri'
    h.font.size = Pt(tam)
    h.font.color.rgb = RGBColor(0x1C, 0x20, 0x29)
    h.paragraph_format.space_before = Pt(14 if nivel == 1 else 10)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True

ANCHO = 6.5  # pulgadas útiles


def parrafo(texto='', negrita=False, centro=False, tam=None, despues=None):
    p = doc.add_paragraph()
    if texto:
        r = p.add_run(texto)
        r.bold = negrita
        if tam:
            r.font.size = Pt(tam)
    if centro:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if despues is not None:
        p.paragraph_format.space_after = Pt(despues)
    return p


def mixto(partes):
    """Párrafo con fragmentos (texto, negrita)."""
    p = doc.add_paragraph()
    for texto, negrita in partes:
        p.add_run(texto).bold = negrita
    return p


def vineta(texto, negrita_inicio=None):
    p = doc.add_paragraph(style='List Bullet')
    if negrita_inicio:
        p.add_run(negrita_inicio).bold = True
    p.add_run(texto)
    p.paragraph_format.space_after = Pt(3)
    return p


def sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd')
    sh.set(qn('w:val'), 'clear')
    sh.set(qn('w:color'), 'auto')
    sh.set(qn('w:fill'), color)
    tcPr.append(sh)


def repetir_encabezado(fila):
    trPr = fila._tr.get_or_add_trPr()
    el = OxmlElement('w:tblHeader')
    el.set(qn('w:val'), 'true')
    trPr.append(el)


def tabla(encabezados, filas, anchos, tam=9.5):
    t = doc.add_table(rows=1, cols=len(encabezados))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, txt in enumerate(encabezados):
        c = t.rows[0].cells[i]
        c.text = ''
        r = c.paragraphs[0].add_run(txt)
        r.bold = True
        r.font.size = Pt(tam)
        sombrear(c, 'E7E8EB')
    repetir_encabezado(t.rows[0])
    for fila in filas:
        celdas = t.add_row().cells
        for i, txt in enumerate(fila):
            celdas[i].text = ''
            negrita = isinstance(txt, tuple)
            r = celdas[i].paragraphs[0].add_run(txt[0] if negrita else txt)
            r.bold = negrita
            r.font.size = Pt(tam)
    # Anchos fijos: tblLayout + tblGrid (Word y LibreOffice leen la rejilla, no solo cada celda)
    tblPr = t._tbl.tblPr
    layout = OxmlElement('w:tblLayout')
    layout.set(qn('w:type'), 'fixed')
    tblPr.append(layout)
    for col, w in zip(t._tbl.tblGrid.findall(qn('w:gridCol')), anchos):
        col.set(qn('w:w'), str(int(w * 1440)))
    for fila in t.rows:
        for i, w in enumerate(anchos):
            fila.cells[i].width = Inches(w)
        for c in fila.cells:
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(1)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


n_figura = [0]


def figura(ruta, pie, ancho=ANCHO):
    n_figura[0] += 1
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(ruta, width=Inches(ancho))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(f'Figura {n_figura[0]}. {pie}')
    r.italic = True
    r.font.size = Pt(9)
    c.paragraph_format.space_after = Pt(10)


def figuras_dobles(pares, ancho=3.05):
    """Dos figuras lado a lado en una tabla sin bordes."""
    t = doc.add_table(rows=0, cols=2)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i in range(0, len(pares), 2):
        celdas = t.add_row().cells
        for j, (ruta, pie) in enumerate(pares[i:i + 2]):
            n_figura[0] += 1
            p = celdas[j].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(ruta, width=Inches(ancho))
            c = celdas[j].add_paragraph()
            c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = c.add_run(f'Figura {n_figura[0]}. {pie}')
            r.italic = True
            r.font.size = Pt(8.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def salto():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ---------------------------------------------------------------- pie de página con número
pie = sec.footer.paragraphs[0]
pie.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r = pie.add_run(f'{TITULO}    Página ')
r.font.size = Pt(8.5)
for tipo, texto in (('begin', None), (None, 'PAGE'), ('end', None)):
    run = pie.add_run()
    run.font.size = Pt(8.5)
    if tipo:
        fc = OxmlElement('w:fldChar')
        fc.set(qn('w:fldCharType'), tipo)
        run._r.append(fc)
    else:
        it = OxmlElement('w:instrText')
        it.set(qn('xml:space'), 'preserve')
        it.text = texto
        run._r.append(it)
sec.different_first_page_header_footer = True

# ---------------------------------------------------------------- portada
for _ in range(4):
    parrafo()
parrafo('Universidad Tecnológica del Norte de Coahuila', negrita=True, centro=True, tam=14, despues=28)
parrafo('Parcial 2', negrita=True, centro=True, tam=20, despues=4)
parrafo('Presentación y demostración de prácticas', negrita=True, centro=True, tam=16, despues=4)
parrafo('Seguimiento y validación de objetivos, técnicas de estimación, diagramas de Gantt y PERT',
        centro=True, tam=12, despues=28)
parrafo('Proyecto: Sistema de gestión de rendimiento', centro=True, tam=12.5, despues=28)
for linea in [
    'Alumno: Hector Alfredo Zamora Guerra',
    'Programa educativo: ITIID',
    '7mo cuatrimestre, grupo 7A',
    'Materia: Formulación de Proyectos de Tecnología',
    'Unidad de aprendizaje: Planificación del proyecto',
    'Docente: Ing. Domingo Fraga Hernández',
    'Cuatrimestre: Septiembre - Diciembre 2026',
]:
    parrafo(linea, centro=True, despues=2)
parrafo()
parrafo('Nava, Coahuila, 25 de octubre de 2026', centro=True)
salto()

# ---------------------------------------------------------------- 1. Prácticas
doc.add_heading('1. Prácticas realizadas', level=1)
parrafo('Entregas del cuatrimestre sobre el proyecto, con su resultado principal.')
tabla(
    ['Entrega', 'Fecha', 'Resultado'],
    [
        [('Presentación inicial del proyecto',), 'Inicio del cuatrimestre',
         'Problema y solución, tecnologías y su justificación (Django, PostgreSQL, Docker, FullCalendar), '
         'elementos del sistema con el modelo entidad-relación de 5 entidades e impacto esperado.'],
        [('Práctica 4. Seguimiento y validación de objetivos',), '06 oct 2026',
         'Objetivos O1–O6 con metodología SMART; avance real de 43 % contra 47 % planeado; validación '
         'funcional con datos de ejemplo y 2 pruebas automáticas aprobadas.'],
        [('Investigación 8. Técnicas de estimación, Gantt y PERT',), '12 oct 2026',
         'Técnicas de estimación (análoga, paramétrica, tres puntos, juicio de expertos, Planning Poker), '
         'elementos del diagrama de Gantt y del PERT, y herramientas gratuitas para elaborarlos.'],
        [('Práctica 6. Gestión de recursos del proyecto',), '22 oct 2026',
         'Recursos humanos (150 h estimadas), materiales y financieros ($19,950 MXN estimados, sin gasto en '
         'efectivo); identificación, asignación y seguimiento de recursos con PERT y Gantt.'],
    ],
    [1.85, 1.0, 3.65],
)
figuras_dobles([
    (f'{IMG}/pr_presentacion-1.png', 'Presentación inicial del proyecto.'),
    (f'{IMG}/pr_practica4-2.png', 'Práctica 4: objetivos actualizados al 06 oct.'),
    (f'{IMG}/pr_investigacion8-3.png', 'Investigación 8: técnicas de estimación.'),
    (f'{IMG}/pr_practica6-2.png', 'Práctica 6: recursos del proyecto.'),
], ancho=2.75)

# ---------------------------------------------------------------- 2. Objetivos
doc.add_heading('2. Objetivos actualizados', level=1)
parrafo('Fecha de corte: 25 de octubre de 2026. Los objetivos conservan la redacción SMART de la Práctica 4; '
        'la línea base no cambia y los ajustes se anotan como fecha estimada.')
tabla(
    ['ID', 'Objetivo', 'Actividades vigentes', 'Criterio de éxito', 'Fecha límite', 'Estado al corte'],
    [
        [('O1',), 'Completar la planificación y el diseño del sistema', 'A0–A3, A12–A14, A26, A27, A32–A35',
         'Requisitos, arquitectura, wireframes y modelo ER terminados', '09 oct 2026',
         '12 de 13 completas; A35 estimada 25–27 oct'],
        [('O2',), 'Tener el calendario funcional con actividades y fechas válidas', 'A4–A6, A8',
         'Actividades visibles en el calendario, con fechas dentro del 30 nov (criterio ajustado)',
         '12 oct 2026', '3 de 4 completas; A8 estimada 25–26 oct'],
        [('O3',), 'Implementar los módulos de gestión y el registro de rendimiento', 'A15–A21, A36–A38',
         'Alta, consulta y edición de cada módulo; rendimiento guardado por actividad', '29 oct 2026',
         '3 completas, 4 avanzadas, 3 por iniciar; ahorro estimado al 31 oct'],
        [('O4',), 'Construir el dashboard de estadísticas', 'A22–A25, A39',
         'Gráficas con cumplimiento, rachas y valor esperado contra obtenido', '10 nov 2026',
         'Por iniciar; Chart.js ya integrado'],
        [('O5',), 'Validar el sistema con pruebas', 'A28, A29',
         'Pruebas unitarias y de integración ejecutadas y aprobadas', '23 nov 2026',
         'Iniciado: 2 pruebas automáticas'],
        [('O6',), 'Documentar y desplegar el sistema en Docker', 'A30, A31',
         'Manual entregado y sistema levantado con Docker Compose', '30 nov 2026', 'Por iniciar'],
    ],
    [0.4, 1.3, 1.05, 1.55, 0.8, 1.4], tam=9,
)
parrafo('Cambios respecto a la Práctica 4:', negrita=True, despues=2)
vineta('A7, A9, A10 y A11 (marcado, filtros, popover y color por categoría dentro del calendario) se descartan. '
       'El estado de cada actividad (pendiente, completada o vencida) y los filtros por estado y categoría '
       'se trasladaron a la lista y al detalle de objetivos (A18). Quedan 36 actividades vigentes.')
vineta('A33 y A34 (wireframes de sesión y ahorro) están terminadas; A35 se estima del 25 al 27 de octubre.')
vineta('El módulo de ahorro (A36–A38) se reduce a su mínimo funcional para proteger la fecha del 30 de noviembre.')
vineta('La línea base no cambia; solo se actualizan las fechas estimadas.')

# ---------------------------------------------------------------- 3. Técnicas de seguimiento
doc.add_heading('3. Técnicas de seguimiento y validación aplicadas', level=1)
parrafo('Se aplicaron las mismas técnicas de la Investigación 6 que en la Práctica 4, ahora con los datos '
        'al 25 de octubre, para comparar ambos cortes con el mismo criterio.')
tabla(
    ['Técnica', 'Cómo se aplicó', 'Resultado'],
    [
        [('Metodología SMART',), 'Se revisó cada objetivo; O2 ajustó su criterio por los descartes (3.1).',
         '6 objetivos medibles; O2 ajustado'],
        [('KPIs',), 'Avance planeado contra real con las 36 actividades vigentes (3.2).',
         '57 % real contra 68 % planeado'],
        [('Herramienta de gestión',), 'Cronograma con fecha de línea base, estimada y real (3.3).',
         'Estado de cada actividad al 25 oct'],
        [('Contraste con la línea base',), 'Se compara lo programado contra lo realizado por actividad (3.3).',
         '11 puntos abajo; atraso en A8, A35 y ahorro'],
        [('Validación funcional',), 'Se ejecutó el sistema con datos de ejemplo y se revisó cada interfaz '
                                    '(sección 5).', 'Autenticación, gestión y rendimiento funcionando'],
        [('Control de calidad',), 'Pruebas automáticas y revisión de cada vista con y sin sesión iniciada (3.4).',
         '2 pruebas automáticas aprobadas'],
        [('Reuniones de estado',), 'Se reporta al docente lo logrado, lo pendiente y los ajustes.',
         'Avance reportado en esta presentación'],
        [('Aceptación formal',), 'El docente valida cada entregable con los criterios de la sección 2.',
         'Pendiente de revisión del docente'],
    ],
    [1.6, 3.2, 1.7],
)

doc.add_heading('3.1 Metodología SMART (ejemplo con el objetivo O3)', level=2)
tabla(
    ['Criterio', 'Aplicación al objetivo O3'],
    [
        [('Específico',), 'Implementar autenticación, gestión de categorías y objetivos, registro de rendimiento '
                          'y módulo de ahorro (A15–A21, A36–A38).'],
        [('Medible',), 'Cada módulo permite alta, consulta y edición, y cada actividad guarda su rendimiento '
                       '(valor esperado, obtenido y calificación).'],
        [('Alcanzable',), 'Django ya incluye autenticación y vistas genéricas (ListView, CreateView, UpdateView); '
                          'el ahorro se limita a su mínimo funcional.'],
        [('Relevante',), 'Sin estos módulos no hay datos para el dashboard de estadísticas (O4).'],
        [('Tiempo',), 'Del 13 al 29 de octubre de 2026; el ahorro, estimado al 31 de octubre.'],
    ],
    [1.3, 5.2],
)

doc.add_heading('3.2 KPIs: avance planeado contra avance real', level=2)
parrafo('Se usa el mismo método de la Práctica 4: todas las actividades pesan lo mismo y las que están en curso '
        'cuentan por la parte realizada. La base pasa de 40 a 36 actividades por los 4 descartes.')
tabla(
    ['Indicador', 'Al 06 oct', 'Al 25 oct'],
    [
        ['Actividades vigentes', '40', '36 (4 descartadas)'],
        ['Actividades completas', '14', '18'],
        ['Actividades en curso', '6', '5 (A15, A16, A17, A21, A28)'],
        ['Avance planeado según la línea base', '47 %', '68 %'],
        ['Avance real', '43 %', '57 %'],
        [('Diferencia',), ('4 puntos abajo',), ('11 puntos abajo',)],
    ],
    [3.0, 1.5, 2.0],
)
parrafo('Lectura: la diferencia supera el umbral de alerta de 5 puntos definido en la Práctica 6. El atraso se '
        'concentra en A8, A35 y el módulo de ahorro (A36–A38); además, el planeado supone un avance lineal en la '
        'ventana de O3 (13 al 29 de octubre), que todavía está abierta. Como el ahorro está en la ruta crítica, se '
        'aplica la acción correctiva de la Práctica 6: reducir su alcance al mínimo funcional para proteger la '
        'fecha del 30 de noviembre.')

doc.add_heading('3.3 Herramienta de gestión y contraste con la línea base', level=2)
parrafo('Las fechas de línea base no cambian; en la fecha real se anota el día en que la actividad se completó. '
        'Se muestran las actividades de Ejecución en adelante y las pendientes de Planificación.')
tabla(
    ['ID', 'Actividad', 'Línea base', 'Estimada', 'Real', 'Estado'],
    [
        ['A33, A34', 'Wireframes de sesión y ahorro', '19–21 sep', '07–09 oct', '—', 'Completa'],
        ['A35', 'Ajuste de BD para ahorro', '19–21 sep', '25–27 oct', 'Pendiente', 'Reprogramada'],
        ['A4', 'Entorno de desarrollo (Docker)', '22 sep', '22 sep', '18–19 sep', 'Completa'],
        ['A5, A6', 'Calendario y registro de actividades', '23 sep – 12 oct', '12 oct', '05 oct', 'Completa'],
        ['A7, A9–A11', 'Marcado, filtros, popover y color en el calendario', '23 sep – 12 oct', '—', '—',
         'Descartadas'],
        ['A8', 'Restricción de fecha límite (30 nov)', '23 sep – 12 oct', '25–26 oct', 'Pendiente', 'Reprogramada'],
        ['A15', 'Autenticación de usuarios', '13–29 oct', '29 oct', 'En curso', 'Avanzada'],
        ['A16', 'Gestión de categorías (CRUD)', '13–29 oct', '29 oct', 'En curso', 'Avanzada'],
        ['A17', 'Gestión de objetivos (CRUD)', '13–29 oct', '29 oct', 'En curso', 'Avanzada'],
        ['A18', 'Lista y detalle de objetivos', '13–29 oct', '29 oct', '23 oct', 'Completa'],
        ['A19', 'Lista global de actividades', '13–29 oct', '29 oct', '22 oct', 'Completa'],
        ['A20', 'Registro de rendimiento', '13–29 oct', '13–29 oct', '06 oct', 'Completa (adelantada)'],
        ['A21', 'Integración con rendimiento', '13–29 oct', '31 oct', 'En curso', 'Avanzada'],
        ['A36–A38', 'Módulo de ahorro', '13–29 oct', '27–31 oct', 'Pendiente', 'Mínimo funcional'],
        ['A22–A25, A39', 'Dashboard de estadísticas y gráficas', '02–10 nov', '02–10 nov', 'Pendiente',
         'Por iniciar'],
        ['A28', 'Pruebas unitarias e integración', '11–23 nov', '11–23 nov', 'En curso', 'Iniciada'],
        ['A29', 'Registro y corrección de errores', '11–23 nov', '11–23 nov', 'Pendiente', 'Por iniciar'],
        ['A30, A31', 'Manual de usuario; despliegue en Docker y demo', '24–30 nov', '24–30 nov', 'Pendiente',
         'Por iniciar'],
    ],
    [0.85, 1.95, 1.0, 0.8, 0.8, 1.1], tam=8.5,
)

doc.add_heading('3.4 Control de calidad', level=2)
vineta('Las 2 pruebas automáticas del registro de rendimiento se adaptaron al inicio de sesión y pasan '
       '(python manage.py test core).')
vineta('Cada página se revisó sin sesión (redirige al inicio de sesión) y con sesión iniciada (responde '
       'correctamente).')
vineta('Las funciones nuevas (filtros, estados pendiente/completada/vencida, registro de usuarios y categorías) '
       'se revisaron con datos de ejemplo; sus pruebas automáticas se agregan en la fase de pruebas (A28).')

# ---------------------------------------------------------------- 4. Justificación
doc.add_heading('4. Justificación de los objetivos de acuerdo al avance', level=1)
for ob, texto in [
    ('O1 (se mantiene). ', 'Los wireframes y el modelo ER están terminados. A35 solo afecta al módulo de ahorro, '
                           'por eso se ejecuta junto con él, del 25 al 27 de octubre.'),
    ('O2 (se mantiene con alcance ajustado). ', 'El calendario muestra las actividades por mes, semana y día. '
                                                'Marcar el estado, filtrar y ver el detalle de cada actividad ya se '
                                                'resuelve en la lista y el detalle de objetivos, así que repetirlo '
                                                'en el calendario no agregaba valor; por eso se descartaron A7, A9, '
                                                'A10 y A11 y se ajustó el criterio. A8 se conserva.'),
    ('O3 (se mantiene; ahorro en mínimo funcional). ', 'La lista y el detalle de objetivos, la lista de '
                                                       'actividades y el registro de rendimiento están terminados; '
                                                       'autenticación, categorías y objetivos están avanzados. El '
                                                       'ahorro es la parte más grande sin iniciar y está en la ruta '
                                                       'crítica, por eso se reduce a su mínimo funcional.'),
    ('O4 (se mantiene). ', 'Los registros de rendimiento ya existen y Chart.js ya funciona en el detalle del '
                           'objetivo, lo que permitió re-estimar el dashboard de 9.2 a 8.0 días.'),
    ('O5 y O6 (se mantienen). ', 'Con la re-estimación, la ruta crítica termina el 28 de noviembre, dentro de la '
                                 'fecha límite del 30 de noviembre.'),
]:
    mixto([(ob, True), (texto, False)])

# ---------------------------------------------------------------- 5. Avance funcional
doc.add_heading('5. Avance funcional', level=1)
parrafo('El 25 de octubre de 2026 se ejecutó el sistema con datos de ejemplo (objetivos "Correr 10K antes de '
        'diciembre", "Terminar curso de inglés B2", "Ahorrar $50,000" y "Entregar informe trimestral" con sus '
        'actividades) y se revisó cada interfaz contra su criterio de éxito. Las capturas se agrupan por fase '
        'del diagrama de Gantt.')

doc.add_heading('M1 · Autenticación (A15)', level=2)
figuras_dobles([
    (f'{CAP}/M1_A15_01_login.png', 'Inicio de sesión; las páginas sin sesión redirigen aquí.'),
    (f'{CAP}/M1_A15_04_registro_validaciones.png', 'Registro de usuarios con validación de contraseña.'),
])
doc.add_heading('E2 · Calendario y registro de actividades (A5, A6)', level=2)
figura(f'{CAP}/E2_A5_01_calendario_mes.png', 'Calendario mensual con las actividades de todos los objetivos.', 5.6)
doc.add_heading('M2 · Categorías y objetivos (A16–A19)', level=2)
figura(f'{CAP}/M2_A18_01_lista_objetivos.png',
       'Lista de objetivos con actividades pendientes, completadas y vencidas, filtros y orden.', 5.6)
figura(f'{CAP}/M2_A18_04_detalle_objetivo.png',
       'Detalle del objetivo: conteos, gráfica esperado contra obtenido y actividades con su estado y '
       'calificación.', 4.6)
figuras_dobles([
    (f'{CAP}/M2_A18_02_objetivos_filtro_activos_salud.png', 'Filtros combinados: activos de la categoría Salud.'),
    (f'{CAP}/M2_A18_05_detalle_objetivo_vencidas.png', 'Pestaña de actividades vencidas del objetivo.'),
    (f'{CAP}/M2_A16_01_lista_categorias.png', 'Lista de categorías con su número de objetivos.'),
    (f'{CAP}/M2_A19_01_lista_actividades.png', 'Lista global de actividades con paginación.'),
])
doc.add_heading('M3 · Registro de rendimiento (A20)', level=2)
figuras_dobles([
    (f'{CAP}/M3_A20_01_registro_rendimiento.png', 'Registro de rendimiento: indicador, esperado, obtenido y '
                                                  'calificación.'),
    (f'{CAP}/M3_A20_02_actividad_completada_en_detalle.png', 'La actividad queda completada y se agrega a la '
                                                             'gráfica.'),
])
parrafo('Resultado: los módulos de autenticación, gestión de objetivos y categorías, y registro de rendimiento '
        'funcionan y cumplen su criterio de éxito en alta y consulta; la edición se completa dentro de O3.')

# ---------------------------------------------------------------- 6. Estimación
doc.add_heading('6. Técnicas de estimación aplicadas', level=1)
tabla(
    ['Técnica', 'Cómo se aplicó'],
    [
        [('Estimación por tres puntos (PERT)',), 'Cada fase pendiente se re-estimó con un tiempo optimista (O), '
                                                 'uno más probable (M) y uno pesimista (P), con t = (O + 4M + P) ÷ 6, '
                                                 'en días, contados desde el corte.'],
        [('Juicio de expertos',), 'Los valores de O, M y P se definieron a partir de la experiencia con las fases '
                                  'ya terminadas del mismo proyecto.'],
        [('Estimación análoga',), 'Lo pendiente se comparó con trabajo ya hecho: A8 repite la validación de fechas '
                                  'del formulario de objetivos; el dashboard reutiliza la gráfica de Chart.js del '
                                  'detalle del objetivo; el ahorro sigue el patrón de lista y alta de categorías.'],
    ],
    [1.9, 4.6],
)
parrafo('Re-estimación al 25 de octubre (días):', negrita=True, despues=2)
tabla(
    ['Fase', 'Pendiente', 'O', 'M', 'P', 't', 't en línea base'],
    [
        ['P2', 'A35', '1', '2', '3', ('2.0',), '3.0'],
        ['E3', 'A8', '0.5', '1', '2', ('1.1',), '20.3'],
        ['M1', 'A15', '1', '2', '4', ('2.2',), '17.3'],
        ['M2', 'A16, A17', '1', '2', '3', ('2.0',), '17.3'],
        ['M4', 'A21, A36–A38 (mínimo funcional)', '3', '4', '6', ('4.2',), '17.3'],
        ['D1', 'A22–A25, A39', '6', '8', '10', ('8.0',), '9.2'],
        ['T1', 'A28, A29', '10', '13', '17', ('13.2',), '13.2'],
        ['C1', 'A30, A31', '6', '7', '9', ('7.2',), '7.2'],
    ],
    [0.55, 2.45, 0.5, 0.5, 0.5, 0.6, 1.4],
)
parrafo('En la línea base, t corresponde a la fase completa; en la re-estimación, solo a lo que falta.')

# ---------------------------------------------------------------- 7. Gantt (páginas horizontales)
from docx.enum.section import WD_ORIENT
hz = doc.add_section(WD_SECTION.NEW_PAGE)
hz.orientation = WD_ORIENT.LANDSCAPE
hz.page_width, hz.page_height = Inches(11), Inches(8.5)
hz.top_margin = hz.bottom_margin = Inches(0.7)
hz.different_first_page_header_footer = False
doc.add_heading('7. Diagrama de Gantt del proyecto (actualizado)', level=1)
figura(f'{IMG}/gantt_actualizado.png',
       'Diagrama de Gantt con línea base, avance real por fase, fechas estimadas, hitos O1–O6 y corte al 25 oct.',
       8.4)
vineta('P1, E1, E2 y M3 están al 100 %; M2 al 75 % y M1 al 70 %.')
vineta('E4 queda descartada y E3 se reduce a A8; ambas fuera de la ruta crítica.')
vineta('A35 y el ahorro (M4) terminan el 31 de octubre; el hueco del 30 de octubre al 01 de noviembre absorbe el '
       'cambio, por lo que D1, T1 y C1 conservan su ventana.')

# ---------------------------------------------------------------- 8. PERT
salto()
doc.add_heading('8. Diagrama PERT del proyecto (actualizado)', level=1)
figura(f'{IMG}/pert_actualizado.png',
       'Red PERT al 25 oct: fases terminadas con su duración, fases pendientes re-estimadas y ruta crítica.', 9.0)
tabla(
    ['Concepto', 'Línea base', 'Al 25 oct'],
    [
        ['Ruta crítica', 'P1 → E1 → E3/E4 → M1–M4 → D1 → T1 → C1', 'Corte → P2 (A35) → M4 → D1 → T1 → C1'],
        ['Duración', '80.7 días (26 nov)', '82.6 días (28 nov)'],
        ['Holgura al 30 nov', '3.3 días', '1.4 días'],
        ['Fases con holgura', 'P2: 18.5 · E2: 0.5', 'E3: 5.1 · M1: 4.0 · M2: 4.2'],
    ],
    [1.6, 3.7, 3.7],
)
parrafo('Lectura: la ruta crítica cambia de la fase de calendario al módulo de ahorro, que ahora es la única fase '
        'de O3 sin holgura. El proyecto sigue dentro de la fecha límite, con 1.4 días de margen.')

doc.save(SALIDA)
print('ok', SALIDA)
