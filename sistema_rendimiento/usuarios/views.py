from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegistroForm


class RegistroView(CreateView):
    """Alta de usuario con RegistroForm; al registrarse inicia sesión."""
    form_class = RegistroForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('core:calendario')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
