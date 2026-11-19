"""Capturas de las interfaces del sistema, ordenadas por fase del Gantt.

Levanta el sistema sobre una base de datos de prueba temporal (no toca la base real),
carga datos de ejemplo del proyecto e inicia sesión con un usuario como lo haría una persona.
"""
import os
import sys
from datetime import date, datetime, timedelta, timezone as tz

import django

PROYECTO = '/home/cbolla/sistema_rendimiento/sistema_rendimiento'
SALIDA = sys.argv[1]
CHROMIUM = sys.argv[2]

sys.path.insert(0, PROYECTO)
os.chdir(PROYECTO)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rendimiento.settings')
django.setup()

from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.test.runner import DiscoverRunner
from django.test.testcases import LiveServerThread

settings.ALLOWED_HOSTS = ['*']
runner = DiscoverRunner(verbosity=0, interactive=False)
old = runner.setup_databases()

try:
    from django.contrib.auth.models import User
    from core.models import Actividad, Categoria, Objetivo, RegistroRendimiento

    # ---------- datos de ejemplo (los del wireframe A3 y la Práctica 4) ----------
    dueno = User.objects.create_user('hector', email='hector@utnc.edu.mx', password='Rendimiento-2026')
    cats = {}
    for nombre, desc in [
        ('Salud', 'Ejercicio, alimentación y descanso.'),
        ('Estudio', 'Cursos, idiomas y materias de la universidad.'),
        ('Trabajo', 'Entregables y pendientes laborales.'),
        ('Finanzas', 'Ahorro y control de gastos.'),
    ]:
        cats[nombre] = Categoria.objects.create(usuario=dueno, nombre=nombre, descripcion=desc)

    hoy = datetime(2026, 10, 25, tzinfo=tz.utc)

    def dia(m, d, h=7, mi=0):
        return datetime(2026, m, d, h, mi, tzinfo=tz.utc)

    def objetivo(titulo, cat, estado, prioridad, ini, meta):
        return Objetivo.objects.create(usuario=dueno, categoria=cats[cat], titulo=titulo, estado=estado,
                                       prioridad=prioridad, fecha_inicio=ini, fecha_meta=meta)

    def actividad(obj, titulo, inicio, minutos, nota='', registro=None):
        a = Actividad.objects.create(objetivo=obj, titulo=titulo, nota=nota, completada=bool(registro),
                                     fecha_inicio=inicio, fecha_fin=inicio + timedelta(minutes=minutos))
        if registro:
            tipo, esperado, valor, cal = registro
            RegistroRendimiento.objects.create(actividad=a, tipo_indicador=tipo, esperado=esperado, valor=valor,
                                               calificacion=cal, fecha=inicio.date())
        return a

    correr = objetivo('Correr 10K antes de diciembre', 'Salud', 'en_progreso', 'alta', dia(9, 1), dia(12, 1))
    actividad(correr, 'Trote suave 5 km', dia(10, 5), 40, 'Ritmo cómodo', ('tiempo', 35, 38, 3))
    actividad(correr, 'Series de velocidad 8x400m', dia(10, 8, 18), 60, '', ('tiempo', 30, 32, 4))
    actividad(correr, 'Trote suave 5 km', dia(10, 12), 40, '', ('tiempo', 35, 34, 4))
    actividad(correr, 'Fondo largo 8 km', dia(10, 15), 60, 'Domingo temprano', ('tiempo', 55, 54, 5))
    actividad(correr, 'Intervalos 6x300m', dia(10, 19, 18), 60)                       # vencida
    actividad(correr, 'Trote suave 5 km', dia(10, 22), 40, '', ('tiempo', 33, 31, 5))
    actividad(correr, 'Series de velocidad 8x400m', dia(10, 28, 18), 60)              # pendiente
    actividad(correr, 'Trote suave 5 km', dia(10, 30), 40)
    actividad(correr, 'Fondo largo 8 km', dia(11, 2), 60)

    ingles = objetivo('Terminar curso de inglés B2', 'Estudio', 'en_progreso', 'media', dia(8, 15), dia(11, 20))
    actividad(ingles, 'Unidad 5: listening', dia(10, 6, 19), 60, '', ('tiempo', 60, 50, 3))
    actividad(ingles, 'Unidad 5: writing', dia(10, 13, 19), 60, '', ('tiempo', 60, 65, 4))
    actividad(ingles, 'Examen de práctica', dia(10, 20, 19), 90)                      # vencida
    actividad(ingles, 'Unidad 6: speaking', dia(10, 27, 19), 60)

    ahorro = objetivo('Ahorrar $50,000', 'Finanzas', 'en_progreso', 'media', dia(9, 7), dia(12, 31))
    actividad(ahorro, 'Depósito quincenal', dia(10, 1, 12), 30, '', ('repeticiones', 1, 1, 5))
    actividad(ahorro, 'Revisar gastos del mes', dia(10, 16, 12), 30, '', ('repeticiones', 1, 1, 4))
    actividad(ahorro, 'Depósito quincenal', dia(10, 31, 12), 30)

    informe = objetivo('Entregar informe trimestral', 'Trabajo', 'completado', 'alta', dia(9, 1), dia(9, 30))
    actividad(informe, 'Recopilar datos', dia(9, 10, 16), 120, '', ('tiempo', 120, 110, 4))
    actividad(informe, 'Redactar informe', dia(9, 22, 16), 180, '', ('tiempo', 180, 200, 3))

    objetivo('Leer 12 libros en el año', 'Estudio', 'pendiente', 'baja', dia(10, 1), dia(12, 20))

    # Más actividades para que la lista global tenga varias páginas
    for i in range(6):
        actividad(ingles, f'Repaso de vocabulario {i + 1}', dia(11, 3 + i * 2, 20), 30)

    # ---------- servidor ----------
    servidor = LiveServerThread('localhost', StaticFilesHandler, port=0)
    servidor.daemon = True
    servidor.start()
    servidor.is_ready.wait()
    if servidor.error:
        raise servidor.error
    base = f'http://localhost:{servidor.port}'

    from playwright.sync_api import sync_playwright

    os.makedirs(SALIDA, exist_ok=True)
    tomadas = []

    def foto(pagina, nombre, pagina_completa=True):
        ruta = os.path.join(SALIDA, nombre + '.png')
        if pagina_completa:
            # El sidebar mide 100vh: se agranda la ventana a la altura de la página para que no se corte
            alto = pagina.evaluate('document.documentElement.scrollHeight')
            pagina.set_viewport_size({'width': 1440, 'height': max(900, alto)})
            pagina.wait_for_timeout(400)
        pagina.screenshot(path=ruta)
        pagina.set_viewport_size({'width': 1440, 'height': 900})
        tomadas.append(nombre)
        print('  ', nombre)

    # Consultas antes de abrir el navegador (Playwright corre en un contexto asíncrono)
    pendiente = Actividad.objects.get(objetivo=correr, fecha_inicio=dia(10, 28, 18))

    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=CHROMIUM)
        ctx = nav.new_context(viewport={'width': 1440, 'height': 900}, locale='es-MX',
                              timezone_id='UTC', device_scale_factor=1)
        pg = ctx.new_page()

        # ---- M1 · Autenticación (A15) ----
        pg.goto(base + '/objetivos/')                      # sin sesión: redirige al login
        pg.wait_for_load_state('networkidle')
        foto(pg, 'M1_A15_01_login')
        pg.fill('#id_username', 'hector')
        pg.fill('#id_password', 'contraseña-incorrecta')
        pg.click('button[type=submit]')
        pg.wait_for_load_state('networkidle')
        foto(pg, 'M1_A15_02_login_error')
        pg.click('text=Regístrate')
        pg.wait_for_load_state('networkidle')
        foto(pg, 'M1_A15_03_registro')
        pg.fill('#id_username', 'nuevo')
        pg.fill('#id_password1', '123')
        pg.fill('#id_password2', '456')
        pg.click('button[type=submit]')
        pg.wait_for_load_state('networkidle')
        foto(pg, 'M1_A15_04_registro_validaciones')

        pg.goto(base + '/user/login/?next=/')
        pg.fill('#id_username', 'hector')
        pg.fill('#id_password', 'Rendimiento-2026')
        pg.click('button[type=submit]')

        # ---- E2 · Calendario y registro (A5, A6) ----
        pg.wait_for_selector('.fc-event', timeout=20000)
        pg.wait_for_load_state('networkidle')
        pg.wait_for_timeout(500)
        foto(pg, 'E2_A5_01_calendario_mes')
        pg.click('.fc-timeGridWeek-button')
        pg.wait_for_timeout(800)
        foto(pg, 'E2_A5_02_calendario_semana')

        pg.goto(base + '/actividades/')
        pg.wait_for_load_state('networkidle')
        foto(pg, 'M2_A19_01_lista_actividades')
        pg.click('#btn-nueva-actividad')
        pg.wait_for_timeout(300)
        foto(pg, 'E2_A6_01_modal_nueva_actividad', pagina_completa=False)

        # ---- M2 · Categorías y objetivos (A16–A19) ----
        pg.goto(base + '/categorias/')
        pg.wait_for_load_state('networkidle')
        foto(pg, 'M2_A16_01_lista_categorias')
        pg.click('text=+ Nueva categoría')
        pg.wait_for_load_state('networkidle')
        pg.fill('#id_nombre', 'Hogar')
        pg.fill('#id_descripcion', 'Pendientes y proyectos de la casa.')
        foto(pg, 'M2_A16_02_nueva_categoria', pagina_completa=False)

        pg.goto(base + '/objetivos/')
        pg.wait_for_load_state('networkidle')
        foto(pg, 'M2_A18_01_lista_objetivos')
        pg.click('#id_estado >> text=Activos')
        pg.wait_for_load_state('networkidle')
        pg.click('#id_categoria >> text=Salud')
        pg.wait_for_load_state('networkidle')
        foto(pg, 'M2_A18_02_objetivos_filtro_activos_salud')
        pg.goto(base + '/objetivos/')
        pg.select_option('#id_orden', 'prioridad')
        pg.wait_for_load_state('networkidle')
        foto(pg, 'M2_A18_03_objetivos_orden_prioridad')
        pg.click('.page-header .js-nuevo-objetivo')
        pg.wait_for_timeout(300)
        foto(pg, 'M2_A17_01_modal_nuevo_objetivo', pagina_completa=False)

        pg.goto(base + f'/objetivos/{correr.pk}/')
        pg.wait_for_selector('canvas.grafica-rendimiento')
        pg.wait_for_load_state('networkidle')
        pg.wait_for_timeout(1500)                          # animación de Chart.js
        foto(pg, 'M2_A18_04_detalle_objetivo')
        pg.click('#id_estado >> text=Vencidas')
        pg.wait_for_load_state('networkidle')
        pg.wait_for_timeout(1500)
        foto(pg, 'M2_A18_05_detalle_objetivo_vencidas')

        # ---- M3 · Registro de rendimiento (A20) ----
        pg.goto(base + f'/actividades/{pendiente.pk}/detalle/')
        pg.wait_for_load_state('networkidle')
        pg.select_option('#id_tipo_indicador', 'tiempo')
        pg.fill('#id_esperado', '30')
        pg.fill('#id_valor', '29')
        foto(pg, 'M3_A20_01_registro_rendimiento', pagina_completa=False)
        pg.click('text=Guardar y completar')
        pg.wait_for_selector('.fc-event', timeout=20000)
        pg.goto(base + f'/objetivos/{correr.pk}/?estado=completadas')
        pg.wait_for_load_state('networkidle')
        pg.wait_for_timeout(1500)
        foto(pg, 'M3_A20_02_actividad_completada_en_detalle')

        nav.close()

    servidor.terminate()
    print(f'{len(tomadas)} capturas en {SALIDA}')
finally:
    runner.teardown_databases(old)
