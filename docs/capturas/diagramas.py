"""Gantt y PERT actualizados al corte del 25 oct 2026 (Parcial 2)."""
import sys
from datetime import date, timedelta

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

SALIDA = sys.argv[1]

TINTA = '#0b0b0b'
TEXTO2 = '#52514e'
GRIS = '#c9c8c3'
GRIS_CLARO = '#ecebe7'
AVANCE = '#2a78d6'          # slot 1 de la paleta de referencia
CRITICA = '#e34948'         # rojo, siempre acompañado de etiqueta y grosor
FONDO = '#ffffff'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 9,
    'axes.edgecolor': GRIS,
    'axes.labelcolor': TEXTO2,
    'xtick.color': TEXTO2,
    'ytick.color': TINTA,
})

CORTE = date(2026, 10, 25)


def d(m, dd):
    return date(2026, m, dd)


# ---------------------------------------------------------------- Gantt
# (código, nombre, inicio LB, fin LB, avance %, estado, estimada (inicio, fin) o None, ruta crítica)
FASES = [
    ('P1', 'Planificación y diseño', d(9, 7), d(9, 19), 100, '', None, False),
    ('E1', 'Entorno de desarrollo (Docker)', d(9, 22), d(9, 22), 100, '', None, False),
    ('P2', 'Wireframes y ajuste de BD (A33–A35)', d(9, 19), d(9, 21), 67, 'A35 pendiente',
     (d(10, 25), d(10, 27)), True),
    ('E2', 'Calendario y registro (A5, A6)', d(9, 23), d(10, 12), 100, '', None, False),
    ('E3', 'Fecha límite 30 nov (A8)', d(9, 23), d(10, 12), 0, 'A7 y A9 descartadas',
     (d(10, 25), d(10, 26)), False),
    ('E4', 'Popover, panel del día (A10, A11)', d(9, 23), d(10, 12), None, 'Descartada', None, False),
    ('M1', 'Autenticación (A15)', d(10, 13), d(10, 29), 70, '', None, False),
    ('M2', 'Categorías y objetivos (A16–A19)', d(10, 13), d(10, 29), 75, '', None, False),
    ('M3', 'Registro de rendimiento (A20)', d(10, 13), d(10, 29), 100, 'Real 06 oct', None, False),
    ('M4', 'Rendimiento y ahorro (A21, A36–A38)', d(10, 13), d(10, 29), 13, 'Mínimo funcional',
     (d(10, 27), d(10, 31)), True),
    ('D1', 'Dashboard (A22–A25, A39)', d(11, 2), d(11, 10), 0, '', None, True),
    ('T1', 'Pruebas y corrección (A28, A29)', d(11, 11), d(11, 23), 25, '', None, True),
    ('C1', 'Manual y despliegue (A30, A31)', d(11, 24), d(11, 30), 0, '', None, True),
]
HITOS = [('O1', d(10, 9)), ('O2', d(10, 12)), ('O3', d(10, 29)),
         ('O4', d(11, 10)), ('O5', d(11, 23)), ('O6', d(11, 30))]

fig, ax = plt.subplots(figsize=(11, 6.4), dpi=200)
fig.patch.set_facecolor(FONDO)
alto = 0.56
n = len(FASES)

for i, (cod, nombre, ini, fin, avance, estado, estimada, critica) in enumerate(FASES):
    y = n - 1 - i
    x0 = mdates.date2num(ini)
    ancho = mdates.date2num(fin + timedelta(days=1)) - x0
    if avance is None:
        ax.add_patch(Rectangle((x0, y - alto / 2), ancho, alto, facecolor=GRIS_CLARO,
                               edgecolor=GRIS, hatch='////', linewidth=0.8))
    else:
        ax.add_patch(Rectangle((x0, y - alto / 2), ancho, alto, facecolor=GRIS_CLARO,
                               edgecolor=GRIS, linewidth=0.8))
        if avance:
            ax.add_patch(Rectangle((x0, y - alto / 2), ancho * avance / 100, alto,
                                   facecolor=AVANCE, edgecolor='none'))
    if critica:
        ax.add_patch(Rectangle((x0, y - alto / 2), ancho, alto, facecolor='none',
                               edgecolor=TINTA, linewidth=1.4))
    fin_x = x0 + ancho
    if estimada:
        e0 = mdates.date2num(estimada[0])
        e1 = mdates.date2num(estimada[1] + timedelta(days=1))
        ax.add_patch(Rectangle((e0, y - 0.13), e1 - e0, 0.26, facecolor='none',
                               edgecolor=TINTA, linewidth=1.0, linestyle=(0, (3, 2))))
        fin_x = max(fin_x, e1)
    etiqueta = 'Descartada' if avance is None else f'{avance} %'
    if estado and avance is not None:
        etiqueta += f' · {estado}'
    ax.text(fin_x + 0.6, y, etiqueta, va='center', ha='left', fontsize=8,
            color=TEXTO2 if avance is None else TINTA)

