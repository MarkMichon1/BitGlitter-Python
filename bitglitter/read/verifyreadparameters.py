import logging
import os

from bitglitter.config.constants import VALID_IMAGE_FORMATS, VALID_VIDEO_FORMATS
from bitglitter.utilities.generalverifyfunctions import isValidDirectory, isIntOverZero, properStringSyntax, isBool


def verifyReadParameters(fileToInput, outputPath, encryptionKey, scryptN, scryptR, scryptP, blockHeightOverride,
                         blockWidthOverride, assembleHold):
    '''This function verifies the arguments going into read() to ensure they comform with the required format for
    processing.
    '''

    logging.info("Verifying read parameters...")

    if not os.path.isfile(fileToInput):
        raise ValueError(f'fileToInput argument {fileToInput} must be a file.')

    if os.path.splitext(fileToInput)[1] not in VALID_VIDEO_FORMATS and \
            os.path.splitext(fileToInput)[1] not in VALID_IMAGE_FORMATS:
        raise ValueError(f'fileToInput argument {fileToInput} is not a valid format.  Only the following are allowed: '
                         f'{VALID_IMAGE_FORMATS}, and {VALID_VIDEO_FORMATS}')

    if outputPath:
        isValidDirectory('fileToInput', outputPath)

    properStringSyntax('encryptionKey', encryptionKey)

    isIntOverZero('scryptOverrideN', scryptN)
    isIntOverZero('scryptOverrideR', scryptR)
    isIntOverZero('scryptOverrideP', scryptP)

    isIntOverZero('blockHeightOverride', blockHeightOverride)
    isIntOverZero('blockWidthOverride', blockWidthOverride)

    isBool('assembleHold', assembleHold)

    logging.info("All read parameters within acceptable range.")