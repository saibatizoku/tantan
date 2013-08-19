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

from time import strftime
from struct import unpack

import sys
import json
from pprint import pprint

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
    ]


# REGEX   '  ND:(.*)|bat:(.*)\[V\]:(.*)\%carga:(.*):contador:(.*)|\%V:(.*)'
#C0 = 40A4D454
#   = \x00\x13\xA2\x00\x40\xA4\xD4\x54
#R1 = 40A09C4D
#   = \x00\x13\xA2\x00\x40\xA0\x9C\x4D
#R2 = 40A09C91
#   = \x00\x13\xA2\x00\x40\xA0\x9C\x91
#F1 = 40A09B79
#   = \x00\x13\xA2\x00\x40\xA0\x9B\x79


def network_discovery(packet):
    #d = defer.Deferred()
    if "command" in packet and packet["command"] == "ND":
        laddr = packet["parameter"]["source_addr_long"].encode('hex')
        addr = packet["parameter"]["source_addr"].encode('hex')
        devt = packet["parameter"]["device_type"].encode('hex')
        devs = packet["parameter"]["status"].encode('hex')
        paddr = packet["parameter"]["parent_address"].encode('hex')
        #sladdr = packet["parameter"]["sender_addr_long"].encode('hex')
        #saddr = packet["parameter"]["sender_addr"].encode('hex')
        #print ":".join(["  ND", addr, laddr, saddr, sladdr])
        print ":".join(["  ND", addr, laddr, devt, devs, paddr]) #, str(packet)])
    return packet


def sleep_time_hex(seconds):
    return hex(int(seconds))

def broadcastToClients(data, source=None, timestamp=False):

    if timestamp:
        data = strftime("%Y-%m-%d %H:%M:%S").encode('utf8') + ": " + data
        
    for client in TCPClients:
        if client != source:
            client.transport.write(data)
    for client in WebSockClients:
        if client != source:
            client.transport.write(data)

class TantanZigBee(txXBee):
    def __init__(self, escaped=True):
        super(TantanZigBee, self).__init__(escaped=escaped)
        self.lc = {}
        #self.lc['zb_data'].task.LoopingCall(self.getSomeData)
        self.zb_net = task.LoopingCall(self.sendND)
        self.zb_dbvolt = task.LoopingCall(self.sendDB_Volt)
        #self.lc['zb_data'].start(10)
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
            print "{0}:{1}:RX:{2}".format(resp['name'], resp['addr'], resp['val'])
            broadcastToClients(response)
        elif response.get("status", "default") == "\x00":
            if response.get("command", "default") == "ND":
                #print "COMMAND>>>:", str(response), str(response["command"])
                nname = ZB_reverse[response["parameter"]["source_addr_long"]]
                laddr = response["parameter"]["source_addr_long"].encode('hex')
                addr = response["parameter"]["source_addr"].encode('hex')
                devt = response["parameter"]["device_type"].encode('hex')
                devs = response["parameter"]["status"].encode('hex')
                paddr = response["parameter"]["parent_address"].encode('hex')
                print ":".join([nname, addr, "ND", laddr, devt, devs, paddr]) #, str(packet)])
            elif response.get("command", "default") == "DB":
                nname = ZB_reverse[response["source_addr_long"]]
                laddr = response["source_addr_long"].encode('hex')
                addr = response["source_addr"].encode('hex')
                val = 0
                if "parameter" in response:
                    val = int(response["parameter"].encode('hex'),16)
                print ":".join([nname, addr, "DB", str(val)])
            elif response.get("command", "default") == "%V":
                if response.get("id", "default") == "remote_at_response":
                    nname = ZB_reverse[response["source_addr_long"]]
                    laddr = response["source_addr_long"].encode('hex')
                    addr = response["source_addr"].encode('hex')
                    val = 0
                    if "parameter" in response:
                        val = int(response["parameter"].encode('hex'),16) * 1200.0 / 1024 / 1000
                    print ":".join([nname, addr, "%V", str(val)])
                else:
                    val = int(response["parameter"].encode('hex'),16) * 1200.0 / 1024 / 1000
                    print "C0 %V:", str(val), "[mV]"
            else:
                print response
        elif 'samples' in response:
            # remove '-' in samples dict, eg: dio-0 > dio0 conforms with javascript scheme.
            #response = str( ZB_reverse[response["source_addr_long"]]  + " SAMPLE >> " \
            #        + str(dict((str(key).replace('-',''), str(value)) \
            #        for (key, value) in response["samples"][0].items())) \
            #        ).replace("'",'"')

            #print strftime("%Y-%m-%d %H:%M:%S").encode('utf8'), "<<< FROM:", response
            nname = ZB_reverse[response["source_addr_long"]]
            laddr = response["source_addr_long"].encode('hex')
            addr = response["source_addr"].encode('hex')
            val = str(dict((str(key).replace('-',''), str(value)) for (key, value) in response["samples"][0].items())).replace("'",'"')
            print ":".join([nname, addr, "RXIO", val])

            broadcastToClients(response)
        else:
            print str(response)
        if True == False:
                # Silently respond "OK" to AT calls (when module starts up).
                #if response["rf_data"]=="AT":
                #    reactor.callFromThread(self.send,
                #            "tx",
                #            frame_id="\x01",
                #            dest_addr_long=response["source_addr_long"],
                #            dest_addr="\xff\xfe",
                #            data="OK")
                #else:
                    #response = ZB_reverse[response["source_addr_long"]]  + " DATA >> " \
                    #        + response["rf_data"]

                    #print strftime("%Y-%m-%d %H:%M:%S").encode('utf8'), "<<< FROM:",response



            if response["id"] == 'remote_at_response':

                #response = ZB_reverse[response["source_addr_long"]]  + " CMD >> " \
                #        + str(response["command"])\
                #        + " STATUS: " + str(response["status"].encode('hex'))

                ##print strftime("%Y-%m-%d %H:%M:%S").encode('utf8'), "<<< FROM:", response

                #if response.get("command", "default") == "PR":
                #    laddr = response["source_addr_long"].encode('hex')
                #    val = response["parameter"].encode('hex')
                #    print "PR", ":".join([laddr, val])
                #nd_resp = network_discovery(response)
                if response.get("command", "default") == "DB":
                    laddr = response["source_addr_long"].encode('hex')
                    addr = response["source_addr"].encode('hex')
                    val = 0
                    if "parameter" in response:
                        val = int(response["parameter"].encode('hex'),16) * 1200.0 / 1024 / 1000
                    print ":".join(["DB", addr, str(val)])
                if response.get("command", "default") == "%V":
                    if response.get("id", "default") == "remote_at_response":
                        laddr = response["source_addr_long"].encode('hex')
                        addr = response["source_addr"].encode('hex')
                        val = 0
                        if "parameter" in response:
                            val = int(response["parameter"].encode('hex'),16) * 1200.0 / 1024 / 1000
                        print ":".join(["  %V", addr, str(val), "[mV]"])
                    else:
                        val = int(response["parameter"].encode('hex'),16) * 1200.0 / 1024 / 1000
                        print "C0 %V:", str(val), "[mV]"
                broadcastToClients(response)

            else:
                print response

