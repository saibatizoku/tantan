/*global TodoMVC */
'use strict';

TanTan.module('API', function (API, App, Backbone, Marionette, $, _) {
    API.Router = Marionette.AppRouter.extend({});

    API.Controller = Marionette.Controller.extend({
        initialize: function () {
            this.nav = new App.Layout.Nav();
            this.main = new App.Layout.Main();
            this.loggedOut();
        },
        showNav: function () {
            App.nav.show(this.nav);
            this.nav.actions.show(new App.Layout.NavActions());
        },
        showUserNav: function () {
            App.nav.show(this.nav);
            this.nav.menu.show(new App.Layout.NavUserMenu());
            this.nav.actions.show(new App.Layout.NavUserActions());
        },
        showMain: function () {
            App.main.show(this.main);
            this.main.right.show(new App.Layout.MainRight());
            this.main.content.show(new App.Layout.MainContent());
            this.main.left.show(new App.Layout.MainLeft());
        },
        loggedIn: function () {
            this.showUserNav();
        },
        loggedOut: function () {
            this.showNav();
            this.showMain();
        }
    });

    API.addInitializer(function () {
        var controller = new API.Controller();
        controller.router = new API.Router({
            controller: controller
        });
        this.controller = controller;
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
        App.vent.on('granjas:logout', function () {
            ab.log('Logging out');
            api.logout();
            controller.loggedOut();
        });
        App.vent.on('granjas:loggedOut', function (info) {
            ab.log('Logged out', info);
            controller.loggedOut();
        });
    });
});
