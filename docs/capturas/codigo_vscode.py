"""Capturas con estilo de VS Code para el Parcial 3: estructura de carpetas, fragmentos de pruebas y su ejecución.

Todo el contenido es real: el árbol sale del disco, el código se lee de los archivos (con sus números de línea)
y la terminal muestra la salida de `manage.py test` ejecutado por este script. Solo la ventana es una reproducción.

Uso (desde la raíz del repo):  python docs/capturas/codigo_vscode.py [--sin-pruebas | --sin-e2e]
        --sin-pruebas: no vuelve a correr las pruebas (deja las capturas de terminal que ya existen)
        --sin-e2e: corre solo las pruebas unitarias (no regenera los videos de evidencia)
Salida: docs/capturas/parcial3/*.png
"""
import ast
import html
import os
import re
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[2]
PROYECTO = RAIZ / 'sistema_rendimiento'
SALIDA = RAIZ / 'docs' / 'capturas' / 'parcial3'
PROMPT = '~/rendimiento/appdesarrollo/sistema_rendimiento $'

ESTILO = """
* { box-sizing: border-box; margin: 0; }
body { background: #fff; padding: 0; font-family: 'Segoe UI', 'Noto Sans', system-ui, sans-serif; }
.ventana { display: inline-block; background: #1e1e1e; color: #d4d4d4; border: 1px solid #3c3c3c; }
.barra { background: #323233; color: #cccccc; font-size: 12px; padding: 7px 70px; text-align: center; position: relative; white-space: nowrap; }
.barra .puntos { position: absolute; left: 12px; top: 6px; letter-spacing: 3px; color: #6e6e6e; }
.cuerpo { display: flex; }
.lateral { background: #252526; width: 290px; padding: 6px 0 10px; font-size: 13px; }
.lateral .titulo { font-size: 11px; color: #bbbbbb; padding: 4px 14px 8px; letter-spacing: .06em; }
.fila { white-space: nowrap; line-height: 22px; color: #cccccc; }
.fila .chev { display: inline-block; width: 14px; color: #c5c5c5; }
.fila.carpeta { color: #e8e8e8; }
.fila.sel { background: #37373d; }
.ic { display: inline-block; width: 18px; font-size: 11px; font-weight: 700; }
.py { color: #3b8eea; } .html { color: #e37933; } .css { color: #519aba; } .js { color: #cbcb41; }
.webm { color: #a074c4; } .png { color: #a074c4; } .md { color: #519aba; }
.editor { min-width: 820px; }
.pestanas { background: #252526; display: flex; }
.pestana { background: #1e1e1e; color: #ffffff; font-size: 13px; padding: 8px 16px; border-top: 1px solid #3b8eea; }
.ruta { font-size: 12px; color: #a9a9a9; padding: 4px 16px 6px; }
.codigo { display: flex; font-family: 'JetBrains Mono', 'DejaVu Sans Mono', monospace; font-size: 13.5px; line-height: 20px; padding: 6px 0 14px; }
.numeros { color: #858585; text-align: right; padding: 0 18px 0 14px; user-select: none; white-space: pre; }
.codigo pre { margin: 0; white-space: pre; font: inherit; padding-right: 24px; }
.codigo pre code.hljs { padding: 0; background: transparent; font: inherit; }
.panel { min-width: 980px; }
.panel .pestanas-panel { display: flex; gap: 22px; font-size: 11px; color: #969696; padding: 8px 16px; letter-spacing: .04em; border-bottom: 1px solid #2b2b2b; }
.panel .pestanas-panel .act { color: #e7e7e7; border-bottom: 1px solid #e7e7e7; padding-bottom: 4px; }
.terminal { font-family: 'JetBrains Mono', 'DejaVu Sans Mono', monospace; font-size: 13px; line-height: 19px; padding: 10px 16px 16px; white-space: pre; color: #cccccc; }
.md-vista { width: 1180px; padding: 10px 26px 22px; font-size: 13.5px; line-height: 1.5; color: #cccccc; }
.md-vista h1 { font-size: 22px; color: #e8e8e8; padding-bottom: 6px; border-bottom: 1px solid #3c3c3c; margin: 6px 0 12px; }
.md-vista h2 { font-size: 17px; color: #e8e8e8; margin: 16px 0 8px; }
.md-vista p { margin: 0 0 9px; }
.md-vista code { font-family: 'DejaVu Sans Mono', monospace; font-size: 12px; background: #2d2d2d; padding: 1px 4px; border-radius: 3px; color: #ce9178; }
.md-vista table { border-collapse: collapse; margin: 6px 0 12px; font-size: 12.5px; }
.md-vista th, .md-vista td { border: 1px solid #454545; padding: 5px 8px; text-align: left; vertical-align: top; }
.md-vista th { background: #2a2a2a; color: #e8e8e8; }
.md-vista pre { font-family: 'DejaVu Sans Mono', monospace; font-size: 12px; background: #2d2d2d; padding: 8px 12px; margin: 0 0 10px; }
.terminal .prompt { color: #23d18b; } .terminal .ok { color: #23d18b; font-weight: 700; } .terminal .omit { color: #6a9955; }
"""

