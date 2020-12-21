from pathlib import Path

import json
import logging
import time

from bitglitter.utilities.compression import compress_bytes
from bitglitter.utilities.display import humanize_file_size
from bitglitter.utilities.encryption import encrypt_bytes, get_hash_from_file
from bitglitter.utilities.filemanipulation import refresh_working_folder, return_file_size
from bitglitter.write.preprocess.file_process import directory_crawler, process_file


class PreProcessor:
    """PreProcessor performs all necessary preparations for the file(s) to be written, prior to rendering.  After all
    files and directories to be rendered are processed and ready to go in a binary file, a few other attributes are
    processed such as stream size and hash, that will be added into the headers.
    """

    def __init__(self, working_directory, input_path, crypto_key, mask_enabled, compression_enabled, scrypt_n, scrypt_r,
                 scrypt_p):
        self.datetime_started = round(time.time())
        self.active_folder = refresh_working_folder(working_directory)
        self.encryption_enabled = True if crypto_key else False
        logging.info("Preprocess initializing...")

        input_path = Path(input_path)
        self.processed_binary_path = working_directory / 'processed.bin'
        if input_path.is_file():
            self.manifest = process_file(input_path, self.processed_binary_path, crypto_key, scrypt_n, scrypt_r,
                                         scrypt_p, compression_enabled)
        else:
            self.manifest = directory_crawler(input_path, self.processed_binary_path, compression_enabled, crypto_key,
                                              scrypt_n, scrypt_r, scrypt_p)

        self.stream_sha = get_hash_from_file(self.processed_binary_path)
        logging.info(f"SHA-256: {self.stream_sha}")

        self.size_in_bytes = return_file_size(self.processed_binary_path)
        logging.info(f'Pre-processed payload size: {humanize_file_size(self.size_in_bytes)}')

        self.manifest = bytes(json.dumps(self.manifest), 'UTF-8')
        self.manifest = compress_bytes(self.manifest)
        if self.encryption_enabled and mask_enabled:
            logging.info('Encrypting manifest...')
            self.manifest = encrypt_bytes(self.manifest, crypto_key, scrypt_n, scrypt_r, scrypt_p)

        logging.info("Preprocess complete.")
