"""Word del Parcial 3: presentación y demostración de prácticas (rúbrica F-ACA-10, unidad Factibilidad del proyecto).

Uso (desde la raíz del repo):  python docs/capturas/documento_parcial3.py
Antes: docs/capturas/codigo_vscode.py y docs/capturas/storyboards_e2e.py generan las imágenes de docs/capturas/parcial3/.
"""

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

from pathlib import Path

DOCS = Path(__file__).resolve().parents[1]
PRACTICAS = DOCS / 'capturas' / 'practicas-anteriores'
P3 = DOCS / 'capturas' / 'parcial3'
SALIDA = DOCS / 'entregas' / 'Parcial3_Presentacion_Demostracion.docx'

TITULO = 'Parcial 3. Presentación y demostración de prácticas'

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
for nivel, tam in ((1, 15), (2, 12.5), (3, 11)):
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
        fila = t.add_row()
        # La fila (imagen y su pie) no se parte entre dos páginas
        fila._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
        celdas = fila.cells
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

def img(ruta):
    return str(ruta)


# ---------------------------------------------------------------- portada
for _ in range(4):
    parrafo()
parrafo('Universidad Tecnológica del Norte de Coahuila', negrita=True, centro=True, tam=14, despues=28)
parrafo('Parcial 3', negrita=True, centro=True, tam=20, despues=4)
parrafo('Presentación y demostración de prácticas', negrita=True, centro=True, tam=16, despues=4)
parrafo('Matriz de riesgos, factibilidad del proyecto y penúltimo avance', centro=True, tam=12, despues=28)
parrafo('Proyecto: Sistema de gestión de rendimiento', centro=True, tam=12.5, despues=28)
for linea in [
    'Alumno: Hector Alfredo Zamora Guerra',
    'Programa educativo: ITIID',
    '7mo cuatrimestre, grupo 7A',
    'Materia: Formulación de Proyectos de Tecnología',
    'Unidad de aprendizaje: Factibilidad del proyecto',
    'Docente: Ing. Domingo Fraga Hernández',
    'Cuatrimestre: Septiembre - Diciembre 2026',
]:
    parrafo(linea, centro=True, despues=2)
parrafo()
parrafo('Nava, Coahuila, 23 de noviembre de 2026', centro=True)
salto()

# ---------------------------------------------------------------- 1. Prácticas
doc.add_heading('1. Prácticas realizadas', level=1)
parrafo('Entregas del cuatrimestre sobre el proyecto y lo que se obtuvo en cada una.')
tabla(
    ['Entrega', 'Fecha', 'Resultado'],
    [
        [('Presentación inicial del proyecto',), 'Inicio del cuatrimestre',
         'Problema que resuelve el sistema, solución propuesta, tecnologías e impacto esperado.'],
        [('Práctica 4. Seguimiento y validación de objetivos',), '06 oct 2026',
         'Objetivos del proyecto redactados con el método SMART y primer seguimiento del avance.'],
        [('Investigación 8. Técnicas de estimación, Gantt y PERT',), '12 oct 2026',
         'Técnicas para estimar tiempos y uso de los diagramas de Gantt y PERT.'],
        [('Práctica 6. Gestión de recursos del proyecto',), '22 oct 2026',
         'Recursos humanos, materiales y económicos del proyecto, y cómo se asignan y vigilan.'],
        [('Parcial 2. Presentación y demostración de prácticas',), '25 oct 2026',
         'Ajuste del alcance, revisión del avance y nuevo calendario de trabajo.'],
        [('Investigación 14. Evaluación y medición de proyectos de TI',), '17 nov 2026',
         'Cómo se evalúa un proyecto de TI al terminarlo y qué resultados deciden si continúa, cambia o se cancela.'],
    ],
    [2.0, 1.1, 3.4],
)
figuras_dobles([
    (img(PRACTICAS / '01_presentacion_inicial' / '01_portada.png'), 'Presentación inicial del proyecto.'),
    (img(PRACTICAS / '02_practica4_seguimiento_validacion' / '01_tabla_objetivos_actualizados.png'),
     'Práctica 4: objetivos del proyecto.'),
    (img(PRACTICAS / '03_investigacion8_estimacion_gantt_pert' / '01_tecnicas_de_estimacion.png'),
     'Investigación 8: técnicas de estimación.'),
    (img(PRACTICAS / '04_practica6_gestion_de_recursos' / '03_tabla_recursos_financieros_19950.png'),
     'Práctica 6: recursos económicos.'),
    (img(DOCS / 'img' / 'gantt_actualizado.png'), 'Parcial 2: calendario de trabajo actualizado.'),
    (img(PRACTICAS / '05_investigacion14_evaluacion_y_medicion' / '02_criterios_de_evaluacion.png'),
     'Investigación 14: criterios para evaluar un proyecto.'),
], ancho=2.9)

