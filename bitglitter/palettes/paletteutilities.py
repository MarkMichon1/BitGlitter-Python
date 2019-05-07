import hashlib
import itertools
import logging
import math

from bitstring import BitArray, ConstBitStream

from bitglitter.config.config import config
from bitglitter.palettes.paletteobjects import CustomPalette

class ValuesToColor:
    '''This generates a dictionary linking a string binary value to an RGB value.  This is how binary data gets directly
    converted to colors.  This step required more than a dictionary, as additional logic was required to switch between
    a standard dictionary used by default and custom palettes, and 24 bit palettes.  They both convert data to colors in
    different ways, and this provides a single clean interface for that.
    '''

    def __init__(self, palette, type):
        logging.debug(f'Generating binary : color dictionary for {type}...')
        self.palette = palette
        self.bitLength = self.palette.bitLength
        self.type = type
        self.returnValue = self.generateDictionary()

    def generateDictionary(self):

        def twentyFourBitValues(value):
            redChannel = value.read('uint : 8')
            greenChannel = value.read('uint : 8')
            blueChannel = value.read('uint : 8')
            return (redChannel, greenChannel, blueChannel)

        colorDict = {}
        if self.palette.bitLength != 24:
            for value in range(len(self.palette.colorSet)):
                tempBinHolder = str(BitArray(uint=value, length=self.palette.bitLength))
                tempBinHolder = ConstBitStream(tempBinHolder)
                colorDict[tempBinHolder] = self.palette.colorSet[value]
            return colorDict
        else:
            return twentyFourBitValues

    def getColor(self, value):
        if self.bitLength != 24:
            return self.returnValue[value]
        else:
            return self.returnValue(value)


class ColorsToValue:
    '''This class does the exact opposite as ValuesToColor.  This first generates a dictionary linking colors to
    specific bit values, and then getValue() accomplishes that.
    '''

    def __init__(self, palette):
        self.palette = palette

        self.returnValue = self.generateDictionary()

    def generateDictionary(self):

        def twentyFourBitValues(color):

            outgoingData = BitArray()
            for colorChannel in color:
                outgoingData.append(BitArray(uint=colorChannel, length=8))

            return outgoingData

        valueDict = {}

        if self.palette.bitLength != 24:
            for value in range(len(self.palette.colorSet)):
                tempBinHolder = str(BitArray(uint=value, length=self.palette.bitLength))
                tempBinHolder = ConstBitStream(tempBinHolder)
                valueDict[self.palette[value]] = tempBinHolder
            return valueDict
        else:
            return twentyFourBitValues

    def getValue(self, color):
        if self.palette.bitLength != 24:
            return self.returnValue[color]
        else:
            return self.returnValue(color)


def _paletteGrabber(idOrNick):
    '''Goes through each of the dictionaries to return the color object.'''

    if idOrNick in config.colorHandler.defaultPaletteList:
        return config.colorHandler.defaultPaletteList[idOrNick]
    elif idOrNick in config.colorHandler.customPaletteList:
        return config.colorHandler.customPaletteList[idOrNick]
    elif idOrNick in config.colorHandler.customPaletteNicknameList:
        return config.colorHandler.customPaletteNicknameList[idOrNick]
    else:
        raise ValueError('_paletteGrabber: This value is not present.')


def _validateAndAddPalette(paletteName, paletteDescription, dateCreated, colorSet):
    '''This is solely to input custom palettes without all of the other prompts.  Returns True if validated and added,
    and false if it isn't.
    '''

    distance = colorDistance(colorSet)

    if distance == 0:
        return False

    if len(colorSet) % 2 != 0 or len(colorSet) < 2:
        return False

    id = returnPaletteID(paletteName, paletteDescription, dateCreated, colorSet)
    _addCustomPaletteDirect(paletteName, paletteDescription, colorSet, distance, dateCreated, id)

    return True


def colorDistance(palette):
    '''This function takes in the set of tuples in a palette, and calculates their proximity to each other in RGB space.
    Higher number denote 'safer' palettes to use in the field, as they are less prone to errors in the field.  Getting 0
    returned means you have at least a single pair of identical RGB values.  All values must be unique!
    '''

    localDistances = []

    for uniqueSet in itertools.combinations(palette, 2):

        activeDistance = math.sqrt(
            ((uniqueSet[1][0] - uniqueSet[0][0]) ** 2) + ((uniqueSet[1][1] - uniqueSet[0][1])
            ** 2) + ((uniqueSet[1][2] - uniqueSet[0][2]) ** 2))
        localDistances.append(activeDistance)

    return round(min(localDistances), 2)


def returnPaletteID(name, description, dateCreated, colorSet):
    '''Taking in the various parameters, this creates a unique ID for the object.'''

    set = str(colorSet)
    hasher = hashlib.sha256(str(name + description + dateCreated + set).encode())
    return(hasher.hexdigest())


def _addCustomPaletteDirect(name, description, colorSet, distance, dateCreated, id, nickname=None):
    '''After validation is done, this function is ran to actually instantiate the palette object, as well as load it
    into the appropriate dictionaries and save the configuration file.  This should never be ran by itself because it
    blindly accepts all values!
    '''

    newPalette = CustomPalette(name, description, colorSet, distance, dateCreated, id, nickname)
    config.colorHandler.customPaletteList[id] = newPalette

    if nickname:
        config.colorHandler.customPaletteNicknameList[nickname] = newPalette

    config.saveSession()
