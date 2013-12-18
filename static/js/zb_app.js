$(function () {
    TanTan.addInitializer(function () {

        var api = new TanTan.WAMP.API();
        var wsprot = "ws://";
        if (window.location.protocol == 'https:') {
            wsprot = "wss://";
        }
        var wsuri = wsprot + window.location.hostname + ":8080/ws_couch";
        api.wsuri = wsuri;
        this.wamp_api = api;
        this.wamp_api.connect();

        var mn = $("#main");

        var ambg = $("<div id='ambg' class='col-md-3'>");
        var potg = $("<div id='potg' class='col-md-3'>");
        var solg = $("<div id='solg' class='col-md-3'>");

        var amb = $("#ambr");
        var pot = $("#potr");
        var sol = $("#solr");

        this.sensores = new TanTan.Sensores.Docs();

        var ambHum = new TimeSeries();
        var ambTem = new TimeSeries();
        var ambPre = new TimeSeries();

        var humsmoothie = new SmoothieChart({
            grid: {
                strokeStyle: 'rgb(125, 0, 0)',
                fillStyle: 'rgb(171, 171, 255)',
                lineWidth: 1,
                verticalSections: 6
            },
            millisPerPixel: 500,
            minValue: 0.0,
            maxValue: 100.0,
            resetBounds: false
        });

        var presmoothie = new SmoothieChart({
            grid: {
                strokeStyle: 'rgb(125, 0, 0)',
                fillStyle: 'rgb(171, 171, 255)',
                lineWidth: 1,
                verticalSections: 6
            },
            millisPerPixel: 500,
            minValue: 900.0,
            maxValue: 1100.0,
            resetBounds: false
        });

        var temsmoothie = new SmoothieChart({
            grid: {
                strokeStyle: 'rgb(125, 0, 0)',
                fillStyle: 'rgb(171, 171, 255)',
                lineWidth: 1,
                verticalSections: 6
            },
            millisPerPixel: 500,
            minValue: 0.0,
            maxValue: 50.0,
            resetBounds: false
        });

        humsmoothie.addTimeSeries(ambHum, { strokeStyle: 'rgb(0, 115, 0)', lineWidth: 2 });
        presmoothie.addTimeSeries(ambPre, { strokeStyle: 'rgb(90, 115, 0)', lineWidth: 2 });
        temsmoothie.addTimeSeries(ambTem, { strokeStyle: 'rgb(0, 115, 90)', lineWidth: 2 });

        humsmoothie.streamTo(document.getElementById('ambgh'));
        presmoothie.streamTo(document.getElementById('ambgp'));
        temsmoothie.streamTo(document.getElementById('ambgt'));

        var volsmoothie = new SmoothieChart({
            grid: {
                strokeStyle: 'rgb(125, 0, 0)',
                fillStyle: 'rgb(171, 171, 255)',
                lineWidth: 1,
                verticalSections: 6
            },
            millisPerPixel: 500,
            minValue: 0.0,
            maxValue: 160.0,
            resetBounds: false
        });

        var corsmoothie = new SmoothieChart({
            grid: {
                strokeStyle: 'rgb(125, 0, 0)',
                fillStyle: 'rgb(171, 171, 255)',
                lineWidth: 1,
                verticalSections: 6
            },
            millisPerPixel: 500,
            minValue: 0.0,
            maxValue: 50.0,
            resetBounds: false
        });

        var watsmoothie = new SmoothieChart({
            grid: {
                strokeStyle: 'rgb(125, 0, 0)',
                fillStyle: 'rgb(171, 171, 255)',
                lineWidth: 1,
                verticalSections: 6
            },
            millisPerPixel: 500,
            minValue: 0.0,
            maxValue: 1500.0,
            resetBounds: false
        });

        var potV = new TimeSeries();
        var potC1 = new TimeSeries();
        var potC2 = new TimeSeries();
        var potC3 = new TimeSeries();
        var potW1 = new TimeSeries();
        var potW2 = new TimeSeries();
        var potW3 = new TimeSeries();

        volsmoothie.addTimeSeries(potV, { strokeStyle: 'rgb(0, 115, 0)', lineWidth: 2 });
        corsmoothie.addTimeSeries(potC1, { strokeStyle: 'rgb(90, 115, 0)', lineWidth: 2 });
        corsmoothie.addTimeSeries(potC2, { strokeStyle: 'rgb(90, 115, 0)', lineWidth: 2 });
        corsmoothie.addTimeSeries(potC3, { strokeStyle: 'rgb(90, 115, 0)', lineWidth: 2 });
        watsmoothie.addTimeSeries(potW1, { strokeStyle: 'rgb(0, 105, 90)', lineWidth: 2 });
        watsmoothie.addTimeSeries(potW2, { strokeStyle: 'rgb(0, 105, 90)', lineWidth: 2 });
        watsmoothie.addTimeSeries(potW3, { strokeStyle: 'rgb(0, 105, 90)', lineWidth: 2 });

        volsmoothie.streamTo(document.getElementById('potgV'));
        corsmoothie.streamTo(document.getElementById('potgC'));
        watsmoothie.streamTo(document.getElementById('potgW'));

        function onRX(topicUri, event) {
            ab.log('RX msg', event);
            var nsens = new TanTan.Sensores.XBee(event);
            console.log('nuevo sensor', nsens);
            switch (event.node_type) {
                case 'AMB':
                    TanTan.vent.trigger('sensor:amb', nsens);
                    switch (event.sensor) {
                        case 'humedad':
                            $("#instH").text(event.value);
                            ambHum.append(new Date().getTime(), event.value);
                            break;
                        case 'presion':
                            $("#instP").text(event.value);
                            ambPre.append(new Date().getTime(), event.value);
                            break;
                        case 'temp':
                            if (event.pin == 'I2C') {
                                $("#instT").text(event.value);
                                ambTem.append(new Date().getTime(), event.value);
                            }
                            break;
                        default:
                            break;
                    }
                    break;
                case 'SOLAR':
                    newp.text('Nodo solar');
                    sol.append(newp);
                    break;
                case 'POT':
                    switch (event.sensor) {
                        case 'volt':
                            $("#instV").text(event.value);
                            potV.append(new Date().getTime(), event.value);
                            break;
                        case 'amp':
                            switch (event.pin) {
                                case 'A1':
                                    $("#instC1").text(event.value);
                                    potC1.append(new Date().getTime(), event.value);
                                    break;
                                case 'A2':
                                    $("#instC2").text(event.value);
                                    potC2.append(new Date().getTime(), event.value);
                                    break;
                                case 'A3':
                                    $("#instC3").text(event.value);
                                    potC3.append(new Date().getTime(), event.value);
                                    break;
                            }
                            break;
                        case 'PotReal':
                            var kw = event.value/1000;
                            kwstr = kw.toFixed();
                            switch (event.pin) {
                                case 'A0A1':
                                    $("#instW1").text(kwstr);
                                    potW1.append(new Date().getTime(), event.value);
                                    break;
                                case 'A0A2':
                                    $("#instW2").text(kwstr);
                                    potW2.append(new Date().getTime(), event.value);
                                    break;
                                case 'A0A3':
                                    $("#instW3").text(kwstr);
                                    potW3.append(new Date().getTime(), event.value);
                                    break;
                                default:
                                    break;
                            }
                            break;
                    }
                    break;
                default:
                    newp.text("Nodo desconocido\r\n");
                    mn.append(newp);
                    break;
            }
        }

        TanTan.vent.on('wamp:success', function (sess) {
            ab.log('WAMP session SUCCESS');
            TanTan.wamp_sess = sess;

            sess.prefix("db", "http://www.tantan.org/api/datos/info#");
            sess.prefix("zb", "http://www.tantan.org/api/sensores#");
            log_line = "Event PubSub ready";
            ab.log(log_line);

            sess.prefix("rpc", "http://www.tantan.org/api/datos#");
            sess.prefix("zbrpc", "http://www.tantan.org/api/sensores-control#");
            log_line = "RPC ready"
            ab.log(log_line);
            
            ab.log('WAMP session OK');

            //sess.subscribe("zb:zb-nd", onND);
            sess.subscribe("zb:amb-rx", onRX);

            TanTan.wamp_api.login(['granja-admin', 'nimda']);
        });
        TanTan.vent.on('wamp:failure', function (session) {
            ab.log('WAMP session FAILED');
            //if (TanTan.wamp_sess) {
            //    delete TanTan.wamp_sess;
            //};
        });
        TanTan.vent.on('granjas:login', function (info) {
            ab.log('Logging in');
            TanTan.wamp_api.login(info.creds);
        });
        TanTan.vent.on('granjas:logout', function () {
            ab.log('Logging out');
            TanTan.wamp_api.logout();
            if (TanTan.user_info) {
                delete TanTan.user_info;
            }
            //controller.loggedOut();
        });
        TanTan.vent.on('granjas:loggedIn', function (info) {
            ab.log('Logged in', info);
            //controller.loggedIn(info);
            TanTan.wamp_api.getSession();
            //var usr = ;
            var usr_view = new TanTan.Layout.Views.UserInfoView();
            TanTan.wamp_api.getGranjaInfo();
            TanTan.wamp_api.getEstanqueInfo();
        });
        TanTan.vent.on('granjas:loggedOut', function (info) {
            ab.log('Logged out', info);
            //controller.loggedOut();
        });
        TanTan.vent.on('granjas:edit-profile', function (info) {
            ab.log('Editing user profile');
            //controller.showUserEdit();
        });
        TanTan.vent.on('granjas:user', function (info) {
            ab.log('Adding user to TanTan');
            TanTan.user_info = info;
        });
        TanTan.vent.on('granjas:anon', function (info) {
            ab.log('Anonymous user');
        });
    });
    TanTan.start();
});