# ---------------------------------------------------------------- 2. Riesgos
doc.add_heading('2. Matriz de riesgos del proyecto', level=1)
parrafo('Un riesgo es algo que puede afectar el tiempo, la calidad o el resultado del proyecto. Se identificaron los '
        'que ya ocurrieron durante el desarrollo y los que todavía pueden ocurrir antes del cierre.')

doc.add_heading('2.1 Riesgos que se presentaron', level=2)
tabla(
    ['Riesgo', 'Impacto que tuvo', 'Medida aplicada'],
    [
        [('Retraso del módulo de ahorro',), 'El avance quedó por debajo de lo planeado y se redujo el margen para '
                                            'terminar a tiempo.',
         'Se dejó el módulo en lo esencial; quedó terminado el 13 de noviembre.'],
        [('Funciones repetidas en el calendario',), 'Se planeaba trabajo que no aportaba nada nuevo.',
         'Se quitaron cuatro actividades del plan sin cambiar la fecha de entrega.'],
        [('Un usuario podía ver los datos de otro',), 'Riesgo para la privacidad de la información.',
         'Ahora cada usuario ve y modifica solo su información.'],
        [('Errores de pantalla difíciles de detectar',), 'Algunos formularios no funcionaban como se esperaba.',
         'Se agregaron pruebas que usan el sistema como un usuario real y se corrigió el error.'],
        [('Trabajo sin respaldo',), 'Parte del avance estaba solo en una computadora.',
         'Se respaldó en el repositorio del proyecto en GitHub.'],
    ],
    [1.9, 2.3, 2.3],
)

doc.add_heading('2.2 Riesgos que pueden ocurrir', level=2)
tabla(
    ['Riesgo', 'Medida'],
    [
        [('No terminar a tiempo el manual y la instalación final',),
         'Preparar la instalación mientras se terminan las pruebas y reutilizar las capturas del sistema en el manual.'],
        [('Falla durante la demostración',),
         'Revisar el sistema un día antes y tener los videos de las pruebas como respaldo.'],
        [('Falta de internet en la exposición',),
         'Guardar dentro del proyecto las librerías del calendario y de las gráficas.'],
        [('Carga de trabajo para una sola persona',), 'Atender primero lo indispensable para la entrega.'],
        [('Cambios de último momento',), 'Revisar cada cambio contra el plan antes de aceptarlo.'],
    ],
    [2.6, 3.9],
)

doc.add_heading('2.3 Tabla de la matriz de riesgos', level=2)
parrafo('Cada riesgo se ubica según qué tan probable es y qué tanto afectaría al proyecto. Rojo: atención inmediata; '
        'amarillo: vigilar; verde: bajo.')
COLOR_NIVEL = {'alto': 'F4CCCC', 'medio': 'FCE8B2', 'bajo': 'D9EAD3'}
celdas_matriz = {
    (3, 3): 'Retraso del ahorro',
    (2, 2): 'Funciones repetidas · Errores de pantalla · Falta de internet · Carga de trabajo',
    (2, 3): 'Datos entre usuarios · Trabajo sin respaldo · Manual e instalación · Falla en la demostración',
    (1, 2): 'Cambios de último momento',
}
matriz = tabla(
    ['Probabilidad \\ Impacto', 'Bajo', 'Medio', 'Alto'],
    [[(nombre,)] + [celdas_matriz.get((p, i), '') for i in (1, 2, 3)]
     for p, nombre in ((3, 'Alta'), (2, 'Media'), (1, 'Baja'))],
    [1.4, 1.3, 1.9, 1.9], tam=9,
)
for fila, p in zip(matriz.rows[1:], (3, 2, 1)):
    for celda, i in zip(fila.cells[1:], (1, 2, 3)):
        nivel = p * i
        sombrear(celda, COLOR_NIVEL['alto' if nivel >= 6 else 'medio' if nivel >= 3 else 'bajo'])

