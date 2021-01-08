from bitstring import ConstBitStream
from PIL import Image, ImageDraw

import logging
import math
from pathlib import Path

from bitglitter.write.render.headers import calibrator_header_process


def total_frames_estimator(block_height, block_width, text_header, size_in_bytes, stream_palette, header_palette,
                           output_mode):
    """This method returns how many frames will be required to complete the rendering process."""

    logging.debug("Calculating how many frames to render...")

    TOTAL_BLOCKS = block_height * block_width
    STREAM_HEADER_OVERHEAD_IN_BITS = 678 + (len(text_header) * 8)
    STREAM_SIZE_IN_BITS = (size_in_bytes * 8)
    HEADER_BIT_LENGTH = header_palette.bit_length
    STREAM_BIT_LENGTH = stream_palette.bit_length

    # Overhead constants
    INITIALIZER_OVERHEAD = block_height + block_width + 323
    FRAME_HEADER_OVERHEAD = 608

    data_left = STREAM_SIZE_IN_BITS
    frame_number = 0
    stream_header_bits_left = STREAM_HEADER_OVERHEAD_IN_BITS  # subtract until zero

    while stream_header_bits_left:

        bits_consumed = FRAME_HEADER_OVERHEAD
        blocks_left = TOTAL_BLOCKS
        blocks_left -= (INITIALIZER_OVERHEAD * int(output_mode == 'image' or frame_number == 0))

        stream_header_bits_available = (blocks_left * HEADER_BIT_LENGTH) - FRAME_HEADER_OVERHEAD

        if stream_header_bits_left >= stream_header_bits_available:
            stream_header_bits_left -= stream_header_bits_available

        else:  # stream_header_combined terminates on this frame
            stream_header_bits_available -= stream_header_bits_left
            bits_consumed += stream_header_bits_left
            stream_header_bits_left = 0

            stream_header_blocks_used = math.ceil(bits_consumed / header_palette.bit_length)
            attachment_bits = header_palette.bit_length - (bits_consumed % header_palette.bit_length)

            if attachment_bits > 0:
                data_left -= attachment_bits

            remaining_blocks_left = blocks_left - stream_header_blocks_used
            leftover_frame_bits = remaining_blocks_left * HEADER_BIT_LENGTH

            if leftover_frame_bits > data_left:
                data_left = 0

            else:
                data_left -= leftover_frame_bits

        frame_number += 1

    # Calculating how much data can be embedded in a regular frame_payload frame, and returning the total frame count
    # needed.
    blocks_left = TOTAL_BLOCKS - (INITIALIZER_OVERHEAD * int(output_mode == 'image'))
    payload_bits_per_frame = (blocks_left * STREAM_BIT_LENGTH) - FRAME_HEADER_OVERHEAD
    total_frames = math.ceil(data_left / payload_bits_per_frame) + frame_number

    logging.info(f'{total_frames} frame(s) required for this operation.')
    return total_frames


def render_coords_generator(block_height, block_width, pixel_width, initializer_enabled):
    """This generator yields the coordinates for each of the blocks used, depending on the geometry of the frame."""

    for y_range in range(block_height - int(initializer_enabled)):
        for x_range in range(block_width - int(initializer_enabled)):
            yield ((pixel_width * int(initializer_enabled)) + (pixel_width * x_range),
                   (pixel_width * int(initializer_enabled)) + (pixel_width * y_range),
                   (pixel_width * int(initializer_enabled)) + (pixel_width * (x_range + 1) - 1),
                   (pixel_width * int(initializer_enabled)) + (pixel_width * (y_range + 1) - 1))


def draw_frame(dict_obj):
    # Unpacking dictionary object into variables to easier reading of function.  A single argument must be passed
    # here because multiprocessing's imap requires it.
    block_height = dict_obj['block_height']
    block_width = dict_obj['block_width']
    pixel_width = dict_obj['pixel_width']
    frame_payload = dict_obj['frame_payload']
    initializer_palette_blocks_used = dict_obj['initializer_palette_blocks_used']
    primary_frame_palette_dict = dict_obj['primary_frame_palette_dict']
    primary_read_length = dict_obj['primary_read_length']
    initializer_palette_dict = dict_obj['initializer_palette_dict']
    initializer_palette = dict_obj['initializer_palette']
    output_mode = dict_obj['output_mode']
    output_name = dict_obj['output_name']
    initializer_enabled = dict_obj['initializer_enabled']
    frame_number = dict_obj['frame_number']
    total_frames = dict_obj['total_frames']
    image_output_path = dict_obj['image_output_path']
    stream_sha = dict_obj['stream_sha']

    logging.debug(f'Rendering {frame_number} of {total_frames} ...')

    image = Image.new('RGB', (pixel_width * block_width, pixel_width * block_height), 'black')
    draw = ImageDraw.Draw(image)

    if initializer_enabled:
        image = calibrator_header_process(image, block_height, block_width, pixel_width)

    next_coordinates = render_coords_generator(block_height, block_width, pixel_width, initializer_enabled)
    block_position = 0
    while len(frame_payload) != frame_payload.bitpos:

        # Primary palette selection (ie, header_palette or stream_palette depending on where we are in the stream)
        if block_position >= initializer_palette_blocks_used:
            active_palette_dict, read_length = primary_frame_palette_dict, primary_read_length

        # Initializer palette selection
        elif block_position < initializer_palette_blocks_used:
            active_palette_dict, read_length = (initializer_palette_dict, initializer_palette.bit_length)

        # Here to signal something has broken.
        else:
            raise RuntimeError('Something has gone wrong in matching block position to palette.  This state'
                               '\nis reached only if something is broken.')

        # This is loading the next bit(s) to be written in the frame, and then converting it to an RGB value.
        next_bits = frame_payload.read(f'bits : {read_length}')
        color_value = active_palette_dict.get_color(ConstBitStream(next_bits))

        # With the color loaded, we'll get the coordinates of the next block (each corner), and draw it in.
        block_coordinates = next(next_coordinates)
        draw.rectangle((block_coordinates[0], block_coordinates[1], block_coordinates[2], block_coordinates[3]),
                       fill=f'rgb{str(color_value)}')

        block_position += 1

    # Frames get saved as .png files.
    frame_number_to_string = str(frame_number)

    if output_mode == 'video':
        file_name = frame_number_to_string.zfill(math.ceil(math.log(total_frames + 1, 10)))

    else:
        if output_name:
            file_name = output_name + ' - ' + str(frame_number)
        else:
            file_name = stream_sha + ' - ' + str(frame_number)

    save_path = Path(image_output_path / f'{str(file_name)}.png')
    image.save(save_path)

    return block_position