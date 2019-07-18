import logging
import os

from bitglitter.filepackager.filepackager import unpackage
from bitglitter.utilities.filemanipulation import decrypt_file, return_hash_from_file, decompress_file


class Decryptor:
    '''This is the first step of the post-processing once assembly is complete.  This will take the assembled binary,
    and, if encryption was enabled on this stream, will attempt to decrypt it with the AES key provided.
    '''

    def __init__(self, working_folder, encryption_enabled, encryption_key, scrypt_n, scrypt_r, scrypt_p, stream_sha):

        input_file = working_folder + '\\assembled.bin'
        self.pass_through = input_file
        self.is_satisfied = False

        if encryption_enabled:

            if encryption_key:

                logging.info('Attempting to decrypt with provided key...')
                logging.debug(f'Trying with key {encryption_key}')
                self.pass_through = working_folder + '\\decrypted.bin'
                decrypt_file(input_file, self.pass_through, encryption_key, scrypt_n, scrypt_r, scrypt_p,
                             remove_input=False)

                # Checking if password is valid
                if stream_sha == return_hash_from_file(self.pass_through):

                    logging.info('Successfully decrypted.')
                    self.is_satisfied = True

                else:

                    logging.info("Password incorrect, cannot continue.")
                    os.remove(self.pass_through)

            else:

                logging.warning(f'Decryption key missing from input argument, cannot continue.')

        else:

            logging.info('Encryption was not enabled on this stream.  Skipping step...')
            self.is_satisfied = True


class Decompressor:
    '''If compression was enabled on this stream, this object will decompress it.'''

    def __init__(self, working_folder, pass_through, compression_enabled):

        self.pass_through = pass_through

        if compression_enabled:
            new_path = working_folder + "\\decompressed.dat"
            logging.info('Decompressing file...')
            decompress_file(self.pass_through, new_path)
            self.pass_through = new_path
            logging.info('Successfully decompressed.')

        else:
            logging.info('Compression was not enabled on this stream.  Skipping step...')


class Unpackager:
    '''This object takes the decompressed binary and 'unpackages' it into the files and/or folders embedded in it.'''

    def __init__(self, pass_through, output_path, stream_sha):

        if output_path == None:
            printed_save_location = 'program run folder'

        else:
            printed_save_location = output_path

        logging.info(f'Unpackaging file(s) at {printed_save_location}...')

        unpackage(pass_through, output_path, stream_sha)
        logging.info('File(s) successfully unpackaged.')
