import os

from bitglitter.config.config import config
from bitglitter.utilities.generalverifyfunctions import isIntOverZero, isValidDirectory, properStringSyntax

# These functions are for end users.

def printFullSaveList(path, debugData = False):
    '''This function will output a text file displaying the current status of all of the partial saves in BitGlitter.
    Path specifies the folder path it will be outputted to.  Argument debugData will show various debug information
    pertaining to the partial save, that the normal user has no need to see.
    '''

    activePath = os.path.join(os.getcwd(), path)

    with open(activePath + '\\BitGlitter Partial Saves.txt', 'w') as writer:
        writer.write('*' * 21 + '\nPartial Saves\n' + '*' * 21 + '\n')

        if config.assembler.saveDict:
            tempHolder = ''

            for partialSave in config.assembler.saveDict:
                tempHolder += ('\n' + config.assembler.saveDict[partialSave].returnStatus(debugData) + '\n\n')
            writer.write(tempHolder)

        else:
            writer.write('\nNo partial saves (yet!)')


def updatePartialSave(streamSHA, reattemptAssembly = True, passwordUpdate = None, scryptN =  None,
                      scryptR = None, scryptP = None, changeOutputPath = None):
    '''This function will update the PartialSave object with the parameters provided, once they've been verified.'''

    if passwordUpdate:
        properStringSyntax('passwordUpdate', passwordUpdate)
    if scryptN:
        isIntOverZero('scryptN', scryptN)
    if scryptR:
        isIntOverZero('scryptR', scryptR)
    if scryptP:
        isIntOverZero('scryptP', scryptP)
    if changeOutputPath:
        isValidDirectory('changeOutputPath', changeOutputPath)

    config.assembler.saveDict[streamSHA].userInputUpdate(passwordUpdate, scryptN, scryptR, scryptP, changeOutputPath)

    if reattemptAssembly == True:
        if config.assembler.saveDict[streamSHA]._attemptAssembly() == True:
            config.assembler.removePartialSave(streamSHA)

    config.saveSession()


def removePartialSave(streamSHA):
    '''Taking the stream SHA as an argument, this function will remove the partial save object, and well as remove any
    temporary data BitGlitter may have had with it.
    '''

    config.assembler.removePartialSave(streamSHA)
    config.saveSession()


def beginAssembly(streamSHA):
    '''This function exists to initiate assembly of a package at a later time, rather than doing so immediately for
    whatever reason.
    '''

    if config.assembler.saveDict[streamSHA]._attemptAssembly() == True:
        config.assembler.removePartialSave(streamSHA)
    config.saveSession()


def removeAllPartialSaves():
    '''This removes all partial save objects saved, as well as any temporary data.'''

    config.assembler.clearPartialSaves()
    config.saveSession()
