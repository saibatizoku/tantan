/*global TodoMVC */
'use strict';

TanTan.module('Routes', function (Routes, App, Backbone, Marionette, $, _) {

    var Router = Marionette.AppRouter.extend({
        appRoutes: {
            'inicio': 'home',
            'acceder': 'login',
            'reportes': 'datastore',
            'sensores': 'sensors'
        }
    });

    var API = {
        home: function () {
            App.Controller.go_home();
        },
        login: function () {
            App.Controller.go_login();
        },
        datastore: function () {
            App.Controller.go_datastore();
        },
        sensors: function () {
            App.Controller.go_sensors();
        }
    };

    App.addInitializer(function (options) {
        var router = new Router({controller: API});
    });
});
