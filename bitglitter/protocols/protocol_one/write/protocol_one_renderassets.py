import hashlib
import logging
import math
import os
import zlib

from bitstring import BitArray, BitStream, ConstBitStream
from PIL import ImageDraw

from bitglitter.palettes.paletteutilities import palette_grabber, ValuesToColor


def ascii_header_process(file_mask_enabled, active_path, stream_palette, bg_version, stream_name, stream_description,
                         post_encryption_hash, encryption_enabled):
    '''This takes all ASCII elements of the stream header, and returns a formatted merged string.'''

    if file_mask_enabled:
        file_list_string = ""

    else:
        with open(active_path + "\\file_list.txt", 'r') as text_file:
            file_list_string = text_file.read()

        os.remove(active_path + '\\file_list.txt')

    custom_palette_string = ""
    if stream_palette.palette_type == 'custom':
        custom_palette_attribute_list = [stream_palette.name, stream_palette.description,
                                      str(stream_palette.date_created), str(stream_palette.color_set)]
        custom_palette_string = "\\\\".join(custom_palette_attribute_list) + "\\\\"

    crypto_string = ""
    if encryption_enabled:
        crypto_string = post_encryption_hash + "\\\\"

    meta_data_string = "\\\\" + "\\\\".join([bg_version, stream_name, stream_description, file_list_string]) + "\\\\"

    merged_string = "".join([meta_data_string, custom_palette_string, crypto_string])
    logging.debug(f'ASCII Stream Header merged: {merged_string}')

    # Next, we're compressing it
    compressed_stream_header = zlib.compress(merged_string.encode(), level=9)
    compressed_file_size = len(compressed_stream_header)
    logging.debug(f'ASCII Stream Header compressed. ({len(merged_string)} B -> {compressed_file_size} B)')

    return compressed_stream_header


def generate_stream_header_binary_preamble(size_in_bytes, total_frames, compression_enabled, encryption_enabled,
                                           file_mask_enabled, is_stream_palette_custom, date_created, stream_palette_id,
                                           ascii_compressed_length):
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

    adding_bits.append(BitArray(uint=ascii_compressed_length, length=32))

    logging.debug('streamHeader generated.')
    return ConstBitStream(adding_bits)


def generate_frame_header(stream_sha, frame_hashable_bits, frame_number, blocks_used):
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


def how_many_frames(block_height, block_width, ascii_compressed_size, size_in_bytes, stream_palette, header_palette,
                    output_mode):
    '''This method returns how many frames will be required to complete the rendering process.'''

    logging.debug("Calculating how many frames to render...")

    total_blocks = block_height * block_width
    stream_header_overhead_in_bits = 422 + (ascii_compressed_size * 8)
    stream_size_in_bits = (size_in_bytes * 8)
    header_bit_length = header_palette.bit_length
    stream_bit_length = stream_palette.bit_length

    # Overhead constants
    initializer_overhead = block_height + block_width + 323
    frame_header_overhead = 608

    data_left = stream_size_in_bits
    frame_number = 0
    stream_header_bits_left = stream_header_overhead_in_bits  # subtract until zero

    while stream_header_bits_left:

        bits_consumed = frame_header_overhead
        blocks_left = total_blocks
        blocks_left -= (initializer_overhead * int(output_mode == 'image' or frame_number == 0))

        stream_header_bits_available = (blocks_left * header_bit_length) - frame_header_overhead

        if stream_header_bits_left >= stream_header_bits_available:
            stream_header_bits_left -= stream_header_bits_available

        else: # stream_header_combined terminates on this frame
            stream_header_bits_available -= stream_header_bits_left
            bits_consumed += stream_header_bits_left
            stream_header_bits_left = 0

            stream_header_blocks_used = math.ceil(bits_consumed / header_palette.bit_length)
            attachment_bits = header_palette.bit_length - (bits_consumed % header_palette.bit_length)

            if attachment_bits > 0:
                data_left -= attachment_bits

            remaining_blocks_left = blocks_left - stream_header_blocks_used
            leftover_frame_bits = remaining_blocks_left * header_bit_length

            if leftover_frame_bits > data_left:
                data_left = 0

            else:
                data_left -= leftover_frame_bits

        frame_number += 1

    # Calculating how much data can be embedded in a regular frame_payload frame, and returning the total frame count
    # needed.
    blocks_left = total_blocks - (initializer_overhead * int(output_mode == 'image'))
    payload_bits_per_frame = (blocks_left * stream_bit_length) - frame_header_overhead

    total_frames = math.ceil(data_left / payload_bits_per_frame) + frame_number
    logging.info(f'{total_frames} frame(s) required for this operation.')
    return total_frames


def generate_initializer(block_height, block_width, protocol_version, header_palette):
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


def render_calibrator(image, block_height, block_width, pixel_width):
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


def loop_generator(block_height, block_width, pixel_width, initializer_enabled):
    '''This generator yields the coordinates for each of the blocks used, depending on the geometry of the frame.'''

    for yRange in range(block_height - int(initializer_enabled)):
        for xRange in range(block_width - int(initializer_enabled)):
            yield ((pixel_width * int(initializer_enabled)) + (pixel_width * xRange),
                   (pixel_width * int(initializer_enabled)) + (pixel_width * yRange),
                   (pixel_width * int(initializer_enabled)) + (pixel_width * (xRange + 1) - 1),
                   (pixel_width * int(initializer_enabled)) + (pixel_width * (yRange + 1) - 1))