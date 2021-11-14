from zlib import crc32

from bitglitter.utilities.encryption import get_sha256_hash_from_bytes


def crc_verify(header):
    """This function takes in the payload, takes the CRC32 of it, then compares it to what
    is encoded.  Will return True or False depending on whether it matches.
    """

    header.pos = 0
    hashable_bits = header.read(f'bits : {len(header.bin) - 32}')
    converted_to_bytes = hashable_bits.tobytes()
    calculated_crc = crc32(converted_to_bytes)
    read_crc = header.read('uint : 32')
    return calculated_crc == read_crc


def sha256_verify(header, read_sha256):
    """Does the same as crc_verify, except with SHA-256, and an externally supplied hash (from stream header)"""
    header.pos = 0
    hashable_bits = header.read(f'bits : {len(header.bin) - 256}')
    converted_to_bytes = hashable_bits.tobytes()
    calculated_sha256 = get_sha256_hash_from_bytes(converted_to_bytes, byte_output=False)
    return calculated_sha256 == read_sha256
