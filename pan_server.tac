# -*- coding: utf-8 -*-
import json
from pprint import pprint

from twisted.application import internet, service
from twisted.internet import reactor, defer, task
from twisted.internet.endpoints import TCP4ClientEndpoint, \
                                       TCP4ServerEndpoint
from twisted.python import components

from zope.interface import Interface, implements

from autobahn.wamp1.protocol import WampServerFactory, \
                                    WampClientFactory, \
                                    exportRpc

from tantan.agents import IAgentManager, PANWampAgentManager
from tantan.pans import IPANServerFactory, TanTanPANServerFactory
from tantan.wamp import WAMPServerProtocol, WAMPClientProtocol

debug = True
debugW = True


class IServerService(Interface):
    """ A client service made to connect Physical-Area-Networks to a
        central server over the network.
    """


class TanTanPANService(service.Service):

    implements(IServerService)

    def __init__(self, *args, **kwargs):
        self.agents = {}
        self.networks = {}
        self.managers = {}
        self.managers['agents'] = IAgentManager(self)

    def startAgent(self, pan_id):
        manager = self.managers['agents']
        manager.agents[pan_id] = "CONNECTING"
        client = manager.addAgent(pan_id, 'localhost', 9000)
        return client

    def stopAgent(self, pan_id):
        manager = self.managers['agents']
        manager.removeAgent(pan_id)

    def getAgent(self, pan_id):
        manager = self.managers['agents']
        return manager.getAgent(pan_id)

    def getPAN(self, pan_id):
        return defer.succeed(self.networks.get(pan_id, None))

    def getPANs(self):
        return defer.succeed(self.networks.keys())

    def startWAMPClient(self, pan_id):
        client = self.startAgent(pan_id)
        return client

    def startWAMPFactory(self):
        factory = WampServerFactory("ws://ejeacuicola.mx:9000", debugWamp = debugW)
        factory.protocol = WAMPServerProtocol
        factory.service = self
        endpoint = TCP4ServerEndpoint(reactor, 9000)
        server = endpoint.listen(factory)

        def setConn(server):
            print "WAMP Service started"
            self.wamp = server
            return server

        def failedConn(failure):
            print "WAMP Factory could not start"
            if self.wamp is not None:
                self.wamp = None
            return None

        server.addCallback(setConn)
        server.addErrback(failedConn)
        return server

    def startService(self):
        self.startWAMPFactory()
        service.Service.startService(self)

    def stopService(self):
        service.Service.stopService(self)


components.registerAdapter(TanTanPANServerFactory,
                           IServerService,
                           IPANServerFactory)

components.registerAdapter(PANWampAgentManager,
                           IServerService,
                           IAgentManager)


application = service.Application('tantanserver')
wsan_service = TanTanPANService()
serviceCollection = service.IServiceCollection(application)
wsan_service.setServiceParent(serviceCollection)
pan_factory = IPANServerFactory(wsan_service)
internet.TCPServer(7780, pan_factory).setServiceParent(serviceCollection)
