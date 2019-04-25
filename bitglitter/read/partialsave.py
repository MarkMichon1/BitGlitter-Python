import datetime
import logging
import os

from bitglitter.utilities.filemanipulation import returnHashFromFile
from bitglitter.utilities.generalverifyfunctions import isIntOverZero, isValidDirectory, properStringSyntax
from bitglitter.read.assemblerassets import formatFileList, readStreamHeaderASCIICompressed, \
    readStreamHeaderBinaryPreamble
from bitglitter.protocols.protocol_one.read.protocol_one_postprocess import PostProcessor

from bitstring import BitStream


class PartialSave:

    def __init__(self, streamSHA, workingFolder, scryptN, scryptR, scryptP, outputPath, encryptionKey):

        # Core object values
        self.saveFolder = workingFolder + f'\\{streamSHA}'
        self.frameReferenceTableName = self.saveFolder + f'\\frameReferenceTable.bin'
        self.streamSHA = streamSHA
        self.assembledSHA = streamSHA
        self.framesIngested = 0
        self.streamHeaderComplete = False
        self.streamHeaderBuffer = None
        self.activeThisSession = True
        self.isAssembled = False

        # Stream Header - Binary Preamble
        self.sizeInBytes = None
        self.totalFrames = None
        self.compressionEnabled = None
        self.encryptionEnabled = None
        self.maskingEnabled = None
        self.customPaletteUsed = None
        self.dateCreated = None
        self.streamPalette = None
        self.asciiHeaderByteSize = None

        # Stream Metadata
        self.bgVersion = None
        self.streamName = None
        self.streamDescription = None
        self.fileList = None

        # Optional ASCII Header Fields
        self.customColorName = None
        self.customColorDescription = None
        self.customColorDateCreated = None
        self.customColorPalette = None
        self.postCompressionSHA = None

        # Changeable Postprocessing Arguments
        self.encryptionKey = encryptionKey
        self.scryptN = scryptN
        self.scryptR = scryptR
        self.scryptP = scryptP
        self.outputPath = outputPath

        self.framesPriorToBinaryPreamble = []

        os.mkdir(self.saveFolder)
        logging.info(f'New partial save! Stream SHA-256: {self.streamSHA}')

    #Returns the status of the object
    def __str__(self):
        return False #todo ???

    '''After being validated in the decoder, this method blindly accepts the data as a piece, saving it within the
    appropriate folder, and adding the frame number to the list.
    '''
    def loadFrame(self, frameData, frameNumber):
        '''After being validated in the decoder, this method blindly accepts the frameData as a piece, saving it within the
        appropriate folder, and adding the frame number to the list.
        '''

        if self.streamHeaderComplete == False:
            frameData = self._streamHeaderAssembly(frameData, frameNumber)

        self._writeFile(frameData, f'frame{frameNumber}')
        self.framesIngested += 1
        self.activeThisSession = True
        logging.debug(f"Frame {frameNumber} for stream {self.streamSHA} successfully saved!")


    def updateMetaData(self, sizeInBytes, totalFrames, compressionEnabled, encryptionEnabled, fileMaskingEnabled,
                       customPaletteUsed):

        self.sizeInBytes = sizeInBytes
        self.totalFrames = totalFrames
        with open(self.saveFolder + '\\completionBinary.bin', 'wb') as makeFile:
            file = BitStream(uint=0, length=totalFrames)
            byteFile = file.tobytes()
            makeFile.write(byteFile)
        self.compressionEnabled = compressionEnabled
        self.encryptionEnabled = encryptionEnabled
        self.maskingEnabled = fileMaskingEnabled
        self.customPaletteUsed = customPaletteUsed



    def updateUserInput(self, passwordUpdate=None, scryptOverrideN=None, scryptOverrideR=None, scryptOverrideP=None,
                        changeOutputPath=None): #todo may put none's on higher level? configObject?
        '''This method changes user related configurations such as password, scrypt parameters, and save location.
        These actions are deliberately separated from updateMetaData, which should remain static.
        '''
        if passwordUpdate:
            properStringSyntax('passwordUpdate', passwordUpdate) #todo update argument once its a function

        if scryptOverrideN:
            isIntOverZero('scryptOverrideN', scryptOverrideN)

        if scryptOverrideR:
            isIntOverZero('scryptOverrideR', scryptOverrideR)

        if scryptOverrideP:
            isIntOverZero('scryptOverrideP', scryptOverrideP)

        if changeOutputPath:
            isValidDirectory('changeOutputPath', changeOutputPath)

        self.encryptionKey = passwordUpdate
        self.scryptN = scryptOverrideN
        self.scryptR = scryptOverrideR
        self.scryptP = scryptOverrideP
        self.outputPath = changeOutputPath

