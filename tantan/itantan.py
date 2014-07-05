# -*- coding: utf-8 -*-
from zope.interface import Interface



class IAgentManager(Interface):
    """
    """


class IPANServerFactory(Interface):
    """ A factory for clients made to publish at a central node.
    """


class IPANClientFactory(Interface):
    """ A factory for clients made to publish at a central node.

        The PAN client factory manages connections to Physical-
        Area-Networks (PANs), by controlling UART connections
        via the PAN service.
    """


class IServerService(Interface):
    """ A client service made to connect Physical-Area-Networks to a
        central server over the network.
    """
    def startAgent():
        """
        """

    def stopAgent():
        """
        """
