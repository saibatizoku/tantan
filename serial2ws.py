###############################################################################
##
##  Copyright (C) 2012-2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################


from twisted.internet.defer import inlineCallbacks
from twisted.internet.serialport import SerialPort

from txXBee.protocol import txXBee

from autobahn.twisted.wamp import ApplicationSession


class McuProtocol(txXBee):

    def __init__(self, session, debug = False, escaped=True):
        super(McuProtocol, self).__init__(escaped=escaped)
        self.debug = debug
        self.session = session

    def connectionMade(self):
        #pans = self.factory.getNetworkInfo()
        #self.factory.resetDelay()
        print "Service PAN IDs" #, repr(pans)

    def handle_packet(self, packet):
        #print packet
        if self.is_RX(packet):
            self.handle_rx(packet)

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
                print reading
                #self.wsMcuFactory.dispatch("http://www.tantan.org/api/sensores#amb-rx", reading)
                #uri = "/".join(["http://www.tantan.org/api/sensores/nodos#", node_id])
                #self.wsMcuFactory.dispatch(uri, {'node_id': node_id, 'msg': l})
            except:
                topic = u".".join(["mx.neutro.energia.api.nodos", node_id])
                print topic, repr(l.strip())
                self.session.publish(topic, {'node_id': node_id, 'msg': l})

    def connectionLost(self, reason):
        print "AGENT connection LOST" #, self.factory.pan_id, self.factory.service.pan.keys()
        #pans = self.factory.service.pan
        #if self.factory.pan_id in pans:
        #    pans[self.factory.pan_id].protocol.transport.loseConnection()

    def _lineReceived(self, line):
        if self.debug:
            print("Serial RX: {0}".format(line))

        try:
            ## parse data received from MCU
            ##
            data = [int(x) for x in line.split()]
        except ValueError:
            print('Unable to parse value {0}'.format(line))
        else:
            ## create payload for WAMP event
            ##
            payload = {u'id': data[0], u'value': data[1]}
  
            ## publish WAMP event to all subscribers on topic
            ##
            self.session.publish(u"com.myapp.mcu.on_analog_value", payload)

    def controlLed(self, turnOn):
        """
        This method is exported as RPC and can be called by connected clients
        """
        if turnOn:
            payload = b'1'
        else:
            payload = b'0'
        if self.debug:
            print("Serial TX: {0}".format(payload))
        self.transport.write(payload)



class McuComponent(ApplicationSession):
    """
    MCU WAMP application component.
    """

    @inlineCallbacks
    def onJoin(self, details):
        print("MyComponent ready! Configuration: {}".format(self.config.extra))

        port = self.config.extra['port']
        baudrate = self.config.extra['baudrate']
        debug = self.config.extra['debug']

        serialProtocol = McuProtocol(self, debug)

        print('About to open serial port {0} [{1} baud] ..'.format(port, baudrate))
        try:
            serialPort = SerialPort(serialProtocol, port, reactor, baudrate = baudrate)
        except Exception as e:
            print('Could not open serial port: {0}'.format(e))
            self.leave()
        else:
            yield self.register(serialProtocol.controlLed, u"com.myapp.mcu.control_led")



if __name__ == '__main__':

    import sys, argparse

    ## parse command line arguments
    ##
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", action = "store_true",
            help = "Enable debug output.")

    parser.add_argument("--baudrate", type = int, default = 9600, choices = [300, 1200, 2400, 4800, 9600, 19200, 57600, 115200],
            help = 'Serial port baudrate.')

    parser.add_argument("--port", type = str, default = '/dev/ttyACM0',
            help = 'Serial port to use (e.g. 3 for a COM port on Windows, /dev/ttyATH0 for Arduino Yun, /dev/ttyACM0 for Serial-over-USB on RaspberryPi.')

    parser.add_argument("--web", type = int, default = 0,
            help = 'Web port to use for embedded Web server. Use 0 to disable.')

    parser.add_argument("--router", type = str, default = 'wss://ruta-energetica-2014.herokuapp.com',
            help = 'If given, connect to this WAMP router. Else run an embedded router on 8080.')

    args = parser.parse_args()

    try:
        ## on Windows, we need port to be an integer
        args.port = int(args.port)
    except ValueError:
        pass

    from twisted.python import log
    log.startLogging(sys.stdout)


    ## import Twisted reactor
    ##
    if sys.platform == 'win32':
        ## on windows, we need to use the following reactor for serial support
        ## http://twistedmatrix.com/trac/ticket/3802
        ##
        from twisted.internet import win32eventreactor
        win32eventreactor.install()

    from twisted.internet import reactor
    print("Using Twisted reactor {0}".format(reactor.__class__))


    ## create embedded web server for static files
    ##
    if args.web:
        from twisted.web.server import Site
        from twisted.web.static import File
        reactor.listenTCP(args.web, Site(File(".")))


    ## run WAMP application component
    ##
    from autobahn.twisted.wamp import ApplicationRunner
    router = args.router or 'ws://localhost:8080'

    runner = ApplicationRunner(router, u"realm1",
            extra = {'port': args.port, 'baudrate': args.baudrate, 'debug': args.debug},
            standalone = not args.router)

    ## start the component and the Twisted reactor ..
    ##
    runner.run(McuComponent)