#todo feed in user arguments somewhere

    # If all pieces are present, we will then decrypt and decompress if needed, and then post-process the final files.
    def _attemptAssembly(self):
        #todo- does something belong here if crypto password failed?

        if self.totalFrames == self.framesIngested:

            logging.info(f'All frame(s) loaded for {self.streamSHA}, attempting assembly...')
            dataLeft = self.sizeInBytes * 8
            assembledPath = f'{self.saveFolder}\\assembled.bin'
            with open(assembledPath, 'ab') as assemblePackage:

                for frameNumber in range(self.totalFrames):
                    activeFrame = self._readFile(f'frame{frameNumber + 1}')

                    if frameNumber + 1 != self.totalFrames: # All frames except the last one.
                        pass #todo

                    else: #This is the last frame
                        dataHolder = activeFrame.read(f'bits : {dataLeft}')
                        toByteType = dataHolder.tobytes()
                        assemblePackage.write(toByteType)

            if returnHashFromFile(assembledPath) != self.assembledSHA:

                logging.critical(f'Assembled frames do not match self.packageSHA.  Cannot continue.')
                return False

            logging.debug(f'Successfully assembled.')
            self.isAssembled = True

            postProcessAttempt = PostProcessor(self.outputPath, self.streamSHA, self.saveFolder,
                                               self.encryptionEnabled, self.encryptionKey, self.scryptN,
                                               self.scryptR, self.scryptP, self.compressionEnabled)
            #todo add something here if there is no pass

        else:

            return False
            #todo replace validatedpiecelist with binary file checking


            # destroy palette if selfDestruct


    def _createFrameReferenceTable(self):
        '''This creates a file inside of the object's folder to keep track of which frames have been ingested.  Bit
        positions correspond to frame number (-1 so position 0 is frame 1, etc).
        '''
        referenceTable = BitStream(length=self.totalFrames)
        self._writeFile(referenceTable, self.frameReferenceTableName) #todo
        #todo make tobytes so save friendly



    def _streamHeaderAssembly(self, frameData, frameNumber):
        '''returns data bits'''
        logging.debug('_streamHeaderAssembly running...')
        if frameNumber == 1:

            if frameData.len >= 422: # The entire binary preamble can be read first frame.

                logging.debug('Able to extract streamHeader binary preamble from first frame.')
                self.streamHeaderBuffer = frameData.read('bits:422')
                self.readStreamHeaderBinaryPreamble()

                if frameData.len - frameData.bitpos >= self.asciiHeaderByteSize * 8:

                    # The entire ASCII stream header can be read on first frame.
                    self.streamHeaderBuffer = frameData.read(f'bits:{self.asciiHeaderByteSize * 8}')
                    self.readStreamHeaderASCIICompressed()
                    payloadData = frameData.read(f'bits:{frameData.len - frameData.bitpos}')
                    return payloadData

                else:

                    # The ASCII stream header cannot be read on this first frame.
                    self.streamHeaderBuffer = frameData.read(f'bits:{self.asciiHeaderByteSize * 8}')

            else: # The binary preamble will continue on into subsequent frames.

                self.streamHeaderBuffer = frameData.read(f'bits:{frameData.len}')
                return BitStream()

    def _writeFile(self, data, fileName, toCompress=False):
        '''This is an internal method used to write data to the object's folder.  Since we are dealing with bits and not
        bytes (which is the smallest size operating systems can work with), there is a special five-byte header that
        decodes as an unsigned integer which is the amount of bits to read.'''
        bitsAppendage = BitStream(uint=data.len, length=40)
        bitsAppendageToBytes = bitsAppendage.tobytes()
        dataToBytes = data.tobytes()

        with open(self.saveFolder + f'\\{fileName}.bin', 'wb') as saveFrameData:
            saveFrameData.write(bitsAppendageToBytes)
            saveFrameData.write(dataToBytes)

        if toCompress == True:
            pass



    def _readFile(self, fileName, toDecompress=False):
        '''This internal method reads the file with the fileName according to how many bits it is, deletes the file, and
        then returns the BitStream object.'''
        filePath = self.saveFolder + f'\\{fileName}.bin'
        with open(filePath, 'rb') as file:
            fileToBits = BitStream(file)
        bitsToRead = fileToBits.read('uint:40')
        retrievedFile = fileToBits.read(f'bits:{bitsToRead}')
        os.remove(filePath)
        return retrievedFile


    def readStreamHeaderBinaryPreamble(self):
        '''This is a method because it was taking up needless space in this module, and it's used multiple times.'''
        self.sizeInBytes, self.totalFrames, self.compressionEnabled, self.encryptionEnabled, self.maskingEnabled, \
        self.customPaletteUsed, self.dateCreated, self.streamPaletteID, self.asciiHeaderByteSize = \
            readStreamHeaderBinaryPreamble(self.streamHeaderBuffer)
        self.streamHeaderBuffer = BitStream()
        self.dateCreated = datetime.datetime.fromtimestamp(int(self.dateCreated)).strftime('%Y-%m-%d %H:%M:%S')

        logging.info(f'*** Part 1/2 of header decoded for {self.streamSHA}: ***\nPayload size: {self.sizeInBytes} B'
                     f'\nTotal frames: {self.totalFrames}\nCompression enabled: {self.compressionEnabled}'
                     f'\nEncryption Enabled: {self.encryptionEnabled}\nFile masking enabled: {self.maskingEnabled}'
                     f'\nCustom Palette Used: {self.customPaletteUsed}\nDate created: {self.dateCreated}'
                     f'\nStream palette ID: {self.streamPaletteID}')


    def readStreamHeaderASCIICompressed(self):
        self.bgVersion, self.streamName, self.streamDescription, self.fileList, self.customColorName, \
        self.customColorDescription, self.customColorDateCreated, self.customColorPalette, self.postCompressionSHA = \
            readStreamHeaderASCIICompressed(self.streamHeaderBuffer, self.customPaletteUsed, self.encryptionEnabled)
        self.streamHeaderBuffer = BitStream()

        if self.maskingEnabled == True:
            self.fileList = "Cannot display, masking enabled!"
        else:
            self.fileList = formatFileList(self.fileList)

        if self.customColorDateCreated is not None:
            self.customColorDateCreated = datetime.datetime.fromtimestamp(int(self.customColorDateCreated))\
                .strftime('%Y-%m-%d %H:%M:%S')

        logging.info(f'*** Part 2/2 of header decoded for {self.streamSHA}: ***\nProgram version of sender: '
                     f'v{self.bgVersion}\nStream name: {self.streamName}\nStream description: {self.streamDescription}'
                     f'\nFile list: {self.fileList}')
        if self.customPaletteUsed == True:
            logging.info(f'\n\nCustom color name: {self.customColorName}\nCustom color description: '
                         f'{self.customColorDescription}\nCustom color date created: {self.customColorDateCreated}'
                         f'\nCustom color palette: {self.customColorPalette}')

        if self.encryptionEnabled == True:
            logging.info(f'\n\nPost-compression hash: {self.postCompressionSHA}')
            self.assembledSHA = self.postCompressionSHA

    def isFrameNeeded(self, frameNumber):
        if self.isAssembled == True:
            return False #todo add binary table check stuff

        return True


    def _closeSession(self):
        '''Called by the Assembler object, this will flush self.frameReferenceTable back to disk, as well as flag it as
        an inactive session.'''
        self.activeThisSession = False #todo still finish the other part