$(function () {
    TanTan.addInitializer(function () {
        var api = TanTan.AutoBahn;
        var wsprot = "ws://";
        if (window.location.protocol == 'https:') {
            wsprot = "wss://";
        }
        var wsuri = wsprot + window.location.hostname + ":8080/ws_couch";
        api.wsuri = wsuri;
        api.connect();

        var controller_tantan = new TanTan.Sistema.Control.Controller();
        var router = new TanTan.Sistema.Control.Router({controller: controller_tantan});
        TanTan.gcontroller = controller_tantan;
        TanTan.grouter = router;

        var granjas_docs = [
    {'_id': 'xamapan-1', 'nombre': 'Xamapan', 'nodos': [{'_id': 'estks', 'nombre': 'Estankes', 'nodos': [{'nombre': 'B1'}, {'nombre': 'B2'}, {'nombre': '1'}, {'nombre': '2'}]}]},
    {'_id': 'exp-1', 'nombre': 'Granja experimental', 'nodos': [{'_id': 'estk2', 'nombre': 'Estankes', 'nodos': [{'nombre': 'B2'}, {'nombre': 'EXP1'}, {'nombre': '2TE'}]}]}];
        var nodos_sensores = [{
                'nombre': 'Central',
                'nodos': [{
                    'nombre': 'Estación base'
                }, {
                    'nombre': 'Red inalámbrica',
                    'nodos': [{
                        'nombre': '48e1',
                    }, {
                        'nombre': '84ac',
                    }]
                }]
        }, {
            'nombre': 'Nodo ambiental',
                'nodos': [{
                    'nombre': 'Humedad',
                }, {
                    'nombre': 'Presión',
                }, {
                    'nombre': 'Temperatura',
                }]
        }, {
            'nombre': 'Acuático Estanke 1',
            'nodos': [{
                'nombre': 'Temperatura',
            }, {
                'nombre': 'pH',
            }, {
                'nombre': 'OD',
            }, {
                'nombre': 'Amonio',
            }, {
                'nombre': 'Nitratos',
            }]
        }];
        //this.items.add([{'_id': 'uno', 'nombre': 'doc uno'}, {'nombre': 'doc dos', '_id': 'dos'}]);
        controller_tantan.granjas.add(granjas_docs);
        controller_tantan.nodos.add(nodos_sensores);

        function onSensor (sensor) {
            ab.log('sensor rx received', sensor);
        }
        TanTan.vent.on('wamp:success', function (sess) {
            ab.log('WAMP session SUCCESS');

            sess.prefix("db", "http://www.tantan.org/api/datos/info#");
            sess.prefix("zb", "http://www.tantan.org/api/sensores#");
            sess.prefix("zbn", "http://www.tantan.org/api/sensores/nodos#");
            log_line = "Event PubSub ready";
            ab.log(log_line);

            sess.prefix("rpc", "http://www.tantan.org/api/datos#");
            sess.prefix("zbrpc", "http://www.tantan.org/api/sensores-control#");
            log_line = "RPC ready"
            ab.log(log_line);
            
            ab.log('WAMP session OK');

            //sess.subscribe("zb:zb-nd", onND);
            sess.subscribe("zbn", onSensor);

            //api.login(['granja-admin', 'nimda']);
            TanTan.vent.trigger('granjas:login', {creds: ['admin', 'nimda']});
        });
        TanTan.vent.on('granjas:login', function (info) {
            ab.log('Logging in');
            api.login(info.creds);
        });
        TanTan.vent.on('granjas:logout', function () {
            ab.log('Logging out');
            api.logout();
        });
        TanTan.vent.on('granjas:loggedIn', function (user) {
            ab.log('loggedIn', user);
            api.get_granjas();
            controller_tantan.user = user;
            controller_tantan.goHome();
        });
        TanTan.vent.on('granjas:loggedOut', function () {
            ab.log('loggedOut');
            delete controller_tantan.user;
            controller_tantan.goHome();
        });
        TanTan.vent.on('nav:click', function (args) {
            //ab.log('nav clicked', args);
            //args.view.toggleCollapse();
        });
        TanTan.vent.on('wamp:failure', function (session) {
            ab.log('WAMP session FAILED');
        });
    });
    TanTan.start();
});
