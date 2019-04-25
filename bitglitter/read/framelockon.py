import logging

from bitstring import BitArray, ConstBitStream

from bitglitter.read.coloranalysis import colorSnap, returnDistance
from bitglitter.read.decoderassets import scanBlock
from bitglitter.palettes.paletteutilities import _paletteGrabber, ColorsToValue


'''This takes the the loaded value
'''
def frameLockOn(image, blockHeightOverride, blockWidthOverride):

    logging.debug('Locking onto frame...')
    initializerPaletteA = _paletteGrabber('1')
    initializerPaletteB = _paletteGrabber('11')
    initializerPaletteADict = ColorsToValue(initializerPaletteA)
    initializerPaletteBDict = ColorsToValue(initializerPaletteB)
    combinedColors = initializerPaletteA.colorSet + initializerPaletteB.colorSet

    pixel = image.load()
    imageWidth, imageHeight = image.size[0], image.size[1]

    if blockHeightOverride and blockWidthOverride: # Jump straight to verification
        logging.info("blockHeightOverride and blockWidthOverride parameters detected.  Attempting to lock with these"
                     " values...")

        pixelWidth = ((imageWidth / blockWidthOverride) + (imageHeight / blockHeightOverride)) / 2

        checkpoint = verifyBlocksX(image, pixelWidth, blockWidthOverride, combinedColors, initializerPaletteADict,
                                   initializerPaletteBDict, override=True)
        if checkpoint == False:
                return False, False, False

        checkpoint = verifyBlocksY(image, pixelWidth, blockHeightOverride, combinedColors, initializerPaletteADict,
                                   initializerPaletteBDict, override=True)
        if checkpoint == False:
                return False, False, False

        blockWidth, blockHeight = blockWidthOverride, blockHeightOverride

    else:

        # First checkpoint.  Does pixel 0,0 have colorDistance value of under 100 for black (0,0,0)?
        if returnDistance(pixel[0, 0], (0,0,0)) > 100:
            logging.warning('Frame lock fail!  Initial pixel value exceeds maximum color distance allowed for a '
                            'reliable lock.')
            return False, False, False

        pixelWidth, blockDimensionGuess = pixelCreep(pixel, initializerPaletteA, initializerPaletteB, combinedColors,
                                                     initializerPaletteADict, initializerPaletteBDict, imageWidth,
                                                     imageHeight, width=True)
        checkpoint = verifyBlocksX(image, pixelWidth, blockDimensionGuess, combinedColors, initializerPaletteADict,
                                   initializerPaletteBDict)
        if checkpoint == False:
            return False, False, False
        blockWidth = blockDimensionGuess

        pixelWidth, blockDimensionGuess = pixelCreep(pixel, initializerPaletteA, initializerPaletteB, combinedColors,
                                                     initializerPaletteADict, initializerPaletteBDict, imageWidth,
                                                     imageHeight, width=False)
        checkpoint = verifyBlocksY(image, pixelWidth, blockDimensionGuess, combinedColors, initializerPaletteADict,
                                   initializerPaletteBDict)
        if checkpoint == False:
            return False, False, False
        blockHeight = blockDimensionGuess


    logging.debug(f'Lockon successful.\npixelWidth: {pixelWidth}\nblockHeight: {blockHeight}\nblockWidth: {blockWidth}')

    return blockHeight, blockWidth, pixelWidth


def verifyBlocksX(image, pixelWidth, blockWidthEstimate, combinedColors, initializerPaletteADict,
                  initializerPaletteBDict, override = False):

    calibratorBitsX = BitArray()
    for xBlock in range(17):
        snappedValue = colorSnap(scanBlock(image, pixelWidth, xBlock, 0), combinedColors)
        if xBlock % 2 == 0:
            calibratorBitsX.append(initializerPaletteADict.getValue(snappedValue))
        else:
            calibratorBitsX.append(initializerPaletteBDict.getValue(snappedValue))

    calibratorBitsX.reverse()
    readCalibratorX = ConstBitStream(calibratorBitsX)

    if readCalibratorX.read('uint:16') != blockWidthEstimate:
        if override == True:
            logging.warning('blockWidthOverride is not equal to what was read on calibrator.  Aborting...')
        else:
            logging.warning('blockWidth verification does not match initial read.  This could be the result of \n'
                            'sufficiently distorted frames.  Aborting...')
        return False

    if readCalibratorX.read('bool') != False:
        logging.warning('0,0 block unexpected value.  Aborting...')
        return False

    if override == True:
        logging.info('blockWidthOverride successfully verified.')

    else:
        logging.debug('blockWidth successfully verified.')

    return True


