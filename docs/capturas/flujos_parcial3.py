"""Capturas paso a paso de los flujos principales para el Parcial 3.

Levanta el sistema sobre una base de datos de prueba temporal (no toca la base real), carga datos de ejemplo
con fechas relativas a hoy (8 semanas de actividades, registros de rendimiento y ahorro) y recorre cada flujo
en el navegador como lo haría el usuario, tomando una captura en cada paso.

Uso (desde la raíz del repo):  python docs/capturas/flujos_parcial3.py
Salida: docs/capturas/parcial3/flujos/F<n>_<paso>_<descripcion>.png
"""
import os
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PROYECTO = RAIZ / 'sistema_rendimiento'
SALIDA = RAIZ / 'docs' / 'capturas' / 'parcial3' / 'flujos'
CLAVE = 'Rendimiento-2026'
TAMANO = {'width': 1280, 'height': 800}

sys.path.insert(0, str(PROYECTO))
os.chdir(PROYECTO)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rendimiento.settings')
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'  # Playwright síncrono corre un event loop en este hilo

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.staticfiles.handlers import StaticFilesHandler  # noqa: E402
from django.test.runner import DiscoverRunner  # noqa: E402
from django.test.testcases import LiveServerThread  # noqa: E402
from django.utils import timezone  # noqa: E402

settings.ALLOWED_HOSTS = ['*']


def cargar_datos():
    from django.contrib.auth.models import User

    from ahorro.models import MetaAhorro, Movimiento
    from core.models import Actividad, Categoria, Objetivo, RegistroRendimiento

    dueno = User.objects.create_user('hector', password=CLAVE)
    hoy = timezone.localdate()

    def momento(dias, hora=7, minuto=0):
        """Fecha y hora local, `dias` antes de hoy (negativo: después)."""
        return timezone.make_aware(datetime.combine(hoy - timedelta(days=dias), time(hora, minuto)))

    # "Trabajo" se crea en el flujo 1, por eso no va aquí
    cats = {nombre: Categoria.objects.create(usuario=dueno, nombre=nombre, descripcion=desc) for nombre, desc in [
        ('Salud', 'Ejercicio, alimentación y descanso.'),
        ('Estudio', 'Cursos, idiomas y materias de la universidad.'),
        ('Finanzas', 'Control de gastos y presupuesto.'),
    ]}

    def objetivo(titulo, cat, estado, prioridad, inicio_hace, meta_en):
        return Objetivo.objects.create(
            usuario=dueno, categoria=cats[cat], titulo=titulo, estado=estado, prioridad=prioridad,
            fecha_inicio=momento(inicio_hace), fecha_meta=momento(-meta_en, 23, 0))

    def actividad(obj, titulo, dias, hora, minutos, registro=None, nota=''):
        inicio = momento(dias, hora)
        a = Actividad.objects.create(objetivo=obj, titulo=titulo, nota=nota, completada=bool(registro),
                                     fecha_inicio=inicio, fecha_fin=inicio + timedelta(minutes=minutos))
        if registro:
            tipo, esperado, valor, calificacion = registro
            RegistroRendimiento.objects.create(actividad=a, tipo_indicador=tipo, esperado=esperado, valor=valor,
                                               calificacion=calificacion, fecha=inicio.date())
        return a

    correr = objetivo('Correr 10K antes de diciembre', 'Salud', 'en_progreso', 'alta', 60, 25)
    # Ocho semanas de entrenamiento: la distancia esperada sube y lo obtenido la sigue de cerca
    sesiones = [(55, 3.0, 2.8, 3), (52, 3.0, 3.2, 4), (48, 3.5, 3.4, 3), (45, 3.5, 3.9, 4), (41, 4.0, None, 0),
                (38, 4.0, 4.1, 4), (34, 4.5, 4.2, 3), (31, 4.5, 4.8, 4), (27, 5.0, 5.0, 4), (24, 5.0, None, 0),
                (20, 5.5, 5.3, 4), (17, 5.5, 5.9, 5), (13, 6.0, 5.8, 4), (10, 6.0, 6.3, 5), (5, 6.5, 6.4, 4),
                (3, 7.0, 7.2, 5), (1, 7.0, 7.1, 5)]
    for dias, esperado, valor, calificacion in sesiones:
        registro = ('distancia', esperado, valor, calificacion) if valor else None
        actividad(correr, f'Trote {esperado:g} km', dias, 7, 50, registro)
    actividad(correr, 'Series de velocidad 6x400m', 0, 7, 45)            # se completa en el flujo 4
    actividad(correr, 'Fondo largo 8 km', -2, 7, 70)
    actividad(correr, 'Trote 7 km', -5, 7, 50)

    ingles = objetivo('Terminar curso de inglés B2', 'Estudio', 'en_progreso', 'media', 70, 9)
    for dias, valor, calificacion in [(54, 45, 3), (47, 60, 4), (40, 50, 3), (33, None, 0), (26, 65, 4),
                                      (19, 55, 4), (12, 70, 5), (4, 60, 4), (2, 75, 5)]:
        registro = ('tiempo', 60, valor, calificacion) if valor else None
        actividad(ingles, 'Sesión de estudio', dias, 19, 60, registro)
    actividad(ingles, 'Examen de práctica', -3, 19, 90)

    gastos = objetivo('Gastar menos de $4,000 al mes en comida', 'Finanzas', 'en_progreso', 'media', 40, 40)
    for dias, valor in [(36, 1), (29, 1), (22, None), (15, 1), (8, 1)]:
        registro = ('repeticiones', 1, valor, 4) if valor else None
        actividad(gastos, 'Revisar gastos de la semana', dias, 20, 30, registro)
    actividad(gastos, 'Revisar gastos de la semana', -6, 20, 30)

    objetivo('Leer 12 libros en el año', 'Estudio', 'pendiente', 'baja', 20, 45)

    fondo = MetaAhorro.objects.create(usuario=dueno, nombre='Fondo de emergencia', monto_meta=50000,
                                      fecha_meta=date(hoy.year, 12, 31))
    for dias, tipo, monto, nota in [(80, 'deposito', 15000, 'Ahorro inicial'), (66, 'deposito', 4000, 'Quincena'),
                                    (52, 'deposito', 4000, 'Quincena'), (45, 'retiro', 2500, 'Reparación del auto'),
                                    (38, 'deposito', 4000, 'Quincena'), (24, 'deposito', 4000, 'Quincena'),
                                    (10, 'deposito', 4000, 'Quincena')]:
        Movimiento.objects.create(meta=fondo, tipo=tipo, monto=monto, fecha=hoy - timedelta(days=dias), nota=nota)
    viaje = MetaAhorro.objects.create(usuario=dueno, nombre='Viaje de fin de año', monto_meta=12000,
                                      fecha_meta=date(hoy.year, 12, 15))
    for dias, monto in [(60, 3000), (40, 3000), (20, 3000)]:
        Movimiento.objects.create(meta=viaje, tipo='deposito', monto=monto, fecha=hoy - timedelta(days=dias),
                                  nota='Aportación mensual')
    MetaAhorro.objects.create(usuario=dueno, nombre='Laptop nueva', monto_meta=25000,
                              fecha_meta=date(hoy.year + 1, 3, 1))
    return correr


