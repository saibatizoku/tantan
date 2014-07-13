# -*- coding: utf-8 -*-
import tantan #.service import TantanPANServerService
from twisted.test import proto_helpers
from twisted.trial import unittest

from base import SERVER_CONFIG, CLIENT_CONFIG

class ZigBeeTestCase(unittest.TestCase):
    def setUp(self):
        self.pan_service = tantan.service.TanTanPANServerService(config=SERVER_CONFIG)
        self.factory = tantan.pans.server.TanTanPANServerFactory(self.pan_service)
        #print dir(self.factory)
        self.proto = self.factory.buildProtocol(('127.0.0.1', 0))
        self.tr = proto_helpers.StringTransport()
        self.proto.makeConnection(self.tr)


    def test_atcommand_id(self):
        self.proto.send('at', command="ID")
        at_id = '\x7e\x00\x04\x08\x01\x49\x44\x69'
        self.assertEqual(self.tr.value(), at_id)

    def test_atcommand_d0(self):
        self.proto.send('remote_at', command="D0", value='04'.decode('hex'))
        expected = '7e000f17000000000000000000fffe02443075'.decode('hex')
        self.assertEqual(self.tr.value(), expected)
        self.tr.clear()

        self.proto.send('remote_at', dest_addr_long="13a20040b13736b9".decode('hex'), dest_addr="0020".decode('hex'), command="D0", value='\x04')
        expected = '7e000f17007d33a20040b13736b9002002443086'.decode('hex')
        self.assertEqual(self.tr.value(), expected)
        self.tr.clear()

        self.proto.send('remote_at', dest_addr_long="13a20040b13736b9".decode('hex'), dest_addr="0020".decode('hex'), command="D0", value='\x05')
        expected = '7e000f17007d33a20040b13736b9002002443086'.decode('hex')
        self.assertEqual(self.tr.value(), expected)
        self.tr.clear()

    def tearDown(self):
        #self.proto.sendClose()
        self.pan_service.stopService()
