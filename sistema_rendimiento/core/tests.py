from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Actividad, Categoria, Objetivo, RegistroRendimiento, Usuario


class RegistroRendimientoTests(TestCase):
    def setUp(self):
        usuario = Usuario.objects.create(email='a@b.com', username='demo', password_hash='x')
        categoria = Categoria.objects.create(usuario=usuario, nombre='Salud')
        ahora = timezone.now()
        objetivo = Objetivo.objects.create(
            usuario=usuario, categoria=categoria, titulo='Correr 10K',
            fecha_inicio=ahora, fecha_meta=ahora + timedelta(days=30),
        )
        self.actividad = Actividad.objects.create(
            objetivo=objetivo, titulo='Series', fecha_inicio=ahora,
            fecha_fin=ahora + timedelta(hours=1),
        )
        self.url = reverse('core:actividad_detalle', args=[self.actividad.pk])
        self.client.force_login(User.objects.create_user('tester', password='x'))

    def test_guardar_registro_completa_la_actividad(self):
        response = self.client.post(self.url, {
            'tipo_indicador': 'tiempo', 'esperado': '30', 'valor': '32', 'calificacion': '4',
        })
        self.assertRedirects(response, reverse('core:calendario'))
        registro = RegistroRendimiento.objects.get(actividad=self.actividad)
        self.assertEqual(registro.esperado, 30)
        self.assertEqual(registro.valor, 32)
        self.actividad.refresh_from_db()
        self.assertTrue(self.actividad.completada)

    def test_registro_sin_esperado_no_guarda_ni_completa(self):
        response = self.client.post(self.url, {
            'tipo_indicador': 'tiempo', 'valor': '32', 'calificacion': '4',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(RegistroRendimiento.objects.exists())
        self.actividad.refresh_from_db()
        self.assertFalse(self.actividad.completada)
