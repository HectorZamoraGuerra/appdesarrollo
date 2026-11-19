from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from ..forms import CategoriaForm
from ..models import Categoria


class CategoriasView(LoginRequiredMixin, ListView):
    """Lista de categorías con cuántos objetivos tiene cada una."""
    template_name = 'core/categorias/lista.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        return (
            Categoria.objects.filter(usuario=self.request.user)
            .annotate(total_objetivos=Count('objetivos')).order_by('nombre')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = 'categorias'
        return context


class CategoriaCrearView(LoginRequiredMixin, CreateView):
    """Alta de una categoría; al guardar regresa a la lista."""
    model = Categoria
    template_name = 'core/categorias/formulario.html'
    form_class = CategoriaForm
    success_url = reverse_lazy('core:categorias')
    extra_context = {'active_nav': 'categorias'}

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)


class CategoriaEditarView(LoginRequiredMixin, UpdateView):
    model = Categoria
    template_name = 'core/categorias/formulario.html'
    form_class = CategoriaForm
    success_url = reverse_lazy('core:categorias')
    extra_context = {'active_nav': 'categorias'}

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)


class CategoriaEliminarView(LoginRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'core/categorias/confirmar_eliminar.html'
    success_url = reverse_lazy('core:categorias')
    extra_context = {'active_nav': 'categorias'}

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)
