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
from pprint import pprint
from urllib import urlencode, quote

from paisley import CouchDB

from autobahn.wamp1.protocol import WampServerFactory, WampCraProtocol, WampCraServerProtocol, exportRpc
 

from couch import TantanCouch
from zb import TantanZB

def thisfunc(r, msg):
    print msg;
    return r


class TantanWampProtocol(WampCraServerProtocol):

    couchHandler = None


    def connectionLost(self, reason):
        print u"Connection lost: %s" % reason
        self.couchHandler = None

    def onSessionOpen(self):
        print u"TanTan WAMP server connection made"
        WampCraServerProtocol.onSessionOpen(self)

        couchHandler = TantanCouch(self.factory)
        self.couchHandler = couchHandler

        #self.registerForPubSub("http://www.tantan.org/api/datos/info#", True)
        self.registerForRpc(self.couchHandler, "http://www.tantan.org/api/datos#")

        if self.factory.zbProtocol:
            self.registerForPubSub("http://www.tantan.org/api/sensores#", True)
            self.registerForRpc(self.factory.zbProtocol, "http://www.tantan.org/api/sensores/control#")


    def getAuthPermissions(self, authKey, authExtra):
        perms = self.couchHandler.PERMISSIONS.get(authKey, None)
        extra = self.couchHandler.AUTHEXTRA
        authperms = {
                'permissions': perms,
                'authextra': extra
                }
        #authperms['permissions'] = {'pubsub': [], 'rpc': []}

        d = defer.Deferred()
        d.addCallback(thisfunc, "AuthPERMISSIONS")
        d.addCallback(thisfunc, perms)
        d.addCallback(thisfunc, extra)
        d.callback(authperms)
        return d

    def getAuthSecret(self, authKey):
        secret = self.couchHandler.getSecret(authKey)
        d = defer.Deferred()
        d.addCallback(thisfunc, "AuthSECRET")
        d.addCallback(thisfunc, secret)
        d.callback(secret)
        return d

    def onAuthenticated(self, authKey, perms):
        self.registerForPubSubFromPermissions(perms['permissions'])

        d = defer.Deferred()
        d.addCallback(thisfunc, "OnAuthenticated")
        return d
        #if authKey is not None:
        #    #self.registerForRPC(self,...
        #    pass



class TantanWampFactory(WampServerFactory):

    protocol = TantanWampProtocol
    appUriPrefix = 'http://www.tantan.org/api/'

    def __init__(self, url, couch_url='localhost', couch_port=5984,
                 db_name='tantan', debug = False, debugCodePaths = False,
                 debugWamp = False, debugApp = False):

        WampServerFactory.__init__(self, url, debug = debug,
                debugWamp = debugWamp, debugApp = debugApp)

        self.db_url = couch_url
        self.db_port = couch_port
        self.db_name = db_name

        self.zbProtocol = TantanZB(wsMcuFactory=self)