for cod, dia in HITOS:
    x = mdates.date2num(dia + timedelta(days=1))
    ax.plot(x, n - 0.35, marker='D', markersize=6, color=TINTA)
    ax.text(x, n - 0.05, cod, ha='center', va='bottom', fontsize=8, color=TINTA)

x_corte = mdates.date2num(CORTE + timedelta(days=1))
ax.axvline(x_corte, color=TINTA, linewidth=1, linestyle=(0, (1, 2)))
ax.text(x_corte, -0.62, 'Corte 25 oct', ha='center', va='center', fontsize=8, color=TINTA,
        bbox=dict(facecolor=FONDO, edgecolor='none', pad=1.5))

ax.set_yticks(range(n))
ax.set_yticklabels([f'{c}  {nm}' for c, nm, *_ in reversed(FASES)])
ax.set_ylim(-1.1, n + 0.45)
ax.set_xlim(mdates.date2num(d(9, 5)), mdates.date2num(d(12, 9)))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
ax.xaxis.set_major_formatter(plt.FuncFormatter(
    lambda x, _: (lambda f: f'{f.day:02d} ' + ['', 'ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago',
                                                'sep', 'oct', 'nov', 'dic'][f.month])(mdates.num2date(x))))
ax.grid(axis='x', color=GRIS_CLARO, linewidth=0.8)
ax.set_axisbelow(True)
for lado in ('top', 'right', 'left'):
    ax.spines[lado].set_visible(False)
ax.tick_params(axis='y', length=0)

