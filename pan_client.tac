import json
from pprint import pprint

from twisted.application import internet, service
from twisted.internet import reactor, defer, task
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.serialport import SerialPort
from twisted.python import components

from zope.interface import Interface, implements

from pans import IPANClientFactory, TanTanPANClientFactory
from agents import IAgentManager, PANTcpAgentManager
from service import IPANService, TanTanPANClientService
from uarts import SerialEcho
from utils import loadConfig


components.registerAdapter(TanTanPANClientFactory,
                           IPANService,
                           IPANClientFactory)

components.registerAdapter(PANTcpAgentManager,
                           IPANService,
                           IAgentManager)

application = service.Application('tantanclient')
client = TanTanPANClientService(config=loadConfig('config.json'))
serviceCollection = service.IServiceCollection(application)
client.setServiceParent(serviceCollection)
#c = IPANClientFactory(client)
#internet.TCPClient('localhost', 8080, c).setServiceParent(serviceCollection)
