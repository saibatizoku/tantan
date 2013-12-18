/*global TodoMVC */
'use strict';

TanTan.module('API', function (API, App, Backbone, Marionette, $, _) {
    API.Router = Marionette.AppRouter.extend({});

    API.Controller = Marionette.Controller.extend({
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
        showUserMain: function (user) {
            App.main.show(this.mainuser);
            var usr_view = new App.Views.UserDocView();
            this.mainuser.tools.show(new App.Layout.MainUserTools({model: user}));
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
    });
});
