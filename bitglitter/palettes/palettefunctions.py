import os
import time

from bitglitter.config.config import config
from bitglitter.utilities.generalverifyfunctions import properStringSyntax
from bitglitter.palettes.paletteutilities import _addCustomPaletteDirect, colorDistance, returnPaletteID



def dictPopper(idOrNick):
    '''This is an internal function used for removeCustomPalette(), addNicknameToCustomPalette(), and
    removeCustomPaletteNicknames().  Since a user can either either the palette ID OR it's nickname as an argument,
    first we must check whether that key exists.  If it does, it will check both dictionaries in the ColorHandler object
    for custom colors, customPaletteList and customPaletteNicknameList.  It will then delete both dictionary keys (if
    available), and  then return the object to optionally be modified (or otherwise discarded)
    '''

    if idOrNick in config.colorHandler.customPaletteNicknameList:
        tempHolder = config.colorHandler.customPaletteNicknameList[idOrNick]
        del config.colorHandler.customPaletteList[tempHolder.id]
        return config.colorHandler.customPaletteNicknameList.pop(idOrNick)
    elif idOrNick in config.colorHandler.customPaletteList:
        tempHolder = config.colorHandler.customPaletteList[idOrNick]
        if config.colorHandler.customPaletteNicknameList[tempHolder.nickname]:
            del config.colorHandler.customPaletteNicknameList[tempHolder.nickname]
        return config.colorHandler.customPaletteList.pop(idOrNick)
    else:
        raise ValueError(f"'{idOrNick}' does not exist.")


def addCustomPalette(paletteName, paletteDescription, colorSet, optionalNickname = ""):
    '''This function allows you to save a custom palette to be used for future writes.  Arguments needed are name,
    description, color set, which is a tuple of tuples, and optionally a nickname.  All other object are attributes are
    added in this process.  Before anything gets added, we need to ensure the arguments are valid.
    '''

    dateCreated = str(round(time.time()))
    nameString = str(paletteName)
    descriptionString = str(paletteDescription)
    nicknameString = str(optionalNickname)

    # Is name, description legal characters?
    properStringSyntax(nameString)
    properStringSyntax(descriptionString)

    # Is nickname legal characters?  Is the name available?
    properStringSyntax(nicknameString)
    if optionalNickname in config.colorHandler.customPaletteNicknameList or optionalNickname in \
            config.colorHandler.customPaletteList or optionalNickname in config.colorHandler.defaultPaletteList:
        raise ValueError(f"'{optionalNickname}' is already taken, please choose another nickname.")

    # Verifying colorset parameters.  2^n length, 3 values per color, values are type int, values are 0-255.  Finally,
    # verify colors aren't overlapping (ie, the same color is used twice).
    if len(colorSet) % 2 != 0 or len(colorSet) < 2:
        raise ValueError("Length of color set must be 2^n length (2 colors, 4, 8, etc) with a minimum of two colors.")

    for colorTuple in colorSet:

        if len(colorTuple) != 3:
            raise ValueError("Each color needs 3 entries, for red green and blue.")

        for color in colorTuple:
            if not isinstance(color, int) or color < 0 or color > 255:
                raise ValueError("For each RGB value, it must be an integer between 0 and 255.")

    minDistance = colorDistance(colorSet)
    if minDistance == 0:
        raise ValueError("Calculated color distance is 0.  This occurs when you have two identical colors in your"
              " palette.  This breaks the communication protocol.  See BitGlitter guide for more information.")

    '''At this point, assuming no errors were raised, we're ready to instantiate the custom color object.  This function
    creates an identification for the object.  For as long as the palette exists, this is a permanent ID that can be
    used as an argument for colorID in write().  This value will get returned at the end of this function.
    '''

    id = returnPaletteID(nameString, descriptionString, dateCreated, colorSet)
    _addCustomPaletteDirect(nameString, descriptionString, colorSet, minDistance, dateCreated, id, nicknameString)

    return id


def removeCustomPalette(idOrNick):
    '''Removes custom palette completely from the config file.'''
    dictPopper(idOrNick)
    config.saveSession()


def editNicknameToCustomPalette(idOrNick, newName):
    '''This changes the nickname of the given palette to something new, first checking if it's valid.'''

    if newName not in config.colorHandler.customPaletteList \
            and newName not in config.colorHandler.customPaletteNicknameList \
            and newName not in config.colorHandler.defaultPaletteList:

        tempHolder = dictPopper(idOrNick)
        tempHolder.nickname = newName
        config.colorHandler.customPaletteList[tempHolder.id] = tempHolder
        config.colorHandler.customPaletteNicknameList[tempHolder.nickname] = tempHolder
        config.saveSession()

    else:

        raise ValueError(f"'{newName}' is already being used, please try another.")


def removeCustomPaletteNickname(idOrNick):
    '''Removes the palette nickname from the corresponding dictionary.  This does not delete the palette, only the
    nickname.
    '''

    tempHolder = dictPopper(idOrNick)
    tempHolder.nickname = ""
    config.colorHandler.customPaletteList[tempHolder.id] = tempHolder
    config.saveSession()


def clearCustomPaletteNicknames():
    '''Clears all custom palette nicknames.  This does not delete the palettes themselves.'''

    config.colorHandler.customPaletteNicknameList = {}

    for palette in config.colorHandler.customPaletteList:

        tempHolder = config.colorHandler.customPaletteList.pop(palette)
        tempHolder.nickname = ""
        config.colorHandler.customPaletteList[tempHolder.id] = tempHolder

    config.saveSession()


def printFullPaletteList(path):
    '''Writes a text file to a file path outlining available color palettes.'''
    activePath = os.path.join(os.getcwd(), path)

    with open(activePath + '\\Palette List.txt', 'w') as writer:
        writer.write('*' * 21 + '\nDefault Palettes\n' + '*' * 21 + '\n')

        for someKey in config.colorHandler.defaultPaletteList:
            writer.write('\n' + str(config.colorHandler.defaultPaletteList[someKey]) + '\n')

        writer.write('*' * 21 + '\nCustom Palettes\n' + '*' * 21 + '\n')

        if config.colorHandler.customPaletteList:

            for someKey in config.colorHandler.customPaletteList:
                writer.write('\n' + str(config.colorHandler.customPaletteList[someKey]) + '\n')
        else:
            writer.write('\nNo custom palettes (yet)')


def clearAllCustomPalettes():
    '''Removes all custom palettes from both the ID dictionary and nickname dictionary.'''
    config.colorHandler.customPaletteNicknameList = {}
    config.colorHandler.customPaletteList = {}
    config.saveSession()