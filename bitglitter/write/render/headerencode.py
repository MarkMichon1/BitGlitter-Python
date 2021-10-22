import json
import logging
import zlib

from bitstring import BitArray, BitStream, ConstBitStream
import cv2

from bitglitter.utilities.compression import compress_bytes
from bitglitter.utilities.encryption import encrypt_bytes, get_sha256_hash_from_bytes


def calibrator_header_render(image, block_height, block_width, pixel_width, initializer_palette_dict,
                             initializer_palette_dict_b):
    """This creates the checkboard-like pattern along the top and left of the first frame of video streams, and every
    frame of image streams.  This is what the reader uses to initially lock onto the frame.  Stream block_width and
    block_height are encoded into this pattern, using alternating color palettes so no two repeating values produce a
    continuous block of color, interfering with the frame lock process."""

    cv2.rectangle(image, (0, 0), (pixel_width - 1, pixel_width - 1), (0, 0, 0), -1)

    block_width_encoded = BitArray(uint=block_width, length=block_width - 1)
    block_width_encoded.reverse()
    readable_block_width = ConstBitStream(block_width_encoded)

    for i in range(block_width - 1):
        next_bit = readable_block_width.read('bits : 1')

        if i % 2 == 0:
            color_value = initializer_palette_dict_b.get_color(ConstBitStream(next_bit))

        else:
            color_value = initializer_palette_dict.get_color(ConstBitStream(next_bit))

        cv2.rectangle(image,
                      (pixel_width * i + pixel_width, 0),
                      (pixel_width * (i + 1) - 1 + pixel_width, pixel_width - 1),
                      (color_value[2], color_value[1], color_value[0]), -1)

    block_height_encoded = BitArray(uint=block_height, length=block_height - 1)
    block_height_encoded.reverse()
    readable_block_height = ConstBitStream(block_height_encoded)

    for i in range(block_height - 1):
        next_bit = readable_block_height.read('bits : 1')

        if i % 2 == 0:
            color_value = initializer_palette_dict_b.get_color(ConstBitStream(next_bit))

        else:
            color_value = initializer_palette_dict.get_color(ConstBitStream(next_bit))

        cv2.rectangle(image,
                      (0, pixel_width * i + pixel_width),
                      (pixel_width - 1, pixel_width * (i + 1) - 1 + pixel_width),
                      (color_value[2], color_value[1], color_value[0]), -1)

    return image


def initializer_header_encode(block_height, block_width, protocol_version, stream_palette, stream_sha256):
    """This generates the initializer header, which is present in black and white colors on the top of the first frame
    of video streams, and every frame of image streams.  It provides import information on stream geometry as well as
    protocol version and what palettes are being used.
    """

    logging.debug('Generating initialization header...')

    adding_bits = BitArray()
    adding_bits.append(BitArray(uint=protocol_version, length=4))
    adding_bits.append(BitArray(uint=block_height, length=16))
    adding_bits.append(BitArray(uint=block_width, length=16))

    if not stream_palette.is_custom:
        adding_bits.append(BitArray(uint=int(stream_palette.palette_id), length=256))
    else:
        adding_bits.append(BitArray(hex=stream_palette.palette_id))

    adding_bits.append(BitArray(bytes=stream_sha256, length=256))

    full_bit_string_to_hash = adding_bits.tobytes()
    crc_output = zlib.crc32(full_bit_string_to_hash)
    adding_bits.append(BitArray(uint=crc_output, length=32))
    assert len(adding_bits.bin) == 580
    logging.debug('Initialization header generated.')

    return adding_bits


