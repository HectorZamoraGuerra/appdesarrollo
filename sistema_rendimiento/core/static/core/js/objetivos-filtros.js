(function () {
    // Al cambiar el orden se conservan los demás filtros de la URL (estado, categoría)
    const orden = document.getElementById('id_orden');

    if (!orden) return;

    orden.addEventListener('change', function () {
        const params = new URLSearchParams(window.location.search);
        params.set('orden', orden.value);
        window.location.search = params.toString();
    });
})();