# ---------------------------------------------------------------- 3. Factibilidad
doc.add_heading('3. Factibilidad del proyecto', level=1)
doc.add_heading('3.1 Justificación', level=2)
parrafo('Muchas personas se proponen metas como hacer ejercicio, ahorrar o estudiar, pero les cuesta darles '
        'seguimiento. El sistema permite planear objetivos, dividirlos en actividades con fecha y registrar los '
        'resultados, para ver con claridad si se avanza y en qué áreas se es más constante.')

doc.add_heading('3.2 ¿Es factible el proyecto?', level=2)
tabla(
    ['Tipo', 'Resultado'],
    [
        [('Técnica',), 'Sí. El sistema ya funciona con sus módulos principales y pasa todas sus pruebas.'],
        [('Económica',), 'Sí. El costo estimado es de $19,950 MXN, casi todo tiempo de trabajo; no hay que pagar '
                         'licencias porque todo el software es libre.'],
        [('Operativa',), 'Sí. Se usa desde el navegador, está en español y cada persona maneja solo su información.'],
        [('De tiempo',), 'Sí, con poco margen. Lo que falta (manual e instalación final) está planeado para el 30 de '
                         'noviembre.'],
    ],
    [1.3, 5.2],
)
mixto([('Conclusión: ', True), ('el proyecto es factible; el punto a vigilar es el tiempo, que se controla con las '
                                'medidas de la matriz de riesgos.', False)])

doc.add_heading('3.3 Por qué estas tecnologías', level=2)
tabla(
    ['Tecnología', 'Por qué se eligió'],
    [
        [('Django (Python)',), 'Facilita crear el sistema por módulos y ya incluye inicio de sesión y seguridad.'],
        [('PostgreSQL',), 'Guarda la información de forma ordenada y confiable, y permite calcular estadísticas.'],
        [('Docker',), 'Permite instalar el sistema igual en cualquier computadora.'],
        [('FullCalendar y Chart.js',), 'Muestran el calendario y las gráficas sin tener que programarlos desde cero.'],
        [('Playwright',), 'Prueba el sistema en un navegador real, como lo haría un usuario.'],
    ],
    [1.8, 4.7],
)

doc.add_heading('3.4 Impactos en los diferentes ámbitos', level=2)
tabla(
    ['Ámbito', 'Impacto'],
    [
        [('Personal',), 'Ayuda a organizar metas y a ver el avance de cada una.'],
        [('Educativo',), 'Apoya la planeación de materias y proyectos y fomenta la constancia en el estudio.'],
        [('Económico',), 'Ayuda a ahorrar con metas de ahorro y no tiene costo para el usuario.'],
        [('Toma de decisiones',), 'Las estadísticas muestran qué se cumple y qué no, para decidir con datos.'],
    ],
    [1.8, 4.7],
)

# ---------------------------------------------------------------- 4. Penúltimo avance
doc.add_heading('4. Penúltimo avance', level=1)
doc.add_heading('4.1 Estado actual del sistema', level=2)
tabla(
    ['Módulo', 'Estado'],
    [
        [('Cuentas de usuario',), 'Terminado: registro, inicio de sesión y datos propios de cada usuario.'],
        [('Objetivos, actividades y categorías',), 'Terminado: crear, consultar, editar y eliminar.'],
        [('Calendario',), 'Terminado; falta limitar las fechas al 30 de noviembre.'],
        [('Registro de rendimiento',), 'Terminado.'],
        [('Estadísticas',), 'Terminado.'],
        [('Ahorro',), 'Terminado.'],
        [('Pruebas',), 'En curso; todas las pruebas actuales pasan.'],
        [('Manual e instalación final',), 'Pendiente (del 24 al 30 de noviembre).'],
    ],
    [2.3, 4.2],
)

doc.add_heading('4.2 Flujos del sistema', level=2)
parrafo('Recorrido de las funciones principales tal como las usa una persona, con datos de ejemplo de dos meses '
        'de uso (entrenamiento para una carrera, un curso de inglés, control de gastos y metas de ahorro).')
