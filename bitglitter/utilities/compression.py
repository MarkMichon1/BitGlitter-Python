import os
import zlib


def compress_file(input_file, output_file, write_mode, remove_input=True):
    """This inputs a file, and writes a compressed one, removing the input file afterwards by default."""
    if write_mode == 'write':
        mode = 'wb'
    elif write_mode == 'append':
        mode = 'ab'
    else:
        raise ValueError('\'write\' and \'append\' are the only allowed strings for write_mode.')

    compressor = zlib.compressobj(9)
    with open(input_file, 'rb') as decompressed:
        with open(output_file, mode) as compressed:
            chunk_size = 1000000
            while True:
                chunk = decompressed.read(chunk_size)
                if chunk:
                    compressed.write(compressor.compress(chunk))
                else:
                    compressed.write(compressor.flush())
                    break

    if remove_input:
        os.remove(input_file)


def compress_bytes(input_bytes):
    compressed = zlib.compress(input_bytes, level=9)
    return compressed


def decompress_file(input_file, output_file, remove_input=True):
    """Doing the opposite as compress_file(), this inputs a compressed file, and writes a decompressed one, while
    removing the original file by default.
    """

    decompressor = zlib.decompressobj()
    with open(input_file, 'rb') as compressed:
        with open(output_file, 'wb') as decompressed:
            chunk_size = 1000000
            while True:
                chunk = compressed.read(chunk_size)
                if chunk:
                    decompressed.write(decompressor.decompress(chunk))
                else:
                    decompressed.write(decompressor.flush())
                    break

    if remove_input:
        os.remove(input_file)


def decompress_bytes(input_bytes):
    decompressed = zlib.decompress(input_bytes)
    return decompressed
