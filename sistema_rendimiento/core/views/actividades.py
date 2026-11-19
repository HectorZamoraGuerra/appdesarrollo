from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView, UpdateView

from ..forms import ActividadForm
from ..models import Actividad


class ActividadesView(LoginRequiredMixin, ListView):
    """Lista de actividades; el POST da de alta una nueva desde el modal."""
    model = Actividad
    paginate_by = 10
    template_name = 'core/actividades/lista.html'
    context_object_name = 'actividades'

    def get_queryset(self):
        return (
            Actividad.objects.filter(objetivo__usuario=self.request.user)
            .select_related('objetivo__categoria').order_by('fecha_inicio')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = 'actividades'
        context.setdefault('form', ActividadForm(usuario=self.request.user))
        return context

    def post(self, request, *args, **kwargs):
        form = ActividadForm(request.POST, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect('core:actividades')
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(form=form))


class ActividadEditarView(LoginRequiredMixin, UpdateView):
    """Al guardar regresa al detalle (Actividad.get_absolute_url)."""
    model = Actividad
    template_name = 'core/actividades/formulario.html'
    form_class = ActividadForm
    extra_context = {'active_nav': 'actividades'}

    def get_queryset(self):
        return Actividad.objects.filter(objetivo__usuario=self.request.user)

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), 'usuario': self.request.user}


class ActividadEliminarView(LoginRequiredMixin, DeleteView):
    model = Actividad
    template_name = 'core/actividades/confirmar_eliminar.html'
    success_url = reverse_lazy('core:actividades')
    extra_context = {'active_nav': 'actividades'}

    def get_queryset(self):
        return Actividad.objects.filter(objetivo__usuario=self.request.user)
