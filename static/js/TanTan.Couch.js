/*global TodoMVC */
'use strict';

TanTan.module('Couch', function (Couch, App, Backbone, Marionette, $, _) {

    Couch.API= function () {
        this.url = '';
        this.sess = null;
        this.wsuri = null;
    };

    _.extend(Couch.API.prototype, {
        connect: function () {
        }
    });

});
