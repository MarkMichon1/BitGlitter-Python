import logging
import shutil

from bitglitter.config.constants import READ_PATH
from bitglitter.read.partialsave import PartialSave


class Assembler:
    '''This object holds PartialSave objects, which holds the state of the file being read until it is fully assembled
    and complete, which then purges the record.
    '''

    def __init__(self):
        self.workingFolder = READ_PATH
        self.saveDict = {}
        self.activeSessionHashes = []


    def checkIfFrameNeeded(self, streamSHA, frameNumber):

        if streamSHA not in self.saveDict:
            return True
        else:
            if self.saveDict[streamSHA].isFrameNeeded(frameNumber) == False:
                logging.info('This frame is already saved!  Skipping...')
            else:
                return True
        return False


    def createPartialSave(self, streamSHA, scryptN, scryptR, scryptP, outputPath, encryptionKey):
        self.saveDict[streamSHA] = PartialSave(streamSHA, self.workingFolder, scryptN, scryptR, scryptP, outputPath,
                                               encryptionKey)


    def saveFrameIntoPartialSave(self, streamSHA, payload, frameNumber):
        logging.debug(payload.len)
        self.saveDict[streamSHA].loadFrameData(payload, frameNumber)


    def acceptFrame(self, streamSHA, payload, frameNumber, scryptN, scryptR, scryptP, outputPath, encryptionKey):
        '''This method accepts a validated frame.'''

        if streamSHA not in self.saveDict:
            self.createPartialSave(streamSHA, scryptN, scryptR, scryptP, outputPath, encryptionKey)

        if streamSHA not in self.activeSessionHashes:
            self.activeSessionHashes.append(streamSHA)

        self.saveFrameIntoPartialSave(streamSHA, payload, frameNumber)


    def reviewActiveSessions(self):
        '''This method will go over all streamSHA's that were read in this read session, and will check to see if
        check if framesIngested == totalFrames AND the table has all trues
        '''

        for partialSave in self.activeSessionHashes:

            if self.saveDict[partialSave]._attemptAssembly() == False: # False = not ready to be assembled this session.
                self.saveDict[partialSave]._closeSession()

            else: # Assembled, temporary files pending deletion.
                logging.info(f'{partialSave} fully read!  Deleting temporary files...')
                self.removePartialSave(partialSave)

        self.activeSessionHashes = []


    def removePartialSave(self, streamSHA):
        '''Removes PartialSave from dictionary.  Is used either through direct user argument, or by read() once a stream
        is successfully converted back into a file.
        '''

        del self.saveDict[streamSHA]
        shutil.rmtree(self.workingFolder + f'\\{streamSHA}')
        logging.debug(f'Temporary files successfully removed.')


    def clearPartialSaves(self):
        '''This removes all save data.  Called by user function removeAllPartialSaves() in savedfilefunctions.'''

        try:
            shutil.rmtree(self.workingFolder)
        except:
            pass

        self.saveDict = {}

