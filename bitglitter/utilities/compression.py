import gzip
import os
import shutil
import zlib


def compress_file(input_file, output_file, remove_input=True):
    """This inputs a file, and writes a compressed one, removing the input file afterwards by default."""

    with open(input_file, 'rb') as process_in:
        with open(output_file, 'wb') as process_out:
            with gzip.GzipFile(None, 'wb', fileobj=process_out, mtime=0.) as process_out:
                shutil.copyfileobj(process_in, process_out)

    if remove_input:
        os.remove(input_file)


def compress_bytes(input_bytes):
    compressed = zlib.compress(input_bytes)
    return compressed


def decompress_file(input_file, output_file, remove_input=True):
    """Doing the opposite as compress_file(), this inputs a compressed file, and writes a decompressed one, while
    removing the original file by default.
    """

    with gzip.open(input_file, 'rb') as process_in:
        with open(output_file, 'wb') as process_out:
            shutil.copyfileobj(process_in, process_out)

    if remove_input:
        os.remove(input_file)


def decompress_bytes(input_bytes):
    decompressed = zlib.decompress(input_bytes)
    return decompressed
