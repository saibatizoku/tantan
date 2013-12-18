/*global TanTanApp */
'use strict';

TanTan.module('Calendario', function(Calendario, App, Backbone) {

    Calendario.DEFAULT_OPTIONS = {
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
                dayClick: function(date, allDay, jsEvent, view) {
                   console.log('dayClick');
                    if (allDay) {
                        console.log('Clicked on the entire day: ' + date);
                    }else{
                        console.log('Clicked on the slot: ' + date);
                    }
                    console.log('Coordinates: ' + jsEvent.pageX + ',' + jsEvent.pageY);
                    console.log('Current view: ' + view.name);
                    // change the day's background color just for fun
                    $(this).css('background-color', 'red');
                },
                selectable: true,
                selectHelper: true,
                defaultView: 'agendaDay',
                allDayText: 'todo día',
                firstDay: 1,
                aspectRatio: 2,
                contentHeight: 600,
                buttonText: {
                    today: 'Ir a hoy',
                    month: 'mes',
                    week: 'semana',
                    day:   'día',
                },
                header: {
                    left: 'prev,,today',
                    center: 'title',
                    right: 'next'
                    //left: 'prev,next today',
                    //center: 'title' //,
                    //right: 'month,agendaWeek,agendaDay'
                },
                editable: true //,
                //events: App.AutoBahn.get_events()
            };
    Calendario.Base = Backbone.Model.extend({
        idAttribute: '_id',
        defaults: {
            created_at: null,
            modified_at: null,
            created_by: null
        },
        initialize: function () {
            if (this.isNew()) {
                var now = new Date();
                this.set('created_at', now.toISOString());
                this.set('modified_at', now.toISOString());
            }
        },
    });

    Calendario.Evento = Calendario.Base.extend({
        defaults: {
            tipo: 'evento',
            title: '',
            description: '',
            url: '',
            start: null,
            end: null,
            allDay: false
        },
        modelAdded: function (model) {
            console.log('model added');
        },
        modelChanged: function (model, value) {
        },
        validate: function (attribs) {
            //if (!attr.nombre) {
            //    return 'Name needed'
            //}
            //if (!attr._id) {
            //    return 'ID Needed'
            //}
        }
    });

    Calendario.EventosColeccion = Backbone.Collection.extend({
        model: Calendario.Evento,
        url: 'eventos-info'
    });

});

