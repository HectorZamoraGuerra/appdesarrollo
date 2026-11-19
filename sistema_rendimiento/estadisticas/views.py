from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from ahorro.models import MetaAhorro, Movimiento
from core.models import Actividad, Objetivo, RegistroRendimiento

from . import calculos


@login_required
def panel(request):
    """Dashboard de estadísticas: indicadores, ahorro, cumplimiento por semana y categoría, logro y objetivos por vencer."""
    hoy = timezone.localdate()
    actividades = Actividad.objects.filter(objetivo__usuario=request.user)
    registros = RegistroRendimiento.objects.filter(actividad__objetivo__usuario=request.user)
    objetivos = Objetivo.objects.filter(usuario=request.user)
    objetivos.marcar_vencidos()

    semanas = calculos.por_semana(actividades, hoy)
    return render(request, 'estadisticas/panel.html', {
        'active_nav': 'estadisticas',
        'cumplimiento': calculos.cumplimiento(actividades),
        'rachas': calculos.rachas(registros, hoy),
        'satisfaccion': calculos.satisfaccion(registros),
        'ahorro': calculos.ahorro(
            MetaAhorro.objects.filter(usuario=request.user),
            Movimiento.objects.filter(meta__usuario=request.user),
        ),
        'semanas': semanas,
        'grafica_semanas': {
            'etiquetas': [s['etiqueta'] for s in semanas],
            'completadas': [s['completadas'] for s in semanas],
            'vencidas': [s['vencidas'] for s in semanas],
        },
        'hay_semanas': any(s['completadas'] or s['vencidas'] for s in semanas),
        'categorias': calculos.por_categoria(actividades),
        'logros': calculos.logro_por_tipo(registros),
        'por_vencer': calculos.por_vencer(objetivos),
    })
