"""Flujos de punta a punta con Playwright; cada flujo se graba en video como evidencia de pruebas.

Correr:     python manage.py test e2e
Evidencia:  docs/evidencias/e2e/<flujo>.webm y <flujo>.png (estado final)

Cada flujo arranca con la base de prueba vacía; los datos previos que no son parte del flujo se crean con el ORM.
"""
import os
import shutil
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.utils import timezone
from playwright.sync_api import expect, sync_playwright

from ahorro.models import MetaAhorro, Movimiento
from core.models import Actividad, Categoria, Objetivo, RegistroRendimiento

EVIDENCIAS = settings.BASE_DIR.parent / 'docs' / 'evidencias' / 'e2e'
TAMANO = {'width': 1280, 'height': 800}
PAUSA_MS = 300  # entre acciones, para que el video se pueda seguir
CLAVE = 'Rendimiento-2026'


def para_input(momento):
    """Fecha y hora en el formato de <input type="datetime-local">, en hora local."""
    return timezone.localtime(momento).strftime('%Y-%m-%dT%H:%M')


@tag('e2e')
class FlujosE2E(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        # Playwright síncrono corre un event loop en este hilo; sin esto Django bloquea el ORM
        os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
        super().setUpClass()
        EVIDENCIAS.mkdir(parents=True, exist_ok=True)
        cls.playwright = sync_playwright().start()
        cls.navegador = cls.playwright.chromium.launch(slow_mo=PAUSA_MS)

    @classmethod
    def tearDownClass(cls):
        cls.navegador.close()
        cls.playwright.stop()
        shutil.rmtree(EVIDENCIAS / 'tmp', ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.contexto = self.navegador.new_context(
            viewport=TAMANO,
            record_video_dir=EVIDENCIAS / 'tmp',
            record_video_size=TAMANO,
            locale='es-MX',
            timezone_id=settings.TIME_ZONE,
        )
        self.pagina = self.contexto.new_page()

    def tearDown(self):
        # Se guarda aunque el flujo falle: el video muestra hasta dónde llegó
        nombre = self._testMethodName.removeprefix('test_')
        self.pagina.wait_for_timeout(1000)
        self.pagina.screenshot(path=EVIDENCIAS / f'{nombre}.png')
        video = self.pagina.video
        self.contexto.close()
        video.save_as(EVIDENCIAS / f'{nombre}.webm')
        video.delete()

    # ---------- ayudas ----------
    def url(self, ruta):
        return self.live_server_url + ruta

    def usuario(self, nombre='hector'):
        return User.objects.create_user(nombre, password=CLAVE)

    def iniciar_sesion(self, nombre='hector'):
        p = self.pagina
        p.goto(self.url('/user/login/'))
        p.fill('#id_username', nombre)
        p.fill('#id_password', CLAVE)
        p.get_by_role('button', name='Entrar').click()
        expect(p.get_by_role('heading', name='Calendario')).to_be_visible()

    def objetivo(self, usuario, titulo, dias_meta=30, estado=Objetivo.Estado.PENDIENTE, categoria='Salud'):
        ahora = timezone.now()
        cat, _ = Categoria.objects.get_or_create(usuario=usuario, nombre=categoria)
        return Objetivo.objects.create(
            usuario=usuario, categoria=cat, titulo=titulo, estado=estado,
            fecha_inicio=ahora - timedelta(days=30), fecha_meta=ahora + timedelta(days=dias_meta),
        )

    def actividad(self, objetivo, titulo, horas_desde_ahora=-2, completada=False):
        fin = timezone.now() + timedelta(hours=horas_desde_ahora)
        return Actividad.objects.create(
            objetivo=objetivo, titulo=titulo, completada=completada,
            fecha_inicio=fin - timedelta(hours=1), fecha_fin=fin,
        )

    # ---------- flujos ----------
    def test_01_registro_e_inicio_de_sesion(self):
        """RF1: sin sesión se redirige al login; registro, cierre de sesión, contraseña incorrecta y entrada."""
        p = self.pagina
        p.goto(self.url('/ahorro/'))
        expect(p).to_have_url(self.url('/user/login/?next=/ahorro/'))

        p.get_by_role('link', name='Regístrate').click()
        p.fill('#id_username', 'hector')
        p.fill('#id_password1', CLAVE)
        p.fill('#id_password2', CLAVE)
        p.get_by_role('button', name='Crear cuenta').click()
        expect(p.get_by_role('heading', name='Calendario')).to_be_visible()

        p.get_by_role('button', name='Cerrar sesión').click()
        p.fill('#id_username', 'hector')
        p.fill('#id_password', 'otra-clave')
        p.get_by_role('button', name='Entrar').click()
        expect(p.get_by_text('Usuario o contraseña incorrectos.')).to_be_visible()

        p.fill('#id_password', CLAVE)
        p.get_by_role('button', name='Entrar').click()
        expect(p.get_by_role('heading', name='Calendario')).to_be_visible()

    def test_02_categoria_objetivo_y_actividad(self):
        """RF3, RF5, RF8, RF12: alta de categoría, objetivo y actividad; la actividad aparece en el calendario."""
        self.usuario()
        self.iniciar_sesion()
        p = self.pagina

        p.get_by_role('link', name='Categorías').click()
        p.get_by_role('link', name='+ Nueva categoría').click()
        p.fill('#id_nombre', 'Salud')
        p.fill('#id_descripcion', 'Ejercicio, alimentación y descanso.')
        p.get_by_role('button', name='Guardar categoría').click()
        expect(p.get_by_text('Ejercicio, alimentación y descanso.')).to_be_visible()

        hoy = timezone.localtime().replace(hour=7, minute=0)
        p.get_by_role('link', name='Objetivos').click()
        p.locator('.js-nuevo-objetivo').first.click()
        p.fill('#id_nuevo-titulo', 'Correr 10K antes de diciembre')
        p.select_option('#id_nuevo-categoria', label='Salud')
        p.select_option('#id_nuevo-prioridad', label='Alta')
        p.fill('#id_nuevo-fecha_inicio', para_input(hoy - timedelta(days=10)))
        p.fill('#id_nuevo-fecha_meta', para_input(hoy + timedelta(days=30)))
        p.get_by_role('button', name='Guardar objetivo').click()
        expect(p.get_by_role('heading', name='Correr 10K antes de diciembre')).to_be_visible()

        p.get_by_role('link', name='Actividades', exact=True).click()
        p.get_by_role('button', name='+ Nueva actividad').click()
        p.fill('#id_titulo', 'Series de velocidad 8x400m')
        p.select_option('#id_objetivo', label='Correr 10K antes de diciembre')
        p.fill('#id_fecha_inicio', para_input(hoy))
        p.fill('#id_fecha_fin', para_input(hoy + timedelta(hours=1)))
        p.get_by_role('button', name='Guardar actividad').click()
        expect(p.get_by_text('Series de velocidad 8x400m')).to_be_visible()

        p.get_by_role('link', name='Calendario').click()
        expect(p.locator('.fc-event', has_text='Series de velocidad 8x400m')).to_be_visible()

    def test_03_registro_de_rendimiento(self):
        """RF10, RF13, RF14: registrar el rendimiento completa la actividad y alimenta la gráfica del objetivo."""
        yo = self.usuario()
        objetivo = self.objetivo(yo, 'Correr 10K antes de diciembre')
        self.actividad(objetivo, 'Trote suave 5 km')
        self.iniciar_sesion()
        p = self.pagina

        p.get_by_role('link', name='Objetivos').click()
        p.get_by_role('link', name='Ver detalle').click()
        expect(p.get_by_text('Sin registro')).to_be_visible()

        p.get_by_role('link', name='Trote suave 5 km').click()
        p.select_option('#id_tipo_indicador', label='Distancia (km)')
        p.fill('#id_esperado', '5')
        p.fill('#id_valor', '5.6')
        p.fill('#id_calificacion', '4')
        p.get_by_role('button', name='Guardar y completar').click()
        expect(p.get_by_role('heading', name='Calendario')).to_be_visible()

        p.goto(self.url(objetivo.get_absolute_url()))
        expect(p.get_by_text('Esperado 5 · Obtenido 5.6')).to_be_visible()
        expect(p.locator('.actividad-estado', has_text='Completada')).to_be_visible()
        expect(p.locator('canvas.grafica-rendimiento')).to_be_visible()

    def test_04_editar_y_eliminar(self):
        """RF4, RF6, RF9: editar un objetivo, eliminar una actividad y eliminar una categoría con aviso de cascada."""
        yo = self.usuario()
        objetivo = self.objetivo(yo, 'Correr 10K')
        self.actividad(objetivo, 'Series de velocidad')
        self.iniciar_sesion()
        p = self.pagina

        p.goto(self.url(objetivo.get_absolute_url()))
        p.get_by_role('link', name='Editar').click()
        p.fill('#id_titulo', 'Correr 21K en marzo')
        p.get_by_role('button', name='Guardar cambios').click()
        expect(p.get_by_role('heading', name='Correr 21K en marzo')).to_be_visible()

        p.get_by_role('link', name='Series de velocidad').click()
        p.get_by_role('link', name='Eliminar').click()
        expect(p.get_by_text('¿Seguro que quieres eliminar «Series de velocidad»?')).to_be_visible()
        p.get_by_role('button', name='Eliminar').click()
        expect(p.get_by_text('No hay actividades todavía.')).to_be_visible()

        p.get_by_role('link', name='Categorías').click()
        p.get_by_role('link', name='Eliminar').click()
        expect(p.get_by_text('También se eliminará 1 objetivo')).to_be_visible()
        p.get_by_role('button', name='Eliminar').click()
        expect(p.get_by_text('No hay categorías todavía.')).to_be_visible()

    def test_05_datos_por_usuario(self):
        """RF2: un usuario no ve ni puede abrir los objetivos de otro."""
        ana = self.usuario('ana')
        ajeno = self.objetivo(ana, 'Plan de Ana')
        self.usuario()
        self.iniciar_sesion()
        p = self.pagina

        p.get_by_role('link', name='Objetivos').click()
        expect(p.get_by_text('Plan de Ana')).to_have_count(0)

        respuesta = p.goto(self.url(ajeno.get_absolute_url()))
        self.assertEqual(respuesta.status, 404)

    def test_06_vencimiento_de_objetivos(self):
        """RF7: un objetivo pendiente con fecha meta pasada aparece como vencido y en su filtro."""
        yo = self.usuario()
        self.objetivo(yo, 'Terminar curso de inglés B2', dias_meta=-1)
        self.objetivo(yo, 'Leer 12 libros', dias_meta=40)
        self.iniciar_sesion()
        p = self.pagina

        p.get_by_role('link', name='Objetivos').click()
        tarjeta = p.locator('.card-objetivo', has_text='Terminar curso de inglés B2')
        expect(tarjeta.locator('.card-objetivo-estado')).to_have_text('Vencido')

        p.get_by_role('link', name='Vencidos').click()
        expect(p.get_by_text('Terminar curso de inglés B2')).to_be_visible()
        expect(p.get_by_text('Leer 12 libros')).to_have_count(0)

    def test_07_ahorro(self):
        """RF16: meta de ahorro, depósito, retiro mayor a lo ahorrado (rechazado) y retiro válido."""
        self.usuario()
        self.iniciar_sesion()
        p = self.pagina

        p.get_by_role('link', name='Ahorro').click()
        p.get_by_role('link', name='+ Nueva meta').click()
        p.fill('#id_nombre', 'Fondo de emergencia')
        p.fill('#id_monto_meta', '50000')
        p.fill('#id_fecha_meta', '2026-12-31')
        p.get_by_role('button', name='Guardar meta').click()
        expect(p.get_by_role('heading', name='Fondo de emergencia')).to_be_visible()

        p.get_by_role('link', name='+ Registrar movimiento').click()
        p.fill('#id_monto', '20000')
        p.fill('#id_nota', 'Ahorro inicial')
        p.get_by_role('button', name='Guardar movimiento').click()
        expect(p.locator('.conteo-actividades')).to_contain_text('$20,000.00')

        p.get_by_role('link', name='+ Registrar movimiento').click()
        p.select_option('#id_tipo', label='Retiro')
        p.fill('#id_monto', '25000')
        p.get_by_role('button', name='Guardar movimiento').click()
        expect(p.get_by_text('El retiro ($25,000.00) es mayor a lo ahorrado ($20,000.00).')).to_be_visible()

        p.fill('#id_monto', '3000')
        p.fill('#id_nota', 'Reparación del auto')
        p.get_by_role('button', name='Guardar movimiento').click()
        expect(p.locator('.conteo-actividades')).to_contain_text('$17,000.00')
        expect(p.locator('.conteo-actividades')).to_contain_text('34 %')

        p.get_by_role('link', name='← Ahorro').click()
        expect(p.get_by_text('Faltan $33,000.00')).to_be_visible()

    def test_08_dashboard_de_estadisticas(self):
        """RF15: el dashboard muestra cumplimiento, racha, gráfica semanal, categorías, logro y ahorro."""
        yo = self.usuario()
        objetivo = self.objetivo(yo, 'Correr 10K antes de diciembre')
        hoy = timezone.localdate()
        for dias, valor in [(1, 4.5), (0, 5.6)]:
            actividad = self.actividad(objetivo, 'Trote', horas_desde_ahora=-24 * dias - 1, completada=True)
            RegistroRendimiento.objects.create(
                actividad=actividad, tipo_indicador='distancia', esperado=5, valor=valor,
                calificacion=4, fecha=hoy - timedelta(days=dias),
            )
        self.actividad(objetivo, 'Series', horas_desde_ahora=-30)  # vencida
        meta = MetaAhorro.objects.create(usuario=yo, nombre='Fondo', monto_meta=10000, fecha_meta=date(2026, 12, 31))
        Movimiento.objects.create(meta=meta, tipo='deposito', monto=2500)
        self.iniciar_sesion()
        p = self.pagina

        p.get_by_role('link', name='Estadísticas').click()
        tarjetas = p.locator('.kpis')
        expect(tarjetas).to_contain_text('67 %')
        expect(tarjetas).to_contain_text('2 de 3')
        expect(tarjetas).to_contain_text('Mejor racha: 2 días')
        expect(tarjetas).to_contain_text('$2,500.00 de $10,000.00')
        expect(p.locator('#grafica-semanas')).to_be_visible()
        expect(p.locator('.medidor', has_text='Distancia (km)')).to_contain_text('101 %')

        p.get_by_text('Ver como tabla').click()
        expect(p.locator('.tabla-datos table')).to_be_visible()
