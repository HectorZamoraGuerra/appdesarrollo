"""Storyboard de cada video E2E: 6 cuadros repartidos a lo largo del flujo, en una cuadrícula de 3 × 2.

Uso (desde la raíz del repo):  python docs/capturas/storyboards_e2e.py
Entrada: docs/evidencias/e2e/*.webm · Salida: docs/capturas/parcial3/E2E_<flujo>.png · Requiere ffmpeg.
"""
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
VIDEOS = RAIZ / 'docs' / 'evidencias' / 'e2e'
SALIDA = RAIZ / 'docs' / 'capturas' / 'parcial3'
CUADROS = 6


def duracion(video):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video],
                       capture_output=True, text=True, check=True)
    return float(r.stdout)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for video in sorted(VIDEOS.glob('*.webm')):
        # fps = CUADROS / duración toma un cuadro cada intervalo; el último cuadro (estado final) entra completo
        fps = CUADROS / duracion(video)
        destino = SALIDA / f'E2E_{video.stem}.png'
        subprocess.run([
            'ffmpeg', '-v', 'error', '-y', '-i', video,
            '-vf', f'fps={fps:.4f},scale=640:-1,tile=3x2:padding=10:margin=10:color=0xD0D3D8',
            '-frames:v', '1', destino,
        ], check=True)
        print('  ', destino.name)


if __name__ == '__main__':
    main()
