# -*- coding: utf-8 -*-
from twisted.application import service
from twisted.internet import reactor, task, defer
from twisted.internet.serialport import SerialPort

from zope.interface import Interface, implements

from txXBee.protocol import txXBee


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
        self.factory.service.stopAgent(self.pan_id)

        if self.pan_id and self.factory.service.networks.get(self.pan_id):
            del self.factory.service.networks[self.pan_id]

    def handle_packet(self, packet):
        #print "{0}".format(self._frame.raw_data.encode('hex'))
        #print "{}".format(packet)
        def print_debug(packet):
            print "FRAME", self._frame.raw_data.encode('hex')
            print "PACKET", packet
            
        def publishPANID(agent):
            self.state = "PUBLISH"
            agent.publish("http://api.tantan.net/pan/sensors#nd", [self.pan_id, addr_long, addr, parent])
            print "Agent present: {0}".format(repr(agent))

        if self.is_PANID(packet):
            self.pan_id = pan_id = packet['parameter'].encode('hex').lstrip('0')
            agent = self.factory.service.startAgent(self.pan_id)
            agent.addCallback(publishPANID)

        #    self.factory.service.networks[pan_id] = self
        #    self.factory.service.startWAMPClient(pan_id)
        #    self.state = "PUBLISH"
        #    print "GOT PAN ID", self.pan_id, self.state
        if self.is_ND(packet):
            #print_debug(packet)
            param = packet['parameter']
            result = {}
            result['source_addr_long'] = param['source_addr_long'].encode('hex')
            result['source_addr'] = param['source_addr'].encode('hex')
            result['parent_address'] = param['parent_address'].encode('hex')
            result['node_identifier'] = param['node_identifier'] #.encode('hex')
            result['device_type'] = param['device_type'].encode('hex')
            result['status'] = param['status'].encode('hex')
            addr_long = packet['parameter']['source_addr_long'].encode('hex')
            addr = packet['parameter']['source_addr'].encode('hex')
            parent = packet['parameter']['parent_address'].encode('hex')
            agent = self.factory.service.getAgent(self.pan_id)
            if agent:
                agent.publish("http://api.tantan.net/pan/sensors#nd", [self.pan_id, addr_long, addr, parent])
                agent.publish("http://api.tantan.net/pan/nd#"+self.pan_id, result)
                result['pan_id'] = self.pan_id
                agent.publish("http://api.tantan.net/pans/nd", result)
        #if self.state == "SILENT":
        #    self.getPanId()
        elif self.state == "PUBLISH":
            if self.is_RX(packet):
                agent = self.factory.service.getAgent(self.pan_id)
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

    def getC0ID(self, dest_addr_long, dest_addr, txdata):
        reactor.callFromThread(self.send,
                "at",
                command="ID",
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


