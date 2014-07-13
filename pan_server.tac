# -*- coding: utf-8 -*-
from twisted.application import internet, service
from twisted.internet import reactor, defer, task
from twisted.python import components

from tantan.agents.wamp import PANWampAgentManager
from tantan.itantan import IAgentManager, IPANServerFactory, IServerService
from tantan.pans.server import TanTanPANServerFactory
from tantan.service import TanTanPANServerService



application = service.Application('tantanserver')
serviceCollection = service.IServiceCollection(application)

wsan_service = TanTanPANServerService()
wsan_service.setServiceParent(serviceCollection)
pan_factory = IPANServerFactory(wsan_service)
internet.TCPServer(7780, pan_factory).setServiceParent(serviceCollection)