leyenda = [
    Rectangle((0, 0), 1, 1, facecolor=AVANCE, edgecolor='none', label='Avance real'),
    Rectangle((0, 0), 1, 1, facecolor=GRIS_CLARO, edgecolor=GRIS, label='Línea base'),
    Rectangle((0, 0), 1, 1, facecolor='none', edgecolor=TINTA, linestyle=(0, (3, 2)), label='Fecha estimada'),
    Rectangle((0, 0), 1, 1, facecolor='none', edgecolor=TINTA, linewidth=1.4, label='Ruta crítica actualizada'),
    Rectangle((0, 0), 1, 1, facecolor=GRIS_CLARO, edgecolor=GRIS, hatch='////', label='Descartada'),
    plt.Line2D([], [], marker='D', color=TINTA, linestyle='none', markersize=6, label='Hito (objetivo)'),
]
ax.legend(handles=leyenda, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=6, frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(f'{SALIDA}/gantt_actualizado.png', facecolor=FONDO)
plt.close(fig)

# ---------------------------------------------------------------- PERT
# Nodos: (código, título, t, ES, EF, holgura, hecho, x, y)
corte = 48.0
nodos = {
    'P1': ('Planificación y diseño', 12.3, 0.0, 12.3, 0, True, 0, 2),
    'E1': ('Entorno Docker', 1.2, 12.3, 13.5, 0, True, 1, 2),
    'E2': ('Calendario y registro', 19.8, 13.5, 33.3, 0, True, 2, 3.4),
    'M3': ('Registro de rendimiento', 17.3, 13.5, 30.8, 0, True, 2, 0.6),
    'CO': ('Corte 25 oct', None, 48.0, 48.0, 0, None, 3, 2),
    'P2': ('Ajuste de BD (A35)', 2.0, 48.0, 50.0, 0, False, 4, 2),
    'E3': ('Fecha límite (A8)', 1.1, 48.0, 49.1, 5.1, False, 4, 3.9),
    'M1': ('Autenticación (A15)', 2.2, 48.0, 50.2, 4.0, False, 5, 3.9),
    'M2': ('Categorías y objetivos', 2.0, 48.0, 50.0, 4.2, False, 4, 0.1),
    'M4': ('Rendimiento y ahorro', 4.2, 50.0, 54.2, 0, False, 5, 2),
    'D1': ('Dashboard', 8.0, 54.2, 62.2, 0, False, 6, 2),
    'T1': ('Pruebas y corrección', 13.2, 62.2, 75.4, 0, False, 7, 2),
    'C1': ('Manual y despliegue', 7.2, 75.4, 82.6, 0, False, 8, 2),
}
aristas = [
    ('P1', 'E1', False), ('E1', 'E2', False), ('E1', 'M3', False), ('E2', 'CO', False), ('M3', 'CO', False),
    ('CO', 'P2', True), ('CO', 'E3', False), ('CO', 'M1', False), ('CO', 'M2', False),
    ('P2', 'M4', True), ('E3', 'D1', False), ('M1', 'D1', False), ('M2', 'D1', False),
    ('M4', 'D1', True), ('D1', 'T1', True), ('T1', 'C1', True),
]
critica = {'P2', 'M4', 'D1', 'T1', 'C1'}

fig, ax = plt.subplots(figsize=(13, 5.6), dpi=200)
fig.patch.set_facecolor(FONDO)
W, H = 1.12, 0.95
esc_x = 1.5


def centro(k):
    _, _, _, _, _, _, x, y = nodos[k]
    return x * esc_x, y


# Fases paralelas después del corte: líneas en ángulo recto que rodean los nodos (sin cruzarlos)
RUTAS = {
    ('CO', 'E3'): [(5.25, 2), (5.25, 3.9)],
    ('CO', 'M1'): [(5.25, 2), (5.25, 3.25), (6.75, 3.25), (6.75, 3.9)],
    ('CO', 'M2'): [(5.25, 2), (5.25, 0.1)],
    ('E3', 'D1'): [(6.68, 3.9), (6.68, 4.6), (8.25, 4.6), (8.25, 2)],
    ('M1', 'D1'): [(8.25, 3.9), (8.25, 2)],
    ('M2', 'D1'): [(8.25, 0.1), (8.25, 2)],
}
for a, b, crit in aristas:
    (x1, y1), (x2, y2) = centro(a), centro(b)
    inicio, fin = (x1 + W / 2, y1), (x2 - W / 2, y2)
    if (a, b) in RUTAS:
        puntos = [inicio] + RUTAS[(a, b)]
        xs, ys = zip(*puntos)
        ax.plot(xs, ys, color=GRIS, linewidth=1.0, solid_joinstyle='miter', zorder=1)
        if b != 'D1':   # las que llegan a D1 se unen a la flecha crítica
            ax.add_patch(FancyArrowPatch(puntos[-1], fin, arrowstyle='-|>', mutation_scale=10,
                                         color=GRIS, linewidth=1.0, shrinkA=0, shrinkB=0))
        else:
            ax.plot(*puntos[-1], marker='o', markersize=3.5, color=GRIS, zorder=2)
        continue
    ax.add_patch(FancyArrowPatch(inicio, fin, arrowstyle='-|>', mutation_scale=10,
                                 color=CRITICA if crit else GRIS, linewidth=2.2 if crit else 1.0,
                                 shrinkA=0, shrinkB=0, zorder=3 if crit else 1))

for k, (titulo, t, es, ef, holgura, hecho, x, y) in nodos.items():
    cx, cy = centro(k)
    crit = k in critica
    if hecho is None:
        ax.add_patch(FancyBboxPatch((cx - W / 2, cy - 0.32), W, 0.64, boxstyle='round,pad=0.02,rounding_size=0.08',
                                    facecolor=TINTA, edgecolor=TINTA))
        ax.text(cx, cy + 0.08, 'Corte', ha='center', va='center', color=FONDO, fontsize=8.5, weight='bold')
        ax.text(cx, cy - 0.15, '25 oct · día 48', ha='center', va='center', color=FONDO, fontsize=7)
        continue
    ax.add_patch(FancyBboxPatch((cx - W / 2, cy - H / 2), W, H, boxstyle='round,pad=0.02,rounding_size=0.06',
                                facecolor=GRIS_CLARO if hecho else FONDO,
                                edgecolor=CRITICA if crit else (GRIS if hecho else TINTA),
                                linewidth=2.0 if crit else 1.0))
    ax.text(cx, cy + 0.31, k, ha='center', va='center', fontsize=10, weight='bold', color=TINTA)
    ax.text(cx, cy + 0.11, titulo, ha='center', va='center', fontsize=6.6, color=TEXTO2)
    ax.text(cx, cy - 0.09, f't = {t}' + (' (real)' if hecho else ''), ha='center', va='center',
            fontsize=7, color=TINTA)
    ax.text(cx, cy - 0.27, f'{es:g} → {ef:g}', ha='center', va='center', fontsize=7, color=TINTA)
    if not hecho:
        ax.text(cx, cy - 0.42, 'Ruta crítica' if crit else f'Holgura {holgura:g}', ha='center', va='center',
                fontsize=6.4, color=CRITICA if crit else TEXTO2, weight='bold' if crit else 'normal')
    else:
        ax.text(cx, cy - 0.42, 'Terminada', ha='center', va='center', fontsize=6.4, color=TEXTO2)

ax.text(centro('C1')[0], centro('C1')[1] - 0.85, 'Fin: día 82.6 = 28 nov\n(límite 30 nov, holgura 1.4)',
        ha='center', va='top', fontsize=7.5, color=TINTA, weight='bold')
ax.set_xlim(-0.7, 8 * esc_x + 0.8)
ax.set_ylim(-0.5, 4.75)
ax.axis('off')
ax.text(-0.65, 4.7, 't en días · ES → EF en días desde el 07 sep 2026 · E4 descartada (A10, A11)',
        fontsize=7.5, color=TEXTO2, va='top')
fig.tight_layout()
fig.savefig(f'{SALIDA}/pert_actualizado.png', facecolor=FONDO)
plt.close(fig)
print('ok')