#        print response
#
    def jjj(self):
        if response.get("status", "default") == '\x00':
            if response.get("command", "default") == "ND":
                nd_resp = network_discovery(response)
            #if response.get("command", "default") == "PR":
            #    laddr = response["source_addr_long"].encode('hex')
            #    val = response["parameter"].encode('hex')
            #    print "PR", ":".join([laddr, val])
            if response.get("command", "default") == "DB":
                laddr = response["source_addr_long"].encode('hex')
                addr = response["source_addr"].encode('hex')
                val = int(response["parameter"].encode('hex'),16)
                print ":".join(["DB", addr, str(val)])
            if response.get("command", "default") == "%V":
                if response.get("id", "default") == "remote_at_response":
                    laddr = response["source_addr_long"].encode('hex')
                    addr = response["source_addr"].encode('hex')
                    val = int(response["parameter"].encode('hex'),16) * 1200.0 / 1024 / 1000
                    print ":".join(["  %V", addr, str(val), "[mV]"])
                else:
                    val = int(response["parameter"].encode('hex'),16) * 1200.0 / 1024 / 1000
                    print "C0 %V:", str(val), "[mV]"
        elif response.get("id", "default") == "rx":
            laddr = response["source_addr_long"].encode('hex')
            addr = response["source_addr"].encode('hex')
            val = response["rf_data"] or []
            print ":".join(["RX", addr, json.dumps(val)])
            #print response
        elif response.get("id", "default") == "rx_io_data_long_addr":
            laddr = response["source_addr_long"].encode('hex')
            addr = response["source_addr"].encode('hex')
            val = response["samples"] or []
            print ":".join(["RXIO", addr, json.dumps(val)])
        else:
            print response

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

    def sendND(self):
        reactor.callFromThread(self.send,
                "remote_at",
                frame_id="\x01",
                command="ND",
                )
    def sendDB_Volt(self):
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

    #def getSomeData(self):
        #reactor.callFromThread(self.send,
        #        "remote_at",
        #        frame_id="\x01",
        #        dest_addr_long="\x00\x00\x00\x00\x00\x00\xff\xff",
        #        dest_addr="\xff\xfe",
        #        command="MY",
        #        #parameter="\x01",
        #        )
        #reactor.callFromThread(self.send,
        #        "remote_at",
        #        frame_id="\x11",
        #        dest_addr_long="\x00\x00\x00\x00\x00\x00\xff\xff",
        #        dest_addr="\xff\xfe",
        #        command="PP",
        #        )
        #reactor.callFromThread(self.send,
        #        "remote_at",
        #        frame_id="\x11",
        #        dest_addr_long="\x00\x00\x00\x00\x00\x00\xff\xff",
        #        dest_addr="\xff\xfe",
        #        command="RP",
        #        )
        #        dest_addr_long="\x00\x00\x00\x00\x00\x00\xff\xff",
        #        dest_addr="\xff\xfe",
        #        #parameter="\x01",
        #reactor.callFromThread(self.send,
        #        "at",
        #        frame_id="\x02",
        #        command="%V",
        #        )
        #reactor.callFromThread(self.send,
        #        "remote_at",
        #        frame_id="\x10",
        #        dest_addr_long="\x00\x00\x00\x00\x00\x00\xff\xff",
        #        dest_addr="\xff\xfe",
        #        command="AR",
        #        #parameter="\x01",
        #        )

    def extra(self):
        reactor.callFromThread(self.send,
                "at",
                frame_id="\x02",
                command="%V",
                parameter="\xff",
                )
        reactor.callFromThread(self.send,
                "remote_at",
                frame_id="\x01",
                command="ND",
                #parameter="\x00",
                )
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

    s = SerialPort(TantanZigBee(escaped=True), o.opts['port'], reactor, baudrate=o.opts['baudrate'])
    #reactor.callLater(10, s.protocol.getSomeData)
    reactor.run()
