/*global TanTanApp */
'use strict';

TanTan.module('Models', function(Models, App, Backbone) {

    Models.Base = Backbone.Model.extend({ idAttribute: '_id' });

    Models.UserDoc = Models.Base.extend({
        defaults: {
            name: '',
            type: 'user',
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

});
