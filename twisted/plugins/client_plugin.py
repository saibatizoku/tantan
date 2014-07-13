from zope.interface import implements

from twisted.python import components
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
from twisted.application import internet
from twisted.application import service

from tantan.agents.tcp import PANTcpAgentManager
from tantan.itantan import IAgentManager, IServerService
from tantan.itantan import IPANClientFactory
from tantan.pans.client import TanTanPANClientFactory
from tantan.service import TanTanPANClientService
from tantan.utils import loadConfig



class Options(usage.Options):
    optParameters = [
                ["config", "c", "./config.json", "The path to the local configuration file."],
            ]


class ClientServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "tantan-client"
    description = "Initializes the Client Services for multiple PANs."
    options = Options

    def makeService(self, options):
        """
           Construct a TCPServer from a factory defined in myproject.
        """
        application = service.Application('tantanclient')
        serviceCollection = service.IServiceCollection(application)

        client = TanTanPANClientService(config=loadConfig(options['config']))
        client.setServiceParent(serviceCollection)
        return serviceCollection


# Now construct an object which *provides* the relevant interfaces
# The name of this variable is irrelevant, as long as there is *some*
# name bound to a provider of IPlugin and IServiceMaker.
serviceMaker = ClientServiceMaker()
