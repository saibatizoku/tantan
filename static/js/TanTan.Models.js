/*global TanTanApp */
'use strict';

TanTan.module('Models', function(Models, App, Backbone) {

    Models.Base = Backbone.Model.extend({ idAttribute: '_id' });

    Models.UserDoc = Models.Base.extend({
        defaults: {
            name: '',
            type: 'user',
            'org.tantan.user': {
                nombre: ''
            },
            password_sha: '',
            salt: '',
            granjas: [],
            roles: []
        },
        validate: function (attribs) {
            if (!attr.name) {
                return 'Name needed'
            }
            if (!attr._id) {
                return 'ID Needed'
            }
        }
    });

    Models.Doc = Models.Base.extend({
        initialize: function () {
            if (this.isNew()) {
                var tdy = new Date(Date.now());
                this.set('created_at', tdy.toISOString());
            }
        }
    });

    Models.Granja = Models.Doc.extend({
        defaults: {
            nombre: '',
            contacto: '',
            direccion: '',
            razonsocial: '',
            localidad: '',
            municipio: '',
            estado: '',
            tipo: 'granja'
        }
    });

    Models.Estanque = Models.Doc.extend({
        defaults: {
            "nombre":"",
            "tipo":"estanque",
            "granja_id":"",
            "forma":"",
            "volumen":"",
            "dimensiones":"",
            "material":""
        }
    });

    Models.Event = Models.Base.extend({
        defaults: {
            name: '',
            type: 'event'
        }
    });

    Models.Task= Models.Event.extend({
        defaults: {
            completed: false,
            name: '',
            type: 'task'
        },
        toggle: function () {
            return this.set('completed', !this.isCompleted());
        },
        isCompleted: function () {
            return this.get('completed');
        }
    });

    //DOCS - Collection of documents
    Models.Docs= Backbone.Collection.extend({
    });

    Models.Granjas = Models.Docs.extend({
        model: Models.Granja,
        url: '/granjas'
    });

    Models.Estanques = Models.Docs.extend({
        model: Models.Estanque,
        url: '/estanques'
    });

    Models.Events = Models.Docs.extend({
        model: Models.Event,
        url: '/eventos',
        getCompleted: function () {
            return this.filter(this._isCompleted);
        },

        getActive: function () {
            return this.reject(this._isCompleted);
        },

        comparator: function (doc) {
            return doc.get('created_at')
        },

        _isCompleted: function (doc) {
            return doc.isCompleted();
        }
    });

    Models.Tasks = Models.Events.extend({
        model: Models.Task,
        url: '/tareas'
    });

});
