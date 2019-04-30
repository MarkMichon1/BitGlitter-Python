import logging

from bitglitter.protocols.protocol_one.read.protocol_one_postprocessobjects import Decryptor, Decompressor, Unpackager


class PostProcessor:
    def __init__(self, outputPath, streamSHA, workingFolder, encryptionEnabled, encryptionKey, scryptN, scryptR,
                 scryptP, compressionEnabled):
        '''Upon successfully assembly of the stream, PostProcessor performs the final steps required to output the
        files- decrypting and decompressing the stream if they were enabled, and then finally unpackaging the files.
        '''

        self.FullyAssembled = False

        decryptor = Decryptor(workingFolder, encryptionEnabled, encryptionKey, scryptN, scryptR,
                 scryptP, streamSHA)
        self.isDecrypted = decryptor

        if decryptor.isSatisfied == True:
            decompressor = Decompressor(workingFolder, decryptor.passThrough, compressionEnabled)
            unpackager = Unpackager(decompressor.passThrough, outputPath, streamSHA)
            self.FullyAssembled = True
            logging.info('Postprocess complete.')
