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

from autobahn.wamp import WampServerFactory, WampCraServerProtocol, exportRpc

from couch import TantanCouch
from zb import TantanZB


class TantanWampProtocol(WampCraServerProtocol):

    couchHandler = None

    def connectionLost(self, reason):
        print u"Connection lost: %s" % reason
        self.couchHandler = None

    def onSessionOpen(self):
        print u"TanTan WAMP server connection made"

        couchHandler = TantanCouch(self.factory)
        self.couchHandler = couchHandler

        self.registerForPubSub("http://www.tantan.org/api/datos/info#", True)
        self.registerForRpc(self.couchHandler, "http://www.tantan.org/api/datos#")

        if self.factory.zbProtocol:
            self.registerForPubSub("http://www.tantan.org/api/sensores#", True)
            self.registerForRpc(self.factory.zbProtocol, "www.tantan.org/api/sensores-control#")


class TantanWampFactory(WampServerFactory):

    protocol = TantanWampProtocol

    def __init__(self, url, couch_url='localhost', couch_port=5984,
            db_name='tantan', debug = False, debugCodePaths = False, debugWamp = False, debugApp = False):
        WampServerFactory.__init__(self, url, debug = debug,
                debugWamp = debugWamp, debugApp = debugApp)
        self.db_url = couch_url
        self.db_port = couch_port
        self.db_name = db_name

        self.zbProtocol = TantanZB(wsMcuFactory=self)
