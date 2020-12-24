import hashlib
import os

from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def encrypt_file(input_file, output_file, write_mode, encryption_key, scrypt_n=14, scrypt_r=8, scrypt_p=1,
                 remove_input=True):
    """Taking an input file as well as the ASCII encryption key, the file is encrypted with AES-256, and outputted to
    output_file.  The input file is removed by default.
    """
    if write_mode == 'write':
        mode = 'wb'
    elif write_mode == 'append':
        mode = 'ab'
    else:
        raise ValueError('\'write\' and \'append\' are the only allowed strings for write_mode.')

    backend = default_backend()
    initialization_vector = os.urandom(AES.block_size // 8)
    salt = os.urandom(AES.block_size // 8)
    key = _derive_key(encryption_key, salt, scrypt_n, scrypt_r, scrypt_p, backend)

    with open(output_file, mode) as encrypted:
        with open(input_file, 'rb') as decrypted:
            encrypted.write(initialization_vector)
            encrypted.write(salt)

            chunk_size = 1048576
            while True:
                chunk = decrypted.read(chunk_size)
                if chunk:
                    encrypted.write(_encrypt_bytes_chunk(key, initialization_vector, chunk, backend,
                                                         chunk_size=chunk_size))
                else:
                    break

    if remove_input:
        os.remove(input_file)


def encrypt_bytes(input_bytes, encryption_key, scrypt_n, scrypt_r, scrypt_p):
    backend = default_backend()
    initialization_vector_aes = os.urandom(AES.block_size // 8)
    salt = os.urandom(AES.block_size // 8)

    encrypted_bytes = b''
    encrypted_bytes += initialization_vector_aes
    encrypted_bytes += salt
    encrypted_bytes += _encrypt_bytes_chunk(_derive_key(encryption_key, salt, scrypt_n, scrypt_r, scrypt_p,
                                                        backend), initialization_vector_aes, input_bytes, backend)

    return encrypted_bytes


def decrypt_file(input_file, output_file, encryption_key, scrypt_n=14, scrypt_r=8, scrypt_p=1,
                 remove_input=True):
    """Taking an input file as well as an encryption key, this function decrypts and saves the file."""

    backend = default_backend()
    with open(output_file, 'wb') as decrypted:
        with open(input_file, 'rb') as encrypted:
            initialization_vector = encrypted.read(AES.block_size // 8)
            salt = encrypted.read(AES.block_size // 8)
            key = _derive_key(encryption_key, salt, scrypt_n, scrypt_r, scrypt_p, backend)
            chunk_size = 1048576
            while True:
                chunk = encrypted.read(chunk_size)
                if chunk:
                    decrypted.write(_decrypt_bytes_chunk(key, initialization_vector, chunk, backend,
                                                         chunk_size=chunk_size))
                else:
                    break

    if remove_input:
        os.remove(input_file)


def decrypt_bytes():
    pass  # todo


def _encrypt_bytes_chunk(key, initialization_vector, data, backend, chunk_size=None):
    """This is an internal function used in encrypt_file(), and for future functionality of this program.  It returns
    32 bytes of encrypted data.
    """

    cipher = Cipher(AES(key), modes.CBC(initialization_vector), backend=backend)
    padder = PKCS7(AES.block_size).padder()
    encryptor = cipher.encryptor()
    if len(data) == chunk_size:
        return encryptor.update(padder.update(data))
    else:
        return encryptor.update(padder.update(data) + padder.finalize()) + encryptor.finalize()


def _decrypt_bytes_chunk(key, initialization_vector_aes, data, backend, chunk_size=None):
    """This is an internal function used in decrypt_file(), and for future functionality of this program.  It returns
    32 bytes of decrypted data.
    """

    cipher = Cipher(AES(key), modes.CBC(initialization_vector_aes), backend=backend)
    unpadder = PKCS7(AES.block_size).unpadder()
    decryptor = cipher.decryptor()
    if len(data) == chunk_size:
        return unpadder.update(decryptor.update(data))
    else:
        return unpadder.update(decryptor.update(data) + decryptor.finalize()) + unpadder.finalize()


def _derive_key(password, salt, scrypt_n, scrypt_r, scrypt_p, backend):
    """This is an internal function used in encrypt_file() and decrypt_file() that creates the text based key, and
    returns a proper AES key in byte format.
    """

    kdf = Scrypt(salt=salt, length=32, n=2 ** scrypt_n, r=scrypt_r, p=scrypt_p,
                 backend=backend)
    return kdf.derive(password.encode())


def get_hash_from_file(file_path, byte_output=False):
    """Taking in a path to a file as an argument, it returns the SHA-256 hash of the file via a string."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file_to_hash:
        buffer = file_to_hash.read(100000)
        while len(buffer) > 0:
            sha256.update(buffer)
            buffer = file_to_hash.read(100000)
    if byte_output:
        return sha256.digest()
    else:
        return sha256.hexdigest()


def get_hash_from_bytes(input_bytes, byte_output=False):
    sha256 = hashlib.sha256()
    sha256.update(input_bytes)
    if byte_output:
        return sha256.digest()
    else:
        return sha256.hexdigest()


import pathlib
in_file = pathlib.Path('/home/m/Desktop/test.mp4')
out_file = pathlib.Path('/home/m/Desktop/encrypted.bin')
final = pathlib.Path('/home/m/Desktop/test2.mp4')
encrypt_file(in_file, out_file, 'write', 'thepass', 14, 8, 1, remove_input=False)
decrypt_file(out_file, final, 'thepass', 14, 8, 1, remove_input=False)