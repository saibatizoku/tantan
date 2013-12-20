$(function () {
    TanTan.addInitializer(function () {
        var controller = new TanTan.API.Controller();
        var router = new TanTan.API.Router({
            controller: controller
        });
        var zbrouter = new TanTan.API.ZBRouter({
            controller: controller
        });
        this.router = router;
        this.zbrouter = zbrouter;
        this.controller = controller;
        //var api = new TanTan.WAMP.API();
        var api = TanTan.AutoBahn;
        var wsprot = "ws://";
        if (window.location.protocol == 'https:') {
            wsprot = "wss://";
        }
        var wsuri = wsprot + window.location.hostname + ":8080/ws_couch";
        api.wsuri = wsuri;
        api.connect();

        function onRX(topicUri, event) {
            ab.log('RX msg', event);
        }

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

            //sess.subscribe("zb:zb-nd", onND);
            sess.subscribe("zb:amb-rx", onRX);

            api.login(['granja-admin', 'nimda']);
        });
        TanTan.vent.on('wamp:failure', function (session) {
            ab.log('WAMP session FAILED');
        });
        TanTan.vent.on('granjas:login', function (info) {
            ab.log('Logging in');
        });
        TanTan.vent.on('granjas:logout', function () {
            ab.log('Logging out');
            api.logout();
            if (TanTan.user_info) {
                delete TanTan.user_info;
            }
            controller.loggedOut();
        });
        TanTan.vent.on('granjas:loggedIn', function (info) {
            ab.log('Logged in', info);
            controller.loggedIn(info);
            api.getSession();
            //var usr = ;
            var usr_view = new TanTan.Layout.Views.UserInfoView();
            api.getGranjaInfo();
            api.getEstanqueInfo();
        });
        TanTan.vent.on('granjas:loggedOut', function (info) {
            ab.log('Logged out', info);
            controller.loggedOut();
        });
        TanTan.vent.on('granjas:edit-profile', function (info) {
            ab.log('Editing user profile');
            controller.showUserEdit();
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
