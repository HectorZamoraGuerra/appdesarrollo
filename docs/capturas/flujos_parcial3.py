"""Capturas paso a paso de los flujos principales para el Parcial 3.

Levanta el sistema sobre una base de datos de prueba temporal (no toca la base real), carga datos de ejemplo
con fechas relativas a hoy (8 semanas de actividades, registros de rendimiento y ahorro) y recorre cada flujo
en el navegador como lo haría el usuario, tomando una captura en cada paso.

Uso (desde la raíz del repo):  python docs/capturas/flujos_parcial3.py
Salida: docs/capturas/parcial3/flujos/F<n>_collage.png (pasos numerados) y F6_estadisticas.png
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
    actividad(correr, 'Series de velocidad 6x400m', -1, 7, 45)           # se completa en el flujo 4
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


COLLAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
* { box-sizing: border-box; margin: 0; }
body { font-family: 'Noto Sans', 'Segoe UI', system-ui, sans-serif; background: #e6e8ec; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; padding: 18px; width: 1640px; }
.paso { background: #fff; border: 1px solid #c9cdd4; border-radius: 8px; overflow: hidden; }
.cab { display: flex; align-items: center; gap: 12px; padding: 12px 16px; font-size: 19px; color: #1c2029; }
.num { flex: none; width: 34px; height: 34px; border-radius: 50%; background: #1c2029; color: #fff;
       display: grid; place-items: center; font-weight: 700; font-size: 17px; }
.paso img { display: block; width: 100%; border-top: 1px solid #dcdfe4; }
</style></head><body><div class="grid">{pasos}</div></body></html>"""


