# -*- coding: utf-8 -*-
import json
from pprint import pprint

from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer, task
from twisted.internet.serialport import SerialPort
from twisted.internet.endpoints import clientFromString
from twisted.internet.endpoints import serverFromString, \
                                       TCP4ClientEndpoint, \
                                       TCP4ServerEndpoint
from twisted.python import components

from txXBee.protocol import txXBee

from zope.interface import Interface, implements

from autobahn.twisted.websocket import WrappingWebSocketServerFactory, \
                                       WrappingWebSocketClientFactory

from autobahn.wamp1.protocol import WampServerFactory, \
                                    WampServerProtocol, \
                                    WampClientFactory, \
                                    WampClientProtocol, \
                                    exportRpc

from wamp import WAMPServerProtocol, WAMPClientProtocol

debug = False
debugW = False


class IPANService(Interface):
    """ A client service made to connect Physical-Area-Networks to a
        central server over the network.
    """


class IPANServerFactory(Interface):
    """ A factory for clients made to publish at a central node.
    """


class PANZigBeeProtocol(txXBee):

    def __init__(self, *args, **kwds):
        super(PANZigBeeProtocol, self).__init__(*args, **kwds)
        self.pan_id = None
        self.lc = task.LoopingCall(self.getSomeData)
        self.lc.start(10.0)
        #self.pan_status = task.LoopingCall(self.obtainPAN)
        #self.pan_status.start(10.0)

    def connectionMade(self):
        print "Connection MADE", self.transport.getPeer()
        self.state = "SILENT"
        self.getPanId()

    def connectionLost(self, reason):
        if self.pan_id and self.factory.service.agents.get(self.pan_id):
            self.factory.service.agents[self.pan_id].sendClose()
            del self.factory.service.agents[self.pan_id]
        if self.pan_id and self.factory.service.networks.get(self.pan_id):
            del self.factory.service.networks[self.pan_id]

    def handle_packet(self, packet):
        def print_debug(packet):
            print "FRAME", self._frame.raw_data.encode('hex')
            print "PACKET", packet

        agent = self.factory.service.agents.get(self.pan_id, None)

        if self.is_PANID(packet):
            self.pan_id = pan_id = packet['parameter'].encode('hex').lstrip('0')
            self.factory.service.networks[pan_id] = self
            self.factory.service.startWAMPClient(pan_id)
            self.state = "PUBLISH"
            print "GOT PAN ID", self.pan_id, self.state
        if self.is_ND(packet):
            #print_debug(packet)
            addr_long = packet['parameter']['source_addr_long'].encode('hex')
            addr = packet['parameter']['source_addr'].encode('hex')
            if agent:
                print dir(agent)
                agent.publish("http://api.tantan.net/pan/sensors#nd", [addr_long, addr])
        if self.state == "SILENT":
            self.getPanId()
        elif self.state == "PUBLISH":
            if self.is_RX(packet):
                rx = packet['rf_data']
                self.handle_rx(packet, agent)

    def is_target_type(self, packet, field, target):
        if field in packet and packet[field].lower() == target:
            return True
        return False

    def is_AT_RESPONSE(self, packet):
        return self.is_target_type(packet, 'id', 'at_response')

    def is_ND(self, packet):
        is_atresp = self.is_AT_RESPONSE(packet)
        is_nd = self.is_target_type(packet, 'command', 'nd')
        return is_atresp and is_nd

    def is_RX(self, packet):
        return self.is_target_type(packet, 'id', 'rx')

    def is_PANID(self, packet):
        is_atresp = self.is_AT_RESPONSE(packet)
        is_nd = self.is_target_type(packet, 'command', 'id')
        return is_atresp and is_nd

    def get_zb_node_info(self, packet):
        try:
            resp = {}
            resp['id'] = packet["source_addr_long"].encode('hex')
            resp['laddr'] = packet["source_addr_long"].encode('hex')
            resp['addr'] = packet["source_addr"].encode('hex')
            resp['data'] = packet["rf_data"] or ''
            return resp
        except:
            return None

    def handle_rx(self, packet, agent):
        if agent:
            resp = {}
            #resp['name'] = ZB_reverse.get(packet["source_addr_long"], "Unknown")
            resp = self.get_zb_node_info(packet)
            rout = "RX:"
            for (key, item) in resp.items():
                rout += "{0}-{1}:".format(key, item)
            msg = "{0}:{1}:RX:".format(resp['id'], resp['addr'], resp['data']) + repr(resp['data'])
            #print 'Evt id: {0}\nVal: {1}'.format(str(resp['name']), resp['data'].decode('utf8'))
            evt = {'id': resp['id'],
                    'type': 'rx',
                    'data': resp['data'],
                    }
            node_id = resp['id']
            data = resp['data']
            data_lines = data.splitlines()
            #print "VAL LINES", val_lines
            for l in data_lines:
                uri = "#".join(["http://www.tantan.org/api/sensores", node_id])
                agent.publish(uri, {'node_id': node_id, 'msg': l})

    def getPanId(self):
        reactor.callFromThread(self.send,
                "at",
                frame_id="\x02",
                command="ID"
                )

    def obtainPAN(self):
        if self.pan_id and self.status == "SILENT":
            self.status == "PUBLISH"
        elif self.status == "SILENT":
            self.getPanId()

    def getSomeData(self):
        self.sendND()
        self.allTX('HOLA')
        self.nodeTX(
                dest_addr_long="\x00\x13\xa2\x00\x40\xa4\xd4\x93",
                dest_addr="\xa7\xe8",
                txdata=u"Joaquín".encode('utf8')
                )

    def sendND(self):
        reactor.callFromThread(self.send,
                "remote_at",
                frame_id="\x01",
                command="ND",
                )

    def nodeTX(self, dest_addr_long, dest_addr, txdata):
        reactor.callFromThread(self.send,
                "tx",
                frame_id="\x03",
                dest_addr_long=dest_addr_long,
                dest_addr=dest_addr,
                data=txdata,
                )
    def allTX(self, txdata):
        reactor.callFromThread(self.send,
                "tx",
                frame_id="\x03",
                dest_addr_long="\x00\x00\x00\x00\x00\x00\xff\xff",
                dest_addr="\xff\xfe",
                data=txdata,
                )


