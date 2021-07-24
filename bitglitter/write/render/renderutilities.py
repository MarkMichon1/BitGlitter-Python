from bitstring import ConstBitStream
from PIL import Image, ImageDraw

import logging
import math
from pathlib import Path

from bitglitter.write.render.headers import calibrator_header_process


def total_frames_estimator(block_height, block_width, metadata_header_length, palette_header_length, size_in_bytes,
                           stream_palette, output_mode):
    """This method returns how many frames will be required to complete the rendering process."""

    logging.debug("Calculating how many frames to render...")

    # Constants
    TOTAL_BLOCKS_PER_FRAME = block_height * block_width
    INITIALIZER_OVERHEAD = block_height + block_width + 835
    FRAME_HEADER_OVERHEAD = 352
    STREAM_SETUP_HEADER = 685
    pre_stream_palette_header_data_left = STREAM_SETUP_HEADER + palette_header_length + metadata_header_length
    payload_data_left = size_in_bytes * 8
    STREAM_PALETTE_BIT_LENGTH = stream_palette.bit_length

    total_frames = 1

    while pre_stream_palette_header_data_left:
        remaining_blocks_this_frame = TOTAL_BLOCKS_PER_FRAME - FRAME_HEADER_OVERHEAD - (INITIALIZER_OVERHEAD *
                                                                    int(total_frames == 1 or output_mode == 'image'))
        if remaining_blocks_this_frame < pre_stream_palette_header_data_left:
            pre_stream_palette_header_data_left -= remaining_blocks_this_frame
            total_frames += 1
        else:
            remaining_blocks_this_frame -= pre_stream_palette_header_data_left
            pre_stream_palette_header_data_left = 0
            payload_data_left = max(0, payload_data_left - (remaining_blocks_this_frame * STREAM_PALETTE_BIT_LENGTH))

    if payload_data_left:
        remaining_blocks = TOTAL_BLOCKS_PER_FRAME - (1 * output_mode == 'image')
        payload_bits_per_frame = (remaining_blocks * STREAM_PALETTE_BIT_LENGTH) - FRAME_HEADER_OVERHEAD
        total_frames += math.ceil(payload_data_left / payload_bits_per_frame)

    logging.info(f'{total_frames} frame(s) required for this write process.')
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
    """Unpacking dictionary object into variables for easier reading of function.  A single argument must be passed
    here because multiprocessing's imap requires it.
    """

    block_height = dict_obj['block_height']
    block_width = dict_obj['block_width']
    pixel_width = dict_obj['pixel_width']
    frame_payload = dict_obj['frame_payload']
    initializer_palette_blocks_used = dict_obj['initializer_palette_blocks_used']
    stream_palette_dict = dict_obj['stream_palette_dict']
    stream_palette_bit_length = dict_obj['stream_palette_bit_length']
    initializer_palette_dict = dict_obj['initializer_palette_dict']
    initializer_palette_dict_b = dict_obj['initializer_palette_dict_b']
    initializer_palette = dict_obj['initializer_palette']
    output_mode = dict_obj['output_mode']
    output_name = dict_obj['output_name']
    initializer_enabled = dict_obj['initializer_enabled']
    frame_number = dict_obj['frame_number']
    total_frames = dict_obj['total_frames']
    image_output_path = dict_obj['image_output_path']
    stream_sha = dict_obj['stream_sha']

    logging.debug(f'Rendering {frame_number} of {total_frames} ...')
    logging.debug(f'{frame_number} {frame_payload.len}')
    image = Image.new('RGB', (pixel_width * block_width, pixel_width * block_height), 'black')
    draw = ImageDraw.Draw(image)

    if initializer_enabled:
        image = calibrator_header_process(image, block_height, block_width, pixel_width, initializer_palette_dict,
                                          initializer_palette_dict_b)

    next_coordinates = render_coords_generator(block_height, block_width, pixel_width, initializer_enabled)
    block_position = 0
    while len(frame_payload) != frame_payload.bitpos:

        # Primary palette selection (ie, header_palette or stream_palette depending on where we are in the stream)
        if block_position >= initializer_palette_blocks_used:
            active_palette_dict, bit_read_length = stream_palette_dict, stream_palette_bit_length

        # Initializer palette selection
        elif block_position < initializer_palette_blocks_used:
            active_palette_dict, bit_read_length = (initializer_palette_dict, initializer_palette.bit_length)

        # Here to signal something has broken.
        else:
            raise RuntimeError('Something has gone wrong in matching block position to palette.  This state'
                               '\nis reached only if something is broken.')

        # This is loading the next bit(s) to be written in the frame, and then converting it to an RGB value.
        next_bits = frame_payload.read(f'bits : {bit_read_length}')
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

    # Ensure every bit in payload is accounted for.
    assert frame_payload.len == frame_payload.bitpos
    return {'block_position': block_position, 'frame_number': frame_number}
