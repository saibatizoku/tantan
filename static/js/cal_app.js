$(function () {
    TanTan.addInitializer(function () {
        var agenda = new TanTan.Calendario.Vistas.Agenda();

        var newevent = new TanTan.Calendario.Vistas.EventoNuevo();
        var evts = TanTan.Calendario.eventos = new TanTan.Calendario.EventosColeccion();

        var vw = new TanTan.Calendario.Vistas.AgendaGranja({
            collection: evts
        });
        var levw = new TanTan.Calendario.Vistas.ListaEventos({
            collection: evts
        });
        TanTan.main.show(agenda);
        agenda.calendar.show(vw);
        agenda.nav.show(levw);

        var api = TanTan.AutoBahn;
        var wsprot = "ws://";
        if (window.location.protocol == 'https:') {
            wsprot = "wss://";
        }
        var wsuri = wsprot + window.location.hostname + ":8080/ws_couch";
        api.wsuri = wsuri;
        api.connect();

        TanTan.vent.on('wamp:success', function (sess) {
            ab.log('WAMP session SUCCESS');

            sess.prefix("db", "http://www.tantan.org/api/datos/info#");
            sess.prefix("zb", "http://www.tantan.org/api/sensores#");
            log_line = "Event PubSub ready";
            ab.log(log_line);

            sess.prefix("rpc", "http://www.tantan.org/api/datos#");
            sess.prefix("zbrpc", "http://www.tantan.org/api/sensores-control#");
            log_line = "RPC ready"
            ab.log(log_line);
            
            ab.log('WAMP session OK');

            api.login(['admin', 'nimda']);
        });

    });
    TanTan.start();
});
