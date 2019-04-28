import logging

from bitstring import BitStream

from bitglitter.palettes.paletteutilities import _paletteGrabber, ColorsToValue
from bitglitter.read.framehandler import FrameHandler
from bitglitter.read.framelockon import frameLockOn
from bitglitter.read.decoderassets import minimumBlockCheckpoint, readFrameHeader, readInitializer, \
    returnStreamPalette, validatePayload

from PIL import Image

class Decoder:
    '''The Decoder object is what ultimately handles all higher level processing of each BitGlitter frame, orchestrating
    lower-level behavior.  After frames are locked onto, and information is validated as not corrupt (or not needed,
    as the frames may have already been previously read), that data is then passed onto the Assembler.
    '''

    def __init__(self, isVideo, configObject, scryptN, scryptR, scryptP, blockHeightOverride, blockWidthOverride,
                 outputPath, encryptionKey):

        self.isVideo = isVideo
        self.frameNumber = 0

        # Input arguments
        self.blockHeightOverride = blockHeightOverride
        self.blockWidthOverride = blockWidthOverride
        self.scryptN = scryptN
        self.scryptR = scryptR
        self.scryptP = scryptP
        self.encryptionKey = encryptionKey
        self.outputPath = outputPath

        # Lock on Characteristics
        self.pixelWidth = None
        self.blockHeight = None
        self.blockWidth = None
        self.protocolVersion = None
        self.headerPalette = None
        self.framePalette = None
        self.blocksToRead = None

        # Palette Variables


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

        self.activeFrame = None
        self.frameHandler = None
        self.checkpointPassed = True

        self.framePayload = None
        self.streamHeaderBinaryPreamble = BitStream()
        self.carryOverBits = None

        # Frame Metadata
        self.bgVersion = None
        self.streamSHA = None
        self.frameSHA = None

        # Auxiliary Components
        self.configObject = configObject
        self.frameHandler = FrameHandler()



    def decodeImage(self, fileToInput):
        '''This method is used to decode a single image (jpg, png, bmp).'''

        self.activeFrame = Image.open(fileToInput)
        self.frameHandler.loadNewFrame(self.activeFrame, True)

        if self._firstFrameSetup() == False:
            return False

        if self._imageFrameSetup() == False:
            return False

        if self._frameValidation('primaryPalette') == False:
            return False

        if self._payloadProcess('primaryPalette') == False:
            return False #todo revisit?



    def decodeVideoFrame(self, fileToInput):
        '''This is the higher level method that decodes and validates data from each video frame, and then passes it to
        the Assembler object for further processing.
        '''

        self.frameNumber += 1
        self.streamSHA = None
        self.frameSHA = None
        self.framePayload = None

        self.activeFrame = Image.open(fileToInput)
        self.frameHandler.loadNewFrame(self.activeFrame, True)

        if self.frameNumber == 1:
            if self._firstFrameSetup() == False:
                return False
        else:
            self._attemptStreamPaletteLoad()

        if self._frameValidation() == False:
            return False

        self._payloadProcess() #todo this will be tied into the whole palette thing.


    def _firstFrameSetup(self):
        '''This is a series of tasks that must be done for the first frames of both video and images.  The frame is
        locked onto, and the initializer from the frame is validated and loaded.
        '''

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

        self.frameHandler.updateScanGeometry(self.blockHeight, self.blockWidth, self.pixelWidth)

        self.protocolVersion, self.framePalette = readInitializer(self.frameHandler.returnInitializer(),
                                                                  self.blockHeight, self.blockWidth,
                                                                  self.configObject.colorHandler.customPaletteList,
                                                                  self.configObject.colorHandler.defaultPaletteList)
        if self.protocolVersion == False:
            return False
        logging.debug(f'framePalette ID loaded: {self.framePalette.id}')


    def _frameValidation(self, paletteType):
        '''This internal method first validates the frame by checking the frame header, and then checks with the
        Assembler object to see if this frame is needed.  This is ran on every frame.
        '''

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
        and then passes it on into the Assembler.  This is ran on every frame.
        '''

        self.carryOverBits.append(self.frameHandler.returnRemainderPayload(paletteType))
        self.framePayload = self.carryOverBits
        self.carryOverBits = BitStream()

        if validatePayload(self.framePayload, self.frameSHA) == False:
            return False

        self.configObject.assembler.acceptFrame(self.streamSHA, self.framePayload, self.frameNumber, self.scryptN,
                                                self.scryptR, self.scryptP, self.outputPath, self.encryptionKey)


    def _attemptStreamPaletteLoad(self):
        '''The stream header is where the data stating the stream palette used is stated.
        Commonly this will be able to be read on the first frame, but for larger stream headers using custom palettes,
        this may take several frames for it to successfully load, since the full compressed header package must be read
        first.  Assuming the stream palette hasn't loaded yet, this will call the Assembler object to check and see if
        the stream header, along with its ASCII component have been fully read yet.  If so, it is loaded into the proper
        class attributes.
        '''

        pass #todo this will be frame 2 ran and on until its loaded.


    def _imageFrameSetup(self):
        '''This method validates the initializer bit string, as well as loads the primary palette into memory.  The
        reason why this must be a separate methof from _videoFirstFrameSetup is because both images and videos handle
        palettes differently.  Images only need to worry about the "primary palette" or the palette that is being used
        on that particular frame, while videos must intelligently switch between the header palette and the stream
        palette.
        '''

        self.protocolVersion, self.primaryPalette = readInitializer(self.frameHandler.returnInitializer(),
                                                                  self.blockHeight, self.blockWidth,
                                                                  self.configObject.colorHandler.customPaletteList,
                                                                  self.configObject.colorHandler.defaultPaletteList)
        if self.protocolVersion == False:
            return False
        logging.debug(f'primaryPalette ID loaded: {self.primaryPalette.id}')

        self.primaryPaletteDict = ColorsToValue(self.primaryPalette)
        self.frameHandler.primaryPaletteBitLength = self.primaryPalette.bitLength
        self.frameHandler.updateDictionaries('primaryPalette', self.primaryPaletteDict, self.primaryPalette)


    def _videoFirstFrameSetup(self):
        '''This method is ran on the first frame of the decoded video, to load in the header palette.  To prevent a
        duplicate explanation, please see _imagePaletteSetup directly above.
        '''

        self.protocolVersion, self.headerPalette = readInitializer(self.frameHandler.returnInitializer(),
                                                                  self.blockHeight, self.blockWidth,
                                                                  self.configObject.colorHandler.customPaletteList,
                                                                  self.configObject.colorHandler.defaultPaletteList)
        if self.protocolVersion == False:
            return False
        logging.debug(f'headerPalette ID loaded: {self.headerPalette.id}')

        # Now with headerPalette loaded, we can get its color set as well as generate its ColorsToValue dictionary,
        # As well as propagate these values to frameHandler.
        self.headerPaletteDict = ColorsToValue(self.headerPalette)
        self.frameHandler.headerPaletteBitLength = self.headerPalette.bitLength
        self.frameHandler.updateDictionaries('headerPalette', self.headerPaletteDict, self.headerPalette.colorSet)