class TanTanPANServerFactory(protocol.ServerFactory):

    implements(IPANServerFactory)

    protocol = PANZigBeeProtocol

    def __init__(self, service):
        self.service = service

    def getNetwork(self, pan_id=None):
        return self.service.getPAN(pan_id)

    def getNetworks(self, pan_id=None):
        return self.service.getPANs()


components.registerAdapter(TanTanPANServerFactory,
                           IPANService,
                           IPANServerFactory)


class TanTanPANService(service.Service):

    implements(IPANService)

    def __init__(self, *args, **kwargs):
        self.config = loadConfig()
        self.agents = {}
        self.networks = {}

    def getPAN(self, pan_id):
        return defer.succeed(self.networks.get(pan_id, None))

    def getPANs(self):
        return defer.succeed(self.networks.keys())

    def startWAMPClient(self, pan_id):
        #wfactory = protocol.Factory.forProtocol(WAMPClientProtocol)
        #wfactory.pan_id = pan_id
        #factory = WrappingWebSocketClientFactory(wfactory,
        #        "ws://localhost:9000",
        #        )
        #factory = protocol.Factory.forProtocol(WAMPClientProtocol)
        factory = WampClientFactory("ws://localhost:9000", debugWamp = True)
        factory.protocol = WAMPClientProtocol
        factory.pan_id = pan_id
        #endpoint = clientFromString(reactor, 'autobahn:tcp\:localhost\:9000:url=ws\://localhost\:9000')
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
        factory = WampServerFactory("ws://ejeacuicola.mx:9000", debugWamp = True)
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


application = service.Application('tantanclient')
wsan_service = TanTanPANService()
serviceCollection = service.IServiceCollection(application)
wsan_service.setServiceParent(serviceCollection)
pan_factory = IPANServerFactory(wsan_service)
internet.TCPServer(7780, pan_factory).setServiceParent(serviceCollection)
