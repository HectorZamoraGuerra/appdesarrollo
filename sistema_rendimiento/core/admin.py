from django.contrib import admin

from .models import Actividad, Categoria, Objetivo, RegistroRendimiento, Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'fecha_registro')
    search_fields = ('username', 'email')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario')
    list_filter = ('usuario',)
    search_fields = ('nombre',)


@admin.register(Objetivo)
class ObjetivoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'estado', 'prioridad', 'fecha_inicio', 'fecha_meta')
    list_filter = ('estado', 'prioridad', 'categoria')
    search_fields = ('titulo',)


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'objetivo', 'fecha_inicio', 'fecha_fin', 'completada')
    list_filter = ('completada', 'objetivo')
    search_fields = ('titulo',)


@admin.register(RegistroRendimiento)
class RegistroRendimientoAdmin(admin.ModelAdmin):
    list_display = ('actividad', 'tipo_indicador', 'valor', 'esperado', 'calificacion', 'fecha')
    list_filter = ('tipo_indicador', 'fecha')