def para_input(momento):
    return timezone.localtime(momento).strftime('%Y-%m-%dT%H:%M')


def recorrer(base, correr):
    from playwright.sync_api import expect, sync_playwright

    SALIDA.mkdir(parents=True, exist_ok=True)
    for viejo in SALIDA.glob('*.png'):
        viejo.unlink()

    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_context(viewport=TAMANO, locale='es-MX', timezone_id=settings.TIME_ZONE).new_page()

        def foto(nombre, completa=False, espera=600):
            pagina.wait_for_timeout(espera)
            if completa:
                # El sidebar mide 100vh: se agranda la ventana a la altura de la página para que no se corte
                alto = pagina.evaluate('document.documentElement.scrollHeight')
                pagina.set_viewport_size({'width': TAMANO['width'], 'height': max(TAMANO['height'], alto)})
                pagina.wait_for_timeout(500)
            pagina.screenshot(path=SALIDA / f'{nombre}.png')
            pagina.set_viewport_size(TAMANO)
            print('  ', nombre)

        pagina.goto(base + '/user/login/')
        pagina.fill('#id_username', 'hector')
        pagina.fill('#id_password', CLAVE)
        pagina.get_by_role('button', name='Entrar').click()
        expect(pagina.locator('.fc-event').first).to_be_visible()

        # ---------- F1 · crear categoría ----------
        pagina.get_by_role('link', name='Categorías').click()
        foto('F1_1_lista_de_categorias')
        pagina.get_by_role('link', name='+ Nueva categoría').click()
        pagina.fill('#id_nombre', 'Trabajo')
        pagina.fill('#id_descripcion', 'Entregables y pendientes de las estadías.')
        foto('F1_2_formulario_de_categoria')
        pagina.get_by_role('button', name='Guardar categoría').click()
        expect(pagina.get_by_text('Entregables y pendientes de las estadías.')).to_be_visible()
        foto('F1_3_categoria_creada')

        # ---------- F2 · crear objetivo ----------
        hoy = timezone.localtime().replace(hour=9, minute=0, second=0, microsecond=0)
        pagina.get_by_role('link', name='Objetivos').click()
        pagina.locator('.js-nuevo-objetivo').first.click()
        pagina.fill('#id_nuevo-titulo', 'Entregar el reporte final de estadías')
        pagina.select_option('#id_nuevo-categoria', label='Trabajo')
        pagina.select_option('#id_nuevo-estado', label='En progreso')
        pagina.select_option('#id_nuevo-prioridad', label='Alta')
        pagina.fill('#id_nuevo-fecha_inicio', para_input(hoy))
        pagina.fill('#id_nuevo-fecha_meta', para_input(hoy + timedelta(days=40)))
        foto('F2_1_formulario_de_objetivo')
        pagina.get_by_role('button', name='Guardar objetivo').click()
        expect(pagina.get_by_role('heading', name='Entregar el reporte final de estadías')).to_be_visible()
        foto('F2_2_lista_de_objetivos', completa=True)

        # ---------- F3 · crear actividad ----------
        manana = hoy + timedelta(days=1)
        pagina.get_by_role('link', name='Actividades', exact=True).click()
        pagina.get_by_role('button', name='+ Nueva actividad').click()
        pagina.fill('#id_titulo', 'Redactar la introducción del reporte')
        pagina.select_option('#id_objetivo', label='Entregar el reporte final de estadías')
        pagina.fill('#id_fecha_inicio', para_input(manana.replace(hour=16)))
        pagina.fill('#id_fecha_fin', para_input(manana.replace(hour=18)))
        pagina.fill('#id_nota', 'Revisar la guía del asesor antes de empezar.')
        foto('F3_1_formulario_de_actividad')
        pagina.get_by_role('button', name='Guardar actividad').click()
        pagina.get_by_role('link', name='Calendario').click()
        expect(pagina.locator('.fc-event', has_text='Redactar la introducción').first).to_be_visible()
        foto('F3_2_actividad_en_el_calendario', espera=900)
        pagina.get_by_role('button', name='Semana').click()
        foto('F3_3_vista_semanal', espera=900)

        # ---------- F4 · registrar rendimiento ----------
        pendiente = correr.actividades.get(titulo='Series de velocidad 6x400m')
        pagina.goto(base + pendiente.get_absolute_url())
        pagina.select_option('#id_tipo_indicador', label='Distancia (km)')
        pagina.fill('#id_esperado', '7.5')
        pagina.fill('#id_valor', '7.8')
        pagina.fill('#id_calificacion', '5')
        foto('F4_1_registro_de_rendimiento')
        pagina.get_by_role('button', name='Guardar y completar').click()
        pagina.goto(base + correr.get_absolute_url())
        expect(pagina.locator('canvas.grafica-rendimiento')).to_be_visible()
        foto('F4_2_objetivo_con_su_grafica', completa=True, espera=1500)

        # ---------- F5 · ahorro ----------
        pagina.get_by_role('link', name='Ahorro').click()
        foto('F5_1_metas_de_ahorro')
        pagina.get_by_role('link', name='Ver detalle').nth(1).click()   # ordenadas por fecha meta: viaje, fondo, laptop
        pagina.get_by_role('link', name='+ Registrar movimiento').click()
        pagina.select_option('#id_tipo', label='Retiro')
        pagina.fill('#id_monto', '40000')
        pagina.get_by_role('button', name='Guardar movimiento').click()
        expect(pagina.get_by_text('es mayor a lo ahorrado')).to_be_visible()
        foto('F5_2_retiro_rechazado')
        pagina.select_option('#id_tipo', label='Depósito')
        pagina.fill('#id_monto', '4000')
        pagina.fill('#id_nota', 'Quincena')
        pagina.get_by_role('button', name='Guardar movimiento').click()
        expect(pagina.get_by_role('heading', name='Movimientos')).to_be_visible()
        foto('F5_3_deposito_registrado', completa=True)

        # ---------- F6 · estadísticas ----------
        pagina.get_by_role('link', name='Estadísticas').click()
        expect(pagina.locator('#grafica-semanas')).to_be_visible()
        foto('F6_1_dashboard_de_estadisticas', completa=True, espera=1500)

        navegador.close()


def main():
    runner = DiscoverRunner(verbosity=0, interactive=False)
    bases = runner.setup_databases()
    try:
        correr = cargar_datos()
        servidor = LiveServerThread('localhost', StaticFilesHandler, port=0)
        servidor.daemon = True
        servidor.start()
        servidor.is_ready.wait()
        if servidor.error:
            raise servidor.error
        try:
            recorrer(f'http://localhost:{servidor.port}', correr)
        finally:
            servidor.terminate()
    finally:
        # Los hilos del servidor de prueba pueden dejar una sesión abierta; se cierra antes de borrar la base
        from django.db import connection, connections
        nombre = connection.settings_dict['NAME']
        connections.close_all()
        with connection._nodb_cursor() as cursor:
            cursor.execute('SELECT pg_terminate_backend(pid) FROM pg_stat_activity '
                           'WHERE datname = %s AND pid <> pg_backend_pid()', [nombre])
        runner.teardown_databases(bases)


if __name__ == '__main__':
    main()
