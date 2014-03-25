# encoding: utf-8
from zope.interface import implements

from twisted.application.service import IServiceMaker
from twisted.application import internet, service
from twisted.cred import credentials, portal
from twisted.cred.strcred import AuthOptionMixin
from twisted.internet import defer, reactor, ssl
from twisted.internet.serialport import SerialPort
from twisted.plugin import IPlugin
from twisted.python import log, usage
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.resource import WebSocketResource, HTTPChannelHixie76Aware

from tantan import TantanWampFactory
from zb import WsMcuFactory as ZBFactory


class Options(usage.Options, AuthOptionMixin):
    supportedInterfaces = (credentials.IUsernamePassword,
            credentials.IAnonymous,)
    optParameters = [
            ['outfile', 'o', None, 'Logfile [default: sys.stdout]'],
            ['host', 'h', 'localhost', 'Hostname or IP address to use for Web server'],
            ['port', 'p', 8080, 'Port to use for embedded Web server'],
            ['serial_port', 's', '/dev/ttyUSB0', 'Port to use for ZigBee serial port'],
            ['secure', 't', True, 'Initialize secure services'],
            ['baudrate', 'b', 38400, 'Baudrate for serial port communications'],
            ['debug', 'd', False, 'Enable debug-level log messaging'],
    ]


class TTServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "tantan-app"
    description = """Servicio web con base de datos CouchDB, via WAMP. Este
                     servicio incorpora las funciones de 'tantan-couch-wamp'
                     y 'tantan-web-site', en un solo puerto.
                  """
    options = Options


    def makeService(self, options):
        """
        Construir un servidor
        """
        host = str(options['host'])
        port = int(options['port'])
        serial_port = str(options['serial_port'])
        bdrate = int(options['baudrate'])
        debug = options['debug']
        is_secure = bool(options['secure'])
        log.msg('IS SECURE')
        log.msg(repr(is_secure))

        log.msg('Attempting to open %s' % (port, ))

        contextFactory = None
        wsprot = "ws"

        if is_secure:
            wsprot = "wss"
            contextFactory = ssl.DefaultOpenSSLContextFactory(
                    'keys/server.key',
                    'keys/server.crt')

        wsurl = "%s://%s:%s" % (wsprot, host, port)

        tantanFactory = TantanWampFactory(wsurl, debug = False,
                            debugCodePaths = True, debugWamp = debug,
                            debugApp = False)
        tantanFactory.setProtocolOptions(allowHixie76 = True)
        tantanFactory.startFactory()

        try:
            serialport = SerialPort(tantanFactory.zbProtocol, serial_port, reactor, baudrate=bdrate)
        except:
            serialport = None


        resource = WebSocketResource(tantanFactory)

        root = File("./static")
        root.putChild("ws_couch", resource)
        if is_secure:
            root.contentTypes['.crt'] = 'application/x-x509-ca-cert'

        site = Site(root)
        site.protocol = HTTPChannelHixie76Aware

        s = service.MultiService()

        web = internet.TCPServer(port, site)

        if is_secure:
            web = internet.SSLServer(port, site, contextFactory)

        web.setServiceParent(s)
        return s

serviceMaker = TTServiceMaker()