PLANTILLA = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/vs2015.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>{estilo}</style></head><body>{cuerpo}
<script>document.querySelectorAll('pre code').forEach(b => hljs.highlightElement(b));</script></body></html>"""

ICONOS = {'.py': ('py', 'Py'), '.html': ('html', '<>'), '.css': ('css', '#'), '.js': ('js', 'JS'),
          '.webm': ('webm', '▶'), '.png': ('png', '▣'), '.md': ('md', 'M↓'), '.json': ('js', '{}')}


def ventana(titulo, contenido):
    return (f'<div class="ventana"><div class="barra"><span class="puntos">● ● ●</span>'
            f'{html.escape(titulo)} — appdesarrollo — Visual Studio Code</div>{contenido}</div>')


# ---------- explorador de carpetas ----------
def fila(nombre, nivel, carpeta=False, abierta=False, sel=False):
    sangria = 10 + nivel * 14
    if carpeta:
        chev = '⌄' if abierta else '›'
        return (f'<div class="fila carpeta{" sel" if sel else ""}" style="padding-left:{sangria}px">'
                f'<span class="chev">{chev}</span>{html.escape(nombre)}</div>')
    clase, letra = ICONOS.get(Path(nombre).suffix, ('', '·'))
    return (f'<div class="fila{" sel" if sel else ""}" style="padding-left:{sangria + 14}px">'
            f'<span class="ic {clase}">{html.escape(letra)}</span>{html.escape(nombre)}</div>')


def arbol(carpeta, abiertas, nivel=0, sel=None):
    """Filas del explorador; solo se despliegan las rutas de `abiertas` (relativas a la raíz del repo)."""
    filas = []
    hijos = sorted(
        (h for h in carpeta.iterdir() if h.name not in ('__pycache__', '.agents', 'skills-lock.json')),
        key=lambda h: (h.is_file(), h.name.lower()),
    )
    for hijo in hijos:
        rel = hijo.relative_to(RAIZ).as_posix()
        if hijo.is_dir():
            abierta = rel in abiertas
            filas.append(fila(hijo.name, nivel, carpeta=True, abierta=abierta))
            if abierta:
                filas += arbol(hijo, abiertas, nivel + 1, sel)
        else:
            filas.append(fila(hijo.name, nivel, sel=(rel == sel)))
    return filas


def explorador(raiz, abiertas, titulo, sel=None):
    filas = [fila(raiz.name.upper() if raiz == RAIZ else raiz.name, 0, carpeta=True, abierta=True)]
    filas += arbol(raiz, abiertas, 1, sel)
    lateral = f'<div class="lateral"><div class="titulo">EXPLORADOR</div>{"".join(filas)}</div>'
    return ventana(titulo, f'<div class="cuerpo">{lateral}</div>')


# ---------- fragmentos de código ----------
def rango_de(archivo, nombre):
    """Líneas (inicio, fin) de la función o método `nombre`, con sus decoradores."""
    arbol_py = ast.parse(archivo.read_text())
    for nodo in ast.walk(arbol_py):
        if isinstance(nodo, (ast.FunctionDef, ast.ClassDef)) and nodo.name == nombre:
            inicio = min([nodo.lineno] + [d.lineno for d in nodo.decorator_list])
            return inicio, nodo.end_lineno
    raise ValueError(f'{nombre} no está en {archivo}')


def fragmento(archivo, nombre, clase=None):
    inicio, fin = rango_de(archivo, nombre)
    lineas = archivo.read_text().splitlines()[inicio - 1:fin]
    numeros = '\n'.join(str(n) for n in range(inicio, fin + 1))
    rel = archivo.relative_to(RAIZ)
    migas = ' › '.join(rel.parts) + (f' › {clase}' if clase else '') + f' › {nombre}'
    editor = (f'<div class="editor"><div class="pestanas"><div class="pestana">'
              f'<span class="ic py">Py</span>{archivo.name}</div></div>'
              f'<div class="ruta">{html.escape(migas)}</div>'
              f'<div class="codigo"><div class="numeros">{numeros}</div>'
              f'<pre><code class="language-python">{html.escape(chr(10).join(lineas))}</code></pre></div></div>')
    return ventana(archivo.name, editor)


# ---------- vista previa de Markdown ----------
def en_linea(texto):
    texto = html.escape(texto)
    texto = re.sub(r'`([^`]+)`', r'<code>\1</code>', texto)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', texto)


def markdown_a_html(md):
    """Lo justo para los índices de evidencia: títulos, párrafos, tablas y bloques de código."""
    partes, tabla, codigo = [], [], None
    for linea in md.splitlines() + ['']:
        if codigo is not None:
            if linea.startswith('```'):
                partes.append(f'<pre>{html.escape(chr(10).join(codigo))}</pre>')
                codigo = None
            else:
                codigo.append(linea)
            continue
        if linea.startswith('|'):
            celdas = [c.strip() for c in linea.strip('|').split('|')]
            if not all(set(c) <= set('-: ') for c in celdas):
                tabla.append(celdas)
            continue
        if tabla:
            cab, *filas = tabla
            partes.append('<table><tr>' + ''.join(f'<th>{en_linea(c)}</th>' for c in cab) + '</tr>'
                          + ''.join('<tr>' + ''.join(f'<td>{en_linea(c)}</td>' for c in f) + '</tr>' for f in filas)
                          + '</table>')
            tabla = []
        if linea.startswith('```'):
            codigo = []
        elif linea.startswith('## '):
            partes.append(f'<h2>{en_linea(linea[3:])}</h2>')
        elif linea.startswith('# '):
            partes.append(f'<h1>{en_linea(linea[2:])}</h1>')
        elif linea.strip():
            partes.append(f'<p>{en_linea(linea)}</p>')
    return ''.join(partes)


def vista_markdown(archivo, hasta=None):
    """Vista previa del archivo; con `hasta`, solo lo que está antes de esa línea (p. ej. el primer '## ')."""
    rel = archivo.relative_to(RAIZ)
    md = archivo.read_text()
    if hasta:
        md = md.split(hasta, 1)[0]
    cuerpo = (f'<div class="editor"><div class="pestanas"><div class="pestana">'
              f'<span class="ic md">M↓</span>Vista previa {archivo.name}</div></div>'
              f'<div class="ruta">{html.escape(" › ".join(rel.parts))}</div>'
              f'<div class="md-vista">{markdown_a_html(md)}</div></div>')
    return ventana(f'Vista previa {archivo.name}', cuerpo)


# ---------- terminal ----------
RUIDO = ('  Apply', 'Operations to perform', '  Apply all migrations', 'Synchroniz', '  Creating table',
         'Running deferred', 'Running migrations', '  Synchronize unmigrated')


def terminal(*ejecuciones):
    """Panel de terminal con uno o varios pares (comando, salida)."""
    bloques = [bloque_terminal(comando, salida) for comando, salida in ejecuciones]
    cuerpo = (f'<div class="panel"><div class="pestanas-panel"><span>PROBLEMAS</span><span>SALIDA</span>'
              f'<span class="act">TERMINAL</span></div><div class="terminal">' + '\n'.join(bloques) + '</div></div>')
    return ventana('Terminal', cuerpo)


def bloque_terminal(comando, salida):
    lineas, omitidas = [], 0
    for linea in salida.splitlines():
        if linea.startswith(RUIDO):
            omitidas += 1
            continue
        if omitidas:
            lineas.append(f'<span class="omit">  … {omitidas} líneas de migraciones de la base de prueba omitidas</span>')
            omitidas = 0
        esc = html.escape(linea)
        if linea.strip() == 'OK' or linea.endswith(' ... ok'):
            esc = esc.replace(' ... ok', ' ... <span class="ok">ok</span>') if ' ... ok' in linea else f'<span class="ok">{esc}</span>'
        lineas.append(esc)
    return f'<span class="prompt">{html.escape(PROMPT)}</span> {html.escape(comando)}\n' + '\n'.join(lineas)


def correr(*args):
    # stdout y stderr juntos y en orden, como se ven en la terminal
    r = subprocess.run([sys.executable, 'manage.py', *args], cwd=PROYECTO, env={**os.environ, 'PYTHONUNBUFFERED': '1'},
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if r.returncode:
        raise SystemExit(f'Falló manage.py {" ".join(args)}:\n{r.stdout}')
    return r.stdout


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    capturas = {
        'P3_01a_carpetas_core': explorador(RAIZ / 'sistema_rendimiento', {
            'sistema_rendimiento/core', 'sistema_rendimiento/core/tests', 'sistema_rendimiento/core/views',
        }, 'Explorador'),
        'P3_01b_carpetas_apps_nuevas': explorador(RAIZ / 'sistema_rendimiento', {
            'sistema_rendimiento/ahorro', 'sistema_rendimiento/e2e', 'sistema_rendimiento/estadisticas',
        }, 'Explorador'),
        'P3_02_carpeta_de_evidencias_e2e': explorador(RAIZ / 'docs', {
            'docs/evidencias', 'docs/evidencias/e2e',
        }, 'Explorador', sel='docs/evidencias/e2e/07_ahorro.webm'),
        'P3_03_prueba_datos_por_usuario': fragmento(
            PROYECTO / 'core' / 'tests' / 'test_por_usuario.py', 'test_paginas_de_datos_ajenos_dan_404', 'DatosPorUsuarioTests'),
        'P3_04_prueba_retiro_rechazado': fragmento(
            PROYECTO / 'ahorro' / 'tests.py', 'test_retiro_mayor_a_lo_ahorrado_se_rechaza', 'AhorroTests'),
        'P3_05_prueba_rachas': fragmento(PROYECTO / 'estadisticas' / 'tests.py', 'test_rachas', 'CalculosTests'),
        'P3_06_prueba_e2e_ahorro': fragmento(PROYECTO / 'e2e' / 'test_flujos.py', 'test_07_ahorro', 'FlujosE2E'),
        'P3_09_documentacion_de_flujos': vista_markdown(RAIZ / 'docs' / 'evidencias' / 'e2e' / 'indice.md', hasta='\n## '),
    }
    if '--sin-pruebas' not in sys.argv:
        print('Ejecutando pruebas unitarias…')
        capturas['P3_07_terminal_pruebas_unitarias'] = terminal(
            *[(f'python manage.py test {app}', correr('test', app)) for app in ('core', 'estadisticas', 'ahorro')])
    if '--sin-pruebas' not in sys.argv and '--sin-e2e' not in sys.argv:
        print('Ejecutando flujos E2E…')
        capturas['P3_08_terminal_pruebas_e2e'] = terminal(('python manage.py test e2e', correr('test', 'e2e')))

    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page(device_scale_factor=2)
        for nombre, cuerpo in capturas.items():
            pagina.set_content(PLANTILLA.format(estilo=ESTILO, cuerpo=cuerpo), wait_until='networkidle')
            pagina.locator('.ventana').screenshot(path=SALIDA / f'{nombre}.png')
            print('  ', nombre)
        navegador.close()


if __name__ == '__main__':
    main()
