"""Vistas de core, una por módulo; aquí se reexportan para que urls.py use views.<Vista>."""
from .calendario import calendario
from .categorias import CategoriasView, CategoriaCrearView, CategoriaEditarView, CategoriaEliminarView
from .objetivos import ObjetivosView, ObjetivoActividadesView, ObjetivoEditarView, ObjetivoEliminarView
from .actividades import ActividadesView, ActividadEditarView, ActividadEliminarView
from .rendimiento import ActividadDetalleView
