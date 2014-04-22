from twisted.internet.protocol import Protocol


class SerialEcho(Protocol):

    def __init__(self, client):
        self.client = client
        self.pan_id = self.client.factory.pan_id

    def connectionMade(self):
        print "Serial connection made"
        print "CLIENT", repr(self.client)

    def connectionLost(self, reason):
        print "Serial port NOT CONNECTED", self.pan_id
        if self.pan_id in self.client.factory.service.pan:
            del self.client.factory.service.pan[self.pan_id]

    def dataReceived(self, data):
        print data.encode('hex')
        self.client.transport.write(data)


