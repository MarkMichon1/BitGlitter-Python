import logging

from bitglitter.protocols.protocol_one.read.protocol_one_postprocessobjects import Decryptor, Decompressor, Unpackager


class PostProcessor:
    def __init__(self, output_path, stream_SHA, working_folder, encryption_enabled, encryption_key, scrypt_n, scrypt_r,
                 scrypt_p, compression_enabled):
        '''Upon successfully assembly of the stream, PostProcessor performs the final steps required to output the
        files- decrypting and decompressing the stream if they were enabled, and then finally unpackaging the files.
        '''

        self.fully_assembled = False

        decryptor = Decryptor(working_folder, encryption_enabled, encryption_key, scrypt_n, scrypt_r,
                              scrypt_p, stream_SHA)
        self.is_decrypted = decryptor

        if decryptor.is_satisfied == True:

            decompressor = Decompressor(working_folder, decryptor.pass_through, compression_enabled)
            unpackager = Unpackager(decompressor.pass_through, output_path, stream_SHA)
            self.fully_assembled = True
            logging.info('Postprocess complete.')
