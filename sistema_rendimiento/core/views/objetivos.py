from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, Count, Prefetch, Q, When
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DeleteView, UpdateView
from django_filters.views import FilterView

from ..filters import ActividadFilter, ObjetivoFilter
from ..forms import ObjetivoForm, RegistroRendimientoForm
from ..models import Objetivo, RegistroRendimiento


class ObjetivosView(LoginRequiredMixin, FilterView):
    """Lista de objetivos filtrada con ObjetivoFilter; el POST da de alta uno nuevo desde el modal."""
    model = Objetivo
    filterset_class = ObjetivoFilter
    strict = False
    template_name = 'core/objetivos/lista.html'
    context_object_name = 'objetivos'

    def get_queryset(self):
        ahora = timezone.now()
        no_completada = Q(actividades__completada=False)
        objetivos = Objetivo.objects.filter(usuario=self.request.user)
        objetivos.marcar_vencidos()
        return objetivos.select_related('categoria').annotate(
            completadas=Count('actividades', filter=Q(actividades__completada=True)),
            pendientes=Count('actividades', filter=no_completada & Q(actividades__fecha_fin__gte=ahora)),
            vencidas=Count('actividades', filter=no_completada & Q(actividades__fecha_fin__lt=ahora)),
            peso_prioridad=Case(
                When(prioridad=Objetivo.Prioridad.ALTA, then=0),
                When(prioridad=Objetivo.Prioridad.MEDIA, then=1),
                default=2,
            ),
        ).order_by('fecha_meta')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todos = Objetivo.objects.filter(usuario=self.request.user)
        context.update({
            'active_nav': 'objetivos',
            'total_objetivos': todos.count(),
            'total_en_curso': todos.filter(estado=Objetivo.Estado.EN_PROGRESO).count(),
            'total_completados': todos.filter(estado=Objetivo.Estado.COMPLETADO).count(),
        })
        # Prefijo: sin él, los campos del modal repiten los id de los filtros (id_estado, id_categoria)
        context.setdefault('form', ObjetivoForm(usuario=self.request.user, prefix='nuevo'))
        return context

    def post(self, request, *args, **kwargs):
        form = ObjetivoForm(request.POST, usuario=request.user, prefix='nuevo')
        if form.is_valid():
            form.instance.usuario = request.user
            form.save()
            return redirect('core:objetivos')
        self.filterset = self.get_filterset(self.get_filterset_class())
        self.object_list = self.filterset.qs
        return self.render_to_response(self.get_context_data(form=form))


class ObjetivoActividadesView(LoginRequiredMixin, FilterView):
    """Detalle de un objetivo: lista sus actividades filtradas por estado; el pk de la URL indica cuál."""
    filterset_class = ActividadFilter
    strict = False
    paginate_by = 10
    template_name = 'core/objetivos/detalle.html'
    context_object_name = 'actividades'

    def get_queryset(self):
        objetivos = Objetivo.objects.filter(usuario=self.request.user, pk=self.kwargs['pk'])
        objetivos.marcar_vencidos()
        self.objetivo = get_object_or_404(objetivos.select_related('categoria'))
        registros = Prefetch(
            'registros',
            queryset=RegistroRendimiento.objects.order_by('fecha', 'pk'),
            to_attr='registros_ordenados',
        )
        return self.objetivo.actividades.prefetch_related(registros).order_by('fecha_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        actividades = self.objetivo.actividades.all()
        context.update({
            'active_nav': 'objetivos',
            'objetivo': self.objetivo,
            'pendientes': actividades.pendientes().count(),
            'completadas': actividades.completadas().count(),
            'vencidas': actividades.vencidas().count(),
            'graficas': self.datos_graficas(),
        })
        return context

    def datos_graficas(self):
        """Esperado vs obtenido por sesión, una gráfica por cada tipo de indicador con registros."""
        registros = (
            RegistroRendimiento.objects
            .filter(actividad__objetivo=self.objetivo)
            .order_by('fecha', 'pk')
        )
        graficas = []
        for tipo, titulo in RegistroRendimientoForm.TIPOS:
            del_tipo = [r for r in registros if r.tipo_indicador == tipo]
            if del_tipo:
                graficas.append({
                    'tipo': tipo,
                    'titulo': titulo,
                    'json_id': f'datos-grafica-{tipo}',
                    'etiquetas': [f'S{i}' for i in range(1, len(del_tipo) + 1)],
                    'esperado': [float(r.esperado) for r in del_tipo],
                    'obtenido': [float(r.valor) for r in del_tipo],
                })
        return graficas


class ObjetivoEditarView(LoginRequiredMixin, UpdateView):
    """Al guardar regresa al detalle (Objetivo.get_absolute_url)."""
    model = Objetivo
    template_name = 'core/objetivos/formulario.html'
    form_class = ObjetivoForm
    extra_context = {'active_nav': 'objetivos'}

    def get_queryset(self):
        return Objetivo.objects.filter(usuario=self.request.user)

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), 'usuario': self.request.user}


class ObjetivoEliminarView(LoginRequiredMixin, DeleteView):
    model = Objetivo
    template_name = 'core/objetivos/confirmar_eliminar.html'
    success_url = reverse_lazy('core:objetivos')
    extra_context = {'active_nav': 'objetivos'}

    def get_queryset(self):
        return Objetivo.objects.filter(usuario=self.request.user)
