from zope.interface import implements

from twisted.python import components
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.application import service

from tantan.agents.wamp import PANWampAgentManager
from tantan.itantan import IAgentManager, IServerService
from tantan.itantan import IPANServerFactory
from tantan.pans.server import TanTanPANServerFactory
from tantan.service import TanTanPANServerService



class Options(usage.Options):
    optParameters = [["port", "p", 1235, "The port number to listen on."]]


class MyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "tantan-server"
    description = "Initializes the Server Services for multiple PANs."
    options = Options

    def makeService(self, options):
        """
           Construct a TCPServer from a factory defined in myproject.
        """
        components.registerAdapter(TanTanPANServerFactory,
                                   IServerService,
                                   IPANServerFactory)

        components.registerAdapter(PANWampAgentManager,
                                   IServerService,
                                   IAgentManager)

        application = service.Application('tantanserver')
        serviceCollection = service.IServiceCollection(application)

        wsan_service = TanTanPANServerService()
        wsan_service.setServiceParent(serviceCollection)
        pan_factory = TanTanPANServerFactory(wsan_service)
        tcp = internet.TCPServer(int(options["port"]), pan_factory)
        tcp.setServiceParent(serviceCollection)
        return serviceCollection


# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.
serviceMaker = MyServiceMaker()
