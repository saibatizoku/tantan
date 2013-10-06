/*global TodoMVC */
'use strict';

TanTan.module('GranjasApp', function (GranjasApp, App, Backbone, Marionette, $, _) {
    GranjasApp.Router = Marionette.AppRouter.extend({});

    GranjasApp.Controller = function () {
    };

    _.extend(GranjasApp.Controller.prototype, {
        start: function () {
            var Nav = new App.Layout.Nav();
            this.nav = Nav;
            this.showNav();
        },
        showNav: function () {
            App.nav.show(this.nav);
            this.nav.actions.show(new App.Layout.NavActions());
        },
        loggedIn: function () {
            this.nav.actions.close();
        },
        loggedOut: function () {
            this.showNav();
        }
    });

    GranjasApp.addInitializer(function () {
        var controller = new GranjasApp.Controller();
        controller.router = new GranjasApp.Router({
            controller: controller
        });
        controller.start();
        var api = new App.Couch.API();
        var wsuri = "ws://" + window.location.hostname + ":8080/ws";
        api.wsuri = wsuri;
        api.connect();

        App.vent.on('granjas:login', function (info) {
            ab.log('Logging in');
            api.login(info.creds);
        });
        App.vent.on('granjas:loggedIn', function (info) {
            ab.log('Logged in', info);
            controller.loggedIn();
        });
        App.vent.on('granjas:loggedOut', function (info) {
            ab.log('Logged out', info);
            controller.loggedOut();
        });
    });
});
