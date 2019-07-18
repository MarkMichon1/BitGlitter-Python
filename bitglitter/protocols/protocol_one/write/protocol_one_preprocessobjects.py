import logging
import os

from bitglitter.filepackager.filepackager import Folder, File, package
from bitglitter.utilities.filemanipulation import compress_file, encrypt_file


class Packager:
    '''Packager object takes all files and folders from argument file_list in write, and begins assembling them into a
    single package.dat file.  All arguments that aren't a file or folder are automatically discarded.
    '''

    def __init__(self, active_folder, file_list, mask_files):

        self.file_list = file_list
        root_folder = Folder(name='Root')
        logging.info("Preparing files for packaging...")
        invalid_input = False

        # If a string was used to denote a single file or file path, this automatically converts it into a tuple.
        if isinstance(file_list, str):
            file_list = (file_list,)

        for item in file_list:

            if os.path.isfile(item):
                logging.debug(f"Adding file: {item}")
                new_object = File(item)
                root_folder + new_object
                invalid_input = True

            if os.path.isdir(item):
                logging.debug(f"Adding folder: {item}")
                root_folder + Folder(file_path=item)
                invalid_input = True

        if invalid_input == False:
            raise ValueError("No valid files or folders were found from your file_list tuple in write()")

        self.pass_through = active_folder + '\\package.dat'

        logging.info("Packaging files...")
        package(root_folder, active_folder, mask_files)
        logging.info("Packaging complete.")


class Compressor:
    '''Compressor takes package.dat created from Packager and compresses the file, assuming compression_enabled == True.
    A hash of the file is taken as well at this point, if encryption_enabled == True.
    '''

    def __init__(self, pass_through, active_folder, compression_enabled):
        self.pass_through = pass_through
        self.pre_encryption_hash = ''

        if compression_enabled == True:
            logging.info('Compressing package...')
            self.new_name = active_folder + '\\compressed.dat'

            compress_file(self.pass_through, self.new_name)
            self.pass_through = self.new_name
            logging.info('Compression complete.')

        else:
            logging.info("Skipping compression.")


class Encryptor:
    '''Encryptor object applies encryption to the file being pre-processed if encryption_key has an argument.'''

    def __init__(self, pass_through, active_folder, encryption_key, scrypt_n,
                 scrypt_r, scrypt_p):
        self.pass_through = pass_through
        self._crypto_key = encryption_key

        if len(encryption_key) == 0:
            logging.info('Skipping encryption.')
            self.encryption_enabled = False

        else:
            new_name = active_folder + '\\encrypted.dat'
            logging.info('Encrypting package...')
            encrypt_file(self.pass_through, new_name, encryption_key, scrypt_n, scrypt_r, scrypt_p)
            logging.info('Encryption complete.')

            logging.debug(f"Removed {self.pass_through}")
            self.pass_through = new_name
            self.encryption_enabled = True