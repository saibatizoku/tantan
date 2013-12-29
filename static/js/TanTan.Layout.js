/*global TodoMVC */
'use strict';

TanTan.module('Layout', function (Layout, App, Backbone) {
    // Navbar Layout 
    // ------------------
    Layout.Nav = Backbone.Marionette.Layout.extend({
        template: '#template-navbar',
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
        className: 'nav navbar-nav',
        ui: {
            'navlinks': 'li a',
            'navhome': 'li a[href=#home]',
            'navsensors': 'li a[href=#sensors]',
            'navagenda': 'li a[href=#agenda]'
        },
        events: {
            'click @ui.navlinks': 'navClick'
        },
        navClick: function (e) {
            var nav_el = $(e.currentTarget).parent();
            if (!nav_el.hasClass('active')) {
                this.toggleActive(nav_el);
            }
        },
        toggleActive: function (el) {
            this.$el.find(".active").toggleClass('active');
            el.toggleClass('active');
        }
    });

    Layout.NavUserActions  = Marionette.ItemView.extend({
        template: '#navuseractions',
        tagName: 'form',
        className: 'navbar-form navbar-right',
        ui: {
            edit: '#edit-profile',
            add: '#add-granja',
            logout: '#logout'
        },

        events: {
            'click #add-granja': 'doAddGranja',
            'click #edit-profile': 'doEditProfile',
            'click #logout': 'doLogout'
        },

        doAddGranja: function (e) {
            e.preventDefault();
            console.log('agregando granja');
            App.vent.trigger('granjas:nueva');
        },

        doEditProfile: function (e) {
            App.vent.trigger('granjas:edit-profile');
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

    Layout.MainUser = Backbone.Marionette.Layout.extend({
        template: '#appmainuser',
        className: 'container',
        regions: {
            content: '#content',
            tools: '#tools'
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

    Layout.MainUserContent = Backbone.Marionette.Layout.extend({
        template: '#mainusercontent',
        className: 'row',
        regions: {
            bar: '#user-bar',
            panel: '#user-panel'
        }
    });

    Layout.MainUserTools = Marionette.ItemView.extend({
        template: '#mainusertools',
        className: 'panel panel-info'
    });

    Layout.UserBar= Marionette.ItemView.extend({
        template: '#userbar',
        className: 'row'
    });

    Layout.UserPanel= Marionette.ItemView.extend({
        template: '#userpanel',
        className: 'panel panel-default'
    });

});
