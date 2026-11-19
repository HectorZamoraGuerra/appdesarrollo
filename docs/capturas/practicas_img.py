"""Imágenes de tablas, figuras y resultados de las entregas anteriores, para documentar."""
import os
import shutil
import sys

import pdfplumber
from PIL import Image

E, T, P6PDF, SALIDA, IMG = sys.argv[1:6]
PAD = 4
os.makedirs(SALIDA, exist_ok=True)


def carpeta(nombre):
    ruta = os.path.join(SALIDA, nombre)
    os.makedirs(ruta, exist_ok=True)
    return ruta


def aplanar(rgb, mascara, destino):
    """Une la imagen con su máscara de transparencia y la deja sobre fondo blanco."""
    im = Image.open(rgb).convert('RGB')
    if mascara and os.path.exists(mascara):
        alfa = Image.open(mascara).convert('L')
        fondo = Image.new('RGB', im.size, 'white')
        fondo.paste(im, mask=alfa)
        im = fondo
    im.save(destino)


def pagina(pdf_ruta, num, destino, dpi=130):
    with pdfplumber.open(pdf_ruta) as pdf:
        pdf.pages[num - 1].to_image(resolution=dpi).save(destino)


def recortes(pdf, partes, destino, dpi=200):
    """Recorta una tabla (o sus partes en varias páginas) y las une en vertical."""
    imgs = []
    for num, indice in partes:
        p = pdf.pages[num - 1]
        x0, top, x1, bottom = p.find_tables()[indice].bbox
        caja = (max(0, x0 - PAD), max(0, top - PAD), min(p.width, x1 + PAD), min(p.height, bottom + PAD))
        imgs.append(p.crop(caja).to_image(resolution=dpi).original.convert('RGB'))
    ancho = max(i.width for i in imgs)
    total = Image.new('RGB', (ancho, sum(i.height for i in imgs)), 'white')
    y = 0
    for i in imgs:
        total.paste(i, (0, y))
        y += i.height
    total.save(destino)


hechos = []


def listo(ruta):
    hechos.append(os.path.relpath(ruta, SALIDA))


# ---------------- Presentación inicial (páginas de diapositiva; la 5 y la 7 están vacías en el PDF)
d = carpeta('01_presentacion_inicial')
pres = f'{E}/Presentacion_Sistema_de_gestion_de_rendimiento.pdf'
for num, nombre in [(1, 'portada'), (2, 'descripcion_general'), (3, 'tecnologias_y_justificacion'),
                    (4, 'elementos_del_proyecto'), (6, 'avances_modelo_er'), (8, 'impacto_del_proyecto')]:
    ruta = f'{d}/{num:02d}_{nombre}.png'
    pagina(pres, num, ruta, dpi=110)
    listo(ruta)
shutil.copy(f'{IMG}/modelo_er.png', f'{d}/modelo_entidad_relacion.png')
listo(f'{d}/modelo_entidad_relacion.png')

# ---------------- Práctica 4 (sus tablas vienen como imágenes dentro del PDF)
d = carpeta('02_practica4_seguimiento_validacion')
p4pdf = f'{E}/Practica4_Seguimiento_y_Validacion.pdf'
# La imagen es solo el fondo de la tabla; el texto va encima: se recorta la página en la zona de la imagen
with pdfplumber.open(p4pdf) as pdf:
    for num, indice, nombre in [
        (2, 0, '01_tabla_objetivos_actualizados'),
        (3, 0, '02_tabla_tecnicas_de_seguimiento'),
        (3, 1, '03_tabla_smart_objetivo_O2'),
        (3, 2, '04_tabla_kpis_avance_43_vs_47'),
        (4, 0, '05_tabla_herramienta_de_gestion_linea_base'),
    ]:
        p = pdf.pages[num - 1]
        im = sorted(p.images, key=lambda i: i['top'])[indice]
        caja = (max(0, im['x0']), max(0, im['top'] + 1), min(p.width, im['x1']), min(p.height, im['bottom'] - 1))
        ruta = f'{d}/{nombre}.png'
        p.crop(caja).to_image(resolution=200).original.convert('RGB').save(ruta)
        listo(ruta)
for num, nombre in [(5, '06_validacion_funcional_figuras_1_2'), (6, '07_validacion_funcional_figuras_3_4'),
                    (7, '08_figuras_5_6_y_justificacion')]:
    ruta = f'{d}/{nombre}.png'
    pagina(p4pdf, num, ruta)
    listo(ruta)

# ---------------- Investigación 8 (páginas diseñadas)
d = carpeta('03_investigacion8_estimacion_gantt_pert')
i8 = f'{E}/Investigacion8_Estimacion_Gantt_PERT.pdf'
for num, nombre in [(3, '01_tecnicas_de_estimacion'), (4, '02_gantt_elementos_y_herramientas'),
                    (5, '03_pert_elementos_y_herramientas'), (6, '04_ejemplo_gantt'), (7, '05_ejemplo_pert')]:
    ruta = f'{d}/{nombre}.png'
    pagina(i8, num, ruta, dpi=110)
    listo(ruta)
for rgb, nombre in [('img-006-010', '06_imagen_ejemplo_gantt'), ('img-007-012', '07_imagen_ejemplo_pert')]:
    ruta = f'{d}/{nombre}.png'
    aplanar(f'{T}/i8/{rgb}.png', None, ruta)
    listo(ruta)

# ---------------- Práctica 6 (tablas reales: se recortan; las partidas entre páginas se unen)
d = carpeta('04_practica6_gestion_de_recursos')
with pdfplumber.open(P6PDF) as pdf:
    for partes, nombre in [
        ([(2, 0)], '01_tabla_recursos_humanos_150h'),
        ([(2, 1)], '02_tabla_recursos_materiales_y_tecnologicos'),
        ([(2, 2), (3, 0)], '03_tabla_recursos_financieros_19950'),
        ([(4, 0), (5, 0)], '04_tabla_asignacion_por_fase'),
        ([(5, 1), (6, 0)], '05_tabla_indicadores_de_seguimiento'),
    ]:
        ruta = f'{d}/{nombre}.png'
        recortes(pdf, partes, ruta)
        listo(ruta)
for origen, nombre in [('pert.png', '06_pert_linea_base_80_7_dias'), ('gantt.png', '07_gantt_avance_06_oct')]:
    shutil.copy(f'{IMG}/{origen}', f'{d}/{nombre}.png')
    listo(f'{d}/{nombre}.png')

print(len(hechos))
for h in hechos:
    print(' ', h)
