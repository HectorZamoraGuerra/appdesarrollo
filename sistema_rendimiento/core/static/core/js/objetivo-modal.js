(function () {
    const modal = document.getElementById('modal-objetivo');
    const openBtn = document.getElementById('btn-nuevo-objetivo');
    const closeBtn = document.getElementById('btn-cerrar-objetivo');
    const cancelBtn = document.getElementById('btn-cancelar-objetivo');
    const form = document.getElementById('form-objetivo');

    if (!modal) return;

    function abrir() {
        modal.hidden = false;
        document.getElementById('id_titulo').focus();
    }

    function cerrar() {
        modal.hidden = true;
        form.reset();
    }

    openBtn.addEventListener('click', abrir);
    closeBtn.addEventListener('click', cerrar);
    cancelBtn.addEventListener('click', cerrar);

    modal.addEventListener('click', function (event) {
        if (event.target === modal) cerrar();
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && !modal.hidden) cerrar();
    });
})();
