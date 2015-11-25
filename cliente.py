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

from autobahn.twisted.wamp import ApplicationSession
from txXBee.protocol import txXBee

from handlers import handle_rx
from handlers import is_RX
from handlers import is_PANID



class McuProtocol(txXBee):
    """ Protocol for communicating with a ZigBee network through a
        coordinator node in API Mode.

        Default values include :escaped = True for ZigBee API=2 mode
    """
    def __init__(self, session, debug = False, escaped=True):
        """ Default values include :escaped = True for ZigBee API=2 mode
        """
        super(McuProtocol, self).__init__(escaped=escaped)
        self.debug = debug
        self.session = session
        self.pan_id = None

    def connectionMade(self):
        self.getPanId()

    def handle_packet(self, packet):
        #print packet
        if is_PANID(self, packet):
            self.pan_id = pan_id = packet['parameter'].encode('hex').lstrip('0')
            print "GOT PAN ID", self.pan_id
        if is_RX(self, packet):
            handle_rx(self, packet)

    def connectionLost(self, reason):
        print "AGENT connection LOST"


    def getPanId(self):
        reactor.callFromThread(self.send,
                "at",
                frame_id="\x02",
                command="ID"
                )

    def sendND(self, evt=None):
        self._sendND()
        return 'ND Sent'

    def _sendND(self):
        reactor.callFromThread(self.send,
                "remote_at",
                frame_id="\x01",
                command="ND",
                )



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
            yield self.register(serialProtocol.getPanId, u"mx.ejeacuicola.api.nodos.pan_id")



if __name__ == '__main__':

    import sys, argparse
    ## parse command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", action = "store_true",
            help = "Enable debug output.")

    parser.add_argument("--baudrate", type = int, default = 9600,
            choices = [300, 1200, 2400, 4800, 9600, 19200, 57600, 115200],
            help = 'Serial port baudrate.')

    parser.add_argument("--port", type = str, default = '/dev/ttyACM0',
            help = 'Serial port to use (e.g. 3 for a COM port on Windows, \
                    /dev/ttyATH0 for Arduino Yun, /dev/ttyACM0 for \
                    Serial-over-USB on RaspberryPi.')

    parser.add_argument("--web", type = int, default = 0,
            help = 'Web port to use for embedded Web server. Use 0 to disable.')

    parser.add_argument("--router", type = str,
            default = 'wss://ruta-energetica-2014.herokuapp.com/ws',
            help = 'If given, connect to this WAMP router. Else run an \
                    embedded router on 8080. Default: \
                    wss://ruta-energetica-2014.herokuapp.com/ws')

    args = parser.parse_args()

    try:
        ## on Windows, we need port to be an integer
        args.port = int(args.port)
    except ValueError:
        pass

    from twisted.python import log
    log.startLogging(sys.stdout)


    ## import Twisted reactor
    if sys.platform == 'win32':
        from twisted.internet import win32eventreactor
        win32eventreactor.install()

    from twisted.internet import reactor
    print("Using Twisted reactor {0}".format(reactor.__class__))

    ## create embedded web server for static files
    if args.web:
        from twisted.web.server import Site
        from twisted.web.static import File
        reactor.listenTCP(args.web, Site(File(".")))

    ## run WAMP application component
    from autobahn.twisted.wamp import ApplicationRunner
    router = args.router or 'ws://localhost:8080'

    runner = ApplicationRunner(router, u"realm1",
            extra = {'port': args.port, 'baudrate': args.baudrate, 'debug': args.debug},
            standalone = not args.router)

    ## start the component and the Twisted reactor ..
    runner.run(McuComponent)
