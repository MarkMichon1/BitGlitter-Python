import logging
import math

from bitstring import BitStream

from bitglitter.read.coloranalysis import colorSnap
from bitglitter.read.decoderassets import scanBlock
from bitglitter.config.config import config

class FrameHandler:
    '''FrameHandler object is what traverses the actual frame, and returns bit data.  It's designed as an easy to use
    API, hiding much of the moving parts behind the scenes of a frame scan.
    '''

    def __init__(self, initializerPalette, initializerPaletteDict):

        # Setup
        self.image = None
        self.blockHeight = None
        self.blockWidth = None
        self.pixelWidth = None

        # Palette Variables
        self.initializerPalette = initializerPalette
        self.initializerPaletteDict = initializerPaletteDict
        self.headerPalette = None
        self.headerPaletteDict = None
        self.streamPalette = None
        self.streamPaletteDict = None
        self.primaryPalette = None
        self.primaryPaletteDict = None

        # Dictionaries
        self.paletteDict = {'initializerPalette': self.initializerPalette,
                            'primaryPalette': self.primaryPalette,
                            'headerPalette': self.headerPalette,
                            'streamPalette': self.streamPalette}
        self.paletteConversionDict = {'initializerPalette' : self.initializerPaletteDict,
                                      'primaryPalette': self.primaryPaletteDict,
                                      'headerPalette' : self.headerPaletteDict,
                                      'streamPalette' : self.streamPaletteDict}

        # Scan State
        self.isFirstFrame = True #todo
        self.nonCalibratorBlocks = 0
        self.nextBlock = 0
        self.blockPosition = 0


    def _setupFrameGrid(self, hasInitializer):
        '''Ran on initialization, this creates a generator that outputs the correct block coordinates for scanBlock
        to utilize.  This depends on whether an initializer is used in this frame or not.
        '''

        for yBlock in range(self.blockHeight - int(hasInitializer)):
            for xBlock in range(self.blockWidth - int(hasInitializer)):
                yield xBlock + int(hasInitializer), yBlock + int(hasInitializer)


    def _blocksToBits(self, howMany, paletteType):
        '''This is an internal method that, based on how many blocks it was told to scan as well as the palette type
        used, will scan that amount on the image and return those converted bits.'''

        bitString = BitStream()
        activeColorSet = self.paletteDict[paletteType].colorSet
        activePaletteDict = self.paletteConversionDict[paletteType]

        for block in range(howMany):
            blockCoords = next(self.nextBlock)
            #logging.debug(blockCoords) #todo
            rawRGB = scanBlock(self.image, self.pixelWidth, blockCoords[0], blockCoords[1])
            if activeColorSet:
                bitString.append(activePaletteDict.getValue(colorSnap(rawRGB, activeColorSet)))
            else:
                bitString.append(activePaletteDict.getValue(rawRGB))

        #logging.debug(f'blocksToBits ran, {howMany} blocks advanced for {paletteType}')
        self.blockPosition += howMany
        config.statsHandler.blocksRead += howMany

        return bitString


    def returnInitializer(self):
        '''This returns the initializer bitstring for the frame.'''

        return self._blocksToBits(324, 'initializerPalette')


    def returnFrameHeader(self, paletteType):
        '''This method returns the bits carrying the frame header for the frame, as well as the "carry over" bits, which
        were the excess capacity within those blocks, assuming there was extra space.
        '''

        # always 608 bits, plus whatever remainder bits that may be present in the final block.  Protocol v1 only!
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
        '''With the other parts of the frame already scanned (initializer if applicable, and frame header), based on how
        many blocks are left, it will scan those and return the bit string.
        '''


        if paletteType != 'streamPalette' and paletteType != 'headerPalette' and paletteType != 'primaryPalette':
            raise ValueError("FrameHandler.returnRemainderPayload: invalid paletteType argument.")

        logging.debug(f'FFF {self.nonCalibratorBlocks} {self.blockPosition}')
        remainderPayload = self._blocksToBits(self.nonCalibratorBlocks - self.blockPosition, f'{paletteType}')
        config.statsHandler.dataRead += remainderPayload.len

        return remainderPayload


    def updateScanGeometry(self, blockHeight, blockWidth, pixelWidth):
        '''FrameHandler is a persistent object between frames, held by Decoder.  Because of it's instantiation at
        Decoder's instantiation, scan geometry cannot be loaded into it immediately.  This function does that.
        '''

        self.blockHeight = blockHeight
        self.blockWidth = blockWidth
        self.pixelWidth = pixelWidth

        self.nonCalibratorBlocks = (self.blockHeight - int(self.isFirstFrame)) * \
                                   (self.blockWidth - int(self.isFirstFrame))


    def updateDictionaries(self, paletteType, paletteDict, palette):
        '''As the stream is setting up, its not possible to instantiate this object with everything at once.  This
        method allows for an easy way to inject new palette objects into the dictionaries used for retrieving values.
        '''

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


    def updateBlocksToRead(self, blocksToRead):
        '''After the frame header bit string is successfully read by readFrameHeader(), this updates how many total
        blocks must be read on this frame.  Until that is known, FrameHandler will simply 'blindly' read the full frame,
        as it is instructed to in pieces.
        '''


        if blocksToRead < self.nonCalibratorBlocks:
            logging.debug(f'Last frame detected, {blocksToRead} to scan.')
        else:
            logging.debug('Full frame detected.')

        self.nonCalibratorBlocks = blocksToRead


    def loadNewFrame(self, image, hasInitializer):
        '''This method loads in the new image, as well as resets the parameters from the previous frame.'''

        self.image = image
        self.isFirstFrame = hasInitializer
        self.nextBlock = self._setupFrameGrid(hasInitializer)
        self.blockPosition = 0

        # This will only fail once, as geometry is not immediately known on the loading of the first frame.
        try:
            self.nonCalibratorBlocks = (self.blockHeight - int(hasInitializer)) * \
                                       (self.blockWidth - int(hasInitializer))
        except:
            pass

        config.statsHandler.framesRead += 1