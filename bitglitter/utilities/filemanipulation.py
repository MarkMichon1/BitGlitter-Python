import hashlib
import gzip
import logging
import os
import shutil

from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

def compress_file(input_file, output_file, remove_input = True):
    '''This inputs a file, and writes a compressed one, removing the input file afterwards by default.'''

    with open(input_file, 'rb') as process_in:
        with open(output_file, 'wb') as process_out:
            with gzip.GzipFile(None, 'wb', fileobj=process_out, mtime=0.) as process_out:
                shutil.copyfileobj(process_in, process_out)

    if remove_input == True:
        os.remove(input_file)


def decompress_file(input_file, output_file, remove_input = True):
    '''Doing the opposite as compress_file(), this inputs a compressed file, and writes a decompressed one, while
    removing the original file by default.
    '''

    with gzip.open(input_file, 'rb') as process_in:
        with open(output_file, 'wb') as process_out:
            shutil.copyfileobj(process_in, process_out)

    if remove_input == True:
        os.remove(input_file)


def encrypt_file(input_file, output_file, encryption_key, scrypt_n = 14, scrypt_r = 8, scrypt_p = 1,
                 remove_input = True):
    '''Taking an input file as well as the ASCII encryption key, the file is encrypted with AES-256, and outputted to
    output_file.  The input file is removed by default.
    '''

    backend = default_backend()
    initialization_vector_aes = os.urandom(AES.block_size // 8)
    salt = os.urandom(AES.block_size // 8)

    with open(output_file, 'wb') as file_out:
        with open(input_file, 'rb') as file_in:
            file_out.write(initialization_vector_aes)
            file_out.write(salt)
            file_out.write(_encrypt_bytes(_derive_key(encryption_key, salt, scrypt_n, scrypt_r, scrypt_p, backend),
                                          initialization_vector_aes, file_in.read(), backend))

    if remove_input == True:
        os.remove(input_file)


def decrypt_file(input_file, output_file, encryption_key, scrypt_n = 14, scrypt_r = 8, scrypt_p = 1,
                 remove_input = True):
    '''Taking an input file as well as an encryption key, this function decrypts and saves the file.'''

    backend = default_backend()
    with open(output_file, 'wb') as file_out:
        with open(input_file, 'rb') as file_in:
            iv = file_in.read(AES.block_size // 8)
            salt = file_in.read(AES.block_size // 8)
            file_out.write(_decrypt_bytes(_derive_key(encryption_key, salt, scrypt_n, scrypt_r, scrypt_p, backend), iv,
                                          file_in.read(), backend))

    if remove_input == True:
        os.remove(input_file)


def _encrypt_bytes(key, initialization_vector, data, backend):
    '''This is an internal function used in encrypt_file(), and for future functionality of this program.  It returns
    32 bytes of encrypted data.
    '''

    cipher = Cipher(AES(key), modes.CBC(initialization_vector), backend=backend)
    padder = PKCS7(AES.block_size).padder()
    encryptor = cipher.encryptor()
    return encryptor.update(padder.update(data) + padder.finalize()) + encryptor.finalize()


def _decrypt_bytes(key, initialization_vector_aes, data, backend):
    '''This is an internal function used in dercryptFile(), and for future functionality of this program.  It returns
    32 bytes of decrypted data.
    '''

    cipher = Cipher(AES(key), modes.CBC(initialization_vector_aes), backend=backend)
    unpadder = PKCS7(AES.block_size).unpadder()
    decryptor = cipher.decryptor()
    return unpadder.update(decryptor.update(data) + decryptor.finalize()) + unpadder.finalize()


def _derive_key(password, salt, scrypt_n, scrypt_r, scrypt_p, backend):
    '''This is an internal function used in encrypt_file() and decrypt_file() that creates the text based key, and
    returns a proper AES key in byte format.
    '''

    kdf = Scrypt(salt=salt, length=32, n=2 ** scrypt_n, r=scrypt_r, p=scrypt_p,
                 backend=backend)
    return kdf.derive(password.encode())


def return_hash_from_file(pass_through):
    '''Taking in a path to a file as an argument, it returns the SHA-256 hash of the file via a string.'''

    sha256 = hashlib.sha256()
    with open(pass_through, 'rb') as file_to_hash:
        buffer = file_to_hash.read(100000)
        while len(buffer) > 0:
            sha256.update(buffer)
            buffer = file_to_hash.read(100000)
    return sha256.hexdigest()


def refresh_working_folder(active_path):
    '''While the temporary folder after write gets automatically deleted, things such as abrupt stops can prevent that
    from happening.  This removes the folder if it is present, and then creates a few one for the next write cycle.
    This runs in the beginning of preProcess.
    '''
    activeFolder = os.path.join(os.getcwd(), active_path)

    if os.path.isdir(active_path):
        shutil.rmtree(active_path)
        logging.debug(f"active_path folder '{active_path}' already exists.  Deleting...")

    os.mkdir(active_path)
    logging.debug(f"Temp folder '{active_path}' created.")
    return activeFolder


def return_file_size(pass_through):
    '''This is taking the final size of the pre-processed file, and this number will be used in the rendering process.
    '''

    size = os.path.getsize(pass_through)
    return size


def format_file_list(file_string):
    '''This takes in the file manifest inside of the stream header, and prints it in a nice formatted way.'''

    broken_apart = file_string.split('|')[1:]
    for position in range(int(len(broken_apart) / 2)):
        print(f"    {broken_apart[2 * position]} - {broken_apart[2 * position + 1]} B")