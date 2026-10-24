from django.db import models
from django.utils import timezone


class Usuario(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Categoria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='categorias')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Objetivo(models.Model):
    class Prioridad(models.TextChoices):
        BAJA = 'baja', 'Baja'
        MEDIA = 'media', 'Media'
        ALTA = 'alta', 'Alta'

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        EN_PROGRESO = 'en_progreso', 'En progreso'
        COMPLETADO = 'completado', 'Completado'
        CANCELADO = 'cancelado', 'Cancelado'

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='objetivos')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='objetivos')
    titulo = models.CharField(max_length=200)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    prioridad = models.CharField(max_length=10, choices=Prioridad.choices, default=Prioridad.MEDIA)
    fecha_inicio = models.DateTimeField()
    fecha_meta = models.DateTimeField()

    def __str__(self):
        return self.titulo


class ActividadQuerySet(models.QuerySet):
    """Estados de la actividad; "vencida" se calcula con fecha_fin, no se guarda."""

    def completadas(self):
        return self.filter(completada=True)

    def pendientes(self):
        return self.filter(completada=False, fecha_fin__gte=timezone.now())

    def vencidas(self):
        return self.filter(completada=False, fecha_fin__lt=timezone.now())


class Actividad(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        COMPLETADA = 'completada', 'Completada'
        VENCIDA = 'vencida', 'Vencida'

    objetivo = models.ForeignKey(Objetivo, on_delete=models.CASCADE, related_name='actividades')
    titulo = models.CharField(max_length=200)
    nota = models.TextField(blank=True)
    completada = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()

    objects = ActividadQuerySet.as_manager()

    def __str__(self):
        return self.titulo

    @property
    def esta_vencida(self):
        return not self.completada and self.fecha_fin < timezone.now()

    @property
    def estado(self):
        if self.completada:
            return self.Estado.COMPLETADA
        return self.Estado.VENCIDA if self.esta_vencida else self.Estado.PENDIENTE


class RegistroRendimiento(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='registros')
    tipo_indicador = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    esperado = models.DecimalField(max_digits=10, decimal_places=2)
    calificacion = models.PositiveSmallIntegerField()
    fecha = models.DateField()

    def __str__(self):
        return f'{self.actividad} - {self.tipo_indicador}'
