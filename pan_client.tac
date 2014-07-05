# encoding: utf-8
from twisted.application import internet, service
from twisted.internet import reactor, defer, task
from twisted.python import components

from tantan.agents import PANTcpAgentManager
from tantan.pans import TanTanPANClientFactory
from tantan.itantan import IAgentManager, IPANClientFactory, IServerService
from tantan.service import TanTanPANClientService
from tantan.utils import loadConfig



components.registerAdapter(TanTanPANClientFactory,
                           IServerService,
                           IPANClientFactory)

components.registerAdapter(PANTcpAgentManager,
                           IServerService,
                           IAgentManager)

application = service.Application('tantanclient')
serviceCollection = service.IServiceCollection(application)

client = TanTanPANClientService(config=loadConfig('config.json'))
client.setServiceParent(serviceCollection)
#c = IPANClientFactory(client)
#internet.TCPClient('localhost', 8080, c).setServiceParent(serviceCollection)
