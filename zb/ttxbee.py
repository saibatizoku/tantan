"""
Copyright (C) 2011 Wagner Sartori Junior <wsartori@gmail.com>
http://www.wsartori.com

This file is part of txXBee.

txXBee program is free software: you can redistribute it and/or modify
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

import sys
import json
from pprint import pprint

from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, WampServerProtocol, exportRpc

from txXBee.protocol import txXBee


devices = {
        "C0": "\x00\x13\xA2\x00\x40\xA4\xD4\x54",
        "R1": "\x00\x13\xA2\x00\x40\xA0\x9C\x4D",
        "R2": "\x00\x13\xA2\x00\x40\xA0\x9C\x91",
        "R3": "\x00\x13\xA2\x00\x40\xA4\xD4\x93",
        "F1": "\x00\x13\xA2\x00\x40\xA0\x9B\x79",
        "00": "\x00\x00\x00\x00\x00\x00\x00\x00",
        }
ZB_reverse = {
        "\x00\x13\xA2\x00\x40\xA4\xD4\x54" : "C0",
        "\x00\x13\xA2\x00\x40\xA0\x9C\x4D" : "R1",
        "\x00\x13\xA2\x00\x40\xA0\x9C\x91" : "R2",
        "\x00\x13\xA2\x00\x40\xA4\xD4\x93" : "R3",
        "\x00\x13\xA2\x00\x40\xA0\x9B\x79" : "F1",
        "\x00\x00\x00\x00\x00\x00\x00\x00" : "00",
        }

TCPClients = []
WebSockClients=[]
xbee=[]
timer = None
delimiter = None
timers={}

class MyOptions(usage.Options):
    optParameters = [
            ['outfile', 'o', None, 'Logfile [default: sys.stdout]'],
            ['baudrate', 'b', 38400, 'Serial baudrate [default: 38400'],
            ['port', 'p', '/dev/ttyUSB0', 'Serial Port device'],
            ['webport', 'w', 8080, 'Web port to use for embedded Web server'],
            ['wsurl', 's', "ws://localhost:9000", 'WebSocket port to use for embedded WebSocket server']
    ]

# REGEX   '  ND:(.*)|bat:(.*)\[V\]:(.*)\%carga:(.*):contador:(.*)|\%V:(.*)'


def sleep_time_hex(seconds):
    return hex(int(seconds))

def broadcastToClients(data, msg=None, source=None, timestamp=False):
    if msg:
        print msg
    else:
        print data

    if timestamp:
        data = strftime("%Y-%m-%d %H:%M:%S").encode('utf8') + ": " + data
        
    for client in TCPClients:
        if client != source:
            client.transport.write(data)
    for client in WebSockClients:
        if client != source:
            client.transport.write(data)

class TantanZB(txXBee):
    def __init__(self, wsMcuFactory=None, escaped=True):
        super(TantanZB, self).__init__(escaped=escaped)
        self.wsMcuFactory = wsMcuFactory
 
        self.zb_net = task.LoopingCall(self.sendND)
        self.zb_dbvolt = task.LoopingCall(self.sendDB_Volt)

        self.zb_net.start(20)
        self.zb_dbvolt.start(30)

    def connectionMade(self):
        print "TanTan ZB Serial port connection made"

    def deferred_handle_packet(self, packet):
        #d = defer.Deferred()
        return packet

    def handle_badpacket(self, packet):
        print "ERROR:", packet

    def handle_packet(self, xbeePacketDictionary):
        response = xbeePacketDictionary
        msg = None
        #if response.get("source_addr_long", "default") in ZB_reverse:
        if response["id"] == "rx":
            resp = {}
            resp['name'] = ZB_reverse[response["source_addr_long"]]
            resp['laddr'] = response["source_addr_long"].encode('hex')
            resp['addr'] = response["source_addr"].encode('hex')
            resp['val'] = response["rf_data"] or ''
            rout = "RX:"
            for (key, item) in resp.items():
                rout += "{0}-{1}:".format(key, item)
            msg = "{0}:{1}:RX:".format(resp['name'], resp['addr'], resp['val']) + repr(resp['val'])
            evt = {'id': resp['name'],
                   'value': resp['val'],
                  }
            self.wsMcuFactory.dispatch("http://example.com/mcu#zb-rx", evt)
            #broadcastToClients(response, msg)
        elif response.get("status", "default") == "\x00":
            if response.get("command", "default") == "ND":
                #print "COMMAND>>>:", str(response), str(response["command"])
                nname = ZB_reverse[response["parameter"]["source_addr_long"]]
                laddr = response["parameter"]["source_addr_long"].encode('hex')
                addr = response["parameter"]["source_addr"].encode('hex')
                devt = response["parameter"]["device_type"].encode('hex')
                devs = response["parameter"]["status"].encode('hex')
                paddr = response["parameter"]["parent_address"].encode('hex')
                msg = ":".join([nname, addr, "ND", laddr, devt, devs, paddr]) #, str(packet)])
                evt = {'id': nname,
                       'value': {'long': laddr,
                                 'short': addr,
                                 'device': devt,
                                 'parent': paddr,
                                 'status': devs,
                                 }
                      }
                self.wsMcuFactory.dispatch("http://example.com/mcu#zb-nd", evt)
            elif response.get("command", "default") == "DB":
                nname = ZB_reverse[response["source_addr_long"]]
                laddr = response["source_addr_long"].encode('hex')
                addr = response["source_addr"].encode('hex')
                val = 0
                if "parameter" in response:
                    val = int(response["parameter"].encode('hex'),16)
                msg = ":".join([nname, addr, "DB", str(val)])
                evt = {'id': nname, 'value': val}
                self.wsMcuFactory.dispatch("http://example.com/mcu#zb-db", evt)
            elif response.get("command", "default") == "%V":
                if response.get("id", "default") == "remote_at_response":
                    nname = ZB_reverse[response["source_addr_long"]]
                    laddr = response["source_addr_long"].encode('hex')
                    addr = response["source_addr"].encode('hex')
                    val = 0
                    if "parameter" in response:
                        val = int(response["parameter"].encode('hex'),16) * 1200.0 / 1024 / 1000
                    msg = ":".join([nname, addr, "%V", str(val)])
                    evt = {'id': nname, 'value': val}
                    self.wsMcuFactory.dispatch("http://example.com/mcu#zb-volt", evt)
                else:
                    val = int(response["parameter"].encode('hex'),16) * 1200.0 / 1024 / 1000
                    msg = "C0 %V:", str(val), "[mV]"
                    evt = {'id': 'C0', 'value': val}
                    self.wsMcuFactory.dispatch("http://example.com/mcu#zb-volt", evt)
                    
        elif 'samples' in response:
            #print strftime("%Y-%m-%d %H:%M:%S").encode('utf8'), "<<< FROM:", response
            nname = ZB_reverse[response["source_addr_long"]]
            laddr = response["source_addr_long"].encode('hex')
            addr = response["source_addr"].encode('hex')
            val = str(dict((str(key).replace('-',''), str(value)) for (key, value) in response["samples"][0].items())).replace("'",'"')
            msg = ":".join([nname, addr, "RXIO", val])

        broadcastToClients(response, msg)

        #if response.get("source_addr_long", "default") == devices["template1"]:
        #    reactor.callFromThread(self.send,
        #            "tx",
        #            frame_id="\x01",
        #            dest_addr_long=devices["template1"],
        #            dest_addr="\xff\xfe",
        #            data="DATA1")
        #    reactor.callFromThread(self.send,
        #            "tx",
        #            frame_id="\x01",
        #            dest_addr_long=devices["template2"],
        #            dest_addr="\xff\xfe",
        #            data="DATA2")

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



    def extra(self):
        reactor.callFromThread(self.send,
                "at",
                frame_id="\x03",
                command="D5",
                parameter="\x04")
        reactor.callFromThread(self.send,
                "remote_at",
                frame_id="\x01",
                command="ND",
                #parameter="\x00",
                )


## WS-MCU protocol
##
class WsMcuProtocol(WampServerProtocol):
 
    def onSessionOpen(self):
        ## register topic prefix under which we will publish MCU measurements
        ##
        self.registerForPubSub("http://example.com/mcu#", True)
 
        ## register methods for RPC
        ##
        self.registerForRpc(self.factory.mcuProtocol, "http://example.com/mcu-control#")


## WS-MCU factory
##
class WsMcuFactory(WampServerFactory):

    protocol = WsMcuProtocol

    def __init__(self, url):
        WampServerFactory.__init__(self, url)
        self.mcuProtocol = TantanZB(wsMcuFactory=self)
        self.serialport = SerialPort(self.mcuProtocol, o.opts['port'], reactor, baudrate=o.opts['baudrate'])



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
    log.msg('Attempting to open %s at %dbps as a %s device' % (port, o.opts['baudrate'], txXBee.__name__))
    webport = int(o.opts['webport'])
    wsurl = o.opts['wsurl']

    wsMcuFactory = WsMcuFactory(wsurl)
    listenWS(wsMcuFactory)

    ## create embedded web server for static files
    ##
    webdir = File(".")
    web = Site(webdir)
    reactor.listenTCP(webport, web)

    reactor.run()
