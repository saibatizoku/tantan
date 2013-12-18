/*global TodoMVC */
'use strict';

TanTan.module('Controller', function (Controller, App, Backbone, Marionette, $, _) {

    App.Controller = {
        go_home: function () {
            console.log('go home');
        },
        go_login: function () {
            console.log('go login');
        },
        go_datastore: function () {
            console.log('go datastore');
        },
        go_sensors: function () {
            console.log('go sensores');
        },
        initialize: function () {
            this.nav = new App.Layout.Nav();
            this.main = new App.Layout.Main();
            this.mainuser = new App.Layout.MainUser();
            this.loggedOut();
        },
        showNav: function () {
            App.nav.show(this.nav);
            this.nav.actions.show(new App.Layout.NavActions());
        },
        showUserNav: function (user) {
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
        showUserMain: function (usermodel) {
            App.main.show(this.mainuser);
            this.mainuser.tools.show(new App.Layout.MainUserTools({model: usermodel}));
            this.maincontent = new App.Layout.MainUserContent();
            this.mainuser.content.show(this.maincontent);
            this.maincontent.bar.show(new App.Layout.UserBar());
            this.maincontent.panel.show(new App.Layout.UserPanel());
        },
        showUserEdit: function () {
            var usermodel = this.user;
            var usr_view = new App.Views.UserDocView({model: usermodel});
            this.maincontent.bar.close();
            this.maincontent.panel.show(usr_view);
        },
        loggedIn: function (userdoc) {
            var user = new App.Models.UserDoc(userdoc);
            ab.log('UserDoc', user);
            this.user = user;
            this.showUserNav();
            this.showUserMain(user);
        },
        loggedOut: function () {
            this.showNav();
            this.showMain();
        }
    };
});
