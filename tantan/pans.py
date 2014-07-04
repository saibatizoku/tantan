from twisted.internet import protocol
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ReconnectingClientFactory

from zope.interface import Interface, implements

from zigbee import PANZigBeeProtocol

class IPANServerFactory(Interface):
    """ A factory for clients made to publish at a central node.
    """


class TanTanPANServerFactory(protocol.ServerFactory):

    implements(IPANServerFactory)

    protocol = PANZigBeeProtocol

    def __init__(self, service):
        self.service = service

    def getNetwork(self, pan_id=None):
        return self.service.getPAN(pan_id)

    def getNetworks(self, pan_id=None):
        return self.service.getPANs()


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


class IPANClientFactory(Interface):
    """ A factory for clients made to publish at a central node.

        The PAN client factory manages connections to Physical-
        Area-Networks (PANs), by controlling UART connections
        via the PAN service.
    """


class TanTanPANClientFactory(ReconnectingClientFactory):

    implements(IPANClientFactory)

    protocol = TanTanPANClientProtocol
    maxDelay = 5

    def __init__(self, service):
        self.service = service
        self.pan_id = None

    def getNetworkInfo(self):
        return self.service.config['networks'].keys()

    #def buildProtocol(self, addr):
    #    print 'Connected.'
    #    print 'Resetting reconnection delay'
    #    self.resetDelay()
    #    prot = TanTanPANClientProtocol()
    #    prot.factory = self
    #    return self

    #def startedConnecting(self, connector):
    #    #self.resetDelay()

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)
