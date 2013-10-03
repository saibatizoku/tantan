# encoding: utf-8
from zope.interface import implements

from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.plugin import IPlugin
from twisted.python import log, usage
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.resource import WebSocketResource, \
                              HTTPChannelHixie76Aware

from couch import TTCouchFactory


class Options(usage.Options):
        optParameters = [
                ['outfile', 'o', None, 'Logfile [default: sys.stdout]'],
                ['host', 'h', 'localhost', 'Logfile [default: sys.stdout]'],
                ['port', 'p', 8080, 'Web port to use for embedded Web server'],
                ['debug', 'd', False, 'Web port to use for embedded Web server'],
        ]


class TantanServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "tantan-couch"
    description = "Sistema de acuacultura TanTan"
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

        root = File("./static")

        root.putChild("ws", resource)

        site = Site(root)
        site.protocol = HTTPChannelHixie76Aware
        return internet.TCPServer(port, site)

serviceMaker = TantanServiceMaker()
#
#application = service.Application("tantan")
#echoService = internet.TCPServer(8000, EchoFactory())
#echoService.setServiceParent(application)
