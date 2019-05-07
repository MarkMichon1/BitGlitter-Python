from bitglitter.config.loggingset import _loggingSetter
from bitglitter.config.constants import READ_PATH, BAD_FRAME_STRIKES, SCRYPT_N_DEFAULT, SCRYPT_R_DEFAULT, \
    SCRYPT_P_DEFAULT
from bitglitter.read.verifyreadparameters import verifyReadParameters

def read(fileToInput,
         outputPath = None,
         badFrameStrikes = BAD_FRAME_STRIKES,

         # Geometry Overrides
         blockHeightOverride = False,
         blockWidthOverride = False,

         # Crypto Input
         encryptionKey = None,
         scryptN = SCRYPT_N_DEFAULT,
         scryptR = SCRYPT_R_DEFAULT,
         scryptP = SCRYPT_P_DEFAULT,

         # Logging Settings
         loggingLevel = 'info',
         loggingScreenOutput = True,
         loggingSaveOutput = False
         ):

    # Logging initializing.
    _loggingSetter(loggingLevel, loggingScreenOutput, loggingSaveOutput)
    from bitglitter.read.fileslicer import fileSlicer
    from bitglitter.config.config import config


    # Are all parameters acceptable?
    verifyReadParameters(fileToInput, outputPath, encryptionKey, scryptN, scryptR, scryptP, blockWidthOverride,
                         blockWidthOverride)


    # This sets the name of the temporary folder while screened data from partial saves is being written.
    activePath = READ_PATH


    # Pull valid frame data from the inputted file.
    checkpointPassed = fileSlicer(fileToInput, activePath, outputPath, blockHeightOverride, blockWidthOverride,
                                  encryptionKey, scryptN, scryptR, scryptP, config, badFrameStrikes)
    if checkpointPassed == False:
        return False

    # Now that all frames have been scanned, we'll have the config object check to see if any files are ready for
    # assembly.  If there are, they will be put together and outputted, as well as removed/flushed from partialSaves.
    config.assembler.reviewActiveSessions()
    config.saveSession()
    return True
