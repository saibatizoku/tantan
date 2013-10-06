/*global TodoMVC */
'use strict';

TanTan.module('Couch', function (Couch, App, Backbone, Marionette, $, _) {

    Couch.API= function () {
        this.url = '';
        this.sess = null;
        this.wsuri = null;
    };

    _.extend(Couch.API.prototype, {
        connect: function () {
            var sess = null;

            function onConnect() {
                var log_line = "WAMP success";
                ab.log(log_line);

                sess.prefix("event", "http://www.tantan.org/api/couchdb/info#");
                log_line = "Event PubSub ready";
                ab.log(log_line);

                sess.prefix("rpc", "http://www.tantan.org/api/couchdb#");
                log_line = "RPC ready"
                ab.log(log_line);
            }

            function onHangup(e) {
                var log_line = "WAMP failed";
                ab.log(log_line,e);
            }

            sess = new ab.Session(this.wsuri, onConnect, onHangup);
            this.sess = sess;
            ab.log('Couch.API session', sess);
            return sess;
        },
        login: function (creds) {
            this.sess.call('rpc:login', creds).always(this.doLogin);
        },
        doLogin: function (resp) {
            ab.log(resp);
            if (resp.ok) {
                App.vent.trigger('granjas:loggedIn', resp);
            } else {
                App.vent.trigger('granjas:loggedOut', resp);
            }
        }
    });

});
