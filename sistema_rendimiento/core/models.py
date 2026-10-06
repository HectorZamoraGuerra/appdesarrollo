from django.db import models


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


class Actividad(models.Model):
    objetivo = models.ForeignKey(Objetivo, on_delete=models.CASCADE, related_name='actividades')
    titulo = models.CharField(max_length=200)
    nota = models.TextField(blank=True)
    completada = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()

    def __str__(self):
        return self.titulo


class RegistroRendimiento(models.Model):
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, related_name='registros')
    tipo_indicador = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    esperado = models.DecimalField(max_digits=10, decimal_places=2)
    calificacion = models.PositiveSmallIntegerField()
    fecha = models.DateField()

    def __str__(self):
        return f'{self.actividad} - {self.tipo_indicador}'
