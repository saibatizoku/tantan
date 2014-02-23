/*global TodoMVC */
'use strict';

TanTan.module('AutoBahn', function (AutoBahn, App, Backbone, Marionette, $, _) {

    var sess;
    var ret;

    AutoBahn.wsuri = null;

    function onConnect (session) {
        var log_line = "AutoBahn Connection success";
        sess = session;
        ab.log(log_line, sess);
        App.vent.trigger('wamp:success', sess);
        anonLogin();
    }

    function onHangup(code, reason, detail) {
        var log_line = "AutoBahn Connection failed";
        ab.log(log_line, code, reason, detail);
        sess = null;
        App.vent.trigger('wamp:failure');
    }

    function userLogin (user, pwd) {
        ab.log("User login", user);
        sess.authreq(user).then(function (challenge) {
            var secret = ab.deriveKey(pwd, JSON.parse(challenge).authextra);
            //var secret = pwd;
            ab.log("User login secret", secret);
            var signature = sess.authsign(challenge, secret);
            ab.log("User login signature", signature);

            sess.auth(signature).then(onAuth, ab.log);
        }, ab.log);
    }

    function anonLogin () {
        ab.log("Anonymous login");
        sess.authreq().then(function () {
            sess.auth().then(onAuth, ab.log);
        }, ab.log);
    }

    function onAuth (permissions) {
        ab.log("perms", JSON.stringify(permissions));
    }

    function getGranjaInfo (resp) {
        //ab.log('getGranjaInfo', resp);
        ret = [];
        if ((resp.rows) && (resp.total_rows > 0)) {
            _.each(resp.rows, function (row) {
                ret.push(row.value);
            });
            //ab.log("granja info", ret);
            App.vent.trigger('granjas:info', ret);
        }
        return ret;
    }

    function getGranjasTree (resp) {
        //ab.log('getGranjaInfo', resp);
        ret = [];
        _.each(resp.nodes, function (row) {
            ret.push(row);
        });
        //ab.log("granja TREE", resp);
        App.vent.trigger('granjas:tree', resp);
        return ret;
    }

    function getEstanqueInfo (granja) {
        sess.call("rpc:estanque-info", granja).always(ab.log);
    };

    function getUser (resp) {
        //ab.log('getUser', resp);
        if ((resp.ok) && (resp.name)) {
            App.vent.trigger('granjas:user', resp);
        } else {
            App.vent.trigger('granjas:anon', resp);
        }
    };

    function getEvents (resp) {
        ret = [];
        if ((resp.rows) && (resp.total_rows > 0)) {
            var rows = resp.rows;
            _.each(rows, function (item) {
                ab.log('event', item.value);
                ret.push(item.value);
            });
        }
        ab.log('getEvents', ret);
        App.vent.trigger('agenda:get-events', ret);
    };

    function getSession (status) {
        sess.call("rpc:session-info", status).always(getUser);
    };

    function doLogout (resp) {
        ab.log('logging out', resp);
        if (resp.ok) {
            App.vent.trigger('granjas:loggedOut', resp);
        } else {
            App.vent.trigger('wamp:failure', resp);
        }
    };

    AutoBahn.connect = function () {
        ab.connect(
                this.wsuri,
                onConnect,
                onHangup,
                {
                    'maxRetries': 60,
                    'retryDelay': 2000
                }
                );
        ab.log('AutoBahn session', sess);
    };

    AutoBahn.login = function (creds) {
        function doLogin (resp) {
            if (resp._id) {
                App.vent.trigger('granjas:loggedIn', resp);
            } else {
                App.vent.trigger('granjas:loggedOut', resp);
            }
        }
        sess.call('rpc:login', creds).always(doLogin);
    };

    AutoBahn.logout = function () {
        sess.call('rpc:logout').always(doLogout);
    };

    AutoBahn.save = function (doc) {
        sess.call('rpc:save-doc', doc).always(ab.log);
    };

    AutoBahn.get_granjas = function (granja) {
        sess.call("rpc:granjas-tree", granja).always(getGranjasTree);
    };

    AutoBahn.get_events = function () {
        sess.call('rpc:eventos-info').always(getEvents);
        return ret;
    };

    function subSensor (topicURI) {
        ab.log('subscribing to', topicURI);
    }

    AutoBahn.subscribe_sensor = function (sensor_id) {
        sess.subscribe("zbn:"+sensor_id, subSensor);
    }

    AutoBahn.unsubscribe_sensor = function (sensor_id) {
        ab.log('unsubscribing from', topicURI);
        sess.unsubscribe("zbn:"+sensor_id);
    }

    AutoBahn.sync = function (method, model, options) {
        function success (result) {
            if (options.success) {
                options.success(result);
            }
        }
        function error (result) {
            if (options.error) {
                options.error(result);
            }
        }
        options || (options = {});

        switch (method) {
            case 'create':
                console.log('create sess', sess);
                if ((sess) && (sess._websocket_connected)) {
                    console.log('AutoBahn created', model);
                    if (model.models) {
                        console.log('creating collection');
                    } else {
                        console.log('creating model');
                        AutoBahn.save(model);
                    }
                    return 'create';
                }
                console.log('AutoBahn create failed', model);
                return error('failed');
            case 'update':
                console.log('AutoBahn update', model);
                if (model.models) {
                    console.log('updating collection');
                    console.log('collection url', model.collection.url);
                } else {
                    console.log('updating model');
                }
                return 'update';
            case 'patch':
                console.log('AutoBahn patch', model);
                return 'patch';
            case 'delete':
                console.log('AutoBahn delete', model);
                if (model.models) {
                    console.log('deleting collection');
                } else {
                    console.log('deleting model');
                }
                return 'delete';
            case 'read':
                console.log('AutoBahn read', model);
                if (model.models) {
                    console.log('reading collection');
                    console.log(model.url);
                    if (model.url == 'eventos-info') {
                        AutoBahn.get_events();
                    }
                } else {
                    console.log('reading model');
                }
                return 'read';
        }
    }

    AutoBahn.addInitializer(function () {
        Backbone.sync = AutoBahn.sync;
    });

});
