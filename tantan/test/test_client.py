# -*- coding: utf-8 -*-
import tantan
from twisted.test import proto_helpers
from twisted.trial import unittest

from base import SERVER_CONFIG, CLIENT_CONFIG


class ClientTestCase(unittest.TestCase):

    def _setUpServer(self):
        self.pan_server = tantan.service.TanTanPANServerService(config=SERVER_CONFIG)
        self.server_factory = tantan.pans.server.TanTanPANServerFactory(self.pan_server)
        self.server_proto = self.server_factory.buildProtocol(('127.0.0.1', 0))
        self.server_tr = proto_helpers.StringTransport()
        self.server_proto.makeConnection(self.server_tr)
        self.pan_server.startService()

    def setUp(self):
        self._setUpServer()
        self.pan_service = tantan.service.TanTanPANClientService(config=CLIENT_CONFIG)

    def test_start(self):
        pass

    def tearDown(self):
        self.pan_server.stopService()