def frame_header_encode(frame_payload_bytes, unpadded_bit_length, frame_number):
    """This is ran on the top of every frame (after the initializer if used) to give important information specifically
    for this frame, such as how many bits to scan, frame number, and its SHA-256 hash.
    """

    adding_bits = BitArray()
    adding_bits.append(BitArray(uint=unpadded_bit_length, length=32))
    adding_bits.append(BitArray(uint=frame_number, length=32))
    byte_hash = get_sha256_hash_from_bytes(frame_payload_bytes, byte_output=True)
    adding_bits.append(BitArray(bytes=byte_hash, length=256))

    full_bit_string_to_hash = adding_bits.tobytes()
    crc_output = zlib.crc32(full_bit_string_to_hash)
    adding_bits.append(BitArray(uint=crc_output, length=32))
    assert len(adding_bits.bin) == 352
    logging.debug('Frame header generated.')

    return adding_bits


def stream_header_encode(size_in_bytes, total_frames, compression_enabled, encryption_enabled,
                         file_mask_enabled, metadata_header_length, metadata_header_hash,
                         custom_palette_header_length, custom_palette_header_hash):
    """The stream header precedes the payload, and contains 2nd priority orientation data."""

    adding_bits = BitStream()

    adding_bits.append(BitArray(uint=size_in_bytes, length=64))
    adding_bits.append(BitArray(uint=total_frames, length=32))
    adding_bits.append(BitArray([int(compression_enabled), int(encryption_enabled),
                                 int(file_mask_enabled if encryption_enabled else False)]))

    adding_bits.append(BitArray(uint=metadata_header_length, length=32))
    adding_bits.append(BitArray(bytes=metadata_header_hash, length=256))

    adding_bits.append(BitArray(uint=custom_palette_header_length, length=10))
    if custom_palette_header_hash:
        adding_bits.append(BitArray(bytes=custom_palette_header_hash, length=256))
    else:
        adding_bits.append(BitArray(bytes=bytearray(32), length=256))
    to_bytes = adding_bits.tobytes()
    crc_output = zlib.crc32(to_bytes)
    adding_bits.append(BitArray(uint=crc_output, length=32))

    assert len(adding_bits.bin) == 685

    logging.debug('Stream header generated.')
    return ConstBitStream(adding_bits)


def metadata_header_encode(file_mask_enabled, crypto_key, scrypt_n, scrypt_r, scrypt_p, bg_version, stream_name,
                           time_created, stream_description, manifest):
    """This header contains the file manifest, and other data not crucial for stream orientation."""

    logging.debug('Building metadata header...')
    json_manifest = json.dumps(manifest)
    logging.debug(f'JSON manifest: {json_manifest}')
    meta_data_string = "\\\\".join([bg_version, stream_name, stream_description, str(time_created), json_manifest])
    logging.debug(f'Text Header merged: {meta_data_string}')

    raw_header_to_bytes = bytes(meta_data_string, 'UTF-8')
    raw_header_hash_bytes = get_sha256_hash_from_bytes(raw_header_to_bytes, byte_output=True)
    processed_header_bytes = compress_bytes(raw_header_to_bytes)

    if file_mask_enabled and crypto_key:
        logging.debug('Encrypting metadata header...')
        processed_header_bytes = encrypt_bytes(processed_header_bytes, crypto_key, scrypt_n, scrypt_r, scrypt_p)

    logging.debug('Metadata header generated.')
    logging.debug(f'Processed metadata length: {len(processed_header_bytes)}')
    return processed_header_bytes, raw_header_hash_bytes


def custom_palette_header_encode(palette):
    """This header is ran after the stream setup header whenever a custom palette is used for the stream."""

    # adding_bits = BitStream()
    text_string_to_bytes = bytes('\\\\'.join([palette.palette_id, palette.name, palette.description,
                                              str(palette.time_created), str(palette.number_of_colors),
                                              str(palette.convert_colors_to_tuple())]), 'utf-8')

    raw_header_hash_bytes = get_sha256_hash_from_bytes(text_string_to_bytes, byte_output=True)
    compressed_header_bytes = compress_bytes(text_string_to_bytes)

    logging.debug('Palette initialization header generated.')
    return compressed_header_bytes, raw_header_hash_bytes
