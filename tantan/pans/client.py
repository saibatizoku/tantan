# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import components

from zope.interface import Interface, implements

from tantan.itantan import IPANClientFactory
from tantan.itantan import IServerService



class TanTanPANClientProtocol(Protocol):

    def connectionMade(self):
        pans = self.factory.getNetworkInfo()
        self.factory.resetDelay()
        print "Service PAN IDs", repr(pans)

    def dataReceived(self, data):
        #print "Client received DATA:", data
        pans = self.factory.service.pan
        if self.factory.pan_id in pans:
            pans[self.factory.pan_id].protocol.transport.write(data)

    def connectionLost(self, reason):
        print "AGENT connection LOST", self.factory.pan_id, self.factory.service.pan.keys()
        pans = self.factory.service.pan
        agents = self.factory.service.managers['agents'].agents

        if self.factory.pan_id in agents:
            print "AGENT FACTORY removed" #, dir(self.factory)
            agents[self.factory.pan_id] = None

        if self.factory.pan_id in pans:
            pans[self.factory.pan_id].protocol.transport.loseConnection()


class TanTanPANClientFactory(ReconnectingClientFactory):

    implements(IPANClientFactory)

    protocol = TanTanPANClientProtocol
    maxDelay = 5

    def __init__(self, service):
        self.service = service
        self.pan_id = None

    def getNetworkInfo(self):
        return self.service.config['networks'].keys()

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)
