from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Actividad, Categoria, Objetivo, RegistroRendimiento


class EditarEliminarTests(TestCase):
    def setUp(self):
        usuario = User.objects.create_user('tester', password='x')
        self.categoria = Categoria.objects.create(usuario=usuario, nombre='Salud')
        ahora = timezone.now()
        self.objetivo = Objetivo.objects.create(
            usuario=usuario, categoria=self.categoria, titulo='Correr 10K',
            fecha_inicio=ahora, fecha_meta=ahora + timedelta(days=30),
        )
        self.actividad = Actividad.objects.create(
            objetivo=self.objetivo, titulo='Series', fecha_inicio=ahora,
            fecha_fin=ahora + timedelta(hours=1),
        )
        self.client.force_login(usuario)

    def test_formulario_nueva_categoria_carga(self):
        response = self.client.get(reverse('core:categoria_crear'))
        self.assertContains(response, 'Nueva categoría')

    def test_editar_categoria(self):
        url = reverse('core:categoria_editar', args=[self.categoria.pk])
        response = self.client.post(url, {'nombre': 'Deporte', 'descripcion': ''})
        self.assertRedirects(response, reverse('core:categorias'))
        self.categoria.refresh_from_db()
        self.assertEqual(self.categoria.nombre, 'Deporte')

    def test_editar_objetivo_valida_fechas(self):
        url = reverse('core:objetivo_editar', args=[self.objetivo.pk])
        response = self.client.post(url, {
            'titulo': 'Correr 21K', 'categoria': self.categoria.pk, 'estado': 'en_progreso',
            'prioridad': 'alta', 'fecha_inicio': '2026-11-10T08:00', 'fecha_meta': '2026-11-01T08:00',
        })
        self.assertEqual(response.status_code, 200)
        self.objetivo.refresh_from_db()
        self.assertEqual(self.objetivo.titulo, 'Correr 10K')

    def test_editar_actividad_regresa_al_detalle(self):
        url = reverse('core:actividad_editar', args=[self.actividad.pk])
        response = self.client.post(url, {
            'titulo': 'Series 10x400m', 'objetivo': self.objetivo.pk,
            'fecha_inicio': '2026-11-10T08:00', 'fecha_fin': '2026-11-10T09:00', 'nota': '',
        })
        self.assertRedirects(response, reverse('core:actividad_detalle', args=[self.actividad.pk]))
        self.actividad.refresh_from_db()
        self.assertEqual(self.actividad.titulo, 'Series 10x400m')

    def test_confirmar_eliminar_objetivo_avisa_cascada(self):
        response = self.client.get(reverse('core:objetivo_eliminar', args=[self.objetivo.pk]))
        self.assertContains(response, 'También se eliminará 1 actividad y sus registros')
        self.assertTrue(Objetivo.objects.exists())

    def test_eliminar_categoria_borra_en_cascada(self):
        response = self.client.post(reverse('core:categoria_eliminar', args=[self.categoria.pk]))
        self.assertRedirects(response, reverse('core:categorias'))
        self.assertFalse(Objetivo.objects.exists())
        self.assertFalse(Actividad.objects.exists())

    def test_eliminar_actividad(self):
        response = self.client.post(reverse('core:actividad_eliminar', args=[self.actividad.pk]))
        self.assertRedirects(response, reverse('core:actividades'))
        self.assertFalse(Actividad.objects.exists())
