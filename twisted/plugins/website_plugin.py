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



class Options(usage.Options, AuthOptionMixin):
    supportedInterfaces = (credentials.IUsernamePassword,
            credentials.IAnonymous,)
    optParameters = [
            ['host', 'h', 'localhost', 'Hostname or IP address to use for Web server'],
            ['port', 'p', 8080, 'Port to use for embedded Web server'],
            ['debug', 'd', False, 'Enable debug-level log messaging'],
    ]


class TantanServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "tantan-web-site"
    description = "Servicio web para la publicación de sitios de internet."
    options = Options

    def makeService(self, options):
        """
        Construir un servidor
        """
        host = str(options['host'])
        port = int(options['port'])
        debug = options['debug']
        log.msg('Attempting to open %s' % (port, ))

        root = File("./static")

        site = Site(root)
        return internet.TCPServer(port, site)

serviceMaker = TantanServiceMaker()
