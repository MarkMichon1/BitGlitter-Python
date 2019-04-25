import hashlib
import logging
import math
import os
import zlib

from bitstring import BitArray, BitStream, ConstBitStream
from PIL import ImageDraw

from bitglitter.palettes.paletteutilities import _paletteGrabber, ValuesToColor


def asciiHeaderProcess(fileMaskEnabled, activePath, streamPalette, bgVersion, streamName, streamDescription,
                       postEncryptionHash, encryptionEnabled):
    '''This takes all ASCII elements of the stream header, and returns a formatted merged string.'''
    if fileMaskEnabled:
        fileListString = ""
    else:
        with open(activePath + "\\fileList.txt", 'r') as textFile:
            fileListString = textFile.read()
        os.remove(activePath + '\\fileList.txt')

    customPaletteString = ""
    if streamPalette.paletteType == 'custom':
        customPaletteAttributeList = [streamPalette.name, streamPalette.description,
                                 str(streamPalette.dateCreated), str(streamPalette.colorSet)]
        customPaletteString = "\\\\".join(customPaletteAttributeList) + "\\\\"

    cryptoString = ""
    if encryptionEnabled:
        cryptoString = postEncryptionHash + "\\\\"

    metaDataString = "\\\\" + "\\\\".join([bgVersion, streamName, streamDescription, fileListString]) + "\\\\"

    mergedString = "".join([metaDataString, customPaletteString, cryptoString])
    logging.debug(f'ASCII Stream Header merged: {mergedString}')

    # Next, we're compressing it
    compressedStreamheader = zlib.compress(mergedString.encode(), level=9)
    compressedFileSize = len(compressedStreamheader)
    logging.debug(f'ASCII Stream Header compressed. ({len(mergedString)} B -> {compressedFileSize} B)')

    return compressedStreamheader


def generateStreamHeaderBinaryPreamble(sizeInBytes, totalFrames, compressionEnabled, encryptionEnabled, fileMaskEnabled,
                                       isStreamPaletteCustom, dateCreated, streamPaletteID, asciiCompressedLength):
    '''The binary preamble for the Stream Header is created here.  For videos and images, this is only needed for the
    first frame.
    '''
    addingBits = BitStream()

    addingBits.append(BitArray(uint=sizeInBytes, length=64))
    addingBits.append(BitArray(uint=totalFrames, length=32))
    addingBits.append(BitArray([int(compressionEnabled), int(encryptionEnabled),
                                int(fileMaskEnabled), isStreamPaletteCustom]))
    addingBits.append(BitArray(uint=dateCreated, length=34))

    if isStreamPaletteCustom:
        addingBits.append(BitArray(hex=streamPaletteID))
    else:
        addingBits.append(BitArray(uint=int(streamPaletteID), length=256))

    addingBits.append(BitArray(uint=asciiCompressedLength, length=32))

    logging.debug('streamHeader generated.')
    return ConstBitStream(addingBits)


def generateFrameHeader(streamSHA, frameHashableBits, frameNumber, blocksUsed):
    '''This creates the header that is present at the beginning of every frame (excluding the first frame or image
    outputs).  These headers orient the reader, in that it tells it where it is in the stream.
    '''

    fullBitString = BitArray()

    fullBitString.append(BitArray(hex=streamSHA))
    tempPayloadHolding = ConstBitStream(frameHashableBits)
    shaHasher = hashlib.sha256()
    shaHasher.update(tempPayloadHolding.tobytes())
    frameSHA = shaHasher.digest()
    #logging.debug(f'This frame SHA: {shaHasher.hexdigest()}')
    fullBitString.append(BitArray(bytes=frameSHA))

    fullBitString.append(BitArray(uint=frameNumber, length=32))

    fullBitString.append(BitArray(uint=blocksUsed, length=32))

    fullBitStringToHash = fullBitString.bytes

    crcOutput = zlib.crc32(fullBitStringToHash)
    fullBitString.append(BitArray(uint=crcOutput, length=32))

    return fullBitString