FL = P3 / 'flujos'
FLUJOS = [
    ('Flujo 1. Crear una categoría',
     'Desde Categorías se abre el formulario, se escribe el nombre y la descripción, y la categoría aparece en la '
     'lista y ya puede usarse en los objetivos.',
     [('F1_2_formulario_de_categoria', 'Formulario de la nueva categoría.'),
      ('F1_3_categoria_creada', 'La categoría aparece en la lista.')]),
    ('Flujo 2. Crear un objetivo',
     'Se elige la categoría, la prioridad y las fechas; el objetivo aparece con el conteo de sus actividades.',
     [('F2_1_formulario_de_objetivo', 'Formulario del nuevo objetivo.'),
      ('F2_2_lista_de_objetivos', 'Lista de objetivos con el nuevo objetivo.')]),
    ('Flujo 3. Crear una actividad',
     'La actividad se liga a un objetivo y se agenda con fecha y hora; de inmediato se ve en el calendario.',
     [('F3_1_formulario_de_actividad', 'Formulario de la nueva actividad.'),
      ('F3_2_actividad_en_el_calendario', 'Calendario del mes con la actividad agendada.')]),
    ('Flujo 4. Registrar el resultado de una actividad',
     'Al terminar una actividad se anota lo esperado, lo obtenido y qué tan satisfecho se quedó; la actividad queda '
     'completada y su resultado se suma a la gráfica del objetivo.',
     [('F4_1_registro_de_rendimiento', 'Registro del resultado de la actividad.'),
      ('F4_2_objetivo_con_su_grafica', 'Objetivo con su gráfica de lo esperado contra lo obtenido.')]),
    ('Flujo 5. Ahorro',
     'Cada meta muestra cuánto se lleva y cuánto falta. El sistema no permite retirar más de lo ahorrado; un depósito '
     'actualiza el avance.',
     [('F5_1_metas_de_ahorro', 'Metas de ahorro con su avance.'),
      ('F5_2_retiro_rechazado', 'Retiro mayor a lo ahorrado: el sistema lo rechaza.')]),
]
for titulo, descripcion, imagenes in FLUJOS:
    doc.add_heading(titulo, level=3)
    # El título y la descripción van en la misma página que sus imágenes
    parrafo(descripcion).paragraph_format.keep_with_next = True
    figuras_dobles([(img(FL / f'{archivo}.png'), pie) for archivo, pie in imagenes])
doc.add_heading('Flujo 6. Estadísticas', level=3)
parrafo('Con la información registrada, el panel resume el cumplimiento, los días seguidos de constancia, el avance '
        'del ahorro, las actividades por semana y los objetivos próximos a vencer.').paragraph_format.keep_with_next = True
figura(img(FL / 'F6_1_dashboard_de_estadisticas.png'), 'Panel de estadísticas.', 5.8)

doc.add_heading('4.3 Pruebas del sistema', level=2)
parrafo('El sistema se revisa con pruebas automáticas que se ejecutan con un solo comando. Hay cuatro tipos:')
tabla(
    ['Tipo de prueba', 'Qué revisa', 'Ejemplo', 'Cantidad'],
    [
        [('Unitarias de modelos',), 'Los cálculos y reglas guardados en los datos.',
         'Lo ahorrado y lo que falta para una meta.', '3'],
        [('Unitarias de vistas',), 'Que cada pantalla responda, valide formularios y proteja la información.',
         'Un retiro mayor a lo ahorrado se rechaza.', '27'],
        [('Unitarias de servicios',), 'Los cálculos de las estadísticas.', 'Cumplimiento y racha de días.', '8'],
        [('De punta a punta (E2E)',), 'Flujos completos en un navegador, como un usuario real; cada uno se graba '
                                     'en video.', 'Crear una meta, depositar y retirar.', '8'],
    ],
    [1.5, 2.3, 2.0, 0.7],
)
figuras_dobles([
    (img(P3 / 'P3_01a_carpetas_core.png'), 'Pruebas y vistas del módulo principal.'),
    (img(P3 / 'P3_01b_carpetas_apps_nuevas.png'), 'Módulos de ahorro y estadísticas, y pruebas E2E.'),
], ancho=2.0)
figura(img(P3 / 'P3_07_terminal_pruebas_unitarias.png'), 'Pruebas unitarias: las 38 pasan.', 5.2)
figura(img(P3 / 'P3_08_terminal_pruebas_e2e.png'), 'Pruebas de punta a punta: los 8 flujos pasan.', 6.3)
figura(img(P3 / 'P3_09_documentacion_de_flujos.png'),
       'Documentación de las pruebas: cada flujo probado, lo que se revisó, su resultado y su video.', 6.3)

doc.save(SALIDA)
print('ok', SALIDA)
