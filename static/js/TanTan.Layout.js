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
            var r = [ this.ui.user.val(), this.ui.password.val()];
            App.vent.trigger('granjas:login', { creds: r, event: e});
        }
    });
});
