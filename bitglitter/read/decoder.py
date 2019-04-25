import logging

from bitstring import BitStream, BitArray

from bitglitter.palettes.paletteutilities import _paletteGrabber, ColorsToValue
from bitglitter.read.framehandler import FrameHandler
from bitglitter.read.framelockon import frameLockOn
from bitglitter.read.decoderassets import minimumBlockCheckpoint, readFrameHeader, readInitializer, \
    returnStreamPalette, validatePayload

from PIL import Image

class Decoder:

    def __init__(self, isVideo, configObject, scryptN, scryptR, scryptP, blockHeightOverride, blockWidthOverride,
                 outputPath, encryptionKey):

        self.isVideo = isVideo
        self.frameNumber = 0

        # Lock on Characteristics
        self.pixelWidth = None
        self.blockHeight = None
        self.blockWidth = None
        self.blockHeightOverride = blockHeightOverride
        self.blockWidthOverride = blockWidthOverride
        self.protocolVersion = None
        self.headerPalette = None
        self.primaryPalette = None
        self.blocksToRead = None

        self.streamSHA = None
        self.frameSHA = None

        # Misc Setup
        self.initializerPalette = _paletteGrabber('1')
        self.initializerPaletteColorSet = self.initializerPalette.colorSet
        self.initializerPaletteDict = ColorsToValue(_paletteGrabber('1'))
        self.headerPaletteDict = None
        self.primaryPaletteDict = None
        self.headerPaletteColorSet = None
        self.primaryPaletteColorSet = None
        self.streamPaletteColorSet = None
        self.streamPalette = None
        self.streamPaletteDict = None

        self.scryptN = scryptN
        self.scryptR = scryptR
        self.scryptP = scryptP
        self.encryptionKey = encryptionKey
        self.outputPath = outputPath

        self.activeFrame = None
        self.frameHandler = None
        self.checkpointPassed = True

        self.framePayload = None
        self.streamHeaderAccumulator = None #todo maybe del?
        self.streamHeaderBinaryPreamble = BitStream()
        self.carryOverBits = None

        # Stream Header ASCII Part
        self.bgVersion = None,
        self.streamName = None
        self.streamDescription = None
        self.fileList = None
        self.customColorName = None
        self.customColorDescription = None
        self.customColorDateCreated = None
        self.customColorPalette = None


        self.configObject = configObject
        self.frameHandler = FrameHandler()



    def decodeImage(self, fileToInput):

        self.activeFrame = Image.open(fileToInput)

        if self._firstFrameSetup() == False:
            return False

        if self._imageSetup() == False:
            return False

        if self._frameValidation('primaryPalette') == False:
            return False

        if self._payloadProcess('primaryPalette') == False:
            return False #todo revisit



    def decodeVideoFrame(self, fileToInput):
        '''This is ran over each video frame.'''
        self.frameNumber += 1
        self.streamSHA = None
        self.frameSHA = None
        self.framePayload = None


        self.activeFrame = Image.open(fileToInput)

        if self.frameNumber == 1:
            if self._firstFrameSetup() == False:
                return False
        else:
            self._attemptStreamPaletteLoad()

        if self._frameValidation() == False:
            return False

        self._payloadProcess()


    def _firstFrameSetup(self):

        self.checkpointPassed = minimumBlockCheckpoint(self.blockHeightOverride, self.blockWidthOverride,
                                                       self.activeFrame.size[0], self.activeFrame.size[1])
        if self.checkpointPassed == False:
            return False

        self.blockHeight = self.blockHeightOverride
        self.blockWidth = self.blockWidthOverride

        self.blockHeight, self.blockWidth, self.pixelWidth = frameLockOn(self.activeFrame, self.blockHeightOverride,
                                                                         self.blockWidthOverride)
        if self.pixelWidth == False:
            return False

        self.frameHandler = FrameHandler.someNewMethod() #todo multiple perhaps, we'll see


    def _frameValidation(self, paletteType):
        '''This internal method first validates the frame by checking the frame header, and then checks with the
        Assembler object to see if this frame is needed.'''

        self.frameHeaderBits, self.carryOverBits = self.frameHandler.returnFrameHeader(paletteType)

        self.streamSHA, self.frameSHA, self.frameNumber, self.blocksToRead = \
            readFrameHeader(self.frameHeaderBits)

        self.frameHandler.updateBlocksToRead(self.blocksToRead)

        if self.streamSHA == False:
            return False

        if self.configObject.assembler.checkIfFrameNeeded(self.streamSHA, self.frameNumber) == False:
            return False


    def _payloadProcess(self, paletteType):
        '''If the frame is validated, this method appends any carry-overy bits from reading the frame handler blocks,
        and then passes it on into the Assembler.'''


        self.carryOverBits.append(self.frameHandler.returnRemainderPayload(paletteType))
        self.framePayload = self.carryOverBits
        self.carryOverBits = BitStream()

        if validatePayload(self.framePayload, self.frameSHA) == False:
            return False

        self.configObject.assembler.acceptFrame(self.streamSHA, self.framePayload, self.frameNumber, self.scryptN,
                                                self.scryptR, self.scryptP, self.outputPath, self.encryptionKey)


    def _attemptStreamPaletteLoad(self):
        pass #todo this will be frame 2 ran


    def _imageSetup(self):
        self.protocolVersion, self.primaryPalette = readInitializer(self.frameHandler.returnInitializer(),
                                                                   self.blockHeight, self.blockWidth,
                                                                    self.configObject.colorHandler.customPaletteList,
                                                                    self.configObject.colorHandler.defaultPaletteList)
        if self.protocolVersion == False:
            return False
        logging.debug(f'primaryPalette ID loaded: {self.primaryPalette.id}')

        # Now with headerPalette loaded, we can get its color set as well as generate its ColorsToValue dictionary,
        # As well as propagate these values to frameHandler.
        self.primaryPaletteDict = ColorsToValue(self.primaryPalette)
        self.frameHandler.primaryPaletteBitLength = self.primaryPalette.bitLength
        self.frameHandler.updateDictionaries('primaryPalette', self.primaryPaletteDict, self.primaryPalette)


    def _videoSetup(self):
        self.protocolVersion, self.headerPalette = readInitializer(self.frameHandler.returnInitializer(),
                                                                   self.blockHeight, self.blockWidth)
        if self.protocolVersion == False:
            return False
        logging.debug(f'headerPalette ID loaded: {self.headerPalette.id}')

        # Now with headerPalette loaded, we can get its color set as well as generate its ColorsToValue dictionary,
        # As well as propagate these values to frameHandler.
        self.headerPaletteDict = ColorsToValue(self.headerPalette)
        self.frameHandler.headerPaletteBitLength = self.headerPalette.bitLength
        self.headerPaletteColorSet = self.headerPalette.colorSet
        self.frameHandler.updateDictionaries('headerPalette', self.headerPaletteDict, self.headerPaletteColorSet)