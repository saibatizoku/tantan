# -*- coding: utf-8 -*-
import json
from pprint import pprint

from twisted.application import internet, service
from twisted.internet import protocol, reactor, defer, task
from twisted.internet.serialport import SerialPort
from twisted.internet.endpoints import clientFromString
from twisted.internet.endpoints import serverFromString, \
                                       TCP4ClientEndpoint, \
                                       TCP4ServerEndpoint
from twisted.python import components
from twisted.python.log import ILogObserver, FileLogObserver
from twisted.python.logfile import DailyLogFile

from txXBee.protocol import txXBee

from zope.interface import Interface, implements

from autobahn.twisted.websocket import WrappingWebSocketServerFactory, \
                                       WrappingWebSocketClientFactory

from autobahn.wamp1.protocol import WampServerFactory, \
                                    WampServerProtocol, \
                                    WampClientFactory, \
                                    WampClientProtocol, \
                                    exportRpc, \
                                    exportSub, \
                                    exportPub


debug = False
debugW = False


class PANTopicService:

    def __init__(self, allowedTopicIds):
        self.allowedTopicIds = allowedTopicIds
        self.counter = 0


    @exportSub("node-status", True)
    def subscribe(self, topicUriPrefix, topicUriSuffix):
        print "client subscribing to {}{}".format(topicUriPrefix, topicUriSuffix)
        try:
            if topicUriSuffix in self.allowedTopicIds:
                print "GOOD SUB node-status {}".format(topicUriPrefix)
            else:
                print "NO GOOD SUB node-status {}".format(topicUriPrefix)
        except:
            print "Bad topic"


    @exportPub("node-status", True)
    def subscribe(self, topicUriPrefix, topicUriSuffix, event):
        print "client publishing to {}{}".format(topicUriPrefix, topicUriSuffix)
        try:
            if topicUriSuffix in self.allowedTopicIds:
                print "GOOD SUB node-status {}".format(topicUriPrefix)
            else:
                print "NO GOOD SUB node-status {}".format(topicUriPrefix)
        except:
            print "Bad topic"


class WAMPServerProtocol(WampServerProtocol):

    def onSessionOpen(self):
        print "WAMP connection started"
        self.registerForPubSub("http://www.tantan.org/api/sensores#", True)
        self.registerForPubSub("http://api.tantan.net/pan/", True)
        self.registerForPubSub("http://api.tantan.net/pans/", True)
        self.call("http://api.tantan.net/pan#getPanId").addCallback(self.onPanId)

    def onPanId(self, result):
        print "WAMP PAN ID", result
        self.dispatch("http://api.tantan.net/pan/id", result)

    def connectionLost(self, reason):
        print "WAMP connection lost"
        WampServerProtocol.connectionLost(self, reason)


class WAMPClientProtocol(WampClientProtocol):

    @exportRpc("getPanId")
    def getPanId(self):
        return self.factory.pan_id

    def onSessionOpen(self):
        pan_id = self.factory.pan_id
        print "WAMP client connected", pan_id
        self.registerForRpc(self, "http://api.tantan.net/pan#")

    def connectionLost(self, reason):
        print "WAMP agent connection lost"
        WampClientProtocol.connectionLost(self, reason)
