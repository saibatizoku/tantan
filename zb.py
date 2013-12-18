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

    def __init__(self, wsMcuFactory=None, dataStore=None, escaped=True):
        super(TantanZB, self).__init__(escaped=escaped)
        self.wsMcuFactory = wsMcuFactory
        self.dataStore = dataStore
        self.devices = {}
        self._AMB = []
 
    def connectionMade(self):
        print "TanTan ZB Serial port connection made"
        self.retry_count = 0
        self.zb_net = task.LoopingCall(self.sendND)
        self.zb_net.start(3)
        #self.zb_dbvolt.start(30)
        #self.zb_dbvolt = task.LoopingCall(self.sendDB_Volt)

    def connectionLost(self, reason):
        print "TanTan ZB Serial port connection lost.", reason
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
 
    def handle_packet(self, xbeePacketDictionary):
        response = xbeePacketDictionary
        msg = None
        #print repr(self._frame.raw_data.encode('hex'))
        #print repr(response)
        if self.is_RX(response):
            self.handle_rx(response)
        if self.is_ND(response):
            self.handle_nd(response)

    def is_AT_RESPONSE(self, response):
        return self.is_target_type(response, 'id', 'at_response')

    def is_ND(self, response):
        is_atresp = self.is_AT_RESPONSE(response)
        is_nd = self.is_target_type(response, 'command', 'nd')
        return is_atresp and is_nd

    def is_target_type(self, response, field, target):
        if field in response and response[field].lower() == target:
            return True
        return False

    def is_RX(self, response):
        return self.is_target_type(response, 'id', 'rx')

    def get_zb_node_info(self, response):
        try:
            resp = {}
            resp['id'] = response["source_addr_long"].encode('hex')
            resp['laddr'] = response["source_addr_long"].encode('hex')
            resp['addr'] = response["source_addr"].encode('hex')
            resp['data'] = response["rf_data"] or ''
            return resp
        except:
            return None

    def handle_rx(self, response):
        resp = {}
        #resp['name'] = ZB_reverse.get(response["source_addr_long"], "Unknown")
        resp = self.get_zb_node_info(response)
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
                ###if node_id in self.devices:
                ###    reading['node'] = self.devices[node_id]
                #print reading
                self.wsMcuFactory.dispatch("http://www.tantan.org/api/sensores#amb-rx", reading)
                #self.wsMcuFactory.dispatch("http://www.tantan.org/api/couchdb#info", reading)
            except:
                self.wsMcuFactory.dispatch("http://www.tantan.org/api/sensores#rx", [node_id, l])
        #self.wsMcuFactory.dispatch("http://www.tantan.org/api/sensores#zb-rx", evt)

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

    def handle_nd(self, response):
        beat = datetime.datetime.today().isoformat()
        device = {}
        if "source_addr_long" in response:
            laddr = response["source_addr_long"].encode('hex')
        elif "source_addr_long" in response["parameter"]:
            laddr = response["parameter"]["source_addr_long"].encode('hex')
        
        #nname = ZB_reverse.get(laddr, "Unknown")
        nname = response["parameter"]["node_identifier"]
        addr = response["parameter"]["source_addr"].encode('hex')
        devt = response["parameter"]["device_type"].encode('hex')
        devs = response["parameter"]["status"].encode('hex')
        paddr = response["parameter"]["parent_address"].encode('hex')
        msg = ":".join([nname, addr, "ND", laddr, devt, devs, paddr]) #, str(packet)])
        #print msg
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
        #print device
        pulse = []
        if laddr in self.devices:
            pulse = self.devices[laddr]['pulse']
            if len(pulse) == 10:
                pulse.pop()
        pulse.insert(0, beat)
        device.update({'pulse': pulse})
        self.devices[laddr] = device
        #print "heartbeat:", nname, beat

        self.wsMcuFactory.dispatch("http://www.tantan.org/api/sensores#zb-nd", device)
        #self.wsMcuFactory.dispatch("http://www.tantan.org/api/couchdb#info", device)


