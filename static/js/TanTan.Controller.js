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
            App.nav.show(this.nav);
        }
    });

    GranjasApp.addInitializer(function () {
        var controller = new GranjasApp.Controller();
        controller.router = new GranjasApp.Router({
            controller: controller
        });
        controller.start();
    });
});
