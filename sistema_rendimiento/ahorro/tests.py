from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import MetaAhorro, Movimiento


class AhorroTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('yo', password='x')
        self.meta = MetaAhorro.objects.create(
            usuario=self.usuario, nombre='Fondo de emergencia', monto_meta=50000, fecha_meta=date(2026, 12, 31),
        )
        self.client.force_login(self.usuario)

    def movimiento(self, tipo, monto):
        return Movimiento.objects.create(meta=self.meta, tipo=tipo, monto=monto, fecha=date(2026, 11, 1))

    def con_saldo(self):
        return MetaAhorro.objects.con_saldo().get(pk=self.meta.pk)

    def test_ahorrado_avance_y_faltante(self):
        self.movimiento(Movimiento.Tipo.DEPOSITO, 30000)
        self.movimiento(Movimiento.Tipo.DEPOSITO, 5000)
        self.movimiento(Movimiento.Tipo.RETIRO, 3000)
        meta = self.con_saldo()
        self.assertEqual(meta.ahorrado, Decimal('32000'))
        self.assertEqual(meta.avance, 64)
        self.assertEqual(meta.faltante, Decimal('18000'))

    def test_meta_sin_movimientos_y_meta_superada(self):
        meta = self.con_saldo()
        self.assertEqual((meta.ahorrado, meta.avance, meta.ancho), (0, 0, 0))
        self.movimiento(Movimiento.Tipo.DEPOSITO, 60000)
        meta = self.con_saldo()
        self.assertEqual((meta.avance, meta.ancho, meta.faltante), (120, 100, 0))

    def test_registrar_deposito(self):
        url = reverse('ahorro:movimiento_crear', args=[self.meta.pk])
        response = self.client.post(url, {'tipo': 'deposito', 'monto': '1500', 'fecha': '2026-11-13', 'nota': 'Quincena'})
        self.assertRedirects(response, reverse('ahorro:meta_detalle', args=[self.meta.pk]))
        self.assertEqual(self.meta.movimientos.saldo(), Decimal('1500'))

    def test_retiro_mayor_a_lo_ahorrado_se_rechaza(self):
        self.movimiento(Movimiento.Tipo.DEPOSITO, 1000)
        url = reverse('ahorro:movimiento_crear', args=[self.meta.pk])
        response = self.client.post(url, {'tipo': 'retiro', 'monto': '1500', 'fecha': '2026-11-13', 'nota': ''})
        self.assertContains(response, 'es mayor a lo ahorrado')
        self.assertEqual(self.meta.movimientos.count(), 1)

    def test_monto_cero_se_rechaza(self):
        url = reverse('ahorro:movimiento_crear', args=[self.meta.pk])
        response = self.client.post(url, {'tipo': 'deposito', 'monto': '0', 'fecha': '2026-11-13', 'nota': ''})
        self.assertContains(response, 'El monto debe ser mayor que 0.')
        self.assertFalse(self.meta.movimientos.exists())

    def test_no_se_borra_deposito_si_el_saldo_queda_negativo(self):
        deposito = self.movimiento(Movimiento.Tipo.DEPOSITO, 1000)
        self.movimiento(Movimiento.Tipo.RETIRO, 800)
        response = self.client.post(reverse('ahorro:movimiento_eliminar', args=[deposito.pk]))
        self.assertContains(response, 'No se puede eliminar')
        self.assertTrue(Movimiento.objects.filter(pk=deposito.pk).exists())

    def test_eliminar_retiro(self):
        retiro = self.movimiento(Movimiento.Tipo.RETIRO, 0.01)
        response = self.client.post(reverse('ahorro:movimiento_eliminar', args=[retiro.pk]))
        self.assertRedirects(response, reverse('ahorro:meta_detalle', args=[self.meta.pk]))
        self.assertFalse(self.meta.movimientos.exists())

    def test_crear_meta_queda_a_mi_nombre(self):
        response = self.client.post(reverse('ahorro:meta_crear'), {
            'nombre': 'Viaje', 'monto_meta': '12000', 'fecha_meta': '2027-06-30',
        })
        meta = MetaAhorro.objects.get(nombre='Viaje')
        self.assertRedirects(response, reverse('ahorro:meta_detalle', args=[meta.pk]))
        self.assertEqual(meta.usuario, self.usuario)

    def test_datos_ajenos(self):
        otro = User.objects.create_user('otro', password='x')
        ajena = MetaAhorro.objects.create(usuario=otro, nombre='Meta ajena', monto_meta=100, fecha_meta=date(2026, 12, 31))
        movimiento = Movimiento.objects.create(meta=ajena, tipo='deposito', monto=50)
        self.assertNotContains(self.client.get(reverse('ahorro:metas')), 'Meta ajena')
        for url in [
            reverse('ahorro:meta_detalle', args=[ajena.pk]),
            reverse('ahorro:meta_editar', args=[ajena.pk]),
            reverse('ahorro:movimiento_crear', args=[ajena.pk]),
            reverse('ahorro:movimiento_eliminar', args=[movimiento.pk]),
        ]:
            self.assertEqual(self.client.get(url).status_code, 404, url)

    def test_tarjeta_en_el_dashboard(self):
        self.movimiento(Movimiento.Tipo.DEPOSITO, 12500)
        response = self.client.get(reverse('estadisticas:panel'))
        self.assertEqual(response.context['ahorro']['porcentaje'], 25)
        self.assertContains(response, '$12,500.00 de $50,000.00')
