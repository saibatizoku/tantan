import json
from pprint import pprint

from twisted.application import internet, service
from twisted.internet import reactor, defer, task
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.serialport import SerialPort
from twisted.python import components

from zope.interface import Interface, implements

from pans import IPANClientFactory, TanTanPANClientFactory
from agents import IAgentManager, PANTcpAgentManager
from utils import loadConfig


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
        self.config = loadConfig('config.json')
        self.pan = {}
        self.agents = {}
        self.managers = {}
        self.managers['agents'] = IAgentManager(self)

        """
        """
    def startAgent(self, pan_id):
        host = self.config['server']['host']
        port = self.config['server']['port']
        manager = self.managers['agents']
        manager.agents[pan_id] = "CONNECTING"
        client = manager.addAgent(pan_id, host, port)
        return client


    def closeAgent(self, pan_id):
        """
        """

    def startCOMM(self, pan_id):
        agents = self.managers['agents'].agents
        if pan_id in agents:
            agent = agents[pan_id]
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

        if agent:
            pan_id = agent.factory.pan_id
        else:
            pan_id = None

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
            print "Failed to connect", pan_id, reason.value
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
            self.startPANClient(pan_id)

    def startPANClient(self, pan_id):
        client = self.startAgent(pan_id)
        client.addCallback(self._startCOMM)

    def stopPANClients(self):
        for pan_id, client in self.managers['agents'].agents.items():
            client.transport.loseConnection()
            print pan_id, " PAN closed"

    def startService(self):
        self.startPANClients()
        service.Service.startService(self)

    def stopService(self):
        self.stopPANClients()
        service.Service.stopService(self)


components.registerAdapter(TanTanPANClientFactory,
                           IPANService,
                           IPANClientFactory)

components.registerAdapter(PANTcpAgentManager,
                           IPANService,
                           IAgentManager)

application = service.Application('tantanclient')
client = TanTanPANService()
serviceCollection = service.IServiceCollection(application)
client.setServiceParent(serviceCollection)
#c = IPANClientFactory(client)
#internet.TCPClient('localhost', 8080, c).setServiceParent(serviceCollection)
