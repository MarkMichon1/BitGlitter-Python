import logging

from PIL import Image

from bitglitter.palettes.paletteutilities import paletteGrabber, ColorsToValue, _validateAndAddPalette
from bitglitter.read.decoderassets import minimumBlockCheckpoint, readFrameHeader, readInitializer, validatePayload
from bitglitter.read.framehandler import FrameHandler
from bitglitter.read.framelockon import frameLockOn


class Decoder:
    '''The Decoder object is what ultimately handles all higher level processing of each BitGlitter frame, orchestrating
    lower-level behavior.  After frames are locked onto, and information is validated as not corrupt (or not needed,
    as the frames may have already been previously read), that data is then passed onto the Assembler.
    '''

    def __init__(self, isVideo, configObject, scryptN, scryptR, scryptP, blockHeightOverride, blockWidthOverride,
                 outputPath, encryptionKey):

        # Misc Setup
        self.isVideo = isVideo
        self.frameNumberofVideo = 0
        self.activeFrame = None
        self.checkpointPassed = True
        self.fatalCheckpoint = True # Non-recoverable errors that require an immediate break from the loop.
        self.streamHeaderCleared = False
        self.duplicateFrameRead = False

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

        # Palette Variables
        self.initializerPalette = paletteGrabber('1')
        self.initializerPaletteDict = ColorsToValue(self.initializerPalette)
        self.primaryPalette = None
        self.primaryPaletteDict = None
        self.headerPalette = None
        self.headerPaletteDict = None
        self.streamPalette = None
        self.streamPaletteDict = None

        # Custom color data used in instantiating new palette
        self.customColorName = None
        self.customColorDescription = None
        self.customColorDateCreated = None
        self.customColorColorSet = None

        # Frame Data
        self.streamSHA = None
        self.frameSHA = None
        self.streamSHAFromLastFrame = None
        self.frameNumberofStream = None
        self.framePayload = None
        self.carryOverBits = None
        self.blocksToRead = None

        # Auxiliary Components
        self.configObject = configObject
        self.frameHandler = FrameHandler(self.initializerPalette, self.initializerPaletteDict)


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
            return False

        if self.configObject.assembler.saveDict[self.streamSHA].streamHeaderASCIIComplete == True \
                and self.configObject.assembler.saveDict[self.streamSHA].streamPaletteRead == False:
            self._attemptStreamPaletteLoad()


    def decodeVideoFrame(self, fileToInput):
        '''This is the higher level method that decodes and validates data from each video frame, and then passes it to
        the Assembler object for further processing.
        '''

        self.frameNumberofVideo += 1
        self.frameNumberofStream = None
        self.frameSHA = None
        self.framePayload = None
        self.carryOverBits = None
        self.duplicateFrameRead = False

        self.activeFrame = Image.open(fileToInput)

        if self.frameNumberofVideo == 1:
            self.frameHandler.loadNewFrame(self.activeFrame, True)

            if self._firstFrameSetup() == False:
                return False

            if self._videoFirstFrameSetup() == False:
                return False

        else:
            self.frameHandler.loadNewFrame(self.activeFrame, False)

            if self.streamHeaderCleared == False:
                self._attemptStreamPaletteLoad()

                if self.fatalCheckpoint == False:
                    return False

        if self.streamHeaderCleared == False: # We are still on headerPalette frames.
            if self._frameValidation('headerPalette') == False:
                return False

            if self._payloadProcess('headerPalette') == False:
                return False

        else: # It has switched to streamPalette frames.
            if self._frameValidation('streamPalette') == False:
                return False

            if self._payloadProcess('streamPalette') == False:
                return False


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


    def _frameValidation(self, paletteType):
        '''This internal method first validates the frame by checking the frame header, and then checks with the
        Assembler object to see if this frame is needed.  This is ran on every frame.
        '''

        self.frameHeaderBits, self.carryOverBits = self.frameHandler.returnFrameHeader(paletteType)

        self.streamSHA, self.frameSHA, self.frameNumberofStream, self.blocksToRead = \
            readFrameHeader(self.frameHeaderBits)

        if self.streamSHA == False:
            return False

        self.streamSHAFromLastFrame = self.streamSHA
        self.frameHandler.updateBlocksToRead(self.blocksToRead)

        if self.configObject.assembler.checkIfFrameNeeded(self.streamSHA, self.frameNumberofStream) == False:
            self.duplicateFrameRead = True
            if self.isVideo == False:
                self.configObject.assembler.saveDict[self.streamSHA]._closeSession()

            return False


    def _payloadProcess(self, paletteType):
        '''If the frame is validated, this method appends any carry-overy bits from reading the frame handler blocks,
        and then passes it on into the Assembler.  This is ran on every frame.
        '''

        self.carryOverBits.append(self.frameHandler.returnRemainderPayload(paletteType))
        self.framePayload = self.carryOverBits

        if validatePayload(self.framePayload, self.frameSHA) == False:
            return False

        self.configObject.assembler.acceptFrame(self.streamSHA, self.framePayload, self.frameNumberofStream,
                                                self.scryptN, self.scryptR, self.scryptP, self.outputPath,
                                                self.encryptionKey)


    def _attemptStreamPaletteLoad(self):
        '''The stream header is where the data stating the stream palette used is stated.
        Commonly this will be able to be read on the first frame, but for larger stream headers using custom palettes,
        this may take several frames for it to successfully load, since the full compressed header package must be read
        first.  Assuming the stream palette hasn't loaded yet, this will call the Assembler object to check and see if
        the stream header, along with its ASCII component have been fully read yet.  If so, it is loaded into the proper
        class attributes.
        '''

        logging.debug('Attempting stream palette load...')
        saveObject = self.configObject.assembler.saveDict[self.streamSHAFromLastFrame].returnStreamHeaderID()

        if saveObject[0] == True:

            self.streamHeaderCleared = True

            # Does stream palette already exist as a custom or default color?
            if saveObject[1] in self.configObject.colorHandler.customPaletteList or saveObject[1] in \
                    self.configObject.colorHandler.defaultPaletteList:

                self.streamPalette = paletteGrabber(saveObject[1])
                logging.info(f'Palette ID {saveObject[1]} already saved in system... successfully loaded!')

            # This is a new palette which will now be instantiation as a custom palette object.
            else:

                self.fatalCheckpoint =_validateAndAddPalette(saveObject[2], saveObject[3], saveObject[4], saveObject[5])

                if self.fatalCheckpoint == False:
                    logging.critical('Palette for this stream cannot be loaded!  This could only be caused by data '
                                     'corrupted during the streams write.  Aborting...')
                    return False

                logging.debug('Custom palette successfully instantiated.')
                self.streamPalette = paletteGrabber(saveObject[1])

            self.streamPaletteDict = ColorsToValue(self.streamPalette)
            self.frameHandler.updateDictionaries('streamPalette', self.streamPaletteDict, self.streamPalette)
            self.configObject.assembler.saveDict[self.streamSHA].streamPaletteRead = True

        else:
            logging.debug('Attempt failed this frame.')


    def _imageFrameSetup(self):
        '''This method validates the initializer bit string, as well as loads the primary palette into memory.  The
        reason why this must be a separate method from _videoFirstFrameSetup is because both images and videos handle
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
        self.frameHandler.updateDictionaries('headerPalette', self.headerPaletteDict, self.headerPalette)