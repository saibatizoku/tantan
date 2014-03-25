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

from autobahn.wamp1.protocol import exportRpc
from autobahn.wamp1.protocol import WampCraProtocol



def failure_print(failure):
    print failure
    return {'ok': False, 'error': repr(failure)}


class TantanCouch:

    couchdb = None
    factory = None
    AUTHEXTRA = None
    SECRETS = {'granja-admin': WampCraProtocol.deriveKey('nimda', AUTHEXTRA)}
    PERMISSIONS = {
            'granja-admin': {
                'pubsub': [
                    {'uri': 'http://www.tantan.org/api/datos/info#',
                        'prefix': True,
                        'pub': True,
                        'sub': True
                        },
                    {'uri': 'http://www.tantan.org/api/sensores#',
                        'prefix': True,
                        'pub': True,
                        'sub': True
                        },
                    ],
                'rpc': [
                    {
                        'uri': 'http://www.tantan.org/api/datos#',
                        'call': True
                        },
                    {
                        'uri': 'http://www.tantan.org/api/sensores/control#',
                        'call': True
                        },
                    ],
                },
            None: {
                'pubsub': [
                    {'uri': 'http://www.tantan.org/api/datos/info#',
                        'prefix': True,
                        'pub': True,
                        'sub': True
                        },
                    {'uri': 'http://www.tantan.org/api/sensores#',
                        'prefix': True,
                        'pub': True,
                        'sub': True
                        },
                    ],
                'rpc': [
                    {
                        'uri': 'http://www.tantan.org/api/datos#',
                        'call': True
                        },
                    {
                        'uri': 'http://www.tantan.org/api/sensores/control#',
                        'call': True
                        },
                    ],
                }
            }


    def __init__(self, factory):
        self.factory = factory
        self.startDB()

    def startDB(self):
        server_url = self.factory.db_url
        port = self.factory.db_port
        dbName = self.factory.db_name
        self.couchdb = CouchDB(server_url, port = port, dbName = dbName)

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
    
    def getSecret(self, authKey):
        if authKey == self.couchdb.username:
            pwd = self.couchdb.password
            extra = self.AUTHEXTRA
            return WampCraProtocol.deriveKey(pwd, extra)

    @exportRpc("save-doc")
    def saveDoc(self, doc, docId=None):
       save = self.couchdb.saveDoc(body=doc, docId=docId)
       def printDoc(resp):
           print "Saved document", repr(resp)
           return resp
       save.addCallback(printDoc)
       return save

    @exportRpc("granjas-tree")
    def getGranjasInfo(self, granja=None):
        if granja is None:
            view = self.couchdb.openView('tantan', 'estanques')
        else:
            view = self.couchdb.openView('tantan', 'estanques', startkey=[granja,0], endkey=[granja,2])

        def addBranchNodes(resp, branch, tipo):
            print "BRANCH NODES", resp
            if ('rows' in resp):
                #items = [ v for g in resp['rows'] for k, v in g.items() if k == tipo]
                items = [ g['value'] for g in resp['rows'] if g['value']['tipo'] == 'granja']
                nodos = [ g['value'] for g in resp['rows'] if g['value']['tipo'] == 'estanque']
                for g in items:
                    ns = [ e for e in nodos if e['granja_id'] == g['_id'] ]
                    g['nodos'] = ns
                    #print "BRANCH estanques de {0}\n{1}".format(g['_id'], ns)
                print "BRANCH granjas", items
                branch['nodos'] = items
            #return branch
            return items

        def addRoot(resp):
            return True

        root = dict(nombre=u'Cultivos de tilapia')
        view.addCallback(addBranchNodes, root, 'granja')
        return view

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
        view = self.couchdb.openView('tantan', 'estanques', key=[granja, 1])

        def estanque_info(results):
            print results
            return results
        view.addCallback(estanque_info)
        return view

    @exportRpc("nodos-info")
    def getNodosInfo(self, estanque):
        view = self.couchdb.openView('tantan', 'nodos', startkey=[estanque, 1])
        
        def estanque_info(results):
            print results
            return results
        view.addCallback(estanque_info)
        return view

    @exportRpc("eventos-info")
    def getEventosInfo(self, granja=''):
        view = self.couchdb.openView('tantan', 'eventos') #, startkey=[granja, 1])
        
        def estanque_info(results):
            print results
            return results
        view.addCallback(estanque_info)
        return view

    @exportRpc("session-info")
    def getSession(self, resp=None):
        sess_uri = '/_session'
        sess = self.couchdb.get(sess_uri, descr='').addCallback(self.couchdb.parseResult)
        return sess

    def getUserDoc(self, resp=None):
        print "Session getUSERDOC: %s" % repr(resp)
        def user_doc(r):
            print "Session USR_DOC: %s" % repr(r)
            self.user_doc = r
            return r

        if resp and u'ok' in resp and resp[u'ok']:
            self.user_session = resp
            print "Session USR_SESSION: %s" % repr(resp)
            if resp[u'userCtx'][u'name'] is not None:
                sess_uri = '/_users/org.couchdb.user:' + resp[u'userCtx'][u'name']
                usr_doc = self.couchdb.get(sess_uri, descr='').addCallback(self.couchdb.parseResult)
                usr_doc.addCallback(user_doc)
                return usr_doc
            return resp


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
        d.addCallback(self.getUserDoc)
        d.addErrback(failure_print)

        def checkCreds(response):
            print 'response: %s' % repr(response)
            if u'name' in response and response[u'name']:
                print 'Good CREDS:', response
                return response
            else:
                self.user_doc = None
                self.user_session = None
                raise Exception("Login failed")
        d.addCallback(checkCreds)
        print 'getCreds:', self.getCreds()

        def failedCreds(reason):
            print "Login failed"
            self.setCreds((None, None))
            return {'ok': False, 'username': 'anonymous', 'msg': repr(reason)}
        d.addErrback(failedCreds)
        return d
