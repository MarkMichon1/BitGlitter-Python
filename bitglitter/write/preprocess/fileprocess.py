import json
import logging
import os
from pathlib import Path
import time

from bitglitter.utilities.compression import compress_bytes
from bitglitter.utilities.encryption import encrypt_bytes, get_hash_from_bytes, get_hash_from_file


def directory_crawler(directory_path, processed_path, compression_enabled, crypto_key, scrypt_n,
                      scrypt_r, scrypt_p):
    logging.info(f'Exploring {directory_path}...')
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
            returned_manifest = process_file(file, processed_path, crypto_key, scrypt_n, scrypt_r, scrypt_p,
                                              compression_enabled)
            file_manifests.append(returned_manifest)
        manifest['f'] = file_manifests

    directory_manifests = []
    if subdirectories:
        for subdirectory in subdirectories:
            returned_manifest =  directory_crawler(subdirectory, processed_path, compression_enabled, crypto_key,
                                                   scrypt_n, scrypt_r, scrypt_p)
            directory_manifests.append(returned_manifest)
        manifest['s'] = directory_manifests

    return manifest


def process_file(file_abs_path, processed_path, crypto_key, scrypt_n, scrypt_r, scrypt_p, compression_enabled):
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

    with open(processed_path, 'ab') as byte_write:
        with open(file_abs_path, 'rb') as file_read:
            file_data = file_read.read()
            if compression_enabled or crypto_key:
                if compression_enabled:
                    file_data = compress_bytes(file_data)
                if crypto_key:
                    file_data = encrypt_bytes(file_data, crypto_key, scrypt_n, scrypt_r, scrypt_p)
                processed_file_size = len(file_data)
                processed_file_hash = get_hash_from_bytes(file_data)
                manifest['ps'] = processed_file_size
                manifest['ph'] = processed_file_hash

            byte_write.write(file_data)
    return manifest


# dir_path = Path('/home/m/Desktop/test')
# processed_path = Path('/home/m/Desktop/testing.bin')
# returned_manifest = directory_crawler(dir_path, processed_path, True, 'testing', 14, 8, 1)
# print(returned_manifest) todo remove