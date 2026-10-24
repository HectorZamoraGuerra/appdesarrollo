from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Case, Count, Prefetch, Q, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView
from django_filters.views import FilterView

from .filters import ActividadFilter, ObjetivoFilter
from .forms import ActividadForm, CategoriaForm, ObjetivoForm, RegistroRendimientoForm
from .models import Actividad, Categoria, Objetivo, RegistroRendimiento, Usuario


@login_required
def calendario(request):
    return render(request, 'core/calendario.html', {'active_nav': 'calendario'})


class ObjetivosView(LoginRequiredMixin, FilterView):
    """Lista de objetivos filtrada con ObjetivoFilter; el POST da de alta uno nuevo desde el modal."""
    model = Objetivo
    filterset_class = ObjetivoFilter
    strict = False
    template_name = 'core/objetivos.html'
    context_object_name = 'objetivos'

    def get_queryset(self):
        ahora = timezone.now()
        no_completada = Q(actividades__completada=False)
        return Objetivo.objects.select_related('categoria').annotate(
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
        todos = Objetivo.objects.all()
        context.update({
            'active_nav': 'objetivos',
            'total_objetivos': todos.count(),
            'total_en_curso': todos.filter(estado=Objetivo.Estado.EN_PROGRESO).count(),
            'total_completados': todos.filter(estado=Objetivo.Estado.COMPLETADO).count(),
        })
        context.setdefault('form', ObjetivoForm())
        return context

    def post(self, request, *args, **kwargs):
        form = ObjetivoForm(request.POST)
        if form.is_valid():
            form.instance.usuario = Usuario.objects.first()
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
    template_name = 'core/objetivo_detalle.html'
    context_object_name = 'actividades'

    def get_queryset(self):
        self.objetivo = get_object_or_404(Objetivo.objects.select_related('categoria'), pk=self.kwargs['pk'])
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


class ActividadesView(LoginRequiredMixin, ListView):
    """Lista de actividades; el POST da de alta una nueva desde el modal."""
    model = Actividad
    paginate_by = 10
    template_name = 'core/actividades.html'
    context_object_name = 'actividades'

    def get_queryset(self):
        return Actividad.objects.select_related('objetivo__categoria').order_by('fecha_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = 'actividades'
        context.setdefault('form', ActividadForm())
        return context

    def post(self, request, *args, **kwargs):
        form = ActividadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('core:actividades')
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form))


class ActividadDetalleView(LoginRequiredMixin, DetailView):
    """Detalle de una actividad; el POST registra el rendimiento y la completa."""
    model = Actividad
    template_name = 'core/actividad_detalle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = 'calendario'
        context['registro_form'] = RegistroRendimientoForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = RegistroRendimientoForm(request.POST)
        if not form.is_valid():
            context = self.get_context_data()
            context['registro_form'] = form
            return self.render_to_response(context)

        with transaction.atomic():
            registro = form.save(commit=False)
            registro.actividad = self.object
            registro.fecha = timezone.localdate()
            registro.save()
            self.object.completada = True
            self.object.save(update_fields=['completada'])
        return redirect('core:calendario')


@login_required
def estadisticas(request):
    return render(request, 'core/estadisticas.html', {'active_nav': 'estadisticas'})


class CategoriasView(LoginRequiredMixin, ListView):
    """Lista de categorías con cuántos objetivos tiene cada una."""
    template_name = 'core/categorias.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        return Categoria.objects.annotate(total_objetivos=Count('objetivos')).order_by('nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = 'categorias'
        return context


class CategoriaCrearView(LoginRequiredMixin, CreateView):
    """Alta de una categoría; al guardar regresa a la lista."""
    model = Categoria
    form_class = CategoriaForm
    template_name = 'core/categoria_form.html'
    success_url = reverse_lazy('core:categorias')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = 'categorias'
        return context

    def form_valid(self, form):
        form.instance.usuario = Usuario.objects.first()
        return super().form_valid(form)
