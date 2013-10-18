/*global TodoMVC */
'use strict';

TanTan.module('Layout', function (Layout, App, Backbone) {
    // Navbar Layout 
    // ------------------
    Layout.Nav = Backbone.Marionette.Layout.extend({
        template: '#appnav',
        className: 'container',
        regions: {
            menu: '#nav-menu',
            user: '#nav-user',
            actions: '#nav-actions'
        }
    });

    Layout.NavActions  = Marionette.ItemView.extend({
        template: '#navactions',
        tagName: 'form',
        className: 'navbar-form navbar-right',
        ui: {
            input: '#login',
            user: '#usuario',
            password: 'input[name=contra]'
        },

        events: {
            'click #login': 'doLogin'
        },

        doLogin: function (e) {
            e.preventDefault();
            var r = [ this.ui.user.val(), this.ui.password.val()];
            App.vent.trigger('granjas:login', { creds: r, event: e});
        }
    });

    Layout.NavUserMenu  = Marionette.ItemView.extend({
        template: '#navmenu',
        tagName: 'ul',
        className: 'nav navbar-nav'
    });

    Layout.NavUserActions  = Marionette.ItemView.extend({
        template: '#navuseractions',
        tagName: 'form',
        className: 'navbar-form navbar-right',
        ui: {
            logout: '#logout'
        },

        events: {
            'click #logout': 'doLogout'
        },

        doLogout: function (e) {
            App.vent.trigger('granjas:logout');
        }
    });

    Layout.Main = Backbone.Marionette.Layout.extend({
        template: '#appmain',
        className: 'container',
        regions: {
            content: '#content',
            right: '#side-right',
            left: '#side-left'
        }
    });

    Layout.MainLeft = Marionette.ItemView.extend({
        template: '#mainleft'
    });

    Layout.MainRight = Marionette.ItemView.extend({
        template: '#mainright'
    });

    Layout.MainContent = Marionette.ItemView.extend({
        template: '#maincontent',
        className: 'container'
    });

});
