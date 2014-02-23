#-*- coding: utf-8 -*-
"""
Copyright (C) 2013 Joaquin Rosales <globojorro@gmail.com>

This file is part of tantan.zb

tantan.zb program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from twisted.python import log, usage
from twisted.internet import defer, reactor, task, threads
from twisted.internet.serialport import SerialPort
from twisted.web.http_headers import Headers
from twisted.web.server import Site
from twisted.web.static import File

from time import strftime
from struct import unpack

import datetime
import sys
import json
from pprint import pprint

from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, WampServerProtocol, exportRpc

from txXBee.protocol import txXBee

from nodos import Nodo, NodoAmbiental
import utils


TCPClients = []
WebSockClients = []
xbee = []
timer = None
delimiter = None
timers = {}
serService = None

class MyOptions(usage.Options):
    optParameters = [
            ['outfile', 'o', None, 'Logfile [default: sys.stdout]'],
            ['baudrate', 'b', 38400, 'Serial baudrate [default: 38400'],
            ['port', 'p', '/dev/ttyUSB0', 'Serial Port device'],
            ['webport', 'w', 8080, 'Web port to use for embedded Web server'],
            ['wsurl', 's', "ws://localhost:9000", 'WebSocket port to use for embedded WebSocket server']
    ]

# REGEX   '  ND:(.*)|bat:(.*)\[V\]:(.*)\%carga:(.*):contador:(.*)|\%V:(.*)'



class TantanZB(txXBee):
    """
    """

    max_retries = None
    retry_interval = 300 #seconds
    retry_count = 0

    def __init__(self, wsMcuFactory=None, escaped=True):
        super(TantanZB, self).__init__(escaped=escaped)
        self.wsMcuFactory = wsMcuFactory
        self.devices = {}
        self._AMB = []
 
    def connectionMade(self):
        print "TanTan ZB Serial port connection made"
        self.retry_count = 0
        self.startPulse(beat=15)

    def startPulse(self, beat=3):
        self.zb_net = task.LoopingCall(self.sendND)
        self.zb_net.start(beat)

    def stopPulse(self):
        self.zb_net.stop()

    def connectionLost(self, reason):
        print "TanTan ZB Serial port connection lost.", reason
        self.stopPulse()
        self.retry_count += 1
            #reactor.stop()
      
    def get_amb_sensors(self):
        #amb_sensors = [ dev for devid, dev in self.devices if dev['name'].startswith('AMB')]
        amb_sensors = [ dev for devid, dev in self.devices.items() if dev['name'].startswith('AMB')]
        #print "AMB_SENSORS:", amb_sensors
        self._AMB = amb_sensors
        for sensor in amb_sensors:
            self.ambiental_humedad(sensor['id'])

    def ambiental_humedad(self, device_id):
        self.send_TX_Command(device_id, 'd')

    def send_TX_Command(self, device_id, command):
        if device_id in self.devices:
            device = self.devices[device_id]
            laddr = device['value']['long']
            saddr = device['value']['short']
            print "sending:", repr(laddr.decode('hex')), repr(saddr.decode('hex')), command
            reactor.callFromThread(self.send,
                    "tx",
                    frame_id="\x01",
                    dest_addr_long=laddr.decode('hex'),
                    dest_addr=saddr.decode('hex'),
                    data=command)

    def deferred_handle_packet(self, packet):
        #d = defer.Deferred()
        return packet
 
    def extractNodeInfo(self, packet):
        if True:
            return Nodo('')

    def handle_packet(self, packet):
        if self.extractNodeInfo(packet):
            if self.is_RX(packet):
                self.handle_rx(packet)
            if self.is_ND(packet):
                self.handle_nd(packet)

    def is_AT_RESPONSE(self, packet):
        return self.is_target_type(packet, 'id', 'at_response')

    def is_ND(self, packet):
        is_atresp = self.is_AT_RESPONSE(packet)
        is_nd = self.is_target_type(packet, 'command', 'nd')
        return is_atresp and is_nd

    def is_target_type(self, packet, field, target):
        if field in packet and packet[field].lower() == target:
            return True
        return False

    def is_RX(self, packet):
        return self.is_target_type(packet, 'id', 'rx')

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

    def handle_rx(self, packet):
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
            try:
                node_type, pin, sensor, value = l.split(":")
                reading = {
                           'node_id': node_id,
                           'node_type': node_type,
                           'pin': pin,
                           'sensor': sensor,
                           'value': float(value),
                           }
                self.wsMcuFactory.dispatch("http://www.tantan.org/api/sensores#amb-rx", reading)
                uri = "/".join(["http://www.tantan.org/api/sensores/nodos#", node_id])
                self.wsMcuFactory.dispatch(uri, {'node_id': node_id, 'msg': l})
            except:
                uri = "#".join(["http://www.tantan.org/api/sensores", node_id])
                self.wsMcuFactory.dispatch(uri, {'node_id': node_id, 'msg': l})

    @exportRpc("send-nd")
    def sendND(self, evt=None):
        self._sendND()
        return 'ND Sent'
        
    def _sendND(self):
        reactor.callFromThread(self.send,
                "remote_at",
                frame_id="\x01",
                command="ND",
                )

    def getNode(self, node_id):
        if node_id in self.devices:
            return Node(node_id)

    def handle_nd(self, packet):
        beat = datetime.datetime.today().isoformat()
        device = {}
        if "source_addr_long" in packet:
            laddr = packet["source_addr_long"].encode('hex')
        elif "source_addr_long" in packet["parameter"]:
            laddr = packet["parameter"]["source_addr_long"].encode('hex')
        
        nname = packet["parameter"]["node_identifier"]
        addr = packet["parameter"]["source_addr"].encode('hex')
        devt = packet["parameter"]["device_type"].encode('hex')
        devs = packet["parameter"]["status"].encode('hex')
        paddr = packet["parameter"]["parent_address"].encode('hex')
        msg = ":".join([nname, addr, "ND", laddr, devt, devs, paddr]) #, str(packet)])
        device.update({'id': laddr,
            'name': nname,
            'value': {'long': laddr,
                'short': addr,
                'node_id': nname,
                'device': devt,
                'parent': paddr,
                'status': devs,
                }
            })
        pulse = []
        if laddr in self.devices:
            pulse = self.devices[laddr]['pulse']
            if len(pulse) == 10:
                pulse.pop()
        pulse.insert(0, beat)
        device.update({'pulse': pulse})
        self.devices[laddr] = device

        self.wsMcuFactory.dispatch("http://www.tantan.org/api/sensores#zb-nd", device)


## WS-MCU protocol
class WsMcuProtocol(WampServerProtocol):
 
    def onSessionOpen(self):
        self.registerForPubSub("http://www.tantan.org/api/sensores#", True)
        self.registerForPubSub("http://www.tantan.org/api/sensores/nodos#", True)
        self.registerForRpc(self.factory.zbProtocol, "http://www.tantan.org/api/sensores/control#", True)


## WS-MCU factory
class WsMcuFactory(WampServerFactory):

    protocol = WsMcuProtocol

    def __init__(self, url, opts=None):
        WampServerFactory.__init__(self, url)
        self.zbProtocol = TantanZB(wsMcuFactory=self)


if __name__ == '__main__':
    o = MyOptions()
    try:
        o.parseOptions()
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        raise SystemExit, 1

    logFile = o.opts['outfile']
    if logFile is None:
        logFile = sys.stdout
    log.startLogging(logFile)

    port = o.opts['port']
    log.msg('Attempting to open %s at %sbps as a %s device' % (port, o.opts['baudrate'], txXBee.__name__))
    webport = int(o.opts['webport'])
    wsurl = o.opts['wsurl']

    wsMcuFactory = WsMcuFactory(wsurl)
    serialport = SerialPort(wsMcuFactory.zbProtocol, o.opts['port'], reactor, baudrate=o.opts['baudrate'])
    listenWS(wsMcuFactory)

    ## create embedded web server for static files
    webdir = File("./static")
    web = Site(webdir)
    reactor.listenTCP(webport, web)

    reactor.run()
