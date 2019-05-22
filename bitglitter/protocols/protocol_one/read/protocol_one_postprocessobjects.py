import logging
import os

from bitglitter.filepackager.filepackager import unpackage
from bitglitter.utilities.filemanipulation import decryptFile, returnHashFromFile, decompressFile


class Decryptor:
    '''This is the first step of the post-processing once assembly is complete.  This will take the assembled binary,
    and, if encryption was enabled on this stream, will attempt to decrypt it with the AES key provided.
    '''

    def __init__(self, workingFolder, encryptionEnabled, encryptionKey, scryptN, scryptR, scryptP, streamSHA):

        inputFile = workingFolder + '\\assembled.bin'
        self.passThrough = inputFile
        self.isSatisfied = False

        if encryptionEnabled:

            if encryptionKey:

                logging.info('Attempting to decrypt with provided key...')
                logging.debug(f'Trying with key {encryptionKey}')
                self.passThrough = workingFolder + '\\decrypted.bin'
                decryptFile(inputFile, self.passThrough, encryptionKey, scryptN, scryptR, scryptP, removeInput=False)

                # Checking if password is valid
                if streamSHA == returnHashFromFile(self.passThrough):

                    logging.info('Successfully decrypted.')
                    self.isSatisfied = True

                else:

                    logging.info("Password incorrect, cannot continue.")
                    os.remove(self.passThrough)

            else:

                logging.warning(f'Decryption key missing from input argument, cannot continue.')

        else:

            logging.info('Encryption was not enabled on this stream.  Skipping step...')
            self.isSatisfied = True


class Decompressor:
    '''If compression was enabled on this stream, this object will decompress it.'''

    def __init__(self, workingFolder, passThrough, compressionEnabled):

        self.passThrough = passThrough

        if compressionEnabled:
            newPath = workingFolder + "\\decompressed.dat"
            logging.info('Decompressing file...')
            decompressFile(self.passThrough, newPath)
            self.passThrough = newPath
            logging.info('Successfully decompressed.')

        else:
            logging.info('Compression was not enabled on this stream.  Skipping step...')


class Unpackager:
    '''This object takes the decompressed binary and 'unpackages' it into the files and/or folders embedded in it.'''

    def __init__(self, passThrough, outputPath, streamSHA):

        if outputPath == None:
            printedSaveLocation = 'program run folder'

        else:
            printedSaveLocation = outputPath

        logging.info(f'Unpackaging file(s) at {printedSaveLocation}...')

        unpackage(passThrough, outputPath, streamSHA)
        logging.info('File(s) successfully unpackaged.')
