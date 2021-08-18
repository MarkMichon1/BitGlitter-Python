import logging
import os

from bitglitter.utilities.compression import compress_file
from bitglitter.utilities.encryption import encrypt_file, get_hash_from_file


def directory_crawler(directory_path, payload_directory, compression_enabled, crypto_key, scrypt_n,
                      scrypt_r, scrypt_p):
    logging.info(f'Scanning {directory_path}...')
    manifest = {}
    # Directory keys:
    # n = directory name
    # f = files in that directory (not including subdirectories)
    # s = subdirectories (only accessible from the given directory, not subdirectories of subdirectories)

    manifest['n'] = directory_path.name

    files = []
    subdirectories = []
    sorted_glob = sorted(directory_path.glob('*'))
    for item in sorted_glob:
        if item.is_file():
            files.append(item)
        else:
            subdirectories.append(item)

    file_manifests = []
    if files:
        for file in files:
            returned_manifest = process_file(file, payload_directory, crypto_key, scrypt_n, scrypt_r, scrypt_p,
                                             compression_enabled)
            file_manifests.append(returned_manifest)
        manifest['f'] = file_manifests

    directory_manifests = []
    if subdirectories:
        for subdirectory in subdirectories:
            returned_manifest = directory_crawler(subdirectory, payload_directory, compression_enabled, crypto_key,
                                                  scrypt_n, scrypt_r, scrypt_p)
            directory_manifests.append(returned_manifest)
        manifest['s'] = directory_manifests

    return manifest


def process_file(file_abs_path, payload_directory, crypto_key, scrypt_n, scrypt_r, scrypt_p, compression_enabled):
    manifest = {}
    # File keys:
    # fn = file name
    # rs = raw file size
    # rh = raw file hash
    # ps = processed file size (only if compression or crypto)
    # ph = processed file hash (only if compression or crypto)

    file_name = file_abs_path.name
    manifest['fn'] = file_name
    logging.info(f'Found: {file_name}')
    raw_file_size = file_abs_path.stat().st_size
    manifest['rs'] = raw_file_size
    raw_file_hash = get_hash_from_file(file_abs_path)
    manifest['rh'] = raw_file_hash

    if compression_enabled or crypto_key:

        if compression_enabled:
            compressed_file_path = payload_directory / 'temp_compressed.bin'
            compress_file(file_abs_path, compressed_file_path, 'write', remove_input=False)
            active_processing_path = compressed_file_path
        if crypto_key:
            encrypted_file_path = payload_directory / 'temp_encrypted.bin'
            if compression_enabled:
                encrypt_file(compressed_file_path, encrypted_file_path, 'write', crypto_key, scrypt_n, scrypt_r,
                             scrypt_p, remove_input=True)
            else:
                encrypt_file(file_abs_path, encrypted_file_path, 'write', crypto_key, scrypt_n, scrypt_r, scrypt_p,
                             remove_input=False)
            active_processing_path = encrypted_file_path

        processed_file_size = active_processing_path.stat().st_size
        processed_file_hash = get_hash_from_file(active_processing_path)
        manifest['ps'] = processed_file_size
        manifest['ph'] = processed_file_hash
    else:
        active_processing_path = file_abs_path

    stream_payload_write_path = payload_directory / 'processed.bin'

    with open(stream_payload_write_path, 'ab') as byte_write:
        with open(active_processing_path, 'rb') as byte_read:
            chunk_size = 1000000
            while True:
                chunk = byte_read.read(chunk_size)
                if chunk:
                    byte_write.write(chunk)
                else:
                    break
    if compression_enabled or crypto_key:
        os.remove(active_processing_path)

    return manifest