class UnUsed:
    def handle_badpacket(self, packet):
        print "ERROR:", packet


    def handle_db(self, response):
        #nname = ZB_reverse.get(response["source_addr_long"], "Unknown")
        #laddr = response["source_addr_long"].encode('hex')
        #addr = response["source_addr"].encode('hex')
        #val = 0
        #if "parameter" in response:
        #    val = int(response["parameter"].encode('hex'),16)
        #msg = ":".join([nname, addr, "DB", str(val)])
        #evt = {'id': nname, 'value': val}
        #print msg
        #self.wsMcuFactory.dispatch("http://example.com/mcu#zb-db", evt)
        topic = "http://www.tantan.org/api/sensores#zb-db"
        utils.handle_factory_db(self.wsMcuFactory, response, topic)

    def handle_packet(self, xbeePacketDictionary):
        response = xbeePacketDictionary
        msg = None
        print repr(self._frame.raw_data.encode('hex'))
        print repr(response)
        #if response.get("source_addr_long", "default") in ZB_reverse:
        if response.get("id", "default") == "rx":
            self.handle_rx(response)
            #broadcastToClients(response, msg)
        elif response.get("status", "default") == "\x00":
            if response.get("command", "default") == "ND":
                self.handle_nd(response)
            elif response.get("command", "default") == "DB":
                self.handle_db(response)
            elif response.get("command", "default") == "%V":
                if response.get("id", "default") == "remote_at_response":
                    nname = ZB_reverse.get(response["source_addr_long"], "Unknown")
                    laddr = response["source_addr_long"].encode('hex')
                    addr = response["source_addr"].encode('hex')
                    val = 0
                    if "parameter" in response:
                        val = int(response["parameter"].encode('hex'),16) * 1200.0 / 1024 / 1000
                    msg = ":".join([nname, addr, "%V", str(val)])
                    evt = {'id': nname, 'value': val}
                    self.wsMcuFactory.dispatch("http://www.tantan.org/api/sensores#zb-volt", evt)
                else:
                    val = int(response["parameter"].encode('hex'),16) * 1200.0 / 1024 / 1000
                    msg = "C0 %V:", str(val), "[mV]"
                    evt = {'id': 'C0', 'value': val}
                    self.wsMcuFactory.dispatch("http://www.tantan.org/api/sensores#zb-volt", evt)
                    
        elif 'samples' in response:
            #print strftime("%Y-%m-%d %H:%M:%S").encode('utf8'), "<<< FROM:", response
            nname = ZB_reverse.get(response["source_addr_long"], "Unknown")
            laddr = response["source_addr_long"].encode('hex')
            addr = response["source_addr"].encode('hex')
            val = str(dict((str(key).replace('-',''), str(value)) for (key, value) in response["samples"][0].items())).replace("'",'"')
            msg = ":".join([nname, addr, "RXIO", val])

        broadcastToClients(response, msg)

        #if response.get("source_addr_long", "default") == devices["template1"]:
        #    reactor.callFromThread(self.send,
        #            "tx",
        #            frame_id="\x01",
        #            dest_addr_long=devices["template2"],
        #            dest_addr="\xff\xfe",
        #            data="DATA2")

    @exportRpc("control-led")
    def controlLed(self, evt=None):
        if evt:
            if evt == "RXTX":
                reactor.callFromThread(self.send,
                    "remote_at",
                    frame_id="\x02",
                    dest_addr_long="\x00\x00\x00\x00\x00\x00\xff\xff",
                    dest_addr="\xff\xfe",
                    command="D5",
                    parameter="\x01"
                    )
            if evt == "ON":
                reactor.callFromThread(self.send,
                    "remote_at",
                    frame_id="\x02",
                    dest_addr_long="\x00\x00\x00\x00\x00\x00\xff\xff",
                    dest_addr="\xff\xfe",
                    command="D5",
                    parameter="\x05"
                    )
            if evt == "OFF":
                reactor.callFromThread(self.send,
                    "remote_at",
                    frame_id="\x02",
                    dest_addr_long="\x00\x00\x00\x00\x00\x00\xff\xff",
                    dest_addr="\xff\xfe",
                    command="D5",
                    parameter="\x04"
                    )
            return 'ASSOC LED Sent: {0}'.format(evt)

    @exportRpc("send-tx")
    def sendTX(self, evt=None):
        #self._sendTX()
        print evt
        return 'TX Sent'
        
    def _sendTX(self):
        reactor.callFromThread(self.send,
                "tx",
                frame_id="\x01",
                command="ND",
                )
    @exportRpc("send-dbvolt")
    def sendDB_Volt(self, evt=None):
        self._sendDB_Volt()
        return "DBVOLT Sent"
    
    def _sendDB_Volt(self):
        reactor.callFromThread(self.send,
                "remote_at",
                frame_id="\x02",
                dest_addr_long="\x00\x00\x00\x00\x00\x00\xff\xff",
                dest_addr="\xff\xfe",
                command="DB",
                )
        reactor.callFromThread(self.send,
                "remote_at",
                frame_id="\x03",
                dest_addr_long="\x00\x00\x00\x00\x00\x00\xff\xff",
                dest_addr="\xff\xfe",
                command="%V",
                )


## WS-MCU protocol
##
class WsMcuProtocol(WampServerProtocol):
 
    def onSessionOpen(self):
        self.registerForPubSub("http://www.tantan.org/api/sensores#", True)
        self.registerForRpc(self.factory.zbProtocol, "www.tantan.org/api/sensores-control#")


## WS-MCU factory
##
class WsMcuFactory(WampServerFactory):

    protocol = WsMcuProtocol

    def __init__(self, url, dataStore=None, opts=None):
        WampServerFactory.__init__(self, url)
        self.zbProtocol = TantanZB(wsMcuFactory=self, dataStore=dataStore)
        #self.serialport = SerialPort(self.zbProtocol, opts['port'], reactor, baudrate=opts['baudrate'])



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
    ##
    webdir = File("./static")
    web = Site(webdir)
    reactor.listenTCP(webport, web)

    reactor.run()
