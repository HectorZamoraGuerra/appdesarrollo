from django.urls import path

from . import api, views

app_name = 'core'

urlpatterns = [
    path('', views.calendario, name='calendario'),
    path('objetivos/', views.ObjetivosView.as_view(), name='objetivos'),
    path('objetivos/<int:pk>/', views.ObjetivoActividadesView.as_view(), name='objetivo_detalle'),
    path('actividades/', views.ActividadesView.as_view(), name='actividades'),
    path('actividades/<int:pk>/detalle/', views.ActividadDetalleView.as_view(), name='actividad_detalle'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('categorias/', views.CategoriasView.as_view(), name='categorias'),
    path('categorias/nueva/', views.CategoriaCrearView.as_view(), name='categoria_crear'),
    path('api/actividades/', api.ActividadListAPIView.as_view(), name='api_actividades'),
]