def howManyFrames(blockHeight, blockWidth, asciiCompressedSize, sizeInBytes, streamPalette, headerPalette, outputMode):
    '''This method returns how many frames will be required to complete the rendering process.'''
    logging.debug("Calculating how many frames to render...")

    totalBlocks = blockHeight * blockWidth
    streamHeaderOverheadInBits = 422 + (asciiCompressedSize * 8)
    StreamSizeInBits = (sizeInBytes * 8)
    headerBitLength = headerPalette.bitLength
    streamBitLength = streamPalette.bitLength

    # Overhead constants
    initializerOverhead = blockHeight + blockWidth + 323
    frameHeaderOverhead = 608

    dataLeft = StreamSizeInBits
    frameNumber = 0
    streamHeaderBitsLeft = streamHeaderOverheadInBits  # subtract until zero

    while streamHeaderBitsLeft:

        bitsConsumed = frameHeaderOverhead
        blocksLeft = totalBlocks
        blocksLeft -= (initializerOverhead * int(outputMode == 'image' or frameNumber == 0))

        streamHeaderBitsAvailable = (blocksLeft * headerBitLength) - frameHeaderOverhead

        if streamHeaderBitsLeft >= streamHeaderBitsAvailable:
            streamHeaderBitsLeft -= streamHeaderBitsAvailable

        else: # streamHeaderCombined terminates on this frame
            streamHeaderBitsAvailable -= streamHeaderBitsLeft
            bitsConsumed += streamHeaderBitsLeft
            streamHeaderBitsLeft = 0

            streamHeaderBlocksUsed = math.ceil(bitsConsumed / headerPalette.bitLength)
            attachmentBits = headerPalette.bitLength - (bitsConsumed % headerPalette.bitLength)

            if attachmentBits > 0:
                dataLeft -= attachmentBits

            remainingBlocksLeft = blocksLeft - streamHeaderBlocksUsed
            leftoverFrameBits = remainingBlocksLeft * headerBitLength

            if leftoverFrameBits > dataLeft:
                dataLeft = 0
            else:
                dataLeft -= leftoverFrameBits

        frameNumber += 1

    # Calculating how much data can be embedded in a regular framePayload frame, and returning the total frame count needed.
    blocksLeft = totalBlocks - (initializerOverhead * int(outputMode == 'image'))
    payloadBitsPerFrame = (blocksLeft * streamBitLength) - frameHeaderOverhead

    totalFrames = math.ceil(dataLeft / payloadBitsPerFrame) + frameNumber
    logging.info(f'{totalFrames} frame(s) required for this operation.')
    return totalFrames


def generateInitializer(blockHeight, blockWidth, protocolVersion, headerPalette):
    '''This generates the initializer header, which is present in black and white colors on the top of the first frame
    of video streams, and every frame of image streams.  It provides import information on stream geometry as well as
    protocol version.
    '''
    fullBitString = BitArray()
    fullBitString.append(BitArray(uint=protocolVersion, length=4))
    fullBitString.append(BitArray(uint=blockHeight, length=16))
    fullBitString.append(BitArray(uint=blockWidth, length=16))

    if headerPalette.paletteType == 'default':
        fullBitString.append(BitArray(uint=int(headerPalette.id), length=256))
    else:
        fullBitString.append(BitArray(hex=headerPalette.id))

    fullBitStringToHash = fullBitString.tobytes()
    crcOutput = zlib.crc32(fullBitStringToHash)
    fullBitString.append(BitArray(uint=crcOutput, length=32))

    return fullBitString


def renderCalibrator(image, blockHeight, blockWidth, pixelWidth):
    '''This creates the checkboard-like pattern along the top and left of the first frame of video streams, and every
    frame of image streams.  This is what the reader uses to initially lock onto the frame.  Stream blockWidth and
    blockHeight are encoded into this pattern, using alternating color palettes so no two repeating values produce a
    continuous block of color, interfering with the frame lock process.'''

    initializerPaletteDictA = ValuesToColor(_paletteGrabber('1'), 'initializerPalette A')
    initializerPaletteDictB = ValuesToColor(_paletteGrabber('11'), 'initializerPalette B')

    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, pixelWidth - 1, pixelWidth - 1),
                    fill='rgb(0,0,0)')

    blockWidthEncoded = BitArray(uint=blockWidth, length=blockWidth - 1)
    blockWidthEncoded.reverse()
    readableBlockWidth = ConstBitStream(blockWidthEncoded)
    for i in range(blockWidth - 1):
        nextBit = readableBlockWidth.read('bits : 1')
        if i % 2 == 0:
            colorValue = initializerPaletteDictB.getColor(ConstBitStream(nextBit))
        else:
            colorValue = initializerPaletteDictA.getColor(ConstBitStream(nextBit))
        draw.rectangle((pixelWidth * i + pixelWidth,
                        0,
                        pixelWidth * (i + 1) - 1 + pixelWidth,
                        pixelWidth - 1),
                       fill=f'rgb{str(colorValue)}')

    blockHeightEncoded = BitArray(uint=blockHeight, length=blockHeight-1)
    blockHeightEncoded.reverse()
    readableBlockHeight = ConstBitStream(blockHeightEncoded)
    for i in range(blockHeight - 1):
        nextBit = readableBlockHeight.read('bits : 1')
        if i % 2 == 0:
            colorValue = initializerPaletteDictB.getColor(ConstBitStream(nextBit))
        else:
            colorValue = initializerPaletteDictA.getColor(ConstBitStream(nextBit))
        draw.rectangle((0,
                        pixelWidth * i + pixelWidth,
                        pixelWidth - 1,
                        pixelWidth * (i + 1) - 1 + pixelWidth),
                       fill=f'rgb{str(colorValue)}')

    return image


def loopGenerator(blockHeight, blockWidth, pixelWidth, initializerEnabled):
    for yRange in range(blockHeight - int(initializerEnabled)):
        for xRange in range(blockWidth - int(initializerEnabled)):
            yield ((pixelWidth * int(initializerEnabled)) + (pixelWidth * xRange),
                (pixelWidth * int(initializerEnabled)) + (pixelWidth * yRange),
                (pixelWidth * int(initializerEnabled)) + (pixelWidth * (xRange + 1) - 1),
                (pixelWidth * int(initializerEnabled)) + (pixelWidth * (yRange + 1) - 1))