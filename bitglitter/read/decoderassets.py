import hashlib
import logging
import numpy
import zlib

from bitglitter.palettes.paletteutilities import paletteGrabber
from bitglitter.protocols.protocolhandler import protocolHandler


def minimumBlockCheckpoint(blockHeightOverride, blockWidthOverride, activeFrameSizeWidth,
                           activeFrameSizeHeight):
    '''If blockHeightOverride and blockWidthOverride have been entered, this checks those values against the height and
    width (in pixels) of the image loaded).  Since the smallest blocks that can be read are one pixels (since that is
    finest detail you can have with an image), any values beyond that are invalid, and stopped here.
    '''

    if blockHeightOverride and blockWidthOverride:
        if activeFrameSizeWidth < blockWidthOverride or activeFrameSizeHeight < \
                blockHeightOverride:
            logging.warning("Block override parameters are too large for a file of these dimensions.  "
                            "Aborting...")
            return False

    return True


def scanBlock(image, pixelWidth, blockWidthPosition, blockHeightPosition):
    '''This function is what's used to scan the blocks used.  First the scan area is determined, and then each of the
    pixels in that area appended to a list.  An average of those values as type int is returned.
    '''

    if pixelWidth < 5:
        startPositionX = int(blockWidthPosition * pixelWidth)
        endPositionX = int((blockWidthPosition * pixelWidth) + pixelWidth - 1)
        startPositionY = int(blockHeightPosition * pixelWidth)
        endPositionY = int((blockHeightPosition * pixelWidth) + pixelWidth - 1)

    else:
        startPositionX = int(round((blockWidthPosition * pixelWidth) + (pixelWidth * .25), 1))
        endPositionX = int(round(startPositionX + (pixelWidth * .5), 1))
        startPositionY = int(round((blockHeightPosition * pixelWidth) + (pixelWidth * .25), 1))
        endPositionY = int(round(startPositionY + (pixelWidth * .5), 1))

    numpyOutput = numpy.flip(image[startPositionY:endPositionY, startPositionX:endPositionX]).mean(axis=(0,1))
    toListFormat = numpyOutput.tolist()

    for value in range(3):
        toListFormat[value] = int(toListFormat[value])

    return toListFormat


def readInitializer(bitStream, blockHeight, blockWidth, customPaletteList, defaultPaletteList):
    '''This function decodes the raw binary data from the initializer header after verifying it's checksum, and will
    emergency stop the read if any of the conditions are met:  If the read checksum differs from the calculated
    checksum, if the read protocol version isn't supported by this BitGlitter version, if the readBlockHeight or
    readBlockWidth differ from what frameLockOn() read, or if the palette ID for the header is unknown (ie, a custom
    color which has not been integrated yet).  Returns protocolVersion and headerPalette object.
    '''

    # First, we're verifying the initializer is not corrupted by comparing its read checksum with a calculated one from
    # it's contents.  If they match, we continue.  If not, this frame aborts.
    logging.debug('readInitializer running...')

    bitStream.pos = 0
    fullBitStreamToHash = bitStream.read('bits : 292')
    convertedToBytes = fullBitStreamToHash.tobytes()
    calculatedCRC = zlib.crc32(convertedToBytes)
    readCRC = bitStream.read('uint : 32')
    if calculatedCRC != readCRC:
        logging.warning('Initializer checksum failure.  Aborting...')
        return False, False

    bitStream.pos = 0
    protocolVersion = bitStream.read('uint : 4')
    logging.debug(f'Protocol version: {protocolVersion}')
    if str(protocolVersion) not in protocolHandler.availableProtocols:
        logging.warning(f'Protocol v{str(protocolVersion)} not supported in this version of BitGlitter.  Please update '
                        f'to fix.  Aborting...')
        return False, False

    readBlockHeight = bitStream.read('uint : 16')
    readBlockWidth = bitStream.read('uint : 16')
    if readBlockHeight != blockHeight or readBlockWidth != blockWidth:
        logging.warning('readInitializer: Geometry assertion failure.  Aborting...')
        logging.debug(f'readBlockHeight: {readBlockHeight}\n blockHeight {blockHeight}'
                      f'\n readBlockWidth {readBlockWidth}\n blockWidth {blockWidth}')

        return False, False

    bitStream.pos += 232
    framePaletteID = bitStream.read('uint : 24')

    if framePaletteID > 100:

        bitStream.pos -= 256
        framePaletteID = bitStream.read('hex : 256')
        framePaletteID.lower()

        if framePaletteID not in customPaletteList:

            logging.warning('readInitializer: This header palette is unknown, reader cannot proceed until it is learned'
                            'through a \nstream header.  This can occur if the creator of the stream uses a non-default'
                            ' palette.  This can also trigger if frames \nare read non-sequentially.  Aborting...')
            return False, False

    else:

        if str(framePaletteID) not in defaultPaletteList:
            logging.warning('readInitializer: This default palette is unknown by this version of BitGlitter.  This\n'
                            "could be the case if you're using an older version.  Aborting...")
            logging.debug(f'framePaletteID: {framePaletteID}\ndefaultPaletteList: {defaultPaletteList}')
            return False, False

    framePalette = paletteGrabber(str(framePaletteID))
    logging.debug('readInitializer successfully ran.')
    return protocolVersion, framePalette


def readFrameHeader(bitStream):
    '''While readInitializer is mostly used for verification of values, this function's purpose is to return values
    needed for the reading process, once verified.  Returns streamSHA, frameSHA, frameNumber, and blocksToRead.
    '''

    logging.debug('readFrameHeader running...')
    fullBitStreamToHash = bitStream.read('bytes : 72')

    calculatedCRC = zlib.crc32(fullBitStreamToHash)
    readCRC = bitStream.read('uint : 32')
    if calculatedCRC != readCRC:
        logging.warning('frameHeader checksum failure.  Aborting...')
        return False, False, False, False

    bitStream.pos = 0
    streamSHA = bitStream.read('hex : 256')
    frameSHA = bitStream.read('hex : 256')
    frameNumber = bitStream.read('uint : 32')
    blocksToRead = bitStream.read('uint : 32')

    logging.debug('readFrameHeader successfully ran.')
    return streamSHA, frameSHA, frameNumber, blocksToRead


def validatePayload(payloadBits, readFrameSHA):
    '''Taking all of the frame bits after the frame header, this takes the SHA-256 hash of them, and compares it against
    the frame SHA written in the frame header.  This is the primary mechanism that validates frame data, which either
    allows it to be passed through to the assembler, or discarded.
    '''

    shaHasher = hashlib.sha256()
    shaHasher.update(payloadBits.tobytes())
    stringOutput = shaHasher.hexdigest()
    logging.debug(f'length of payloadBits: {payloadBits.len}')

    if stringOutput != readFrameSHA:
        logging.warning('validatePayload: readFrameSHA does not match calculated one.  Aborting...')
        logging.debug(f'Read from frameHeader: {readFrameSHA}\nCalculated just now: {stringOutput}')
        return False

    logging.debug('Payload validated this frame.')
    return True