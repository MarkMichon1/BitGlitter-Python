import logging
import time

from bitglitter.protocols.protocol_one.write.protocol_one_preprocessobjects import Packager, Compressor, Encryptor
from bitglitter.utilities.filemanipulation import refresh_working_folder, return_file_size, return_hash_from_file


class PreProcessor:
    '''The PreProcessor object performs all necessary preparations for the file(s) to be written, prior to rendering.
    After packaging, and optional compression and encryption, it contains some attributes that will be encoded in
    headers during the render process.
    '''

    def __init__(self, active_path, file_list, crypto_key, mask_files, compression_enabled, scrypt_n, scrypt_r,
                 scrypt_p):

        logging.info("Preprocess initializing...")
        self.date_created = round(time.time())

        self.active_folder = refresh_working_folder(active_path)
        packager = Packager(self.active_folder, file_list, mask_files)
        compressor = Compressor(packager.pass_through, self.active_folder, compression_enabled)
        self.stream_sha = return_hash_from_file(compressor.pass_through)
        logging.info(f"SHA-256: {self.stream_sha}")
        encryptor = Encryptor(compressor.pass_through, self.active_folder, crypto_key, scrypt_n, scrypt_r,
                              scrypt_p)

        self.encryption_enabled = encryptor.encryption_enabled
        self.post_encryption_hash = None

        if crypto_key:
            self.post_encryption_hash = return_hash_from_file(encryptor.pass_through)
            logging.debug(f'Post-encryption SHA-256: {self.post_encryption_hash}')

        self.size_in_bytes = return_file_size(encryptor.pass_through)
        logging.info(f'Package size: {self.size_in_bytes}B')
        self.pass_through = encryptor.pass_through

        logging.info("Preprocess complete.")