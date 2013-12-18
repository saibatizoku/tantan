/*global TodoMVC */
'use strict';

TanTan.module('AutoBahn', function (AutoBahn, App, Backbone, Marionette, $, _) {

    var sess;

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

    function getUser (resp) {
        ab.log('getUser', resp);
        if ((resp.ok) && (resp.name)) {
            App.vent.trigger('granjas:user', resp);
        } else {
            App.vent.trigger('granjas:anon', resp);
        }
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
        anonLogin();
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
            ab.log('doLogin CREDS', creds);
            if (resp._id) {
                ab.log('good login', resp);
                //userLogin(creds[0], creds[1]);
                App.vent.trigger('granjas:loggedIn', resp);
            } else {
                ab.log('bad login', resp);
                //anonLogin();
                App.vent.trigger('granjas:loggedOut', resp);
            }
        }
        sess.call('rpc:login', creds).always(doLogin);
    };

    AutoBahn.logout = function () {
        sess.call('rpc:logout').always(ab.log);
    };

});
