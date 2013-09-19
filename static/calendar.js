$(document).ready(function() {
    var date = new Date();
    var d = date.getDate();
    var m = date.getMonth();
    var y = date.getFullYear();
    var evts =  [
        {title: 'Evento 1', start: new Date(y, m, 1)},
        {title: 'Evento 2', start: new Date(y, m, d-5), end: new Date(y, m, d-2)},
        {id: 999, title: 'Evento 3', start: new Date(y, m, d-3, 16, 0), allDay: false},
        {id: 999,title: 'Evento 3', start: new Date(y, m, d+4, 16, 0), allDay: false},
        {title: 'Evento 4', start: new Date(y, m, d, 10, 30), allDay: false},
        {title: 'Evento 5', start: new Date(y, m, d, 12, 0), end: new Date(y, m, d, 14, 0), allDay: false},
        {title: 'Evento 6', start: new Date(y, m, d+1, 19, 0), end: new Date(y, m, d+1, 22, 30), allDay: false},
        {title: 'Evento 7 con url', start: new Date(y, m, 28), end: new Date(y, m, 29), url: 'http://google.com/'}
    ];

    $('.calendario').fullCalendar({
        dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
        dayNamesShort: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa'],
        monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
            'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        monthNamesShort: ['Ene', 'Feb', 'Mar', 'Abr', 'Mayo', 'Jun', 'Jul',
            'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        titleFormat: {
            month: 'MMM yyyy',                             // September 2009
            week: "MMM d[ yyyy]{ '&#8212;'[ MMM] d yyyy}", // Sep 7 - 13 2009
            day: 'd/MMM/yy'                  // 8/Sep/09
        },
        defaultView: 'agendaDay',
        allDayText: 'todo día',
        firstDay: 1,
        aspectRatio: 2,
        buttonText: {
            today: 'hoy',
            month: 'mes',
            week: 'semana',
            day:   'día',
        },
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        editable: true,
        events: evts
    });
});
