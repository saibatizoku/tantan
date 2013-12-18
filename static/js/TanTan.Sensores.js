/*global TanTanApp */
'use strict';

TanTan.module('Sensores', function(Sensores, App, Backbone) {

    Sensores.XBee = App.Models.Base.extend({
        idAttribute: 'node_id',
        defaults: {
            nombre: '',
            node_id: '',
            node_type: '',
            sensor: '',
            value: '',
            pin: '',
            pan_id: ''
        }
    });

    //DOCS - Collection of documents
    Sensores.Docs= Backbone.Collection.extend({
    });

});
