/*global TanTan */
'use strict';

TanTan.module('Views', function (Views, App, Backbone, Marionette, $) {

    Views.BaseItemView = Marionette.ItemView.extend({
        modelEvents: {
            'change': 'render'
        }
    });

     Views.UserDocView = Views.BaseItemView.extend({
         template: '#template-userdoc'
    });

});
