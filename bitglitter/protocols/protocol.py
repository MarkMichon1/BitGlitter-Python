class Protocol:
    '''Protocol objects are a container for what other funtionality is needed to carry out processing in Bitglitter.
    Those objects are stored in two sub-objects, ProtocolWrite and ProtocolRead.
    '''

    def __init__(self,

                 # Required values; it's lookup key, how data is converted, and how frames are decoded back into data.
                 version_number,
                 frame_processor,
                 decoder,

                 # Optional write process steps.
                 verify_write_params_function = None,
                 pre_processing = None,
                 initializer_used = None,

                 # Optional read process steps.
                 post_processing = None
                 ):

        self.version_number = version_number

        self.write = ProtocolWrite(version_number, verify_write_params_function, pre_processing, frame_processor,
                                   initializer_used, )
        self.read = ProtocolRead(decoder, post_processing)


class ProtocolWrite:
    '''Holds objects needed to perform a write for the Protocol object it is instantiated in.'''

    def __init__(self, versionNumber, verifyWriteParamsFunction, preProcessing, frameProcessor, initializerUsed):

        self.version_number = versionNumber

        self.verify_write_parameters = verifyWriteParamsFunction
        self.pre_processing = preProcessing
        self.frame_processor = frameProcessor

        self.initializer_used = initializerUsed


class ProtocolRead:
    '''Holds objects needed to read a stream for the Protocol object it is instantiated in.'''

    def __init__(self, decoder, postProcessing):

        self.decoder = decoder
        self.post_processing = postProcessing