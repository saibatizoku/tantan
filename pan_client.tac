import json
from pprint import pprint

from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.serialport import SerialPort
from twisted.python import components

from zope.interface import Interface, implements


def loadConfig():
    try:
        cfg = json.load(open('config.json', 'r'))
        pprint(cfg, depth=4)
    except:
        cfg = {}
    return cfg


class IPANService(Interface):
    """ A client service made to connect Physical-Area-Networks to a
        central server over the network.
    """
    def startAgent():
        """
        """

    def startCOMM():
        """
        """

    def closeAgent():
        """
        """

    def closeCOMM():
        """
        """


class IPANClientFactory(Interface):
    """ A factory for clients made to publish at a central node.

        The PAN client factory manages connections to Physical-
        Area-Networks (PANs), by controlling UART connections
        via the PAN service.
    """


class TanTanPANClientProtocol(protocol.Protocol):

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
        if self.factory.pan_id in pans:
            pans[self.factory.pan_id].protocol.transport.loseConnection()


class TanTanPANClientFactory(protocol.ReconnectingClientFactory):

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
    #    return TanTanPANClientProtocol()

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)

components.registerAdapter(TanTanPANClientFactory,
                           IPANService,
                           IPANClientFactory)


class SerialEcho(protocol.Protocol):

    def __init__(self, client):
        self.client = client
        self.pan_id = self.client.factory.pan_id

    def connectionMade(self):
        print "Serial connection made"
        print "CLIENT", repr(self.client)

    def connectionLost(self, reason):
        print "Serial port NOT CONNECTED", self.pan_id
        if self.pan_id in self.client.factory.service.pan:
            del self.client.factory.service.pan[self.pan_id]

    def dataReceived(self, data):
        print data.encode('hex')
        self.client.transport.write(data)


class TanTanPANService(service.Service):

    implements(IPANService)

    def __init__(self, *args, **kwargs):
        self.config = loadConfig()
        self.pan = {}
        self.agents = {}

        """
        """
    def startAgent(self, pan_id):
        host = self.config['server']['host']
        port = self.config['server']['port']
        factory = IPANClientFactory(self)
        factory.pan_id = pan_id
        endpoint = TCP4ClientEndpoint(reactor, host, port)
        client = endpoint.connect(factory)

        def setConn(client):
            print "CONN", client.transport.getPeer()
            self.agents[pan_id] = client
            #self._readConfigNetworks()
            return client

        def failedConn(failure):
            print "UART not found"
            if pan_id in self.agents:
                del self.agents[pan_id]
            return None

        client.addCallback(setConn)
        client.addErrback(failedConn)
        return client


    def closeAgent(self, pan_id):
        """
        """

    def startCOMM(self, pan_id):
        if pan_id in self.agents:
            agent = self.agents[pan_id]
        else:
            agent = None
        return self._startCOMM(agent)

    def closeCOMM(self, pan_id):
        """
        """

    def get_pan_info(self, pan_id):
        return defer.succeed(self.config['networks'].get(pan_id, None))

    def getPANs(self):
        return self.config['networks'].keys()

    def _startCOMM(self, agent):

        pan_id = agent.factory.pan_id

        def open_serial_port(agent):
            if pan_id in self.config['networks']:
                pan = self.config['networks'][pan_id]
                port = pan.get('port')
                baud = pan.get('baud')
                print "opening PAN {0}, PORT {1}, BAUD {2}".format(pan_id, port, baud)
                return SerialPort(
                    SerialEcho(agent),
                    port,
                    reactor,
                    baudrate=baud
                    )
            return None

        def connection_error(reason):
            print "Failed to connect", pan_id, reason
            if pan_id in self.pan:
                del self.pan[pan_id]
            return None

        def setComm(serial):
            if serial:
                print "Setting COMM", pan_id, serial
                self.pan[pan_id] = serial
                return serial

        d = defer.Deferred()
        d.addCallback(open_serial_port)
        d.addErrback(connection_error)
        d.addCallback(setComm)
        return d.callback(agent)

    def startPANClients(self):
        for pan_id in self.getPANs():
            client = self.startAgent(pan_id)
            client.addCallback(self._startCOMM)

    def stopPANClients(self):
        for pan_id, client in self.agents.items():
            client.transport.loseConnection()
            print pan_id, " PAN closed"

    def startService(self):
        self.startPANClients()
        service.Service.startService(self)

    def stopService(self):
        self.stopPANClients()
        service.Service.stopService(self)


application = service.Application('tantanclient')
client = TanTanPANService()
serviceCollection = service.IServiceCollection(application)
client.setServiceParent(serviceCollection)
#c = IPANClientFactory(client)
#internet.TCPClient('localhost', 8080, c).setServiceParent(serviceCollection)
