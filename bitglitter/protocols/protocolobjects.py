class Protocol:
    '''Protocol objects are a container for what other funtionality is needed to carry out processing in Bitglitter.
    Those objects are stored in two sub-objects, ProtocolWrite and ProtocolRead.
    '''

    def __init__(self,

                 # Required values; it's lookup key, how data is converted, and how frames are decoded back into data.
                 versionNumber,
                 frameProcessor,
                 decoder,

                 # Optional write process steps.
                 verifyWriteParamsFunction = None,
                 preProcessing = None,
                 initializerUsed = None,

                 # Optional read process steps.
                 postProcessing = None
                 ):

        self.versionNumber = versionNumber

        self.write = ProtocolWrite(versionNumber, verifyWriteParamsFunction, preProcessing, frameProcessor,
                                   initializerUsed,)
        self.read = ProtocolRead(decoder, postProcessing)


class ProtocolWrite:
    '''Holds objects needed to perform a write for the Protocol object it is instantiated in.'''

    def __init__(self, versionNumber, verifyWriteParamsFunction, preProcessing, frameProcessor, initializerUsed):

        self.versionNumber = versionNumber

        self.verifyWriteParameters = verifyWriteParamsFunction
        self.preProcessing = preProcessing
        self.frameProcessor = frameProcessor

        self.initializerUsed = initializerUsed


class ProtocolRead:
    '''Holds objects needed to read a stream for the Protocol object it is instantiated in.'''

    def __init__(self, decoder, postProcessing):

        self.decoder = decoder
        self.postProcessing = postProcessing