from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import DetailView

from ..forms import RegistroRendimientoForm
from ..models import Actividad


class ActividadDetalleView(LoginRequiredMixin, DetailView):
    """Detalle de una actividad; el POST registra el rendimiento y la completa."""
    model = Actividad
    template_name = 'core/actividades/detalle.html'

    def get_queryset(self):
        return Actividad.objects.filter(objetivo__usuario=self.request.user)

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
