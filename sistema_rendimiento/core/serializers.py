from django.urls import reverse
from rest_framework import serializers

from .models import Actividad


class ActividadEventoSerializer(serializers.ModelSerializer):
    """Serializa una Actividad con el formato de evento de FullCalendar."""
    title = serializers.CharField(source='titulo')
    start = serializers.DateTimeField(source='fecha_inicio')
    end = serializers.DateTimeField(source='fecha_fin')
    url = serializers.SerializerMethodField()  # FullCalendar navega a esta URL al hacer clic

    class Meta:
        model = Actividad
        fields = ['id', 'title', 'start', 'end', 'completada', 'url']

    def get_url(self, obj):
        return reverse('core:actividad_detalle', args=[obj.pk])

