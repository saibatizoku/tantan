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


class MyOptions(usage.Options):
    optParameters = [
            ['outfile', 'o', None, 'Logfile [default: sys.stdout]'],
            ['baudrate', 'b', 38400, 'Serial baudrate [default: 38400'],
            ['port', 'p', '/dev/ttyUSB0', 'Serial Port device'],
            ['webport', 'w', 8080, 'Web port to use for embedded Web server'],
            ['wsurl', 's', "ws://localhost:9000", 'WebSocket port to use for embedded WebSocket server']
    ]


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

    #port = o.opts['port']
    #log.msg('Attempting to open %s at %dbps as a %s device' % (port, o.opts['baudrate'], txXBee.__name__))
    webport = int(o.opts['webport'])
    #wsurl = o.opts['wsurl']

    #wsMcuFactory = WsMcuFactory(wsurl)
    #listenWS(wsMcuFactory)
    webdir = File("./static")
    web = Site(webdir)
    reactor.listenTCP(webport, web)

    reactor.run()
