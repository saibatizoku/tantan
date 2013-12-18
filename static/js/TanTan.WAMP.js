/*global TodoMVC */
'use strict';

TanTan.module('WAMP', function (WAMP, App, Backbone, Marionette, $, _) {

    WAMP.API= function () {
        this.url = '';
        this.sess = null;
        this.wsuri = null;
    };

    _.extend(WAMP.API.prototype, {
        connect: function () {
            var sess = null;

            function onConnect() {
                var log_line = "WAMP Connection success";
                ab.log(log_line);
                App.vent.trigger('wamp:success', sess);
            }

            function onHangup(e) {
                var log_line = "WAMP Connection failed";
                ab.log(log_line,e);
                App.vent.trigger('wamp:failure');
            }

            sess = new ab.Session(this.wsuri, onConnect, onHangup);
            this.sess = sess;
            ab.log('WAMP.API session', sess);
            return sess;
        },
        login: function (creds) {
            this.sess.call('rpc:login', creds).always(this.doLogin);
        },
        doLogin: function (resp) {
            //ab.log(resp);
            if (resp._id) {
                App.vent.trigger('granjas:loggedIn', resp);
            } else {
                App.vent.trigger('granjas:loggedOut', resp);
            }
        },
        getGranjaInfo: function (granja) {
            this.sess.call("rpc:granja-info", granja).always(ab.log);
        },
        getEstanqueInfo: function (granja) {
            this.sess.call("rpc:estanque-info", granja).always(ab.log);
        },
        getSession: function (status) {
            this.sess.call("rpc:session-info", status).always(this.getUser);
        },
        getUser: function (resp) {
            ab.log('getUser', resp);
            if ((resp.ok) && (resp.name)) {
                App.vent.trigger('granjas:user', resp);
            } else {
                App.vent.trigger('granjas:anon', resp);
            }
        },
        logout: function () {
            this.sess.call('rpc:logout').always(ab.log);
        },
        doLogout: function (resp) {
            ab.log('logging out', resp);
            if (resp.ok) {
                App.vent.trigger('granjas:loggedOut', resp);
            } else {
                App.vent.trigger('wamp:failure', resp);
            }
        },
        create: function (model, success, error) {
            if (this.sess) {
                console.log('WAMP.API created', model);
                if (model.collection) {
                    console.log('creating collection');
                } else {
                    console.log('creating model');
                }
                return 'create';
            }
            console.log('WAMP.API create failed', model);
            return error('failed');
        },
        update: function (model, success, error) {
            console.log('WAMP.API update', model);
            if (model.collection) {
                console.log('updating collection');
            } else {
                console.log('updating model');
            }
            return 'update';
        },
        patch: function (model, success, error) {
            console.log('WAMP.API patch', model);
            return 'patch';
        },
        delete: function (model, success, error) {
            console.log('WAMP.API delete', model);
            if (model.collection) {
                console.log('deleting collection');
            } else {
                console.log('deleting model');
            }
            return 'delete';
        },
        read: function (model, success, error) {
            console.log('WAMP.API read', model);
            if (model.collection) {
                console.log('reading collection');
            } else {
                console.log('reading model');
            }
            return 'read';
        }
    });

});
