from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView

from .forms import ActividadForm, ObjetivoForm, RegistroRendimientoForm
from .models import Actividad, Objetivo, Usuario


def calendario(request):
    return render(request, 'core/calendario.html', {'active_nav': 'calendario'})


class ObjetivoCrearView(CreateView):
    model = Objetivo
    form_class = ObjetivoForm
    template_name = 'core/objetivos.html'
    success_url = reverse_lazy('core:objetivos')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context['active_nav'] = 'objetivos'
        return context

    def form_valid(self, form):
        form.instance.usuario = Usuario.objects.first()
        return super().form_valid(form)


class ActividadesCrearView(CreateView):
    model = Actividad
    form_class = ActividadForm
    template_name = 'core/actividades.html'
    success_url = reverse_lazy('core:actividades')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        context['active_nav'] = 'actividades'
        return context


class ActividadDetalleView(DetailView):
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


def estadisticas(request):
    return render(request, 'core/estadisticas.html', {'active_nav': 'estadisticas'})


def categorias(request):
    return render(request, 'core/categorias.html', {'active_nav': 'categorias'})
