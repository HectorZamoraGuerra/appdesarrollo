"""Cálculos del dashboard. Reciben querysets ya filtrados por usuario en la vista."""
from datetime import timedelta

from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

from core.forms import RegistroRendimientoForm
from core.models import Categoria, Objetivo

MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']


def cumplimiento(actividades):
    """completadas ÷ (completadas + vencidas); las pendientes con fecha futura no cuentan. Sin datos el % es None."""
    completadas = actividades.completadas().count()
    vencidas = actividades.vencidas().count()
    total = completadas + vencidas
    return {
        'completadas': completadas,
        'vencidas': vencidas,
        'total': total,
        'porcentaje': round(100 * completadas / total) if total else None,
    }


def por_categoria(actividades):
    """Cumplimiento de cada categoría con actividades que ya se pueden contar; de mayor a menor %."""
    categorias = Categoria.objects.filter(objetivos__actividades__in=actividades).distinct()
    filas = []
    for categoria in categorias:
        datos = cumplimiento(actividades.filter(objetivo__categoria=categoria))
        if datos['total']:
            filas.append({'nombre': categoria.nombre, **datos})
    return sorted(filas, key=lambda f: (-f['porcentaje'], f['nombre']))


def por_semana(actividades, hoy, semanas=8):
    """Completadas y vencidas por semana (lunes a domingo) según la fecha de fin; la última es la semana actual."""
    inicio_actual = hoy - timedelta(days=hoy.weekday())
    inicios = [inicio_actual - timedelta(weeks=i) for i in range(semanas - 1, -1, -1)]
    filas = [{'etiqueta': f'{d.day} {MESES[d.month - 1]}', 'completadas': 0, 'vencidas': 0} for d in inicios]

    en_rango = actividades.filter(
        fecha_fin__date__gte=inicios[0],
        fecha_fin__date__lt=inicio_actual + timedelta(weeks=1),
    )
    for actividad in en_rango:
        semana = (timezone.localtime(actividad.fecha_fin).date() - inicios[0]).days // 7
        if actividad.completada:
            filas[semana]['completadas'] += 1
        elif actividad.esta_vencida:
            filas[semana]['vencidas'] += 1
    return filas


def rachas(registros, hoy):
    """Días seguidos con al menos un registro de rendimiento (registrar es lo que completa una actividad).

    La racha actual sigue viva si hoy todavía no hay registro pero ayer sí.
    """
    dias = sorted(set(registros.values_list('fecha', flat=True)))
    mejor = seguidos = 0
    anterior = None
    for dia in dias:
        seguidos = seguidos + 1 if anterior and dia - anterior == timedelta(days=1) else 1
        mejor = max(mejor, seguidos)
        anterior = dia

    presentes = set(dias)
    dia = hoy if hoy in presentes else hoy - timedelta(days=1)
    actual = 0
    while dia in presentes:
        actual += 1
        dia -= timedelta(days=1)
    return {'actual': actual, 'mejor': mejor}


def satisfaccion(registros):
    """Promedio de la calificación (1 a 5) con un decimal; None si no hay registros."""
    promedio = registros.aggregate(promedio=Avg('calificacion'))['promedio']
    return round(promedio, 1) if promedio is not None else None


def logro_por_tipo(registros):
    """Suma obtenida ÷ suma esperada por tipo de indicador; se toma "más es mejor" para los tres tipos."""
    sumas = {
        fila['tipo_indicador']: fila
        for fila in registros.values('tipo_indicador').annotate(esperado=Sum('esperado'), obtenido=Sum('valor'))
    }
    filas = []
    for tipo, titulo in RegistroRendimientoForm.TIPOS:
        fila = sumas.get(tipo)
        if fila and fila['esperado']:
            porcentaje = round(100 * fila['obtenido'] / fila['esperado'])
            filas.append({
                'titulo': titulo,
                'esperado': fila['esperado'],
                'obtenido': fila['obtenido'],
                'porcentaje': porcentaje,
                'ancho': min(porcentaje, 100),  #ente
            })
    return filas


def ahorro(metas, movimientos):
    """Total ahorrado contra la suma de las metas; None si no hay metas."""
    total_metas = metas.aggregate(total=Sum('monto_meta'))['total']
    if not total_metas:
        return None
    ahorrado = movimientos.saldo()
    return {'ahorrado': ahorrado, 'total_metas': total_metas, 'porcentaje': round(100 * ahorrado / total_metas)}


def por_vencer(objetivos, dias=14):
    """Objetivos activos cuya fecha meta cae en los próximos `dias` días, con su avance de actividades."""
    ahora = timezone.now()
    return (
        objetivos
        .filter(
            estado__in=[Objetivo.Estado.PENDIENTE, Objetivo.Estado.EN_PROGRESO],
            fecha_meta__gte=ahora,
            fecha_meta__lt=ahora + timedelta(days=dias),
        )
        .select_related('categoria')
        .annotate(
            total=Count('actividades'),
            completadas=Count('actividades', filter=Q(actividades__completada=True)),
        )
        .order_by('fecha_meta')
    )
