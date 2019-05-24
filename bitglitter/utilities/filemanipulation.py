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

def compressFile(inputFile, outputFile, removeInput = True):
    '''This inputs a file, and writes a compressed one, removing the input file afterwards by default.'''

    with open(inputFile, 'rb') as processIn:
        with open(outputFile, 'wb') as processOut:
            with gzip.GzipFile(None, 'wb', fileobj=processOut, mtime=0.) as processOut:
                shutil.copyfileobj(processIn, processOut)

    if removeInput == True:
        os.remove(inputFile)


def decompressFile(inputFile, outputFile, removeInput = True):
    '''Doing the opposite as compressFile(), this inputs a compressed file, and writes a decompressed one, while
    removing the original file by default.
    '''

    with gzip.open(inputFile, 'rb') as processIn:
        with open(outputFile, 'wb') as processOut:
            shutil.copyfileobj(processIn, processOut)

    if removeInput == True:
        os.remove(inputFile)


def encryptFile(inputFile, outputFile, encryptionKey, scryptN = 14, scryptR = 8, scryptP = 1,
                removeInput = True):
    '''Taking an input file as well as the ASCII encryption key, the file is encrypted with AES-256, and outputted to
    outputFile.  The input file is removed by default.
    '''

    backend = default_backend()
    initializationVectorAES = os.urandom(AES.block_size // 8)
    salt = os.urandom(AES.block_size // 8)

    with open(outputFile, 'wb') as fileOut:
        with open(inputFile, 'rb') as fileIn:
            fileOut.write(initializationVectorAES)
            fileOut.write(salt)
            fileOut.write(_encryptBytes(_deriveKey(encryptionKey, salt, scryptN, scryptR, scryptP, backend),
                                         initializationVectorAES, fileIn.read(), backend))

    if removeInput == True:
        os.remove(inputFile)


def decryptFile(inputFile, outputFile, encryptionKey, scryptN = 14, scryptR = 8, scryptP = 1, removeInput = True):
    '''Taking an input file as well as an encryption key, this function decrypts and saves the file.'''

    backend = default_backend()
    with open(outputFile, 'wb') as fileOut:
        with open(inputFile, 'rb') as fileIn:
            iv = fileIn.read(AES.block_size // 8)
            salt = fileIn.read(AES.block_size // 8)
            fileOut.write(_decryptBytes(_deriveKey(encryptionKey, salt, scryptN, scryptR, scryptP, backend), iv,
                                            fileIn.read(), backend))

    if removeInput == True:
        os.remove(inputFile)


def _encryptBytes(key, initializationVector, data, backend):
    '''This is an internal function used in encryptFile(), and for future functionality of this program.  It returns
    32 bytes of encrypted data.
    '''

    cipher = Cipher(AES(key), modes.CBC(initializationVector), backend=backend)
    padder = PKCS7(AES.block_size).padder()
    encryptor = cipher.encryptor()
    return encryptor.update(padder.update(data) + padder.finalize()) + encryptor.finalize()


def _decryptBytes(key, initializationVectorAES, data, backend):
    '''This is an internal function used in dercryptFile(), and for future functionality of this program.  It returns
    32 bytes of decrypted data.
    '''

    cipher = Cipher(AES(key), modes.CBC(initializationVectorAES), backend=backend)
    unpadder = PKCS7(AES.block_size).unpadder()
    decryptor = cipher.decryptor()
    return unpadder.update(decryptor.update(data) + decryptor.finalize()) + unpadder.finalize()


def _deriveKey(password, salt, scryptN, scryptR, scryptP, backend):
    '''This is an internal function used in encryptFile() and decryptFile() that creates the text based key, and returns
    a proper AES key in byte format.
    '''

    kdf = Scrypt(salt=salt, length=32, n=2 ** scryptN, r=scryptR, p=scryptP,
                 backend=backend)
    return kdf.derive(password.encode())


def returnHashFromFile(passThrough):
    '''Taking in a path to a file as an argument, it returns the SHA-256 hash of the file via a string.'''

    sha256 = hashlib.sha256()
    with open(passThrough, 'rb') as fileToHash:
        buffer = fileToHash.read(100000)
        while len(buffer) > 0:
            sha256.update(buffer)
            buffer = fileToHash.read(100000)
    return sha256.hexdigest()


def refreshWorkingFolder(activePath):
    '''While the temporary folder after write gets automatically deleted, things such as abrupt stops can prevent that
    from happening.  This removes the folder if it is present, and then creates a few one for the next write cycle.
    This runs in the beginning of preProcess.
    '''
    activeFolder = os.path.join(os.getcwd(), activePath)

    if os.path.isdir(activePath):
        shutil.rmtree(activePath)
        logging.debug(f"activePath folder '{activePath}' already exists.  Deleting...")

    os.mkdir(activePath)
    logging.debug(f"Temp folder '{activePath}' created.")
    return activeFolder


def returnFileSize(passThrough):
    '''This is taking the final size of the pre-processed file, and this number will be used in the rendering process.
    '''

    size = os.path.getsize(passThrough)
    return size


def formatFileList(fileString):
    '''This takes in the file manifest inside of the stream header, and prints it in a nice formatted way.'''

    brokenApart = fileString.split('|')[1:]
    for position in range(int(len(brokenApart) / 2)):
        print(f"    {brokenApart[2 * position]} - {brokenApart[2 * position + 1]} B")