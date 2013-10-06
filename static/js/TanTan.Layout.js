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
        className: 'navbar-form navbar-right'
    });
});
