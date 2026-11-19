from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone

MONTO_MINIMO = MinValueValidator(Decimal('0.01'), 'El monto debe ser mayor que 0.')


def saldo(prefijo=''):
    """Depósitos − retiros como expresión de suma; con prefijo 'movimientos__' sirve para anotar metas."""
    def suma(tipo):
        return Coalesce(Sum(f'{prefijo}monto', filter=Q(**{f'{prefijo}tipo': tipo})), Decimal('0'))
    return suma(Movimiento.Tipo.DEPOSITO) - suma(Movimiento.Tipo.RETIRO)


class MetaAhorroQuerySet(models.QuerySet):
    def con_saldo(self):
        """Anota `ahorrado`; avance y faltante lo necesitan."""
        return self.annotate(ahorrado=saldo('movimientos__'))


class MetaAhorro(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='metas_ahorro')
    nombre = models.CharField(max_length=200)
    monto_meta = models.DecimalField(max_digits=12, decimal_places=2, validators=[MONTO_MINIMO])
    fecha_meta = models.DateField()

    objects = MetaAhorroQuerySet.as_manager()

    def __str__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse('ahorro:meta_detalle', args=[self.pk])

    @property
    def avance(self):
        """% de la meta ya ahorrado; requiere con_saldo()."""
        return round(100 * self.ahorrado / self.monto_meta)

    @property
    def ancho(self):
        """Ancho de la barra: el avance limitado a 0–100 %."""
        return max(0, min(self.avance, 100))

    @property
    def faltante(self):
        """Lo que falta para la meta (0 si ya se alcanzó); requiere con_saldo()."""
        return max(self.monto_meta - self.ahorrado, Decimal('0'))


class MovimientoQuerySet(models.QuerySet):
    def saldo(self):
        return self.aggregate(saldo=saldo())['saldo']


class Movimiento(models.Model):
    class Tipo(models.TextChoices):
        DEPOSITO = 'deposito', 'Depósito'
        RETIRO = 'retiro', 'Retiro'

    meta = models.ForeignKey(MetaAhorro, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=Tipo.choices, default=Tipo.DEPOSITO)
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MONTO_MINIMO])
    fecha = models.DateField(default=timezone.localdate)
    nota = models.CharField(max_length=200, blank=True)

    objects = MovimientoQuerySet.as_manager()

    def __str__(self):
        return f'{self.get_tipo_display()} de ${self.monto:,.2f}'
