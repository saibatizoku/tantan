# -*- coding: utf-8 -*-
from twisted.internet import protocol
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import components

from zope.interface import Interface, implements

from tantan.itantan import IPANServerFactory
from tantan.itantan import IServerService
from tantan.zigbee import PANZigBeeProtocol



class TanTanPANServerFactory(protocol.ServerFactory):

    implements(IPANServerFactory)

    protocol = PANZigBeeProtocol

    def __init__(self, service):
        self.service = service

    def getNetwork(self, pan_id=None):
        return self.service.getPAN(pan_id)

    def getNetworks(self, pan_id=None):
        return self.service.getPANs()


components.registerAdapter(TanTanPANServerFactory,
                           IServerService,
                           IPANServerFactory)
