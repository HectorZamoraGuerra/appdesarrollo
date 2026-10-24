(function () {
    // Una gráfica por cada <canvas class="grafica-rendimiento">; sus datos vienen de json_script
    // (ObjetivoActividadesView.datos_graficas): etiquetas, esperado, obtenido
    if (typeof Chart === 'undefined') return;

    const estilos = getComputedStyle(document.documentElement);
    const tinta = estilos.getPropertyValue('--ink').trim();
    const tenue = estilos.getPropertyValue('--muted').trim();
    const linea = estilos.getPropertyValue('--line').trim();

    Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
    Chart.defaults.color = tenue;

    document.querySelectorAll('canvas.grafica-rendimiento').forEach(function (canvas) {
        const fuente = document.getElementById(canvas.dataset.fuente);
        if (!fuente) return;
        const datos = JSON.parse(fuente.textContent);

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: datos.etiquetas,
                datasets: [
                    {
                        label: 'Obtenido',
                        data: datos.obtenido,
                        borderColor: tinta,
                        backgroundColor: tinta,
                        tension: 0.2,
                    },
                    {
                        label: 'Esperado',
                        data: datos.esperado,
                        borderColor: tenue,
                        backgroundColor: tenue,
                        borderDash: [6, 4],
                        // Con puntos para que se vea aunque haya una sola sesión
                        pointStyle: 'rectRot',
                        pointRadius: 4,
                    },
                ],
            },
            options: {
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: { legend: { position: 'bottom', labels: { usePointStyle: true } } },
                scales: {
                    // offset: deja margen a los lados; con una sola sesión el punto queda centrado
                    x: { offset: true, grid: { display: false } },
                    y: { beginAtZero: true, grid: { color: linea } },
                },
            },
        });
    });
})();
