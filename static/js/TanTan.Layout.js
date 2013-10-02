/*global TodoMVC */
'use strict';

TanTan.module('Layout', function (Layout, App, Backbone) {
    // Navbar Layout 
    // ------------------
    Layout.Nav = Backbone.Marionette.Layout.extend({
        template: '#appnav',
        regions: {
            menu: '#nav-menu',
            actions: '#nav-actions'
        }
    });
});
