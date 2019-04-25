import logging
import math
import time

from bitglitter.protocols.protocol_one.write.protocol_one_renderassets import renderCalibrator, generateInitializer, \
    generateFrameHeader, generateStreamHeaderBinaryPreamble, loopGenerator

from bitstring import BitArray, BitStream, ConstBitStream
from PIL import Image, ImageDraw


def renderLoop(blockHeight, blockWidth, pixelWidth, protocolVersion, initializerPalette, headerPalette, streamPalette,
               outputMode, streamOutputPath, activePath, passThrough, sizeInBytes, totalFrames, compressionEnabled,
               encryptionEnabled, fileMaskEnabled, dateCreated, asciiCompressed, streamSHA, initializerPaletteDict,
               headerPaletteDict, streamPaletteDict):
    '''This function iterates over the preProcessed data, and assembles and renders the frames.  There are plenty of
    # comments in this function that describe what each part is doing, to follow along.'''

    logging.debug('Entering renderLoop...')

    # Determining output for images.
    if outputMode == 'image':
        if streamOutputPath:
            imageOutputPath = streamOutputPath + '\\'
        else:
            imageOutputPath = ""
    if outputMode == 'video':
        imageOutputPath = activePath + '\\'

    # Constants
    TOTAL_BLOCKS = blockHeight * blockWidth
    INITIALIZER_OVERHEAD = blockHeight + blockWidth + 323
    INITIALIZER_DATA_BITS = 324
    FRAME_HEADER_OVERHEAD = 608

    activePayload = ConstBitStream(filename=passThrough)
    frameNumber = 1
    primaryFramePaletteDict, primaryReadLength = headerPaletteDict, headerPalette.bitLength
    activePalette = headerPalette
    streamPaletteUsed = False
    lastFrame = False

    # Final preparations for stream header parts.
    streamHeaderBinaryPreamble = generateStreamHeaderBinaryPreamble(sizeInBytes, totalFrames, compressionEnabled,
                                                                    encryptionEnabled, fileMaskEnabled,
                                                                    streamPalette.paletteType == "custom", dateCreated,
                                                                    streamPalette.id, len(asciiCompressed))
    streamHeaderCombined = BitStream(streamHeaderBinaryPreamble)
    streamHeaderCombined.append(asciiCompressed)

    # This is the primary loop where all rendering takes place.  It'll continue until it traverses the entire file.
    while activePayload.bitpos != activePayload.length:
        logging.info(f'Rendering frame {frameNumber} of {totalFrames} ...')

        # Setting up frame to draw on.
        image = Image.new('RGB', (pixelWidth * blockWidth, pixelWidth * blockHeight), 'white')
        draw = ImageDraw.Draw(image)

        streamHeaderChunk = BitStream()
        payloadHolder = BitStream()
        attachmentBitsAppend = BitStream()
        remainderBlocksIntoBits = BitStream()
        bitsToPad = BitStream()

        maxAllowablePayloadBits = len(activePayload) - activePayload.bitpos
        bitsConsumed = FRAME_HEADER_OVERHEAD
        blocksLeft = TOTAL_BLOCKS
        initializerEnabled = False
        blocksUsed = 0
        initializerPaletteBlocksUsed = 0
        streamHeaderBlocksUsed = 0

        if streamPaletteUsed == True:
            primaryFramePaletteDict, primaryReadLength = streamPaletteDict, streamPalette.bitLength
            activePalette = streamPalette

        # Adding an initializer header if necessity.  initializerEnabled is a boolean that signals whether the
        # initializer is on or not.
        initializerHolder = BitArray()
        if frameNumber == 1 or outputMode == 'image':

            image = renderCalibrator(image, blockHeight, blockWidth, pixelWidth)
            initializerHolder = generateInitializer(blockHeight, blockWidth, protocolVersion, activePalette)
            initializerPaletteBlocksUsed += INITIALIZER_DATA_BITS
            blocksLeft -= INITIALIZER_OVERHEAD
            initializerEnabled = True

        bitsLeftThisFrame = (blocksLeft * activePalette.bitLength) - FRAME_HEADER_OVERHEAD

        # Here, we're calculating how many bits we can fit into the stream based on the palettes used.
        # Normal framePayload frames.
        if streamPaletteUsed == True:

            # Standard framePayload frame in the middle of the stream.
            if bitsLeftThisFrame <= maxAllowablePayloadBits:
                payloadHolder = activePayload.read(bitsLeftThisFrame)

            # Payload Frame terminates on this frame.
            else:
                logging.debug('Payload termination frame')
                payloadHolder = activePayload.read(maxAllowablePayloadBits)
                lastFrame = True


        # Frames that need streamHeaderCombined added to them.
        else:

            # This frame has more bits left for the streamHeader than capacity.
            if len(streamHeaderCombined) - streamHeaderCombined.bitpos > bitsLeftThisFrame:

                streamHeaderChunk = streamHeaderCombined.read(bitsLeftThisFrame)
                streamHeaderBlocksUsed = math.ceil(len(streamHeaderChunk + FRAME_HEADER_OVERHEAD)
                                                   / activePalette.bitLength)


            # streamHeaderCombined terminates on this frame
            else:

                logging.debug("Streamheader terminates this frame.")

                streamHeaderChunk = streamHeaderCombined.read(len(streamHeaderCombined)
                                                                    - streamHeaderCombined.bitpos)
                bitsLeftThisFrame -= len(streamHeaderCombined)
                bitsConsumed += len(streamHeaderChunk)

                streamPaletteUsed = True
                streamHeaderBlocksUsed = math.ceil(bitsConsumed / activePalette.bitLength)

                # There may be extra bits available at the end of the blocks used for the headerPalette.  If that's
                # the case, they will be calculated here.
                finalBlockPartialFill = bitsConsumed % activePalette.bitLength

                if finalBlockPartialFill > 0:
                    attachmentBits = activePalette.bitLength - (finalBlockPartialFill)
                    attachmentBitsAppend = activePayload.read(attachmentBits)

                    bitsConsumed += attachmentBits
                    maxAllowablePayloadBits -= attachmentBits

                remainingBlocksLeft = blocksLeft - streamHeaderBlocksUsed

                # If there are remaining streamPalette blocks available for this frame, we go here.
                if remainingBlocksLeft > 0:
                    bitsLeftThisFrame = remainingBlocksLeft * activePalette.bitLength

                    if maxAllowablePayloadBits > bitsLeftThisFrame: # Payload continues on in next frame(s)
                        remainderBlocksIntoBits = activePayload.read(bitsLeftThisFrame)

                    else: # Full framePayload can terminate on streamHeader termination frame.
                        remainderBlocksIntoBits = activePayload.read(maxAllowablePayloadBits)
                        lastFrame = True

        frameHashableBits = streamHeaderChunk + attachmentBitsAppend + remainderBlocksIntoBits + payloadHolder
        # logging.debug(f'frameHashableBits.len {frameHashableBits.len}')
        # logging.debug(f'streamHeaderChunk.len {streamHeaderChunk.len}')
        # logging.debug(f'attachmentBitsAppend.len {attachmentBitsAppend.len}') #todo
        # logging.debug(f'remainderBlocksIntoBits.len {remainderBlocksIntoBits.len}')
        # logging.debug(f'payloadHolder.len {payloadHolder.len}')
        combinedFrameLength = frameHashableBits.len + FRAME_HEADER_OVERHEAD
        blocksUsed = (int(initializerEnabled) * INITIALIZER_DATA_BITS) + math.ceil(combinedFrameLength
                                                                                   / activePalette.bitLength)

        #On the last frame, there may be excess capacity in the final block.  This pads the payload as needed so it
        #cleanly fits into the block.
        if lastFrame == True:
            remainderBits = activePalette.bitLength - (combinedFrameLength % activePalette.bitLength)
            # logging.debug(f'remainderBits: {remainderBits}')
            # logging.debug(f'combinedFrameLength: {combinedFrameLength}')
            bitsToPad = BitArray(bin=f"{'0' * remainderBits}")
            frameHashableBits.append(bitsToPad)

        frameHeaderHolder = generateFrameHeader(streamSHA, frameHashableBits, frameNumber, blocksUsed)
        combiningBits = initializerHolder + frameHeaderHolder + streamHeaderChunk + attachmentBitsAppend \
                        + remainderBlocksIntoBits + payloadHolder + bitsToPad

        allBitsToWrite = ConstBitStream(combiningBits)
        # logging.debug(f'allBitsToWrite.len {allBitsToWrite.len}')
        nextCoordinates = loopGenerator(blockHeight, blockWidth, pixelWidth, initializerEnabled)
        blockPosition = 0

        # Drawing blocks to screen.
        while len(allBitsToWrite) != allBitsToWrite.bitpos:

            #logging.debug(blockPosition)
            # Primary palette selection (ie, headerPalette or streamPalette)
            if blockPosition >= initializerPaletteBlocksUsed:
                activePaletteDict, readLength = primaryFramePaletteDict, primaryReadLength

            # Initializer palette selection
            elif blockPosition < initializerPaletteBlocksUsed:
                activePaletteDict, readLength = (initializerPaletteDict, initializerPalette.bitLength)

            # Here to signal something has broken.
            else:
                raise Exception('Something has gone wrong in matching block position to palette.  This state'
                                '\nis reached only if something is broken.')

            nextBit = allBitsToWrite.read(f'bits : {readLength}')
            colorValue = activePaletteDict.getColor(ConstBitStream(nextBit))

            activeCoordinates = next(nextCoordinates)
            draw.rectangle((activeCoordinates[0], activeCoordinates[1], activeCoordinates[2], activeCoordinates[3]),
                           fill=f'rgb{str(colorValue)}')

            blockPosition += 1

        # Frames get saved as .png files.
        frameNumberToString = str(frameNumber)

        if outputMode == 'video':
            fileName = frameNumberToString.zfill(math.ceil(math.log(totalFrames + 1, 10)))
        else:
            fileName = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(dateCreated)) + ' - ' + str(frameNumber)

        image.save(f'{imageOutputPath}{str(fileName)}.png')
        frameNumber += 1

    logging.debug('Render complete, running cleanup()...')
    return blockPosition, imageOutputPath, str(frameNumber)