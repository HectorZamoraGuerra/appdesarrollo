from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Actividad, Categoria, Objetivo


class DatosPorUsuarioTests(TestCase):
    """RF2: cada usuario ve y modifica solo sus categorías, objetivos y actividades."""

    def setUp(self):
        ahora = timezone.now()
        self.yo = User.objects.create_user('yo', password='x')
        otro = User.objects.create_user('otro', password='x')
        self.mi_categoria = Categoria.objects.create(usuario=self.yo, nombre='Salud')
        self.su_categoria = Categoria.objects.create(usuario=otro, nombre='Ajena')
        self.su_objetivo = Objetivo.objects.create(
            usuario=otro, categoria=self.su_categoria, titulo='Objetivo ajeno',
            fecha_inicio=ahora, fecha_meta=ahora + timedelta(days=30),
        )
        self.su_actividad = Actividad.objects.create(
            objetivo=self.su_objetivo, titulo='Actividad ajena',
            fecha_inicio=ahora, fecha_fin=ahora + timedelta(hours=1),
        )
        self.client.force_login(self.yo)

    def test_listas_y_api_no_muestran_datos_ajenos(self):
        for url in ['core:objetivos', 'core:actividades', 'core:categorias', 'core:api_actividades']:
            response = self.client.get(reverse(url))
            self.assertNotContains(response, 'ajen', msg_prefix=url)

    def test_paginas_de_datos_ajenos_dan_404(self):
        urls = [
            reverse('core:objetivo_detalle', args=[self.su_objetivo.pk]),
            reverse('core:objetivo_editar', args=[self.su_objetivo.pk]),
            reverse('core:actividad_detalle', args=[self.su_actividad.pk]),
            reverse('core:actividad_editar', args=[self.su_actividad.pk]),
            reverse('core:categoria_editar', args=[self.su_categoria.pk]),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 404, url)

    def test_no_se_pueden_borrar_datos_ajenos(self):
        response = self.client.post(reverse('core:categoria_eliminar', args=[self.su_categoria.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Objetivo.objects.filter(pk=self.su_objetivo.pk).exists())

    def test_alta_de_objetivo_queda_a_mi_nombre_y_rechaza_categoria_ajena(self):
        datos = {
            'nuevo-titulo': 'Correr 10K', 'nuevo-estado': 'pendiente', 'nuevo-prioridad': 'media',
            'nuevo-fecha_inicio': '2026-11-10T08:00', 'nuevo-fecha_meta': '2026-11-28T08:00',
        }
        self.client.post(reverse('core:objetivos'), {**datos, 'nuevo-categoria': self.su_categoria.pk})
        self.assertFalse(Objetivo.objects.filter(titulo='Correr 10K').exists())

        self.client.post(reverse('core:objetivos'), {**datos, 'nuevo-categoria': self.mi_categoria.pk})
        self.assertEqual(Objetivo.objects.get(titulo='Correr 10K').usuario, self.yo)

    def test_alta_de_categoria_queda_a_mi_nombre(self):
        self.client.post(reverse('core:categoria_crear'), {'nombre': 'Estudio', 'descripcion': ''})
        self.assertEqual(Categoria.objects.get(nombre='Estudio').usuario, self.yo)


class VencimientoDeObjetivosTests(TestCase):
    """RF7: un objetivo pendiente o en progreso pasa a "vencido" cuando su fecha meta ya pasó."""

    def setUp(self):
        self.usuario = User.objects.create_user('yo', password='x')
        self.categoria = Categoria.objects.create(usuario=self.usuario, nombre='Salud')
        self.client.force_login(self.usuario)

    def objetivo(self, titulo, estado, dias_meta):
        ahora = timezone.now()
        return Objetivo.objects.create(
            usuario=self.usuario, categoria=self.categoria, titulo=titulo, estado=estado,
            fecha_inicio=ahora - timedelta(days=60), fecha_meta=ahora + timedelta(days=dias_meta),
        )

    def test_marcar_vencidos(self):
        pasado = self.objetivo('Pasado', Objetivo.Estado.EN_PROGRESO, -1)
        hecho = self.objetivo('Hecho', Objetivo.Estado.COMPLETADO, -1)
        a_tiempo = self.objetivo('A tiempo', Objetivo.Estado.PENDIENTE, 5)

        self.assertEqual(Objetivo.objects.marcar_vencidos(), 1)
        estados = {o.titulo: o.estado for o in Objetivo.objects.all()}
        self.assertEqual(estados, {
            pasado.titulo: Objetivo.Estado.VENCIDO,
            hecho.titulo: Objetivo.Estado.COMPLETADO,
            a_tiempo.titulo: Objetivo.Estado.PENDIENTE,
        })

    def test_la_lista_los_marca_y_los_filtra(self):
        self.objetivo('Pasado', Objetivo.Estado.PENDIENTE, -1)
        self.objetivo('A tiempo', Objetivo.Estado.PENDIENTE, 5)
        response = self.client.get(reverse('core:objetivos'), {'estado': 'vencidos'})
        self.assertContains(response, 'Pasado')
        self.assertNotContains(response, 'A tiempo')


class ListaDeObjetivosTests(TestCase):
    def test_sin_ids_repetidos_entre_filtros_y_modal(self):
        """Hallazgo E2E (13 nov): los filtros y el modal compartían id_estado e id_categoria."""
        import re
        from collections import Counter

        self.client.force_login(User.objects.create_user('yo', password='x'))
        html = self.client.get(reverse('core:objetivos')).content.decode()
        repetidos = [i for i, n in Counter(re.findall(r'\bid="([^"]+)"', html)).items() if n > 1]
        self.assertEqual(repetidos, [])
