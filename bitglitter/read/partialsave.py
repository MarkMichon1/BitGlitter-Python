import datetime
import logging
import os

from bitstring import BitStream

from bitglitter.protocols.protocol_one.read.protocol_one_postprocess import PostProcessor
from bitglitter.read.partialsaveassets import formatFileList, decodeStreamHeaderASCIICompressed, \
    decodeStreamHeaderBinaryPreamble
from bitglitter.utilities.filemanipulation import compressFile, decompressFile, returnHashFromFile


class PartialSave:
    '''PartialSave objects are essentially containers for the state of streams as they are being read, frame by frame.
    This mainly interacts through the Assembler object.  All of the functionality needed to convert raw frame data back
    into the original package is done through it's contained methods.
    '''

    def __init__(self, streamSHA, workingFolder, scryptN, scryptR, scryptP, outputPath, encryptionKey):

        # Core object state data
        self.saveFolder = workingFolder + f'\\{streamSHA}'
        self.streamSHA = streamSHA
        self.assembledSHA = streamSHA
        self.framesIngested = 0
        self.streamHeaderPreambleComplete = False
        self.streamHeaderASCIIComplete = False
        self.streamHeaderPreambleBuffer = BitStream()
        self.streamHeaderASCIIBuffer = BitStream()
        self.nextStreamHeaderSequentialFrame = 1
        self.payloadBeginsThisFrame = None
        self.activeThisSession = True
        self.isAssembled = False # Did the frames successfully merge into a single binary?
        self.postProcessorDecrypted = False # Was the stream successfully decrypted?
        self.frameReferenceTable = None
        self.framesPriorToBinaryPreamble = []
        self.streamPaletteRead = False


        # Stream Header - Binary Preamble
        self.sizeInBytes = None
        self.totalFrames = '???'
        self.compressionEnabled = None
        self.encryptionEnabled = None
        self.maskingEnabled = None
        self.customPaletteUsed = None
        self.dateCreated = None
        self.streamPaletteID = None
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

        os.mkdir(self.saveFolder)
        logging.info(f'New partial save! Stream SHA-256: {self.streamSHA}')


    def loadFrameData(self, frameData, frameNumber):
        '''After being validated in the decoder, this method blindly accepts the frameData as a piece, saving it within
        the appropriate folder, and adding the frame number to the list.
        '''

        if self.streamHeaderASCIIComplete == False and frameNumber == self.nextStreamHeaderSequentialFrame:
            frameData = self._streamHeaderAssembly(frameData, frameNumber)

        if frameData.len > 0:
            self._writeFile(frameData, f'frame{frameNumber}')

        self.framesIngested += 1
        self.activeThisSession = True

        if self.streamHeaderPreambleComplete == True:
            self.frameReferenceTable.set(True, frameNumber - 1)

        else:
            self.framesPriorToBinaryPreamble.append(frameNumber)

        logging.debug(f"Frame {frameNumber} for stream {self.streamSHA} successfully saved!")


    def userInputUpdate(self, passwordUpdate, scryptN, scryptR, scryptP, changeOutputPath):
        '''This method changes user related configurations such as password, scrypt parameters, and save location.
        These arguments are blindly accepted from updatePartialSave() in savedfilefunctions, as the inputs are validated
        there.
        '''

        if passwordUpdate:
            self.encryptionKey = passwordUpdate

        if scryptN:
            self.scryptN = scryptN
        if scryptR:
            self.scryptR = scryptR
        if scryptP:
            self.scryptP = scryptP

        if changeOutputPath:
            self.outputPath = changeOutputPath


    def _attemptAssembly(self):
        '''This method will check to see if all frames for the stream have been read.  If so, they will be assembled
        into a single binary, it's hash will be validated, and then it will be ran through post-processing,
        which is what ultimately yields the original files encoded in the stream.
        '''

        if self.isAssembled == False: # If false, assembly will be attempted.  Otherwise, we skip to postprocessing.

            if self.totalFrames == self.framesIngested:
                logging.info(f'All frame(s) loaded for {self.streamSHA}, attempting assembly...')
                dataLeft = self.sizeInBytes * 8
                assembledPath = f'{self.saveFolder}\\assembled.bin'
                interFrameBitBuffer = BitStream()

                with open(assembledPath, 'ab') as assemblePackage:

                    for frame in range(self.totalFrames - self.payloadBeginsThisFrame + 1):

                        frameNumber = frame + self.payloadBeginsThisFrame
                        logging.debug(f'Assembling {frameNumber}/{self.totalFrames}')
                        activeFrame = self._readFile(f'frame{frameNumber}')

                        if frameNumber != self.totalFrames: # All frames except the last one.
                            bitMerge = BitStream(interFrameBitBuffer + activeFrame)
                            dataHolder = bitMerge.read(f'bytes: {bitMerge.len // 8}')

                            if bitMerge.len - bitMerge.pos > 0:
                                interFrameBitBuffer = bitMerge.read(f'bits : {bitMerge.len - bitMerge.pos}')

                            else:
                                interFrameBitBuffer = BitStream()

                            if isinstance(dataHolder, bytes):
                                logging.debug('was bytes this frame!')
                                assemblePackage.write(dataHolder)

                            else:
                                logging.debug('bits to bytes this frame')
                                toByteType = dataHolder.tobytes()
                                assemblePackage.write(toByteType)
                            dataLeft -= activeFrame.len

                        else: #This is the last frame
                            bitMerge = interFrameBitBuffer + activeFrame.read(f'bits : {dataLeft}')
                            toByteType = bitMerge.tobytes()
                            assemblePackage.write(toByteType)

                if returnHashFromFile(assembledPath) != self.assembledSHA:
                    logging.critical(f'Assembled frames do not match self.packageSHA.  Cannot continue.')
                    return False

                logging.debug(f'Successfully assembled.')
                self.isAssembled = True

            else:
                logging.info(f'{self.framesIngested} / {self.totalFrames}  frames have been loaded for '
                             f'{self.streamSHA}\n so far, cannot assemble yet.')
                return False

        postProcessAttempt = PostProcessor(self.outputPath, self.streamSHA, self.saveFolder,
                                           self.encryptionEnabled, self.encryptionKey, self.scryptN,
                                           self.scryptR, self.scryptP, self.compressionEnabled)

        # Did all three stages of PostProcess successfully run?
        if postProcessAttempt.FullyAssembled != True:
            return False

        return True


    def _createFrameReferenceTable(self):
        '''This creates a file inside of the object's folder to keep track of which frames have been ingested.  Bit
        positions correspond to frame number (-1 so position 0 is frame 1, etc).
        '''

        self.frameReferenceTable = BitStream(length=self.totalFrames)

        for position in self.framesPriorToBinaryPreamble:
            self.frameReferenceTable.set(True, position - 1)

        self.framesPriorToBinaryPreamble = []


    def _streamHeaderAssembly(self, frameData, frameNumber):
        '''Stream headers may span over numerous frames, and could be read non-sequentially.  This function manages this
        aspect.  Both stream headers are stripped from the raw frame data, returning payload data (if applicable).
        '''

        logging.debug('_streamHeaderAssembly running...')
        self.nextStreamHeaderSequentialFrame += 1

        if self.streamHeaderPreambleComplete == False:

            # Preamble header uses all of this frame.
            if 422 - self.streamHeaderPreambleBuffer.len >= frameData.len:

                logging.debug('Preamble header uses all of this frame.')
                readLength = frameData.len

            # Preamble terminates on this frame.
            else:

                logging.debug('Preamble terminates on this frame.')
                readLength = 422 - self.streamHeaderPreambleBuffer.len

            self.streamHeaderPreambleBuffer.append(frameData.read(f'bits:{readLength}'))

            if self.streamHeaderPreambleBuffer.len == 422:
                self.readStreamHeaderBinaryPreamble()

        if self.streamHeaderASCIIComplete == False and frameData.len - frameData.bitpos > 0:
            # ASCII header rolls over to the next frame.
            if self.asciiHeaderByteSize * 8 - self.streamHeaderASCIIBuffer.len >= frameData.len \
                    - frameData.bitpos:

                logging.debug('ASCII header rolls over to another frame.')
                readLength = frameData.len - frameData.bitpos

            # ASCII header terminates on this frame.
            else:
                logging.debug('ASCII header terminates on this frame.')
                readLength = self.asciiHeaderByteSize * 8 - self.streamHeaderASCIIBuffer.len

            self.streamHeaderASCIIBuffer.append(frameData.read(f'bits:{readLength}'))

            if self.streamHeaderASCIIBuffer.len == self.asciiHeaderByteSize * 8:
                self.payloadBeginsThisFrame = frameNumber
                self.readStreamHeaderASCIICompressed()

            if frameData.len - frameData.bitpos > 0:
                return frameData.read(f'bits:{frameData.len - frameData.bitpos}')

        return BitStream()


    def _writeFile(self, data, fileName, toCompress=False):
        '''This is an internal method used to write data to the object's folder.  Since we are dealing with bits and not
        bytes (which is the smallest size operating systems can work with), there is a special five-byte header that
        decodes as an unsigned integer which is the amount of bits to read.
        '''

        bitsAppendage = BitStream(uint=data.len, length=40)
        bitsAppendageToBytes = bitsAppendage.tobytes()
        dataToBytes = data.tobytes()

        if toCompress == True:
            tempName = self.saveFolder + '\\temp.bin'
            with open(tempName, 'wb') as writeData:
                writeData.write(bitsAppendageToBytes)
                writeData.write(dataToBytes)

            compressFile(tempName, self.saveFolder + f'\\{fileName}.bin')

        else:
            with open(self.saveFolder + f'\\{fileName}.bin', 'wb') as writeData:
                writeData.write(bitsAppendageToBytes)
                writeData.write(dataToBytes)


    def _readFile(self, fileName, toDecompress=False):
        '''This internal method reads the file with the fileName according to how many bits it is, deletes the file, and
        then returns the BitStream object.
        '''

        filePath = self.saveFolder + f'\\{fileName}.bin'

        if toDecompress == False:
            with open(filePath, 'rb') as readData:
                fileToBits = BitStream(readData)
                bitsToRead = fileToBits.read('uint:40')
                retrievedFile = fileToBits.read(f'bits:{bitsToRead}')
            os.remove(filePath)

        else:
            decompressFile(filePath, self.saveFolder + '\\temp.bin')
            with open(self.saveFolder + '\\temp.bin', 'rb') as readData:
                fileToBits = BitStream(readData)
                bitsToRead = fileToBits.read('uint:40')
                retrievedFile = fileToBits.read(f'bits:{bitsToRead}')
            os.remove(self.saveFolder + '\\temp.bin')

        return retrievedFile


    def readStreamHeaderBinaryPreamble(self):
        '''This method converts the raw full binary preamble into the various PartialSave attributes.'''

        self.sizeInBytes, self.totalFrames, self.compressionEnabled, self.encryptionEnabled, self.maskingEnabled, \
        self.customPaletteUsed, self.dateCreated, self.streamPaletteID, self.asciiHeaderByteSize = \
            decodeStreamHeaderBinaryPreamble(self.streamHeaderPreambleBuffer)
        self.streamHeaderPreambleBuffer = None
        self.dateCreated = datetime.datetime.fromtimestamp(int(self.dateCreated)).strftime('%Y-%m-%d %H:%M:%S')

        logging.info(f'*** Part 1/2 of header decoded for {self.streamSHA}: ***\nPayload size: {self.sizeInBytes} B'
                     f'\nTotal frames: {self.totalFrames}\nCompression enabled: {self.compressionEnabled}'
                     f'\nEncryption Enabled: {self.encryptionEnabled}\nFile masking enabled: {self.maskingEnabled}'
                     f'\nCustom Palette Used: {self.customPaletteUsed}\nDate created: {self.dateCreated}'
                     f'\nStream palette ID: {self.streamPaletteID}')
        logging.debug(f'ASCII header byte size: {self.asciiHeaderByteSize} B')

        self._createFrameReferenceTable()
        self.streamHeaderPreambleComplete = True


    def readStreamHeaderASCIICompressed(self):
        '''This method converts the raw full ASCII stream header into the various PartialSave attributes.'''

        self.bgVersion, self.streamName, self.streamDescription, self.fileList, self.customColorName, \
        self.customColorDescription, self.customColorDateCreated, self.customColorPalette, self.postCompressionSHA = \
         decodeStreamHeaderASCIICompressed(self.streamHeaderASCIIBuffer, self.customPaletteUsed, self.encryptionEnabled)
        self.streamHeaderASCIIBuffer = None

        if self.maskingEnabled == True:
            self.fileList = "Cannot display, file masking enabled for this stream!"

        else:
            self.fileList = formatFileList(self.fileList)

        logging.info(f'*** Part 2/2 of header decoded for {self.streamSHA}: ***\nProgram version of sender: '
                     f'v{self.bgVersion}\nStream name: {self.streamName}\nStream description: {self.streamDescription}'
                     f'\nFile list: {self.fileList}')

        if self.customPaletteUsed == True:
            logging.info(f'\nCustom color name: {self.customColorName}\nCustom color description: '
                         f'{self.customColorDescription}\nCustom color date created: '
                    f'{datetime.datetime.fromtimestamp(int(self.customColorDateCreated)).strftime("%Y-%m-%d %H:%M:%S")}'
                         f'\nCustom color palette: {self.customColorPalette}')

        if self.encryptionEnabled == True:
            logging.info(f'Post-compression hash: {self.postCompressionSHA}')
            self.assembledSHA = self.postCompressionSHA

        self.streamHeaderASCIIComplete = True


    def isFrameNeeded(self, frameNumber):
        '''This determines whether a given frame is needed for this stream or not.'''

        # Is the stream already assembled?  If so, no more frames need to be accepted.
        if self.isAssembled == True:
            return False

        # The stream is not assembled.
        else:

            # If the stream header binary preamble isn't loaded yet, then by default we accept the frame, unless that
            # frame number is already in self.framesPriorToBinaryPreamble, which is a list of processed frames prior to
            # the binary preamble being read.
            if self.streamHeaderPreambleComplete == False:
                if frameNumber not in self.framesPriorToBinaryPreamble:
                    return True

                else:
                    return False

            # The preamble has been loaded, checking the reference table.
            else:

                # Frame reference table is not in memory and must be loaded.
                if self.frameReferenceTable == None:

                    self.frameReferenceTable = BitStream(self._readFile('\\frameReferenceTable', toDecompress=True))

                self.frameReferenceTable.bitpos = frameNumber - 1
                isFrameLoaded = self.frameReferenceTable.read('bool')
                return not isFrameLoaded


    def _closeSession(self):
        '''Called by the Assembler object, this will flush self.frameReferenceTable back to disk, as well as flag it as
        an inactive session.
        '''

        self.activeThisSession = False

        if self.streamHeaderPreambleComplete == True:
            self._writeFile(self.frameReferenceTable, '\\frameReferenceTable', toCompress=True)
        self.frameReferenceTable = None


    def returnStatus(self, debugData):
        '''This is used in printFullSaveList in savedfunctions module; it returns the state of the object, as well as
        various information read from the reader.  __str__ is not used, as debugData controls what level of data is
        returned, whether for end users, or debugging purposes.
        '''

        tempHolder = f"{'*' * 8} {self.streamSHA} {'*' * 8}" \
            f"\n\n{self.framesIngested} / {self.totalFrames} frames saved" \
            f"\n\nStream header complete: {self.streamHeaderASCIIComplete}" \
            f"\nIs assembled: {self.isAssembled}" \
            f"\n\nStream name: {self.streamName}" \
            f"\nStream Description: {self.streamDescription}" \
            f"\nDate Created: {self.dateCreated}" \
            f"\nSize in bytes: {self.sizeInBytes} B" \
            f"\nCompression enabled: {self.compressionEnabled}" \
            f"\nEncryption enabled: {self.encryptionEnabled}" \
            f"\nFile masking enabled: {self.maskingEnabled}" \
            f"\n\nEncryption key: {self.encryptionKey} " \
            f"\nScrypt N: {self.scryptN}" \
            f"\nScrypt R: {self.scryptR}" \
            f"\nScrypt P: {self.scryptP}" \
            f"\nOutput path upon assembly: {self.outputPath}" \
            f"\n\nFile list: {self.fileList}"

        if debugData == True:
            tempHolder += f"\n\n{'*' * 3} {'DEBUG'} {'*' * 3}" \
                f"\nBG version: {self.bgVersion}" \
                f"\nASCII header byte size: {self.asciiHeaderByteSize}" \
                f"\nPost compression SHA: {self.postCompressionSHA}" \
                f"\nStream Palette ID: {self.streamPaletteID}" \
                f"\n\nCustom color data (if applicable)" \
                f"\nCustom color name: {self.customColorName}" \
                f"\nCustom color description: {self.customColorDescription}" \
                f"\nCustom color date created: {self.customColorDateCreated}" \
                f"\nCustom color palette: {self.customColorPalette}"

        return tempHolder


    def returnStreamHeaderID(self):
        '''This method releases the streamPalette ID (and custom color data if applicable) for the Decoder to use to
        create the palette.
        '''

        return self.streamHeaderASCIIComplete, self.streamPaletteID, self.customColorName, self.customColorDescription,\
               self.customColorDateCreated, self.customColorPalette