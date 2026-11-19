from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import MetaAhorroForm, MovimientoForm
from .models import MetaAhorro, Movimiento


class MetasView(LoginRequiredMixin, ListView):
    """Metas de ahorro del usuario con lo ahorrado y su avance."""
    template_name = 'ahorro/metas/lista.html'
    context_object_name = 'metas'
    extra_context = {'active_nav': 'ahorro'}

    def get_queryset(self):
        return MetaAhorro.objects.filter(usuario=self.request.user).con_saldo().order_by('fecha_meta')


class MetaDetalleView(LoginRequiredMixin, DetailView):
    """Resumen de la meta y sus movimientos, del más reciente al más antiguo."""
    template_name = 'ahorro/metas/detalle.html'
    context_object_name = 'meta'
    extra_context = {'active_nav': 'ahorro'}

    def get_queryset(self):
        return MetaAhorro.objects.filter(usuario=self.request.user).con_saldo()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movimientos'] = self.object.movimientos.order_by('-fecha', '-pk')
        return context


class MetaCrearView(LoginRequiredMixin, CreateView):
    """Al guardar va al detalle de la meta nueva (MetaAhorro.get_absolute_url)."""
    model = MetaAhorro
    template_name = 'ahorro/metas/formulario.html'
    form_class = MetaAhorroForm
    extra_context = {'active_nav': 'ahorro'}

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class MetaEditarView(LoginRequiredMixin, UpdateView):
    model = MetaAhorro
    template_name = 'ahorro/metas/formulario.html'
    form_class = MetaAhorroForm
    extra_context = {'active_nav': 'ahorro'}

    def get_queryset(self):
        return MetaAhorro.objects.filter(usuario=self.request.user)


class MetaEliminarView(LoginRequiredMixin, DeleteView):
    model = MetaAhorro
    template_name = 'ahorro/metas/confirmar_eliminar.html'
    success_url = reverse_lazy('ahorro:metas')
    extra_context = {'active_nav': 'ahorro'}

    def get_queryset(self):
        return MetaAhorro.objects.filter(usuario=self.request.user)


class MovimientoCrearView(LoginRequiredMixin, CreateView):
    """Registra un depósito o retiro en la meta de la URL; el formulario impide retirar más de lo ahorrado."""
    model = Movimiento
    template_name = 'ahorro/movimientos/formulario.html'
    form_class = MovimientoForm
    extra_context = {'active_nav': 'ahorro'}

    def dispatch(self, request, *args, **kwargs):
        self.meta = get_object_or_404(MetaAhorro, pk=kwargs['pk'], usuario=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), 'meta': self.meta}

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), 'meta': self.meta}

    def form_valid(self, form):
        form.instance.meta = self.meta
        return super().form_valid(form)

    def get_success_url(self):
        return self.meta.get_absolute_url()


class MovimientoEliminarView(LoginRequiredMixin, DeleteView):
    """No deja borrar un depósito si lo ahorrado quedaría en negativo."""
    model = Movimiento
    template_name = 'ahorro/movimientos/confirmar_eliminar.html'
    extra_context = {'active_nav': 'ahorro'}

    def get_queryset(self):
        return Movimiento.objects.filter(meta__usuario=self.request.user).select_related('meta')

    def form_valid(self, form):
        if self.object.meta.movimientos.exclude(pk=self.object.pk).saldo() < 0:
            form.add_error(None, 'No se puede eliminar: los retiros quedarían por encima de lo depositado.')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.meta.get_absolute_url()
