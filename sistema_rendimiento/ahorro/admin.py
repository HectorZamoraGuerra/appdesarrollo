from django.contrib import admin

from .models import MetaAhorro, Movimiento


@admin.register(MetaAhorro)
class MetaAhorroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'monto_meta', 'fecha_meta')
    list_filter = ('usuario',)
    search_fields = ('nombre',)


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ('meta', 'tipo', 'monto', 'fecha', 'nota')
    list_filter = ('tipo', 'fecha')
