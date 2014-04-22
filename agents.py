from twisted.internet import reactor, task, defer
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.serialport import SerialPort

from zope.interface import Interface, implements
from autobahn.wamp1.protocol import WampClientFactory

from pans import IPANClientFactory
from uarts import SerialEcho
from utils import compDictKeys
from wamp import WAMPClientProtocol


class IAgentManager(Interface):
    """
    """


class PANTcpAgentManager(object):

    implements(IAgentManager)

    def __init__(self, service):
        self.service = service
        self.agents = {}
        self.agent_check = task.LoopingCall(self.checkAgents)
        self.agent_check.start(6)

    def makeFactory(self, pan_id=None):
        factory = IPANClientFactory(self.service)
        factory.pan_id = pan_id
        return factory

    def addAgent(self, pan_id, host, port):
        factory = self.makeFactory(pan_id)
        endpoint = TCP4ClientEndpoint(reactor, host, port)
        agent = endpoint.connect(factory)

        def setConn(client):
            host = client.transport.getHost()
            peer = client.transport.getPeer()
            print "{0} AGENT; {1}; {2}".format(pan_id, host, peer)
            self.agents[pan_id] = client
            return client

        def failedConn(failure):
            print "Could not connect {0} AGENT; {1}".format(pan_id, failure.value)
            if pan_id in self.agents:
                self.agents[pan_id] = None
            return None

        agent.addCallback(setConn)
        agent.addErrback(failedConn)
        return agent

    def hasDisconnectedAgents(self):
        agents = self.agents
        networks = self.service.config.get('networks', {})
        diff = compDictKeys(agents, networks)
        return len(diff) > 0

    def checkAgents(self):
        print "CHECKING AGENTS"
        #if self.hasDisconnectedAgents():
        for pan_id in self.agents:
            agent = self.agents.get(pan_id, None)
            if agent and agent == "CONNECTING":
                print "Agent present; already trying to connect", pan_id
            elif agent:
                print "Agent present", pan_id, agent.connected
            else:
                print "Agent NOT present", pan_id
                self.agents[pan_id] = "CONNECTING"
                self.service.startPANClient(pan_id)


class PANWampAgentManager(PANTcpAgentManager):

    implements(IAgentManager)

    def makeFactory(self, pan_id=None):
        factory = WampClientFactory("ws://localhost:9000", debugWamp = debugW)
        factory.protocol = WAMPClientProtocol
        factory.pan_id = pan_id
        return factory
