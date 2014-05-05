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

from pans import IPANServerFactory, TanTanPANServerFactory
from wamp import WAMPServerProtocol, WAMPClientProtocol

debug = False
debugW = True


class IPANService(Interface):
    """ A client service made to connect Physical-Area-Networks to a
        central server over the network.
    """


class TanTanPANService(service.Service):

    implements(IPANService)

    def __init__(self, *args, **kwargs):
        self.agents = {}
        self.networks = {}

    def getPAN(self, pan_id):
        return defer.succeed(self.networks.get(pan_id, None))

    def getPANs(self):
        return defer.succeed(self.networks.keys())

    def startWAMPClient(self, pan_id):
        factory = WampClientFactory("ws://localhost:9000", debugWamp = debugW)
        factory.protocol = WAMPClientProtocol
        factory.pan_id = pan_id
        endpoint = TCP4ClientEndpoint(reactor, 'localhost', 9000)
        client = endpoint.connect(factory)

        def setConn(client):
            print "CONN", client.transport.getPeer()
            self.agents[pan_id] = client
            return client

        def failedConn(failure):
            print "UART not found"
            if pan_id in self.agents:
                del self.agents[pan_id]
            return None

        client.addCallback(setConn)
        client.addErrback(failedConn)
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
                           IPANService,
                           IPANServerFactory)


application = service.Application('tantanserver')
wsan_service = TanTanPANService()
serviceCollection = service.IServiceCollection(application)
wsan_service.setServiceParent(serviceCollection)
pan_factory = IPANServerFactory(wsan_service)
internet.TCPServer(7780, pan_factory).setServiceParent(serviceCollection)
