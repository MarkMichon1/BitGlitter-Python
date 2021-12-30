import logging
from pathlib import Path
import time

from bitglitter.config.configmodels import CurrentJobState
from bitglitter.utilities.display import humanize_file_size
from bitglitter.utilities.cryptography import get_hash_from_file
from bitglitter.utilities.filemanipulation import refresh_directory, return_file_size
from bitglitter.write.preprocess.fileprocess import directory_crawler, process_file


class PreProcessor:
    """PreProcessor performs all necessary preparations for the file(s) to be written, prior to rendering.  After all
    files and directories to be rendered are processed and ready to go in a binary file, a few other attributes are
    processed such as stream size and hash, that will be added into the headers.
    """

    def __init__(self, working_directory, input_path, crypto_key, compression_enabled, scrypt_n, scrypt_r, scrypt_p):
        self.datetime_started = int(time.time())
        self.active_folder = refresh_directory(working_directory)
        self.encryption_enabled = True if crypto_key else False
        logging.info("Preprocess initializing...")

        input_path = Path(input_path)
        if input_path.is_file():
            self.manifest = process_file(input_path, working_directory, crypto_key, scrypt_n, scrypt_r,
                                         scrypt_p, compression_enabled)
        else:
            self.manifest = directory_crawler(input_path, working_directory, compression_enabled, crypto_key,
                                              scrypt_n, scrypt_r, scrypt_p)

        self.processed_binary_path = working_directory / 'processed.bin'
        self.stream_sha256 = get_hash_from_file(self.processed_binary_path)
        logging.info(f"Stream SHA-256 Hash: {self.stream_sha256}")
        CurrentJobState.new_task(self.stream_sha256)
        self.size_in_bytes = return_file_size(self.processed_binary_path)
        logging.info(f'Pre-Processed Payload Size: {humanize_file_size(self.size_in_bytes)}')
        logging.debug(f'^ ({self.size_in_bytes} B)')
        logging.info("Preprocess complete.")
