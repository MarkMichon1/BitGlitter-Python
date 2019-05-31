import logging
import os

from bitglitter.filepackager.filepackager import Folder, File, package
from bitglitter.utilities.filemanipulation import compressFile, encryptFile


class Packager:
    '''Packager object takes all files and folders from argument fileList in write, and begins assembling them into a
    single package.dat file.  All arguments that aren't a file or folder are automatically discarded.
    '''

    def __init__(self, activeFolder, fileList, maskFiles):

        self.fileList = fileList
        rootFolder = Folder(name='Root')
        logging.info("Preparing files for packaging...")
        invalidInput = False

        # If a string was used to denote a single file or file path, this automatically converts it into a tuple.
        if isinstance(fileList, str):
            fileList = (fileList,)

        for item in fileList:

            if os.path.isfile(item):
                logging.debug(f"Adding file: {item}")
                newObject = File(item)
                rootFolder + newObject
                invalidInput = True

            if os.path.isdir(item):
                logging.debug(f"Adding folder: {item}")
                rootFolder + Folder(filePath=item)
                invalidInput = True

        if invalidInput == False:
            raise ValueError("No valid files or folders were found from your fileList tuple in write()")

        self.passThrough = activeFolder + '\\package.dat'

        logging.info("Packaging files...")
        package(rootFolder, activeFolder, maskFiles)
        logging.info("Packaging complete.")


class Compressor:
    '''Compressor takes package.dat created from Packager and compresses the file, assuming compressionEnabled == True.
    A hash of the file is taken as well at this point, if encryptionEnabled == True.
    '''

    def __init__(self, passThrough, activeFolder, compressionEnabled):
        self.passThrough = passThrough
        self.preEncryptionHash = ''

        if compressionEnabled == True:
            logging.info('Compressing package...')
            self.newName = activeFolder + '\\compressed.dat'

            compressFile(self.passThrough, self.newName)
            self.passThrough = self.newName
            logging.info('Compression complete.')

        else:
            logging.info("Skipping compression.")


class Encryptor:
    '''Encryptor object applies encryption to the file being pre-processed if encryptionKey has an argument.'''

    def __init__(self, passThrough, activeFolder, encryptionKey, scryptOverrideN,
                 scryptOverrideR, scryptOverrideP):
        self.passThrough = passThrough
        self._cryptoKey = encryptionKey

        if len(encryptionKey) == 0:
            logging.info('Skipping encryption.')
            self.encryptionEnabled = False

        else:
            newName = activeFolder + '\\encrypted.dat'
            logging.info('Encrypting package...')
            encryptFile(self.passThrough, newName, encryptionKey, scryptOverrideN, scryptOverrideR, scryptOverrideP)
            logging.info('Encryption complete.')

            logging.debug(f"Removed {self.passThrough}")
            self.passThrough = newName
            self.encryptionEnabled = True