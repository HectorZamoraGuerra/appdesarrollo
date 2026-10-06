(function () {
    const modal = document.getElementById('modal-actividad');
    const openBtn = document.getElementById('btn-nueva-actividad');
    const closeBtn = document.getElementById('btn-cerrar-actividad');
    const cancelBtn = document.getElementById('btn-cancelar-actividad');
    const form = document.getElementById('form-actividad');

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
