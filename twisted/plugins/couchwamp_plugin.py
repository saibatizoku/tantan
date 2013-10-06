# encoding: utf-8
from zope.interface import implements

from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.cred import credentials, portal
from twisted.cred.strcred import AuthOptionMixin
from twisted.plugin import IPlugin
from twisted.python import log, usage
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.resource import WebSocketResource, \
                              HTTPChannelHixie76Aware

from couch import TTCouchFactory


class Options(usage.Options, AuthOptionMixin):
    supportedInterfaces = (credentials.IUsernamePassword,
            credentials.IAnonymous,)
    optParameters = [
            ['outfile', 'o', None, 'Logfile [default: sys.stdout]'],
            ['host', 'h', 'localhost', 'Hostname or IP address to use for Web server'],
            ['port', 'p', 9001, 'Port to use for embedded Web server'],
            ['debug', 'd', False, 'Enable debug-level log messaging'],
    ]


class TantanServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "tantan-couch-wamp"
    description = """Servicio de websockets para interactuar con WAMP y
                     servidores CouchDB.
                  """
    options = Options

    def makeService(self, options):
        """
        Construir un servidor
        """
        host = str(options['host'])
        port = int(options['port'])
        debug = options['debug']
        log.msg('Attempting to open %s' % (port, ))
        wsurl = "ws://%s:%s" % (host, port)
        ttCouchFactory = TTCouchFactory(wsurl, debug = debug)
        ttCouchFactory.setProtocolOptions(allowHixie76 = True)
        ttCouchFactory.startFactory()

        resource = WebSocketResource(ttCouchFactory)

        root = resource

        site = Site(root)
        site.protocol = HTTPChannelHixie76Aware
        return internet.TCPServer(port, site)

serviceMaker = TantanServiceMaker()
