import json
from pprint import pprint

from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer
from twisted.internet.serialport import SerialPort
from twisted.python import components

from zope.interface import Interface, implements


def loadConfig():
    cfg = json.load(open('config.json', 'r'))
    pprint(cfg, depth=4)
    return cfg


class IPANService(Interface):
    """ A client service made to connect Physical-Area-Networks to a
        central server over the network.
    """


class IPANClientFactory(Interface):
    """ A factory for clients made to publish at a central node.
    """


class TanTanPANClientProtocol(protocol.Protocol):

    def connectionMade(self):
        d = self.factory.getNetworks()

        def printNetworkInfo(msg):
            print "Service PAN IDs", repr(msg)

        d.addCallback(printNetworkInfo)

    def dataReceived(self, data):
        print "Client received DATA:", data


class TanTanPANClientFactory(protocol.ClientFactory):

    implements(IPANClientFactory)

    protocol = TanTanPANClientProtocol

    def __init__(self, service):
        self.service = service

    def getNetwork(self, pan_id=None):
        return self.service.getPAN(pan_id)

    def getNetworks(self, pan_id=None):
        return self.service.getPANs()


components.registerAdapter(TanTanPANClientFactory,
                           IPANService,
                           IPANClientFactory)


class SerialEcho(protocol.Protocol):

    def connectionMade(self):
        print "Serial connection made"

    def connectionLost(self):
        print "Serial connection COULD NOT BE made"


class TanTanPANService(service.Service):

    implements(IPANService)

    def __init__(self, *args, **kwargs):
        self.config = {}
        self.networks = {}
        self.config = loadConfig()

    def getPAN(self, pan_id):
        return defer.succeed(self.networks.get(pan_id, "No such network"))

    def getPANs(self):
        return defer.succeed(self.networks.keys())

    def openUART(self, pan_id):

        def open_serial_port(pan_id):
            if pan_id in self.networks:
                pan = self.networks.get(pan_id)
                port = pan.get('port')
                baud = pan.get('baud')
                return SerialPort(
                    SerialEcho,
                    port,
                    reactor,
                    baudrate=baud
                    )

        def connection_error(reason):
            print "Failed to connect", pan_id

        d = defer.Deferred()
        d.addCallback(open_serial_port)
        d.addErrback(connection_error)
        return d


    def startPAN(self, pan_id=None):
        if pan_id:
            pan = self.getPAN(pan_id)
            uart = pan.get('uart', None)
            print "UART", dir(uart)

    def stopPAN(self, pan_id=None):
        
        def stopUART(pan):
            uart = pan.get('uart', None)
            print "UART", dir(uart)

    def _readConfigNetworks(self):
        nets = self.config.get('networks', {})
        networks = [net for net in nets.values()]
        for net in networks:
            try:
                pan = net['pan_id']
                self.networks[pan] = self.openUART(net['port'], net['baud'])
                print "Network started", pan
            except:
                print "COULD NOT CONNECT", net['port']

    def startService(self):
        self._readConfigNetworks()
        service.Service.startService(self)

    def stopService(self):
        service.Service.stopService(self)


application = service.Application('tantanclient')
client = TanTanPANService()
serviceCollection = service.IServiceCollection(application)
client.setServiceParent(serviceCollection)
c = IPANClientFactory(client)
internet.TCPClient('localhost', 8080, c).setServiceParent(serviceCollection)
