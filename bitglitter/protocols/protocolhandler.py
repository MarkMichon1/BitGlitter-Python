import logging

import bitglitter.protocols.protocolversions as protocolversions

class ProtocolHandler:
    '''This is the master protocol object that holds Protocol 1, and will hold future protocols down the road.'''

    def __init__(self):

        logging.debug('Protocol handler initializing...')

        self.available_protocols = {}
        self.available_write_protocols = {}
        self.available_read_protocols = {}


    def _accept_new_protocol(self, protocol):
        '''Internal method that takes protocols and loads them into the above dictionaries.'''

        self.available_protocols[protocol.version_number] = protocol
        self.available_write_protocols[protocol.version_number] = protocol.write
        self.available_read_protocols[protocol.version_number] = protocol.read


    def return_read_protocol(self, version_key):
        '''This returns the read protocol object.'''

        return self.available_read_protocols[version_key]


    def return_write_protocol(self, version_key):
        '''This returns the collection of write protocol objects to render a stream.'''

        return self.available_write_protocols[version_key]

# This is where new protocols get added.
protocol_handler = ProtocolHandler()
protocol_handler._accept_new_protocol(protocolversions.protocolOne)