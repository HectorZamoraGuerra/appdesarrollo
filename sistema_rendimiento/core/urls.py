from django.urls import path

from . import api, views

app_name = 'core'

urlpatterns = [
    path('', views.calendario, name='calendario'),
    path('objetivos/', views.ObjetivoCrearView.as_view(), name='objetivos'),
    path('actividades/', views.ActividadesCrearView.as_view(), name='actividades'),
    path('actividades/<int:pk>/detalle/', views.ActividadDetalleView.as_view(), name='actividad_detalle'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('categorias/', views.categorias, name='categorias'),
    path('api/actividades/', api.ActividadListAPIView.as_view(), name='api_actividades'),
]
