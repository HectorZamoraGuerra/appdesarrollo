from django.urls import path

from . import api, views

app_name = 'core'

urlpatterns = [
    path('', views.calendario, name='calendario'),
    path('objetivos/', views.ObjetivosView.as_view(), name='objetivos'),
    path('objetivos/<int:pk>/', views.ObjetivoActividadesView.as_view(), name='objetivo_detalle'),
    path('objetivos/<int:pk>/editar/', views.ObjetivoEditarView.as_view(), name='objetivo_editar'),
    path('objetivos/<int:pk>/eliminar/', views.ObjetivoEliminarView.as_view(), name='objetivo_eliminar'),
    path('actividades/', views.ActividadesView.as_view(), name='actividades'),
    path('actividades/<int:pk>/detalle/', views.ActividadDetalleView.as_view(), name='actividad_detalle'),
    path('actividades/<int:pk>/editar/', views.ActividadEditarView.as_view(), name='actividad_editar'),
    path('actividades/<int:pk>/eliminar/', views.ActividadEliminarView.as_view(), name='actividad_eliminar'),
    path('categorias/', views.CategoriasView.as_view(), name='categorias'),
    path('categorias/nueva/', views.CategoriaCrearView.as_view(), name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.CategoriaEditarView.as_view(), name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaEliminarView.as_view(), name='categoria_eliminar'),
    path('api/actividades/', api.ActividadListAPIView.as_view(), name='api_actividades'),
]
