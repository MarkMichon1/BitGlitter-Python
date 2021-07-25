import json
import logging
import zlib

from bitstring import BitArray, BitStream, ConstBitStream
from PIL import ImageDraw

from bitglitter.utilities.compression import compress_bytes
from bitglitter.utilities.encryption import encrypt_bytes, get_sha256_hash_from_bytes


def metadata_header_process(file_mask_enabled, crypto_key, scrypt_n, scrypt_r, scrypt_p, bg_version, stream_name,
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


def custom_palette_header_process(palette):
    """This header is ran after the stream setup header whenever a custom palette is used for the stream."""

    adding_bits = BitStream()
    text_string_to_bytes = bytes('\\\\'.join([palette.palette_id, palette.name, palette.description,
                                              str(palette.time_created), palette.number_of_colors]), 'utf-8')
    adding_bits.append(BitArray(text_string_to_bytes))
    for color in palette.convert_colors_to_tuple():
        for rgb_color_channel in color:
            adding_bits.append(BitArray(uint=rgb_color_channel, length=8))
    to_bytes = bytes(adding_bits)
    raw_header_hash_bytes = get_sha256_hash_from_bytes(to_bytes, byte_output=True)

    compressed_header_bytes = compress_bytes(to_bytes)

    logging.debug('Palette initialization header generated.')
    return compressed_header_bytes, raw_header_hash_bytes


def stream_header_process(size_in_bytes, total_frames, compression_enabled, encryption_enabled,
                          file_mask_enabled, metadata_header, metadata_header_hash,
                          custom_palette_header, custom_palette_header_hash):
    """The stream header precedes the payload, and contains 2nd priority orientation data."""

    adding_bits = BitStream()

    adding_bits.append(BitArray(uint=size_in_bytes, length=64))
    adding_bits.append(BitArray(uint=total_frames, length=32))
    adding_bits.append(BitArray([int(compression_enabled), int(encryption_enabled),
                                 int(file_mask_enabled)]))

    adding_bits.append(BitArray(uint=len(metadata_header), length=32))
    adding_bits.append(BitArray(bytes=metadata_header_hash, length=256))

    adding_bits.append(BitArray(uint=len(custom_palette_header), length=10))
    if custom_palette_header_hash:
        adding_bits.append(BitArray(bytes=custom_palette_header_hash, length=256))
    else:
        adding_bits.append(BitArray(bytes=bytearray(256), length=256))
    to_bytes = bytes(adding_bits)
    crc_output = zlib.crc32(to_bytes)
    adding_bits.append(BitArray(uint=crc_output, length=32))

    assert len(adding_bits.bin) == 685

    logging.debug('Stream header generated.')
    return ConstBitStream(adding_bits)


def frame_header_process(frame_payload_bits, frame_number):
    """This is ran on the top of every frame (after the initializer if used) to give important information specifically
    for this frame, such as the area to scan, and the hash of the frame.
    """

    adding_bits = BitArray()
    adding_bits.append(BitArray(uint=len(frame_payload_bits), length=32))
    adding_bits.append(BitArray(uint=frame_number, length=32))
    byte_hash = get_sha256_hash_from_bytes(frame_payload_bits, byte_output=True)
    adding_bits.append(BitArray(bytes=byte_hash, length=256))

    full_bit_string_to_hash = adding_bits.bytes
    crc_output = zlib.crc32(full_bit_string_to_hash)
    adding_bits.append(BitArray(uint=crc_output, length=32))
    assert len(adding_bits.bin) == 352
    logging.debug('Frame header generated.')

    return adding_bits


def initializer_header_process(block_height, block_width, protocol_version, stream_palette, stream_sha256):
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

    logging.debug('Initialization header generated.')

    assert len(adding_bits.bin) == 580
    return adding_bits


def calibrator_header_process(image, block_height, block_width, pixel_width, initializer_palette_dict,
                              initializer_palette_dict_b):
    """This creates the checkboard-like pattern along the top and left of the first frame of video streams, and every
    frame of image streams.  This is what the reader uses to initially lock onto the frame.  Stream block_width and
    block_height are encoded into this pattern, using alternating color palettes so no two repeating values produce a
    continuous block of color, interfering with the frame lock process."""

    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, pixel_width - 1, pixel_width - 1),
                   fill='rgb(0,0,0)')

    block_width_encoded = BitArray(uint=block_width, length=block_width - 1)
    block_width_encoded.reverse()
    readable_block_width = ConstBitStream(block_width_encoded)

    for i in range(block_width - 1):
        next_bit = readable_block_width.read('bits : 1')

        if i % 2 == 0:
            color_value = initializer_palette_dict_b.get_color(ConstBitStream(next_bit))

        else:
            color_value = initializer_palette_dict.get_color(ConstBitStream(next_bit))

        draw.rectangle((pixel_width * i + pixel_width,
                        0,
                        pixel_width * (i + 1) - 1 + pixel_width,
                        pixel_width - 1),
                       fill=f'rgb{str(color_value)}')

    block_height_encoded = BitArray(uint=block_height, length=block_height - 1)
    block_height_encoded.reverse()
    readable_block_height = ConstBitStream(block_height_encoded)

    for i in range(block_height - 1):
        next_bit = readable_block_height.read('bits : 1')

        if i % 2 == 0:
            color_value = initializer_palette_dict_b.get_color(ConstBitStream(next_bit))

        else:
            color_value = initializer_palette_dict.get_color(ConstBitStream(next_bit))

        draw.rectangle((0,
                        pixel_width * i + pixel_width,
                        pixel_width - 1,
                        pixel_width * (i + 1) - 1 + pixel_width),
                       fill=f'rgb{str(color_value)}')

    return image
