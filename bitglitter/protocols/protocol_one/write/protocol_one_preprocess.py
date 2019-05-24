import logging
import time

from bitglitter.protocols.protocol_one.write.protocol_one_preprocessobjects import Packager, Compressor, Encryptor
from bitglitter.utilities.filemanipulation import refreshWorkingFolder, returnFileSize, returnHashFromFile


class PreProcessor:
    '''The PreProcessor object performs all necessary preparations for the file(s) to be written, prior to rendering.
    After packaging, and optional compression and encryption, it contains some attributes that will be encoded in
    headers during the render process.
    '''

    def __init__(self, activePath, fileList, cryptoKey, maskFiles, compressionEnabled, scryptOverrideN, scryptOverrideR,
                 scryptOverrideP):

        logging.info("Preprocess initializing...")
        self.dateCreated = round(time.time())

        self.activeFolder = refreshWorkingFolder(activePath)
        packager = Packager(self.activeFolder, fileList, maskFiles)
        compressor = Compressor(packager.passThrough, self.activeFolder, compressionEnabled)
        self.streamSHA = returnHashFromFile(compressor.passThrough)
        logging.info(f"SHA-256: {self.streamSHA}")
        encryptor = Encryptor(compressor.passThrough, self.activeFolder, cryptoKey, scryptOverrideN, scryptOverrideR,
                              scryptOverrideP)

        self.encryptionEnabled = encryptor.encryptionEnabled
        self.postEncryptionHash = None

        if cryptoKey:
            self.postEncryptionHash = returnHashFromFile(encryptor.passThrough)
            logging.debug(f'Post-encryption SHA-256: {self.postEncryptionHash}')

        self.sizeInBytes = returnFileSize(encryptor.passThrough)
        logging.info(f'Package size: {self.sizeInBytes}B')
        self.passThrough = encryptor.passThrough

        logging.info("Preprocess complete.")