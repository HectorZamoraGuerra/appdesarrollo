import django_filters
from django_filters.widgets import LinkWidget

from .models import Actividad, Categoria, Objetivo


class LinkSinPagina(LinkWidget):
    """LinkWidget que no copia ?page= en sus enlaces: al cambiar de pestaña se vuelve a la página 1."""

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        self.data = data.copy()
        self.data.pop('page', None)
        return value


class OrdenObjetivos(django_filters.OrderingFilter):
    """Ordena por el campo elegido y desempata por fecha meta."""

    def filter(self, qs, value):
        qs = super().filter(qs, value)
        return qs.order_by(*qs.query.order_by, 'fecha_meta') if value else qs


class ObjetivoFilter(django_filters.FilterSet):
    """Filtros de la lista de objetivos por estado, categoría y orden.

    El queryset debe traer anotado `peso_prioridad` (ver ObjetivosView).
    """
    GRUPOS_ESTADO = {
        'activos': [Objetivo.Estado.PENDIENTE, Objetivo.Estado.EN_PROGRESO],
        'completados': [Objetivo.Estado.COMPLETADO],
        'cancelados': [Objetivo.Estado.CANCELADO],
    }

    estado = django_filters.ChoiceFilter(
        label='Estado',
        choices=[('activos', 'Activos'), ('completados', 'Completados'), ('cancelados', 'Cancelados')],
        method='filtrar_estado',
        empty_label='Todos',
        widget=LinkWidget,
    )
    categoria = django_filters.ModelChoiceFilter(
        label='Categoría',
        queryset=Categoria.objects.order_by('nombre'),
        empty_label='Todas',
        widget=LinkWidget,
    )
    orden = OrdenObjetivos(
        label='Ordenar por',
        fields=(
            ('fecha_meta', 'fecha_meta'),
            ('peso_prioridad', 'prioridad'),
        ),
        # Solo orden ascendente: fecha meta más próxima y prioridad alta primero
        choices=[('fecha_meta', 'Fecha meta'), ('prioridad', 'Prioridad')],
        empty_label=None,
    )

    class Meta:
        model = Objetivo
        fields = ['estado', 'categoria']

    def filtrar_estado(self, queryset, name, value):
        return queryset.filter(estado__in=self.GRUPOS_ESTADO[value])


class ActividadFilter(django_filters.FilterSet):
    """Pestañas de actividades por estado; usa los métodos de ActividadQuerySet."""
    estado = django_filters.ChoiceFilter(
        label='Estado',
        choices=[('pendientes', 'Pendientes'), ('completadas', 'Completadas'), ('vencidas', 'Vencidas')],
        method='filtrar_estado',
        empty_label='Todas',
        widget=LinkSinPagina,
    )

    class Meta:
        model = Actividad
        fields = ['estado']

    def filtrar_estado(self, queryset, name, value):
        return getattr(queryset, value)()