TanTan.module('Calendario.Vistas', function(CalView, App, Backbone) {

    CalView.Agenda = Marionette.Layout.extend({
        template: '#template-agenda',
        className: 'container',
        regions: {
            calendar: '#cal-region',
            nav: '#cal-nav-region',
            user: '#cal-usr-region'
        },

        ui: {
            input: '#login',
            user: '#usuario',
            password: 'input[name=contra]'
        },

        events: {
            'click @ui.input': 'doLogin'
        },

        doLogin: function (e) {
            e.preventDefault();
            var r = [ this.ui.user.val(), this.ui.password.val()];
            App.vent.trigger('granjas:login', { creds: r, event: e});
        }
    });

    CalView.EventoNuevo = Marionette.ItemView.extend({
        className: 'panel panel-default',
        template: '#template-evento-nuevo',
    });

    CalView.EventoNav = Marionette.ItemView.extend({
        className: 'list-group-item',
        tagName: 'a',
        attributes: {
            'href': '#'
        },
        template: '#template-evento-nav',
        model: App.Calendario.Evento
    });

    CalView.ListaEventos = Marionette.CompositeView.extend({
        className: 'panel panel-default',
        template: '#template-lista-eventos',
        itemView: CalView.EventoNav,
        itemViewContainer: '#lista-eventos'
    });

    CalView.AgendaGranja = Marionette.ItemView.extend({
        className: 'panel panel-default',
        template: '#template-calendario',
        ui: {
            cal: '.calendario',
            vistas: '.btn-group',
            mes: '#ver-mes',
            semana: '#ver-semana',
            dia: '#ver-dia',
            prev: '#ver-prev',
            sig: '#ver-sig',
            date: 'div.bfh-datepicker',
            time: 'div.bfh-timepicker'
        },
        events: {
            'click @ui.mes': 'monthView',
            'click @ui.semana': 'weekView',
            'click @ui.dia': 'dayView',
            'click @ui.prev': 'goPrev',
            'click @ui.sig': 'goNext',
        },
        goPrev: function (e) {
            var thiscal = this.ui.cal;
            thiscal.fullCalendar('prev');
        },
        goNext: function (e) {
            var thiscal = this.ui.cal;
            thiscal.fullCalendar('next');
        },
        viewChoose: function (viewName, viewBtn) {
            var thiscal = this.ui.cal;
            //var thisview = thiscal.fullCalendar('getView');
            //if (thisview.name == viewName) {
            //    return;
            //}
            var viewbtns = this.ui.vistas;
            viewbtns.find('.active').removeClass('active');
            thiscal.fullCalendar('changeView', viewName);
            viewBtn.addClass('active');
            viewBtn.focus();
        },
        monthView: function () {
            this.viewChoose('month', this.ui.mes);
        },
        weekView: function () {
            this.viewChoose('agendaWeek', this.ui.semana);
        },
        dayView: function () {
            this.viewChoose('agendaDay', this.ui.dia);
        },
        startCal: function (calElem, opts) {
            calElem.fullCalendar(opts);
            calElem.fullCalendar('render');
        },
        closeCal: function (calElem) {
            calElem.fullCalendar('destroy');
        },
        //onRender: function () {
        onShowCalled: function () {
            var calview = this;
            var thiscal = this.ui.cal;
            var thisdia = this.ui.dia;
            function selectEvent (start, end, allDay, jsEvent, view) {
                console.log('selectEvent');
                var title = prompt('Event Title:');
                if (title) {
                    var evt = {
                            title: title,
                            start: start,
                            end: end,
                            allDay: allDay
                        };
                    //var new_evt = new App.Calendario.Evento(evt);
                    //new_evt.save();
                    calview.collection.create(evt);
                    thiscal.fullCalendar('renderEvent',
                            evt,
                            true // make the event "stick"
                            );
                    console.log('created event', evt);
                }
                thiscal.fullCalendar('unselect');
            };
            function dayClick (date, allDay, jsEvent, view) {
                var year = date.getUTCFullYear();
                var month = date.getUTCMonth();
                var day = date.getUTCDate();
                var thisview = thiscal.fullCalendar('getView');
                console.log('dayclick view', date, thisview);
                if (thisview.name != 'agendaDay') {
                    calview.viewChoose('agendaDay');
                }
                thiscal.fullCalendar('gotoDate', year, month, day);
            };
            function eventClick (event, jsEvent, view) {
                console.log('eventClick', event, jsEvent, view);
                if (view.name == 'agendaDay') {
                    var evdt = event.start;
                    console.log('edit event', evdt);
                } else {
                    var evdt = event.start;
                    var year = evdt.getUTCFullYear();
                    var month = evdt.getUTCMonth();
                    var day = evdt.getUTCDate();
                    console.log('going to', year, month, day);
                    thiscal.fullCalendar('gotoDate', year, month, day);
                    calview.dayView();
                }
                return false;
            };
            console.log('evento view rendered');
            var opts = App.Calendario.DEFAULT_OPTIONS;
            opts.select = selectEvent;
            opts.dayClick = null; //dayClick;
            opts.eventClick = eventClick;
            this.startCal(thiscal, opts);
            this.dayView();
            this.ui.time.each(function () {
                var $timepicker;
                $timepicker = $(this);
                $timepicker.bfhtimepicker($timepicker.data());
            });
            this.ui.date.each(function () {
                var $timepicker;
                $timepicker = $(this);
                $timepicker.bfhdatepicker($timepicker.data());
            });
        },
        onClose: function () {
            console.log('calendar closed'); this.closeCal(this.ui.cal);
        }
    });

});

TanTan.module('Calendario.Control', function(CalControl, App, Backbone) {
    CalControl.Controller = Marionette.Controller.extend({
        initialize: function () {
            var events = App.AutoBahn.get_events();
            console.log('app.autobahn.events', App.AutoBahn.get_events());
        }
    });
});
