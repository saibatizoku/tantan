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

from twisted.python import log, usage
from twisted.internet import defer, reactor, task, threads

import json
import sys
from urllib import urlencode, quote

from paisley import CouchDB

from autobahn.websocket import listenWS, connectWS
from autobahn.wamp import WampServerFactory, WampServerProtocol, exportRpc


class TantanCouchProtocol(WampServerProtocol):

    def connectionLost(self, reason):
        print u"Connection lost: %s" % reason

    def onSessionOpen(self):
        self.registerForPubSub("http://www.tantan.org/db#", True)
        self.registerForRpc(self.factory, "http://www.tantan.org/cmd-db#")


class TTCouchFactory(WampServerFactory):

    protocol = TantanCouchProtocol

    def __init__(self, url):
        WampServerFactory.__init__(self, url)
        self.couchdb = CouchDB('localhost', dbName='tantan')


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

    @exportRpc("session")
    def getSession(self, event=None):
        uri = '/tantan/_session'
        dbs = self.couchdb.listDB()
        
        usr, pwd = event
        def buildUri(**kwargs):
            return "/_session?%s" % (urlencode(kwargs))
        def printdbs(DBS):
            print DBS
            return DBS
            

        print 'Sessión: %s %s' % (repr(usr), repr(pwd))
        sessuri = buildUri(username=usr, password=pwd)
        sess = self.couchdb.get(sessuri, descr='getSession').addCallback(self.couchdb.parseResult)
        #view = self.couchdb.openView('tantan', 'granjas')
        sess.addCallback(printdbs)
        dbs.addCallback(printdbs)
        #return dbs
        return 'Sessión: %s' % repr(event)


if __name__ == '__main__':

    class MyOptions(usage.Options):
        optParameters = [
                ['outfile', 'o', None, 'Logfile [default: sys.stdout]'],
                ['webport', 'w', 8080, 'Web port to use for embedded Web server'],
                ['wsurl', 's', "ws://localhost:9001", 'WebSocket port to use for embedded WebSocket server']
        ]

    o = MyOptions()
    try:
        o.parseOptions()
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        raise SystemExit, 1

    logFile = o.opts['outfile']
    if logFile is None:
        logFile = sys.stdout
    log.startLogging(logFile)

    webport = int(o.opts['webport'])
    wsurl = o.opts['wsurl']
    log.msg('Attempting to open %s, as a %s device' % (wsurl, CouchDB.__name__))

    ttCouchFactory = TTCouchFactory(wsurl)
    listenWS(ttCouchFactory)

    ## create embedded web server for static files
    ##
    #webdir = File("../static")
    #web = Site(webdir)
    #reactor.listenTCP(webport, web)

    reactor.run()
