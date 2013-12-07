/*global TodoMVC */
'use strict';

TanTan.module('AutoBahn', function (AutoBahn, App, Backbone, Marionette, $, _) {

    var sess;

    AutoBahn.wsuri = null;

    function onConnect() {
        var log_line = "AutoBahn Connection success";
        ab.log(log_line);
        App.vent.trigger('wamp:success', sess);
    }

    function onHangup(e) {
        var log_line = "AutoBahn Connection failed";
        ab.log(log_line,e);
        App.vent.trigger('wamp:failure');
    }

    AutoBahn.connect = function () {
        sess = new ab.Session(this.wsuri, onConnect, onHangup);
        ab.log('AutoBahn session', sess);
    };

});
