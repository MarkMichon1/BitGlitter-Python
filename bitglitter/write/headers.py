import hashlib
import json
import logging
import zlib

from bitstring import BitArray, BitStream, ConstBitStream
from PIL import ImageDraw

from bitglitter.palettes.utilities import palette_grabber, ValuesToColor
from bitglitter.utilities.compression import compress_bytes
from bitglitter.utilities.encryption import encrypt_bytes, get_hash_from_bytes


def text_header_process(file_mask_enabled, crypto_key, scrypt_n, scrypt_r, scrypt_p, bg_version, stream_palette,
                        stream_name, stream_description, manifest):


    logging.debug('Building text header...')
    custom_palette_string = ""
    if stream_palette.palette_type == 'custom':
        custom_palette_attribute_list = [stream_palette.id, stream_palette.name, stream_palette.description,
                                         str(stream_palette.datetime_started), str(stream_palette.color_set)]
        custom_palette_string = "\\\\".join(custom_palette_attribute_list) + "\\\\"
    meta_data_string = "\\\\".join([stream_name, stream_description, bg_version])

    json_manifest = json.dumps(manifest)
    logging.debug(f'Manifest JSON:\n\n{json_manifest}')

    raw_header = "".join([meta_data_string, custom_palette_string, json_manifest])
    logging.debug(f'Text Header merged: {raw_header}')

    raw_header_to_bytes = bytes(raw_header, 'UTF-8')
    raw_header_hash_bytes = get_hash_from_bytes(raw_header_to_bytes, byte_output=True)

    processed_header = compress_bytes(raw_header_to_bytes)
    if file_mask_enabled and crypto_key:
        logging.debug('Encrypting...')
        processed_header = encrypt_bytes(processed_header, crypto_key, scrypt_n, scrypt_r, scrypt_p)

    logging.debug('Text header ready.')
    return processed_header, raw_header_hash_bytes


def stream_header_process(size_in_bytes, total_frames, compression_enabled, encryption_enabled,
                          file_mask_enabled, is_stream_palette_custom, date_created, stream_palette_id,
                          text_header_processed_length, raw_text_header_hash_bytes):
    '''The binary preamble for the Stream Header is created here.  For videos and images, this is only needed for the
    first frame.
    '''

    adding_bits = BitStream()

    adding_bits.append(BitArray(uint=size_in_bytes, length=64))
    adding_bits.append(BitArray(uint=total_frames, length=32))
    adding_bits.append(BitArray([int(compression_enabled), int(encryption_enabled),
                                 int(file_mask_enabled), is_stream_palette_custom]))
    adding_bits.append(BitArray(uint=date_created, length=34))

    if is_stream_palette_custom:
        adding_bits.append(BitArray(hex=stream_palette_id))

    else:
        adding_bits.append(BitArray(uint=int(stream_palette_id), length=256))

    adding_bits.append(BitArray(uint=text_header_processed_length, length=32))
    adding_bits.append(BitArray(bytes=raw_text_header_hash_bytes))

    assert len(bytes(adding_bits)) == 678

    logging.debug('streamHeader generated.')
    return ConstBitStream(adding_bits)


def frame_header_process(stream_sha, frame_hashable_bits, frame_number, blocks_used):
    '''This creates the header that is present at the beginning of every frame (excluding the first frame or image
    outputs).  These headers orient the reader, in that it tells it where it is in the stream.
    '''

    full_bit_string = BitArray()

    full_bit_string.append(BitArray(hex=stream_sha))
    temp_payload_holding = ConstBitStream(frame_hashable_bits)
    sha_hasher = hashlib.sha256()
    sha_hasher.update(temp_payload_holding.tobytes())
    frame_sha = sha_hasher.digest()

    full_bit_string.append(BitArray(bytes=frame_sha))
    full_bit_string.append(BitArray(uint=frame_number, length=32))
    full_bit_string.append(BitArray(uint=blocks_used, length=32))
    full_bit_string_to_hash = full_bit_string.bytes

    crc_output = zlib.crc32(full_bit_string_to_hash)
    full_bit_string.append(BitArray(uint=crc_output, length=32))

    return full_bit_string


def initializer_header_process(block_height, block_width, protocol_version, header_palette):
    '''This generates the initializer header, which is present in black and white colors on the top of the first frame
    of video streams, and every frame of image streams.  It provides import information on stream geometry as well as
    protocol version.
    '''

    full_bit_string = BitArray()
    full_bit_string.append(BitArray(uint=protocol_version, length=4))
    full_bit_string.append(BitArray(uint=block_height, length=16))
    full_bit_string.append(BitArray(uint=block_width, length=16))

    if header_palette.palette_type == 'default':
        full_bit_string.append(BitArray(uint=int(header_palette.id), length=256))

    else:
        full_bit_string.append(BitArray(hex=header_palette.id))

    full_bit_string_to_hash = full_bit_string.tobytes()
    crc_output = zlib.crc32(full_bit_string_to_hash)
    full_bit_string.append(BitArray(uint=crc_output, length=32))

    return full_bit_string


def calibrator_header_process(image, block_height, block_width, pixel_width):
    '''This creates the checkboard-like pattern along the top and left of the first frame of video streams, and every
    frame of image streams.  This is what the reader uses to initially lock onto the frame.  Stream block_width and
    block_height are encoded into this pattern, using alternating color palettes so no two repeating values produce a
    continuous block of color, interfering with the frame lock process.'''

    initializer_palette_dict_a = ValuesToColor(palette_grabber('1'), 'initializer_palette A')
    initializer_palette_dict_b = ValuesToColor(palette_grabber('11'), 'initializer_palette B')

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
            color_value = initializer_palette_dict_a.get_color(ConstBitStream(next_bit))

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
            color_value = initializer_palette_dict_a.get_color(ConstBitStream(next_bit))

        draw.rectangle((0,
                        pixel_width * i + pixel_width,
                        pixel_width - 1,
                        pixel_width * (i + 1) - 1 + pixel_width),
                       fill=f'rgb{str(color_value)}')

    return image
