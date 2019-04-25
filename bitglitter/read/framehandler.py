import logging
import math

from bitstring import BitStream

from bitglitter.read.coloranalysis import colorSnap
from bitglitter.read.decoderassets import scanBlock
from bitglitter.config.config import config

class FrameHandler:
    '''FrameHandler object is what traverses the actual frame, and returns bit data.  It's designed as an easy to use
    API, making this step of read easy to use.
    '''

    def __init__(self):

    # def __init__(self, image, hasInitializer, initializerPaletteColorSet, initializerPaletteDict, blockHeight,
    #              blockWidth, pixelWidth, headerPaletteDict=None, headerPalette=None,
    #              headerPaletteBitLength=None, streamPaletteDict=None, streamPalette=None,
    #              streamPaletteBitLength=None):

        self.image = None
        self.hasInitializer = None
        self.initializerPaletteDict = None
        self.initializerPalette = None

        self.blockHeight = None
        self.blockWidth = None
        self.pixelWidth = None

        self.headerPaletteDict = None
        self.headerPalette = None
        self.headerPaletteBitLength = None
        self.streamPaletteDict = None
        self.streamPalette = None
        self.streamPaletteBitLength = None

        self.primaryPaletteBitLength = None

        self.paletteConversionDict = {'initializerPalette' : self.initializerPaletteDict,
                                'headerPalette' : self.headerPaletteDict,
                                'streamPalette' : self.streamPaletteDict}
        self.paletteDict = {'initializerPalette' : self.initializerPalette,
                                'headerPalette' : self.headerPalette,
                                'streamPalette' : self.streamPalette}

        self.nonCalibratorBlocks = 0
        self.nextBlock = 0
        self.blockPosition = 0


    def _setupFrameGrid(self):
        '''Ran on initialization, this creates a generator that outputs the correct block coordinates for scanBlock
        to utilize.
        '''
        # logging.debug(f'frameGrid setting up.... bW {self.blockHeight - int(self.hasInitializer)} '
        #               f'bH {self.blockWidth - int(self.hasInitializer)}\n'
        #               f'Initializer this frame: {self.hasInitializer}')

        for yBlock in range(self.blockHeight - int(self.hasInitializer)):
            for xBlock in range(self.blockWidth - int(self.hasInitializer)):
                yield xBlock + int(self.hasInitializer), yBlock + int(self.hasInitializer)


    def _blocksToBits(self, howMany, paletteType):
        bitString = BitStream()
        activeColorSet = self.paletteDict[paletteType].colorSet
        activePaletteDict = self.paletteConversionDict[paletteType]

        for block in range(howMany):
            blockCoords = next(self.nextBlock)
            rawRGB = scanBlock(self.image, self.pixelWidth, blockCoords[0], blockCoords[1])
            if activeColorSet:
                bitString.append(activePaletteDict.getValue(colorSnap(rawRGB, activeColorSet)))
            else:
                bitString.append(activePaletteDict.getValue(rawRGB))

        logging.debug(f'blocksToBits ran, {howMany} blocks advanced for {paletteType}')
        self.blockPosition += howMany
        config.statsHandler.blocksRead += howMany

        return bitString


    def returnInitializer(self): #always 324 blocks
        return self._blocksToBits(324, 'initializerPalette')


    def returnFrameHeader(self, paletteType):
        # always 608 bits, plus whatever remainder bits that may be present in the final block.
        if paletteType != 'streamPalette' and paletteType != 'headerPalette' and paletteType != 'primaryPalette':
            raise ValueError("FrameHandler.returnFrameHeader: invalid paletteType argument.")
        fullBlockData = self._blocksToBits(math.ceil(608 / self.paletteDict[paletteType].bitLength), f'{paletteType}')
        carryOverBits = BitStream()
        if fullBlockData.len > 608:
            fullBlockData.pos = 608
            carryOverBits.append(fullBlockData.read(f'bits : {fullBlockData.len - 608}'))
            fullBlockData.pos = 0

        config.statsHandler.dataRead += carryOverBits.len
        return fullBlockData.read('bits : 608'), carryOverBits


    def returnRemainderPayload(self, paletteType):
        if paletteType != 'streamPalette' and paletteType != 'headerPalette' and paletteType != 'primaryPalette':
            raise ValueError("FrameHandler.returnRemainderPayload: invalid paletteType argument.")
        remainderPayload = self._blocksToBits(self.nonCalibratorBlocks - self.blockPosition, f'{paletteType}')
        config.statsHandler.dataRead += remainderPayload.len
        return remainderPayload


    def updateDictionaries(self, paletteType, paletteDict, palette):
        '''As the stream is setting up, its not possible to instantiate this object with everything at once.  This
        method allows for an easy way to inject new palette objects into the dictionaries used for retrieving values.'''
        if paletteType == 'headerPalette':
            self.paletteConversionDict['headerPalette'] = paletteDict
            self.paletteDict['headerPalette'] = palette
        elif paletteType == 'streamPalette':
            self.paletteConversionDict['streamPalette'] = paletteDict
            self.paletteDict['streamPalette'] = palette
        elif paletteType == 'primaryPalette':
            self.paletteConversionDict['primaryPalette'] = paletteDict
            self.paletteDict['primaryPalette'] = palette
        else:
            raise ValueError('FrameHandler.updateDictionary: invalid paletteType argument.')


    def updateBlocksToRead(self, blocksToRead): #todo look at this?
        if blocksToRead > 0:
            self.nonCalibratorBlocks = blocksToRead
            logging.debug(f'Last frame detected, {blocksToRead} to scan.')
        else:
            logging.debug('Full frame detected.')


    def loadNewFrame(self, image, hasInitializer):
        '''This method loads in the new image, as well as resets the parameters from the previous frame.'''

        self.image = image
        self.nextBlock = self._setupFrameGrid()
        self.nonCalibratorBlocks = (self.blockHeight - int(self.hasInitializer)) * (self.blockWidth
                                                                                    - int(self.hasInitializer))
        config.statsHandler.framesRead += 1
