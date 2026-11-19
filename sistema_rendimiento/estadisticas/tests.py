from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Actividad, Categoria, Objetivo, RegistroRendimiento

from . import calculos


class CalculosTests(TestCase):
    def setUp(self):
        usuario = User.objects.create_user('demo', password='x')
        self.salud = Categoria.objects.create(usuario=usuario, nombre='Salud')
        self.estudio = Categoria.objects.create(usuario=usuario, nombre='Estudio')
        self.ahora = timezone.now()
        self.correr = self.objetivo('Correr 10K', self.salud, dias_meta=30)
        self.ingles = self.objetivo('Inglés B2', self.estudio, dias_meta=60)
        self.usuario = usuario

    def objetivo(self, titulo, categoria, dias_meta, estado=Objetivo.Estado.PENDIENTE):
        return Objetivo.objects.create(
            usuario=categoria.usuario, categoria=categoria, titulo=titulo, estado=estado,
            fecha_inicio=self.ahora - timedelta(days=30), fecha_meta=self.ahora + timedelta(days=dias_meta),
        )

    def actividad(self, objetivo, dias, completada=False):
        """Actividad de una hora que termina hace `dias` días (negativo: en el futuro)."""
        fin = self.ahora - timedelta(days=dias)
        return Actividad.objects.create(
            objetivo=objetivo, titulo='Sesión', completada=completada,
            fecha_inicio=fin - timedelta(hours=1), fecha_fin=fin,
        )

    def registro(self, fecha, tipo='tiempo', esperado=30, valor=30, calificacion=3):
        return RegistroRendimiento.objects.create(
            actividad=self.actividad(self.correr, 1, completada=True), tipo_indicador=tipo,
            esperado=esperado, valor=valor, calificacion=calificacion, fecha=fecha,
        )

    def test_cumplimiento_no_cuenta_pendientes_futuras(self):
        self.actividad(self.correr, 3, completada=True)
        self.actividad(self.correr, 2, completada=True)
        self.actividad(self.correr, 1)       # vencida
        self.actividad(self.correr, -2)      # pendiente, todavía no cuenta
        datos = calculos.cumplimiento(Actividad.objects.all())
        self.assertEqual((datos['completadas'], datos['vencidas'], datos['total']), (2, 1, 3))
        self.assertEqual(datos['porcentaje'], 67)

    def test_cumplimiento_sin_datos_es_none(self):
        self.actividad(self.correr, -2)
        self.assertIsNone(calculos.cumplimiento(Actividad.objects.all())['porcentaje'])

    def test_por_categoria_ordena_por_porcentaje(self):
        self.actividad(self.correr, 2, completada=True)
        self.actividad(self.correr, 1)
        self.actividad(self.ingles, 1, completada=True)
        filas = calculos.por_categoria(Actividad.objects.all())
        self.assertEqual([(f['nombre'], f['porcentaje']) for f in filas], [('Estudio', 100), ('Salud', 50)])

    def test_por_semana_agrupa_por_fecha_de_fin(self):
        hoy = timezone.localdate()
        self.actividad(self.correr, 0, completada=True)
        self.actividad(self.correr, 7, completada=True)
        self.actividad(self.correr, 7)
        self.actividad(self.correr, 70, completada=True)  # fuera de las 8 semanas
        semanas = calculos.por_semana(Actividad.objects.all(), hoy)
        self.assertEqual(len(semanas), 8)
        self.assertEqual(sum(s['completadas'] for s in semanas), 2)
        self.assertEqual(sum(s['vencidas'] for s in semanas), 1)
        self.assertEqual(semanas[-1]['completadas'], 1)

    def test_rachas(self):
        for dia in [1, 2, 3, 5, 6]:
            self.registro(date(2026, 11, dia))
        registros = RegistroRendimiento.objects.all()
        self.assertEqual(calculos.rachas(registros, date(2026, 11, 6)), {'actual': 2, 'mejor': 3})
        # Hoy todavía sin registro: la racha de ayer sigue viva
        self.assertEqual(calculos.rachas(registros, date(2026, 11, 7))['actual'], 2)
        self.assertEqual(calculos.rachas(registros, date(2026, 11, 8))['actual'], 0)

    def test_satisfaccion_y_logro_por_tipo(self):
        hoy = timezone.localdate()
        self.registro(hoy, 'tiempo', esperado=30, valor=33, calificacion=4)
        self.registro(hoy, 'tiempo', esperado=30, valor=27, calificacion=5)
        self.registro(hoy, 'distancia', esperado=10, valor=5, calificacion=2)
        registros = RegistroRendimiento.objects.all()
        self.assertEqual(calculos.satisfaccion(registros), 3.7)
        logros = {f['titulo']: (f['porcentaje'], f['ancho']) for f in calculos.logro_por_tipo(registros)}
        self.assertEqual(logros, {'Tiempo (min)': (100, 100), 'Distancia (km)': (50, 50)})

    def test_logro_arriba_de_100_limita_la_barra(self):
        self.registro(timezone.localdate(), 'repeticiones', esperado=10, valor=15)
        fila = calculos.logro_por_tipo(RegistroRendimiento.objects.all())[0]
        self.assertEqual((fila['porcentaje'], fila['ancho']), (150, 100))

    def test_por_vencer_solo_activos_en_14_dias(self):
        pronto = self.objetivo('Examen', self.estudio, dias_meta=5)
        self.objetivo('Ya hecho', self.estudio, dias_meta=5, estado=Objetivo.Estado.COMPLETADO)
        self.actividad(pronto, 1, completada=True)
        self.actividad(pronto, -1)
        filas = list(calculos.por_vencer(Objetivo.objects.all()))
        self.assertEqual([o.titulo for o in filas], ['Examen'])
        self.assertEqual((filas[0].completadas, filas[0].total), (1, 2))


class PanelViewTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_user('tester', password='x'))

    def test_panel_sin_datos_muestra_estados_vacios(self):
        response = self.client.get(reverse('estadisticas:panel'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Todavía no hay registros de rendimiento')
        self.assertNotContains(response, 'chart.umd.min.js')

    def test_panel_solo_cuenta_datos_propios(self):
        otro = User.objects.create_user('otro', password='x')
        categoria = Categoria.objects.create(usuario=otro, nombre='Ajena')
        ahora = timezone.now()
        objetivo = Objetivo.objects.create(
            usuario=otro, categoria=categoria, titulo='Ajeno',
            fecha_inicio=ahora - timedelta(days=5), fecha_meta=ahora + timedelta(days=5),
        )
        Actividad.objects.create(
            objetivo=objetivo, titulo='Sesión', completada=True,
            fecha_inicio=ahora - timedelta(days=1, hours=1), fecha_fin=ahora - timedelta(days=1),
        )
        response = self.client.get(reverse('estadisticas:panel'))
        self.assertEqual(response.context['cumplimiento']['total'], 0)
        self.assertNotContains(response, 'Ajeno')

    def test_panel_requiere_sesion(self):
        self.client.logout()
        response = self.client.get(reverse('estadisticas:panel'))
        self.assertEqual(response.status_code, 302)
