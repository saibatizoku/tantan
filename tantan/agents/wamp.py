# -*- coding: utf-8 -*-
from twisted.internet import reactor, task, defer
from twisted.python import components

from zope.interface import Interface, implements
from autobahn.wamp1.protocol import WampClientFactory

from tantan.itantan import IAgentManager, IPANClientFactory
from tantan.itantan import IServerService

from tantan.agents.tcp import PANTcpAgentManager
from tantan.wamp import WAMPClientProtocol

debug = True
debugW = False



class PANWampAgentManager(PANTcpAgentManager):

    implements(IAgentManager)

    client_protocol = WAMPClientProtocol

    def __init__(self, service):
        self.service = service
        self.agents = {}

    def makeFactory(self, pan_id=None):
        factory = WampClientFactory("ws://localhost:9000", debugWamp = debugW)
        factory.protocol = self.client_protocol
        factory.pan_id = pan_id
        return factory


components.registerAdapter(PANWampAgentManager,
        IServerService,
        IAgentManager)
