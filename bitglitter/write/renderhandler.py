import logging
import shutil

from bitglitter.config.config import config
from bitglitter.palettes.paletteutilities import paletteGrabber, ValuesToColor


class RenderHandler:
    '''This is where the rendering process is set up, and fed into the appropriate protocol objects and objects.  While
    this may seem like an unnecessary module currently (as of v1.0), I think it's purpose will become more apparent as
    we need a uniform place to handle various future protocols.
    '''

    def __init__(self,

                 # Initializer
                 protocol, blockHeight, blockWidth, headerPaletteID,

                 # Frame Header
                 streamSHA,

                 # Stream Header - Binary Preamble
                 sizeInBytes, compressionEnabled, encryptionEnabled, fileMaskEnabled, dateCreated, streamPaletteID,

                 # Stream Header - ASCII Encoded
                 bgVersion, streamName, streamDescription, postEncryptionHash,

                 # Render argument
                 pixelWidth, outputMode, streamOutputPath, framesPerSecond,

                 # Misc
                 activeFolder, passThrough
                 ):

        logging.debug('RenderHandler initializing...')

        self.protocol = protocol
        self.blockHeight = blockHeight
        self.blockWidth = blockWidth

        self.streamSHA = streamSHA

        self.sizeInBytes = sizeInBytes
        self.compressionEnabled = compressionEnabled
        self.encryptionEnabled = encryptionEnabled
        self.fileMaskEnabled = fileMaskEnabled
        self.dateCreated = dateCreated

        self.bgVersion = bgVersion
        self.streamName = streamName
        self.streamDescription = streamDescription
        self.postEncryptionHash = postEncryptionHash

        self.pixelWidth = pixelWidth
        self.outputMode = outputMode
        self.streamOutputPath = streamOutputPath
        self.framesPerSecond = framesPerSecond

        self.activePath = activeFolder
        self.passThrough = passThrough

        self.headerPalette = paletteGrabber(headerPaletteID)
        self.streamPalette = paletteGrabber(streamPaletteID)
        self.initializerPalette = paletteGrabber('1')

        self.headerPaletteDict = ValuesToColor(self.headerPalette, 'headerPalette')
        self.streamPaletteDict = ValuesToColor(self.streamPalette, 'streamPalette')
        self.initializerPaletteDict = ValuesToColor(self.initializerPalette, 'initializerPalette')

        self.protocol.beginSessionProcess(self.activePath, self.passThrough, self.streamOutputPath, self.bgVersion,
                                          self.initializerPalette, self.headerPalette, self.streamPalette,
                                          self.initializerPaletteDict, self.headerPaletteDict, self.streamPaletteDict,
                                          self.blockHeight, self.blockWidth, self.pixelWidth, self.framesPerSecond,
                                          self.outputMode, self.streamSHA, self.sizeInBytes, self.compressionEnabled,
                                          self.encryptionEnabled, self.fileMaskEnabled, self.dateCreated,
                                          self.streamName, self.streamDescription, self.postEncryptionHash)

        config.statsHandler.writeUpdate(((self.protocol.totalFrames - 1) * (self.blockHeight * self.blockWidth) +
                                         self.protocol.remainderBlocks), self.protocol.totalFrames, self.sizeInBytes)

        self.cleanup()


    def cleanup(self, blockPosition=0):
        '''Removes temporary folder, updates statistics.'''

        logging.debug("Deleting temporary folder....")
        shutil.rmtree(self.activePath)

        config.saveSession()
        logging.info('Write process complete!')