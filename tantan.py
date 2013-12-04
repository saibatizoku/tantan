#-*- coding: utf-8 -*-
"""
Copyright (C) 2013 Joaquin Rosales <globojorro@gmail.com>

This file is part of tantan.couch

tantan.couch program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from twisted.python import log
from twisted.internet import defer, reactor, task, threads

import json
import sys
from urllib import urlencode, quote

from paisley import CouchDB

from autobahn.websocket import listenWS, connectWS
from autobahn.wamp import WampServerFactory, WampServerProtocol, exportRpc



class TantanWampProtocol(WampServerProtocol):

    def connectionLost(self, reason):
        print u"Connection lost: %s" % reason

    def onSessionOpen(self):
        self.registerForPubSub("http://www.tantan.org/api/couchdb/info#", True)
        self.registerForRpc(self.factory, "http://www.tantan.org/api/couchdb#")


def failure_print(failure):
    print failure
    return {'ok': False, 'error': repr(failure)}
    

class TantanWampFactory(WampServerFactory):

    protocol = TantanWampProtocol

    def __init__(self, url, couch_url='localhost', couch_port=5984,
            db_name='tantan', debug = False, debugCodePaths = False, debugWamp = False, debugApp = False):
        WampServerFactory.__init__(self, url, debug = debug,
                debugWamp = debugWamp, debugApp = debugApp)
        self.couch_url = couch_url
        self.couch_port = couch_port
        self.db_name = db_name
        self.couchdb = CouchDB(couch_url, port=couch_port, dbName=db_name)


    @exportRpc("granja-info")
    def getGranjaInfo(self, granja=None):
        if granja is None:
            view = self.couchdb.openView('tantan', 'granjas')
        else:
            view = self.couchdb.openDoc(docId=granja)

        def granja_info(results):
            print results
            return results
        view.addCallback(granja_info)
        return view

    @exportRpc("estanque-info")
    def getEstanqueInfo(self, granja=''):
        view = self.couchdb.openView('tantan', 'estanques', startkey=[granja, 1])
        
        def estanque_info(results):
            print results
            return results
        view.addCallback(estanque_info)
        return view

    @exportRpc("session-info")
    def getSession(self, resp=None):
        sess_uri = '/_session'
        sess = self.couchdb.get(sess_uri, descr='').addCallback(self.couchdb.parseResult)
        def usr_info(r):
            print "Session USR_INFO: %s" % repr(r)
            if  u'ok' in r and r[u'ok']:
                usr = {u'userCtx': r[u'userCtx']}
                if r[u'userCtx'][u'name'] is not None:
                    sess_uri = '/_users/org.couchdb.user:' + r[u'userCtx'][u'name']
                    usr_doc = self.couchdb.get(sess_uri, descr='').addCallback(self.couchdb.parseResult)
                    return usr_doc
            return r
        sess.addCallback(usr_info)
        def usr_doc(r):
            print "Session USR_DOC: %s" % repr(r)
            return r
        sess.addCallback(usr_doc)

        return sess

    def getCreds(self):
        cred_info = {
                "username": self.couchdb.username,
                "password": self.couchdb.password,
                }
        return cred_info
    
    def setCreds(self, creds):
        usr, pwd = creds
        self.couchdb.username = usr
        self.couchdb.password = pwd
        return (self.couchdb.username, self.couchdb.password,)
    
    @exportRpc("logout")
    def doLogout(self, creds=None):
        if self.couchdb.username:
            self.setCreds((None, None))
            return {'ok': True, 'username': None, 'msg': "Logged out."}
        return {'ok': True, 'username': None, 'msg': "Not logged in."}

    @exportRpc("login")
    def doLogin(self, creds=None):
        if creds and len(creds) == 2:
            usr, pwd = creds[:2]
            print 'RPC LOGIN RECEIVED: %s:%s' % (usr, pwd,)
            self.setCreds(creds)

        d = self.getSession()
        d.addErrback(failure_print)

        def checkCreds(response):
            print 'response: %s' % repr(response)
            if u'name' in response and response[u'name']:
                self.user = response
                print 'Good CREDS:', response
                return response
            else:
                self.user = None
                raise Exception("Login failed")
        d.addCallback(checkCreds)
        print 'getCreds:', self.getCreds()

        def failedCreds(reason):
            print "Login failed"
            self.setCreds((None, None))
            return {'ok': False, 'username': 'anonymous', 'msg': repr(reason)}
        d.addErrback(failedCreds)
        return d
