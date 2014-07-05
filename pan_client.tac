import json
from pprint import pprint

from twisted.application import internet, service
from twisted.internet import reactor, defer, task
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.serialport import SerialPort
from twisted.python import components

from zope.interface import Interface, implements

from tantan.agents import PANTcpAgentManager
from tantan.pans import TanTanPANClientFactory
from tantan.itantan import IAgentManager, IPANClientFactory, IServerService
from tantan.service import TanTanPANClientService
from tantan.uarts import SerialEcho
from tantan.utils import loadConfig


components.registerAdapter(TanTanPANClientFactory,
                           IServerService,
                           IPANClientFactory)

components.registerAdapter(PANTcpAgentManager,
                           IServerService,
                           IAgentManager)

application = service.Application('tantanclient')
client = TanTanPANClientService(config=loadConfig('config.json'))
serviceCollection = service.IServiceCollection(application)
client.setServiceParent(serviceCollection)
#c = IPANClientFactory(client)
#internet.TCPClient('localhost', 8080, c).setServiceParent(serviceCollection)
