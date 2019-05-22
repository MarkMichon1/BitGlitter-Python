import logging
from math import ceil

from bitglitter.config.config import config
from bitglitter.utilities.generalverifyfunctions import isBool, isValidDirectory, isIntOverZero, properStringSyntax

def paletteVerify(headerType, bitLength, blockWidth, blockHeight, outputType, fps=0):
    '''This function calculates the necessary overhead for both images and videos for subsequent frames after 1.  It
    returns a number between 0-100%, for what percentage the overhead occupies.  The lower the value, the higher the
    frame efficiency.
    '''

    totalBlocks = blockWidth * blockHeight

    blockOverhead = blockHeight + blockWidth + 323
    frameHeaderInBits = 608

    blocksNeeded = 0

    if headerType == 'headerPalette' or outputType == 'image':
        blocksNeeded += blockOverhead

    bitsAvailable = (totalBlocks - blocksNeeded) * bitLength
    bitsAvailable -= frameHeaderInBits
    occupiedBlocks = blocksNeeded + ceil(frameHeaderInBits / bitLength)

    if occupiedBlocks > totalBlocks:
        raise ValueError(f"{headerType} has {occupiedBlocks - totalBlocks} too few blocks with this configuration."
                         f"\nPlease fix this by using a palette with a larger bitlength or use more blocks per frame.")

    outputPerSec = None
    if outputType == 'video' and headerType == 'streamPalette':
        outputPerSec = bitsAvailable * fps

    return ((round(100 - (occupiedBlocks / totalBlocks * 100), 2)), bitsAvailable, outputPerSec)


def verifyWriteParameters(fileList, streamName, streamDescription, streamOutputPath, outputMode, compressionEnabled,
                          fileMaskEnabled, scryptOverrideN, scryptOverrideR, scryptOverrideP, streamPalette,
                          headerPalette, pixelWidth, blockHeight, blockWidth, framesPerSecond):
    '''This function verifies all write() parameters for Protocol v1.  Look at this as the gatekeeper that stops
    invalid arguments from proceeding through the process, potentially breaking the stream (or causing BitGlitter to
    crash).
    '''

    logging.info("Verifying write parameters...")

    if not fileList:
        raise FileNotFoundError("A minimum of one file or folder is required for stream creation for argument fileList"
                                " in write().")

    properStringSyntax(streamName, 'streamName')
    properStringSyntax(streamDescription, 'streamDescription')

    if streamOutputPath:
        isValidDirectory('streamOutputPath', streamOutputPath)

    if outputMode != 'video' and outputMode != 'image':
        raise ValueError("Argument outputMode in write() only accepts 'video' or 'image'.")

    isBool('compressionEnabled', compressionEnabled)
    isBool('fileMaskEnabled', fileMaskEnabled)

    isIntOverZero('scryptOverrideN', scryptOverrideN)
    isIntOverZero('scryptOverrideR', scryptOverrideR)
    isIntOverZero('scryptOverrideP', scryptOverrideP)

    # is streamPalette valid?  We're simultaneously setting up a variable for a geometry just check below.
    def doesPaletteExist(palette, type):
        if palette in config.colorHandler.defaultPaletteList:
            paletteToReturn = config.colorHandler.defaultPaletteList[palette]
        elif palette in config.colorHandler.customPaletteList:
            paletteToReturn = config.colorHandler.customPaletteList[palette]
        elif palette in config.colorHandler.customPaletteNicknameList:
            paletteToReturn = config.colorHandler.customPaletteNicknameList[palette]
        else:
            raise ValueError(f"Argument {type} in write() is not a valid ID or nickname.  Verify that exact value "
                             "exists.")
        return paletteToReturn

    activeHeaderPalette = doesPaletteExist(headerPalette, 'headerPalette')
    activeStreamPalette = doesPaletteExist(streamPalette, 'streamPalette')

    isIntOverZero('pixelWidth', pixelWidth)
    isIntOverZero('blockHeight', blockHeight)
    isIntOverZero('blockWidth', blockWidth)
    isIntOverZero('framesPerSecond', framesPerSecond)

    if framesPerSecond != 30 and framesPerSecond != 60:
        raise ValueError("framesPerSecond must either be 30 or 60 at this time (we're working on this!)")

    if blockWidth < 17 or blockHeight < 17:
        raise ValueError('Minimum block dimensions for Protocol 1 are 17 x 17.')

    # With the given dimensions and bit length, is it sufficient?
    returnedHeaderValues = paletteVerify('headerPalette', activeHeaderPalette.bitLength, blockWidth, blockHeight,
                                         outputMode, framesPerSecond)
    logging.info(f'{returnedHeaderValues[0]}% of the frame for initial header is allocated for frame payload (higher is'
                 ' better)')

    returnedStreamValues = paletteVerify('streamPalette', activeStreamPalette.bitLength, blockWidth, blockHeight,
                                         outputMode, framesPerSecond)
    logging.info(f'{returnedStreamValues[1]} B, or {returnedStreamValues[0]}% of subsequent frames is allocated for '
                 f'frame payload (higher is better)')

    if outputMode == 'video':
        logging.info(f'As a video, it will effectively be transporting {round(returnedStreamValues[2] / 8)} B/sec of '
                     f'data.')

    logging.info('Minimum geometry requirements met.')
    logging.info("Write parameters validated.")