def verifyBlocksY(image, pixelWidth, blockHeightEstimate, combinedColors, initializerPaletteADict,
                  initializerPaletteBDict, override = False):
    calibratorBitsY = BitArray()
    for yBlock in range(17):
        snappedValue = colorSnap(scanBlock(image, pixelWidth, 0, yBlock), combinedColors)
        if yBlock % 2 == 0:
            calibratorBitsY.append(initializerPaletteADict.getValue(snappedValue))
        else:
            calibratorBitsY.append(initializerPaletteBDict.getValue(snappedValue))

    calibratorBitsY.reverse()
    readCalibratorY = ConstBitStream(calibratorBitsY)

    if readCalibratorY.read('uint:16') != blockHeightEstimate:
        if override == True:
            logging.warning('blockHeightOverride is not equal to what was read on calibrator.  Aborting...')
        else:
            logging.warning('blockHeight verification does not match initial read.  This could be the result of \n'
                            'sufficiently distorted frames.  Aborting...')
        return False

    if readCalibratorY.read('bool') != False:
        logging.warning('0,0 block unexpected value.  Aborting...')
        return False

    if override == True:
        logging.info('blockHeightOverride successfully verified.')

    else:
        logging.debug('blockHeight successfully verified.')

    return True


def pixelCreep(pixelObject, initializerPaletteA, initializerPaletteB, combinedColors, initializerPaletteADict,
               initializerPaletteBDict, imageWidth, imageHeight, width):
    calibratorBits = BitArray()
    snappedValues = []
    activeColor = (0, 0, 0)
    activeDistance = 0
    pixelOnDimension = 1
    paletteAIsActive = False

    if width == True:
        axisOnImage = pixelOnDimension, 0
        axisAnalyzed = imageWidth
    else:
        axisOnImage = 0, pixelOnDimension
        axisAnalyzed = imageHeight

    for value in range(16):
        while True:
            if width == True:
                axisOnImage = pixelOnDimension, 0
                axisAnalyzed = imageWidth
            else:
                axisOnImage = 0, pixelOnDimension
                axisAnalyzed = imageHeight

            newPaletteLocked = False
            activeScan = pixelObject[axisOnImage]
            activeDistance = returnDistance(activeScan, activeColor)
            # logging.info('pixelOnDimension {} activeScan {} activeDistance {} activeColor {}'.format(
            #     pixelOnDimension, activeScan, activeDistance, activeColor))
            pixelOnDimension += 1
            if activeDistance < 100:  # Iterating over same colored blocks, until distance exceeds 100.
                continue
            else:  # We are determining if we are within < 100 dist of a new color, or are in fuzzy space.
                # logging.info('OVER 100!')
                if paletteAIsActive == False:
                    activePalette = initializerPaletteB.colorSet
                else:
                    activePalette = initializerPaletteA.colorSet
                for color in activePalette:
                    activeDistance = returnDistance(activeScan, color)
                    # logging.info('attempted color {} distance {}'.format(color, activeDistance))
                    if activeDistance < 100:
                        # logging.info('new one found {}'.format(color))
                        paletteAIsActive = not paletteAIsActive
                        newPaletteLocked = True
                        break
                    else:
                        # logging.info('guess is not close enough yet, continuing...')
                        continue

            if newPaletteLocked == True:
                break

        activeColor = colorSnap(activeScan, combinedColors)
        snappedValues.append(activeColor)
        if value % 2 != 0:
            calibratorBits.append(initializerPaletteADict.getValue(activeColor))
        else:
            calibratorBits.append(initializerPaletteBDict.getValue(activeColor))
        # logging.info('**** color being added, activeScan {} activeColor {}'.format(activeScan, activeColor))
        activeDistance = 0

    calibratorBits.reverse()
    readCalibratorBits = ConstBitStream(calibratorBits)
    blockDimensionGuess = readCalibratorBits.read('uint:16')
    pixelWidth = axisAnalyzed / blockDimensionGuess

    return pixelWidth, blockDimensionGuess