def recorrer(base, correr):
    import base64

    from playwright.sync_api import expect, sync_playwright

    SALIDA.mkdir(parents=True, exist_ok=True)
    for viejo in SALIDA.glob('*.png'):
        viejo.unlink()
    pasos = {}  # flujo -> [(archivo, texto)]

    with sync_playwright() as p:
        navegador = p.chromium.launch(args=['--lang=es-MX'])
        pagina = navegador.new_context(viewport=TAMANO, locale='es-MX', timezone_id=settings.TIME_ZONE).new_page()

        def paso(flujo, texto, *marcas, completa=False, espera=600):
            """Captura del paso con un recuadro rojo en los elementos de `marcas`."""
            pagina.wait_for_timeout(espera)
            for marca in marcas:
                marca.first.evaluate("e => { e.style.outline = '4px solid #e5484d'; e.style.outlineOffset = '3px'; }")
            if completa:
                alto = pagina.evaluate('document.documentElement.scrollHeight')
                pagina.set_viewport_size({'width': TAMANO['width'], 'height': max(TAMANO['height'], alto)})
                pagina.wait_for_timeout(500)
            n = len(pasos.setdefault(flujo, [])) + 1
            archivo = SALIDA / f'{flujo}_{n}.png'
            pagina.screenshot(path=archivo)
            pagina.set_viewport_size(TAMANO)
            for marca in marcas:
                marca.first.evaluate("e => { e.style.outline = ''; e.style.outlineOffset = ''; }")
            pasos[flujo].append((archivo, texto))
            print('  ', archivo.name, texto)

        pagina.goto(base + '/user/login/')
        pagina.fill('#id_username', 'hector')
        pagina.fill('#id_password', CLAVE)
        pagina.get_by_role('button', name='Entrar').click()
        expect(pagina.locator('.fc-event').first).to_be_visible()
        hoy = timezone.localtime().replace(hour=9, minute=0, second=0, microsecond=0)
        manana = hoy + timedelta(days=1)

        # ---------- F1 · crear categoría ----------
        pagina.get_by_role('link', name='Categorías').click()
        paso('F1', 'Se entra a Categorías y se elige «Nueva categoría».', pagina.get_by_role('link', name='+ Nueva categoría'))
        pagina.get_by_role('link', name='+ Nueva categoría').click()
        pagina.fill('#id_nombre', 'Trabajo')
        pagina.fill('#id_descripcion', 'Entregables y pendientes de las estadías.')
        paso('F1', 'Se escriben el nombre y la descripción.', pagina.locator('#form-categoria'))
        pagina.get_by_role('button', name='Guardar categoría').click()
        nueva = pagina.locator('.actividad', has_text='Trabajo')
        expect(nueva).to_be_visible()
        paso('F1', 'Al guardar, la categoría aparece en la lista.', nueva)
        pagina.get_by_role('link', name='Objetivos').click()
        pagina.locator('.js-nuevo-objetivo').first.click()
        pagina.select_option('#id_nuevo-categoria', label='Trabajo')
        paso('F1', 'Ya se puede elegir al crear un objetivo.', pagina.locator('#id_nuevo-categoria'))

        # ---------- F2 · crear objetivo ----------
        pagina.fill('#id_nuevo-titulo', 'Entregar el reporte final de estadías')
        pagina.select_option('#id_nuevo-categoria', label='Trabajo')
        pagina.select_option('#id_nuevo-estado', label='En progreso')
        pagina.select_option('#id_nuevo-prioridad', label='Alta')
        pagina.fill('#id_nuevo-fecha_inicio', para_input(hoy))
        pagina.fill('#id_nuevo-fecha_meta', para_input(hoy + timedelta(days=40)))
        paso('F2', 'En Objetivos se abre el formulario y se llenan los datos.', pagina.locator('#form-objetivo'))
        pagina.get_by_role('button', name='Guardar objetivo').click()
        tarjeta = pagina.locator('.card-objetivo', has_text='Entregar el reporte final de estadías')
        expect(tarjeta).to_be_visible()
        tarjeta.scroll_into_view_if_needed()
        paso('F2', 'El objetivo aparece en la lista con su categoría y prioridad.', tarjeta)
        tarjeta.get_by_role('link', name='Ver detalle').click()
        paso('F2', 'Su detalle queda listo para agregarle actividades.',
             pagina.get_by_role('heading', name='Entregar el reporte final de estadías'))
        pagina.get_by_role('link', name='Categorías').click()
        paso('F2', 'La categoría Trabajo ya cuenta 1 objetivo.', pagina.locator('.actividad', has_text='Trabajo'))

        # ---------- F3 · crear actividad ----------
        pagina.get_by_role('link', name='Actividades', exact=True).click()
        pagina.get_by_role('button', name='+ Nueva actividad').click()
        pagina.fill('#id_titulo', 'Redactar la introducción del reporte')
        pagina.select_option('#id_objetivo', label='Entregar el reporte final de estadías')
        pagina.fill('#id_fecha_inicio', para_input(manana.replace(hour=16)))
        pagina.fill('#id_fecha_fin', para_input(manana.replace(hour=18)))
        pagina.fill('#id_nota', 'Revisar la guía del asesor antes de empezar.')
        paso('F3', 'En Actividades se llena el formulario y se liga al objetivo.', pagina.locator('#form-actividad'))
        pagina.get_by_role('button', name='Guardar actividad').click()
        pagina.get_by_role('link', name='Calendario').click()
        evento = pagina.locator('.fc-event', has_text='Redactar la introducción')
        expect(evento.first).to_be_visible()
        paso('F3', 'La actividad aparece en el calendario, en su día.', evento, espera=900)
        pagina.get_by_role('button', name='Semana').click()
        pagina.locator('.fc-event', has_text='Redactar la introducción').first.scroll_into_view_if_needed()
        paso('F3', 'En la vista semanal se ve en su horario.',
             pagina.locator('.fc-event', has_text='Redactar la introducción'), espera=900)
        pagina.locator('.fc-event', has_text='Redactar la introducción').first.click()
        expect(pagina.get_by_role('heading', name='Redactar la introducción del reporte')).to_be_visible()
        paso('F3', 'Al abrirla se ven su objetivo, horario y nota.', pagina.locator('.modal-body'))

        # ---------- F4 · registrar rendimiento ----------
        pagina.goto(base + correr.get_absolute_url())
        paso('F4', 'Antes: el objetivo tiene actividades pendientes y su gráfica.',
             pagina.locator('.conteo-actividades'))
        pagina.get_by_role('link', name='Calendario').click()
        sesion = pagina.locator('.fc-event', has_text='Series de velocidad')
        expect(sesion.first).to_be_visible()
        paso('F4', 'En el calendario se abre la actividad realizada.', sesion, espera=900)
        sesion.first.click()
        pagina.select_option('#id_tipo_indicador', label='Distancia (km)')
        pagina.fill('#id_esperado', '7.5')
        pagina.fill('#id_valor', '7.8')
        pagina.fill('#id_calificacion', '5')
        paso('F4', 'Se anotan lo esperado, lo obtenido y la satisfacción.', pagina.locator('#form-registro .modal-body'))
        pagina.get_by_role('button', name='Guardar y completar').click()
        pagina.goto(base + correr.get_absolute_url())
        expect(pagina.locator('canvas.grafica-rendimiento')).to_be_visible()
        paso('F4', 'Después: una completada más y un punto nuevo en la gráfica.',
             pagina.locator('.conteo-actividades'), pagina.locator('.panel-grafica'), espera=1500)

        # ---------- F5 · ahorro ----------
        pagina.get_by_role('link', name='Ahorro').click()
        meta = pagina.locator('.card-objetivo', has_text='Fondo de emergencia')
        paso('F5', 'En Ahorro se elige la meta.', meta)
        meta.get_by_role('link', name='Ver detalle').click()
        paso('F5', 'Antes: lo ahorrado, lo que falta y el avance.', pagina.locator('.conteo-actividades'))
        pagina.get_by_role('link', name='+ Registrar movimiento').click()
        pagina.fill('#id_monto', '4000')
        pagina.fill('#id_nota', 'Quincena')
        paso('F5', 'Se registra un depósito.', pagina.locator('#form-movimiento'))
        pagina.get_by_role('button', name='Guardar movimiento').click()
        expect(pagina.get_by_role('heading', name='Movimientos')).to_be_visible()
        paso('F5', 'Después: el saldo y el avance se actualizan y el depósito queda en la lista.',
             pagina.locator('.conteo-actividades'), pagina.locator('.lista-actividades .actividad'))

        # ---------- estadísticas (resultado de todo lo anterior) ----------
        pagina.get_by_role('link', name='Estadísticas').click()
        expect(pagina.locator('#grafica-semanas')).to_be_visible()
        pagina.wait_for_timeout(1500)
        alto = pagina.evaluate('document.documentElement.scrollHeight')
        pagina.set_viewport_size({'width': TAMANO['width'], 'height': max(TAMANO['height'], alto)})
        pagina.wait_for_timeout(500)
        pagina.screenshot(path=SALIDA / 'F6_estadisticas.png')
        print('   F6_estadisticas.png')

        # ---------- collages ----------
        lienzo = navegador.new_page(device_scale_factor=1)
        for flujo, lista in pasos.items():
            tarjetas = ''.join(
                f'<div class="paso"><div class="cab"><span class="num">{n}</span>{texto}</div>'
                f'<img src="data:image/png;base64,{base64.b64encode(archivo.read_bytes()).decode()}"></div>'
                for n, (archivo, texto) in enumerate(lista, 1))
            lienzo.set_content(COLLAGE.replace('{pasos}', tarjetas), wait_until='load')
            lienzo.locator('.grid').screenshot(path=SALIDA / f'{flujo}_collage.png')
            for archivo, _ in lista:
                archivo.unlink()
            print('  ', f'{flujo}_collage.png')
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
