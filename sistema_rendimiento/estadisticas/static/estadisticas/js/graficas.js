(function () {
    // Barras apiladas de completadas y vencidas por semana; los datos vienen de json_script
    // (estadisticas.views.panel): etiquetas, completadas, vencidas
    if (typeof Chart === 'undefined') return;

    const canvas = document.getElementById('grafica-semanas');
    const fuente = canvas && document.getElementById(canvas.dataset.fuente);
    if (!fuente) return;
    const datos = JSON.parse(fuente.textContent);

    const estilos = getComputedStyle(document.documentElement);
    const tinta = estilos.getPropertyValue('--ink').trim();
    const tenue = estilos.getPropertyValue('--muted').trim();
    const claro = estilos.getPropertyValue('--faint').trim();
    const linea = estilos.getPropertyValue('--line').trim();
    const superficie = estilos.getPropertyValue('--surface').trim();

    Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
    Chart.defaults.color = tenue;

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: datos.etiquetas,
            datasets: [
                {
                    label: 'Completadas',
                    data: datos.completadas,
                    backgroundColor: tinta,
                    // Punta redondeada solo si esa semana no tiene vencidas encima
                    borderRadius: (ctx) => (datos.vencidas[ctx.dataIndex] ? 0 : { topLeft: 4, topRight: 4 }),
                    maxBarThickness: 24,
                },
                {
                    // Va arriba: punta redondeada y 2px de separación con el color de la superficie
                    label: 'Vencidas',
                    data: datos.vencidas,
                    backgroundColor: claro,
                    borderColor: superficie,
                    borderWidth: { bottom: 2 },
                    borderSkipped: false,
                    borderRadius: { topLeft: 4, topRight: 4 },
                    maxBarThickness: 24,
                },
            ],
        },
        options: {
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, pointStyle: 'rectRounded' } },
                tooltip: { callbacks: { title: (items) => 'Semana del ' + items[0].label } },
            },
            scales: {
                x: { stacked: true, grid: { display: false } },
                y: { stacked: true, beginAtZero: true, ticks: { precision: 0 }, grid: { color: linea } },
            },
        },
    });
})();
