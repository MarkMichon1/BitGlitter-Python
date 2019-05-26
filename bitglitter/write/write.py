from bitglitter.config.constants import BG_VERSION, WRITE_PATH, SCRYPT_N_DEFAULT, SCRYPT_R_DEFAULT, SCRYPT_P_DEFAULT, \
    HEADER_PALETTE_ID, STREAM_PALETTE_ID, PIXEL_WIDTH, BLOCK_HEIGHT, BLOCK_WIDTH, FRAMES_PER_SECOND
from bitglitter.config.loggingset import loggingSetter
from bitglitter.write.renderhandler import RenderHandler


def write(   # Basic setup
             fileList,
             streamName = "",
             streamDescription = "",
             outputPath = False,
             outputMode = "video",

             # Stream configuration
             compressionEnabled = True,
             fileMaskEnabled = False,

             # Encryption
             encryptionKey = "",
             scryptOverrideN = SCRYPT_N_DEFAULT,
             scryptOverrideR = SCRYPT_R_DEFAULT,
             scryptOverrideP = SCRYPT_P_DEFAULT,

             # Stream geometry, color
             #protocolVersion = '1' # Currently disabled, will enable once multiple choices of protocols are available.
             headerPaletteID = HEADER_PALETTE_ID,
             streamPaletteID = STREAM_PALETTE_ID,
             pixelWidth = PIXEL_WIDTH,
             blockHeight = BLOCK_HEIGHT,
             blockWidth = BLOCK_WIDTH,

             # Video rendering
             framesPerSecond = FRAMES_PER_SECOND,

             # Logging
             loggingLevel ='info',
             loggingScreenOutput = True,
             loggingSaveOutput = False,
             ):
    '''This is the primary function in creating BitGlitter streams from files.  Please see Wiki page for more
    information.
    '''

    # Logging initializing.
    loggingSetter(loggingLevel, loggingScreenOutput, loggingSaveOutput)

    # Loading write protocol.  This import function is here deliberately because of logging.
    from bitglitter.protocols.protocolhandler import protocolHandler
    writeProtocol = protocolHandler.returnWriteProtocol('1')

    # Are all parameters acceptable?
    writeProtocol.verifyWriteParameters(fileList, streamName, streamDescription, outputPath, outputMode, compressionEnabled,
                                        fileMaskEnabled, scryptOverrideN, scryptOverrideR, scryptOverrideP, streamPaletteID,
                                        headerPaletteID, pixelWidth, blockHeight, blockWidth, framesPerSecond)

    # This sets the name of the temporary folder while the file is being written.
    activePath = WRITE_PATH

    # This is what takes the raw input files and runs them through several processes in preparation for rendering.
    preProcess = writeProtocol.preProcessing(activePath, fileList, encryptionKey, fileMaskEnabled, compressionEnabled,
                                             scryptOverrideN, scryptOverrideR, scryptOverrideP)

    # After the data is prepared, this is what renders the data into images.
    frameProcessor = writeProtocol.frameProcessor()

    renderHandler = RenderHandler(frameProcessor, blockHeight, blockWidth, headerPaletteID, preProcess.streamSHA,
                                  preProcess.sizeInBytes, compressionEnabled, encryptionKey != "", fileMaskEnabled,
                                  preProcess.dateCreated, streamPaletteID, BG_VERSION, streamName, streamDescription,
                                  preProcess.postEncryptionHash, pixelWidth, outputMode, outputPath,
                                  framesPerSecond, activePath, preProcess.passThrough)


    # Returns the SHA of the preprocessed file in string format for optional storage of it.
    return preProcess.streamSHA
