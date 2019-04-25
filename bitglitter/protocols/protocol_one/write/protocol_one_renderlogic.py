from bitglitter.protocols.protocol_one.write.protocol_one_renderassets import asciiHeaderProcess, howManyFrames
from bitglitter.protocols.protocol_one.write.protocol_one_renderloop import renderLoop
from bitglitter.write.rendervideo import renderVideo

import logging

class EncodeFrame:
    '''This object takes what has already been processed from preProcessing, renders that data into images.'''

    def __init__(self):

        logging.debug('EncodeFrame initializing...')

        self.protocolVersion = 1

        self.activePath = None
        self.passThrough = None
        self.streamOutputPath = None
        self.bgVersion = None

        self.headerPalette = None
        self.initializerPalette = None
        self.streamPalette = None

        self.initializerPaletteDict = None
        self.headerPaletteDict = None
        self.streamPaletteDict = None

        self.blockHeight = None
        self.blockWidth = None
        self.pixelWidth = None
        self.framesPerSecond = None
        self.outputMode = None

        self.streamSHA = None

        self.sizeInBytes = None
        self.totalFrames = None
        self.compressionEnabled = None
        self.encryptionEnabled = None
        self.fileMaskEnabled = None
        self.dateCreated = None

        self.streamName = None
        self.streamDescription = None
        self.encryptionSalt = None
        self.postEncryptionHash = None


        self.includeInitializer = None

        self.framePosition = 1
        self.totalFrames = 0 #todo integrate into renderloop?


    def beginSessionProcess(self,

                            # General- Path and Protocol
                            activePath, passThrough, streamOutputPath, bgVersion,

                            # Palettes
                            initializerPalette, headerPalette, streamPalette,

                            # Color Dictionaries
                            initializerPaletteDict, headerPaletteDict, streamPaletteDict,

                            # Geometry & General Render Configuration
                            blockHeight, blockWidth, pixelWidth, framesPerSecond, outputMode,

                            # Frame Header
                            streamSHA,

                            # Stream Header - Binary Preamble
                            sizeInBytes, compressionEnabled, encryptionEnabled, fileMaskEnabled,
                            dateCreated,

                            # Stream Header - ASCII Encoded
                            streamName, streamDescription, preEncryptionHash

                            ):

        #Load arguments
        self.activePath = activePath
        self.passThrough = passThrough
        self.streamOutputPath = streamOutputPath
        self.bgVersion = bgVersion

        self.headerPalette = headerPalette
        self.initializerPalette = initializerPalette
        self.streamPalette = streamPalette

        self.initializerPaletteDict = initializerPaletteDict
        self.headerPaletteDict = headerPaletteDict
        self.streamPaletteDict = streamPaletteDict

        self.blockHeight = blockHeight
        self.blockWidth = blockWidth
        self.pixelWidth = pixelWidth
        self.framesPerSecond = framesPerSecond
        self.outputMode = outputMode

        self.streamSHA = streamSHA

        self.sizeInBytes = sizeInBytes
        self.compressionEnabled = compressionEnabled
        self.encryptionEnabled = encryptionEnabled
        self.fileMaskEnabled = fileMaskEnabled
        self.dateCreated = dateCreated

        self.streamName = streamName
        self.streamDescription = streamDescription
        self.postEncryptionHash = preEncryptionHash

        self.asciiCompressed = asciiHeaderProcess(self.fileMaskEnabled, self.activePath,
                                                  self.streamPalette, self.bgVersion, self.streamName,
                                                  self.streamDescription, self.postEncryptionHash, self.encryptionEnabled)

        self.totalFrames = howManyFrames(self.blockHeight, self.blockWidth, len(self.asciiCompressed), self.sizeInBytes,
                                                self.streamPalette, self.headerPalette, self.outputMode)

        self.remainderBlocks, self.imageOutputPath, self.frameNumberFormatted = renderLoop(self.blockHeight,
                                                self.blockWidth, self.pixelWidth, self.protocolVersion,
                                                self.initializerPalette, self.headerPalette, self.streamPalette,
                                                self.outputMode, self.streamOutputPath, self.activePath,
                                                self.passThrough, self.sizeInBytes, self.totalFrames,
                                                self.compressionEnabled, self.encryptionEnabled, self.fileMaskEnabled,
                                                self.dateCreated, self.asciiCompressed, self.streamSHA,
                                                self.initializerPaletteDict, self.headerPaletteDict,
                                                self.streamPaletteDict)

        if outputMode == 'video':
            renderVideo(self.streamOutputPath, self.dateCreated, self.imageOutputPath, self.frameNumberFormatted,
                        self.framesPerSecond)