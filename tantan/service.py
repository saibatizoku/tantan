from twisted.application import service
from twisted.internet import reactor, task, defer
from twisted.internet.endpoints import TCP4ClientEndpoint, \
                                       TCP4ServerEndpoint
from twisted.internet.serialport import SerialPort

from zope.interface import Interface, implements
from autobahn.wamp1.protocol import WampServerFactory

from tantan.agents.tcp import PANTcpAgentManager
from tantan.itantan import IAgentManager, IServerService
from tantan.itantan import IPANServerFactory, IPANClientFactory
from tantan.uarts import SerialEcho
from tantan.utils import loadConfig
from tantan.wamp import WAMPServerProtocol


debugW = True
WSURI_DEFAULT = u'localhost'
WSPORT_DEFAULT = 9899

class TanTanPANServerService(service.Service):

    implements(IServerService)

    def __init__(self, *args, **kwargs):
        self.config = kwargs.get('config', {})
        self.agents = {}
        self.networks = {}
        self.managers = {}
        self.managers['agents'] = IAgentManager(self)
        self.wamp = None

    def startAgent(self, pan_id):
        wsuri = self.config.get('wsuri', WSURI_DEFAULT)
        wsport = self.config.get('wsport', WSPORT_DEFAULT)
        manager = self.managers['agents']
        manager.agents[pan_id] = "CONNECTING"
        client = manager.addAgent(pan_id, wsuri, wsport)
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
        wsuri = self.config.get('wsuri', WSURI_DEFAULT)
        wsport = self.config.get('wsport', WSPORT_DEFAULT)
        wamp_uri = "ws://{0}:{1}".format(wsuri, wsport)
        factory = WampServerFactory(wamp_uri, debugWamp = debugW)
        factory.protocol = WAMPServerProtocol
        factory.service = self
        endpoint = TCP4ServerEndpoint(reactor, wsport)
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
        if self.wamp is not None:
            try:
                self.wamp.loseConnection()
            except:
                pass
            self.wamp = None
        service.Service.stopService(self)


class TanTanPANClientService(service.Service):

    implements(IServerService)

    def __init__(self, *args, **kwargs):
        print "PAN CLIENT ARGS; KWARGS: \n{0}\n{1}".format(
                repr(args), repr(kwargs))
        self.config = kwargs.get('config', {})
        self.pan = {}
        self.agents = {}
        self.managers = {}
        self.managers['agents'] = IAgentManager(self)

    def startAgent(self, pan_id):
        host = self.config['server']['host']
        port = self.config['server']['port']
        manager = self.managers['agents']
        manager.agents[pan_id] = "CONNECTING"
        client = manager.addAgent(pan_id, host, port)
        return client


    def startCOMM(self, pan_id):
        agents = self.managers['agents'].agents
        if pan_id in agents:
            agent = agents[pan_id]
        else:
            agent = None
        return self._startCOMM(agent)

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
