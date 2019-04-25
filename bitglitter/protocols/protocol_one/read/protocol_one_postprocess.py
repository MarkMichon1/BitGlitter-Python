import logging

from bitglitter.protocols.protocol_one.read.protocol_one_postprocessobjects import Decryptor, Decompressor, Unpackager


class PostProcessor:
    def __init__(self, outputPath, streamSHA, workingFolder, encryptionEnabled, encryptionKey, scryptN, scryptR,
                 scryptP, compressionEnabled):
        '''Upon successfully assembly of the stream, PostProcessor performs the final steps required to output the
        files- decrypting and decompressing the stream if they were enabled, and then finally unpackaging the files.
        '''

        # The first thing we need to do is check to ensure this is the right file.
        #setup output folder

        decryptor = Decryptor(workingFolder, encryptionEnabled, encryptionKey, scryptN, scryptR,
                 scryptP, streamSHA)

        if decryptor.isSatisfied == True:
            decompressor = Decompressor(workingFolder, decryptor.passThrough, compressionEnabled)
            unpackager = Unpackager(decompressor.passThrough, outputPath, streamSHA)
            logging.info('Postprocess complete.')