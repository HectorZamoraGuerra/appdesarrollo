from django.urls import path

from . import views

app_name = 'ahorro'

urlpatterns = [
    path('', views.MetasView.as_view(), name='metas'),
    path('nueva/', views.MetaCrearView.as_view(), name='meta_crear'),
    path('<int:pk>/', views.MetaDetalleView.as_view(), name='meta_detalle'),
    path('<int:pk>/editar/', views.MetaEditarView.as_view(), name='meta_editar'),
    path('<int:pk>/eliminar/', views.MetaEliminarView.as_view(), name='meta_eliminar'),
    path('<int:pk>/movimiento/', views.MovimientoCrearView.as_view(), name='movimiento_crear'),
    path('movimientos/<int:pk>/eliminar/', views.MovimientoEliminarView.as_view(), name='movimiento_eliminar'),
]
