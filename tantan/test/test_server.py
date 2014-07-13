# -*- coding: utf-8 -*-
import tantan #.service import TantanPANServerService
from twisted.test import proto_helpers
from twisted.trial import unittest


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.pan_service = tantan.service.TanTanPANServerService()
        self.factory = tantan.pans.server.TanTanPANServerFactory(self.pan_service)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)

        self.pan_service.startService()

    def tearDown(self):
        self.pan_service.stopService()

    def test_start(self):
        self.assertNotEqual(self.pan_service.wamp, None)
