/*global TanTanApp */
'use strict';

TanTan.module('Models', function(Models, App, Backbone) {

    Models.Base = Backbone.Model.extend({ idAttribute: '_id' });

});
