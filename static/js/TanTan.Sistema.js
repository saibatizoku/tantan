/*global TanTanApp */
'use strict';

TanTan.module('Sistema', function(Sistema, App, Backbone) {

    Sistema.Base = Backbone.Model.extend({
        idAttribute: '_id',
        defaults: {
            created_at: null,
            modified_at: null,
            created_by: null
        },
        initialize: function () {
            if (this.isNew()) {
                var now = new Date();
                this.set('created_at', now.toISOString());
                this.set('modified_at', now.toISOString());
            }
        },
    });

    Sistema.Documento= Sistema.Base.extend({
        defaults: {
            tipo: 'documento',
            title: '',
            description: ''
        },
        modelAdded: function (model) {
            console.log('model added');
        },
        modelChanged: function (model, value) {
        },
        validate: function (attribs) {
            //if (!attr.nombre) {
            //    return 'Name needed'
            //}
            //if (!attr._id) {
            //    return 'ID Needed'
            //}
        }
    });

    Sistema.Documentos = Backbone.Collection.extend({
        model: Sistema.Documento,
        url: 'documentos-info'
    });

    Sistema.Nodo = Sistema.Base.extend({
        initialize: function () {
            this.setNodes();
        },
        nodeCollection: function (nodes) {
            return new Sistema.Nodos(nodes);
        },
        setNodes: function () {
            var nodes = this.get('nodos');
            if (nodes) {
                this.nodos = this.nodeCollection(nodes);
                this.unset('nodos');
            }
        }
    });

    Sistema.ArbolGranjas = Sistema.Nodo.extend({
        nodeCollection: function (nodes) {
            return new Sistema.Granjas(nodes);
        }
    });

    Sistema.ArbolSensores = Sistema.Nodo.extend({
        nodeCollection: function (nodes) {
            return new Sistema.Estanques(nodes);
        }
    });

    Sistema.Granja = Sistema.Nodo.extend({
        defaults: {
            tipo: 'granja'
        },
        nodeCollection: function (nodes) {
            return new Sistema.Estanques(nodes);
        }
    });

    Sistema.Estanque = Sistema.Nodo.extend({
        defaults: {
            tipo: 'estanque'
        }
    });
    Sistema.Nodos = Backbone.Collection.extend({
        model: Sistema.Nodo,
        url: 'nodos'
    });
    Sistema.Granjas = Backbone.Collection.extend({
        model: Sistema.Granja,
        url: 'granjas'
    });
    Sistema.Estanques = Backbone.Collection.extend({
        model: Sistema.Estanque,
        url: 'estanque'
    });
});
