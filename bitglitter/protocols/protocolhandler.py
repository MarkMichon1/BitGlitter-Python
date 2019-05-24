import logging

import bitglitter.protocols.protocolversions as protocolversions

class ProtocolHandler:
    '''This is the master protocol object that holds Protocol 1, and will hold future protocols down the road.'''

    def __init__(self):

        logging.debug('Protocol handler initializing...')

        self.availableProtocols = {}
        self.availableWriteProtocols = {}
        self.availableReadProtocols = {}


    def _acceptNewProtocol(self, protocol):
        '''Internal method that takes protocols and loads them into the above dictionaries.'''

        self.availableProtocols[protocol.versionNumber] = protocol
        self.availableWriteProtocols[protocol.versionNumber] = protocol.write
        self.availableReadProtocols[protocol.versionNumber] = protocol.read


    def returnReadProtocol(self, versionKey):
        '''This returns the read protocol object.'''

        return self.availableReadProtocols[versionKey]


    def returnWriteProtocol(self, versionKey):
        '''This returns the collection of write protocol objects to render a stream.'''

        return self.availableWriteProtocols[versionKey]

# This is where new protocols get added.
protocolHandler = ProtocolHandler()
protocolHandler._acceptNewProtocol(protocolversions.protocolOne)