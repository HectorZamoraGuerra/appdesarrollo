document.addEventListener('DOMContentLoaded', () => {
  const calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
    locale: 'es',
    firstDay: 1,
    initialView: 'dayGridMonth',
    height: 'auto',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay',
    },
    // Cada evento trae `url`: al hacer clic el navegador va al detalle de la actividad
    events: '/api/actividades/',
  });
  calendar.render();
});
