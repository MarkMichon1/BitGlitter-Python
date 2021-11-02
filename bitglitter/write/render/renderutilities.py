from bitstring import ConstBitStream
import cv2
import numpy

import logging
import math
from pathlib import Path

from bitglitter.write.render.headerencode import calibrator_header_render


def total_frames_estimator(block_height, block_width, metadata_header_length, palette_header_length, size_in_bytes,
                           stream_palette, output_mode):
    """This method returns how many frames will be required to complete the rendering process."""

    logging.debug("Calculating how many frames to render...")

    # Constants
    TOTAL_BLOCKS_PER_FRAME = block_height * block_width
    CALIBRATOR_BLOCK_OVERHEAD = block_height + block_width - 1
    INITIALIZER_BIT_OVERHEAD = 580
    FRAME_HEADER_BIT_OVERHEAD = 352
    STREAM_HEADER_BIT_OVERHEAD = 685
    pre_stream_data_left_bits = STREAM_HEADER_BIT_OVERHEAD + ((palette_header_length + metadata_header_length) * 8)
    logging.info(f'palette_header_length {palette_header_length} metadata_header_length {metadata_header_length}')
    payload_data_left_bits = size_in_bytes * 8
    STREAM_PALETTE_BIT_LENGTH = stream_palette.bit_length

    total_frames = 1

    while pre_stream_data_left_bits:
        remaining_blocks_this_frame = TOTAL_BLOCKS_PER_FRAME - FRAME_HEADER_BIT_OVERHEAD - ((INITIALIZER_BIT_OVERHEAD +
                                         CALIBRATOR_BLOCK_OVERHEAD) * int(total_frames == 1 or output_mode == 'image'))
        if remaining_blocks_this_frame < pre_stream_data_left_bits:
            pre_stream_data_left_bits -= remaining_blocks_this_frame
            total_frames += 1
        else:
            remaining_blocks_this_frame -= pre_stream_data_left_bits
            pre_stream_data_left_bits = 0
            payload_data_left_bits = max(0, payload_data_left_bits - (remaining_blocks_this_frame *
                                                                      STREAM_PALETTE_BIT_LENGTH))

    if payload_data_left_bits:
        remaining_blocks = TOTAL_BLOCKS_PER_FRAME - ((INITIALIZER_BIT_OVERHEAD + CALIBRATOR_BLOCK_OVERHEAD)
                                                     * int(output_mode == 'image'))
        payload_bits_per_frame = (remaining_blocks * STREAM_PALETTE_BIT_LENGTH) - FRAME_HEADER_BIT_OVERHEAD
        total_frames += math.ceil(payload_data_left_bits / payload_bits_per_frame)

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
    stream_name_file_output = dict_obj['stream_name_file_output']
    stream_name = dict_obj['stream_name']
    initializer_enabled = dict_obj['initializer_enabled']
    frame_number = dict_obj['frame_number']
    total_frames = dict_obj['total_frames']
    image_output_path = dict_obj['image_output_path']
    stream_sha256 = dict_obj['stream_sha256']
    save_statistics = dict_obj['save_statistics']

    logging.debug(f'Rendering {frame_number} of {total_frames} ...')
    image = numpy.zeros((pixel_width * block_height, pixel_width * block_width, 3), dtype='uint8')

    if initializer_enabled:
        image = calibrator_header_render(image, block_height, block_width, pixel_width, initializer_palette_dict,
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

        # With the color loaded, we'll get the coordinates of the next block (top left + bottom corner), and draw it in.
        block_coordinates = next(next_coordinates)
        cv2.rectangle(image, (block_coordinates[0], block_coordinates[1]), (block_coordinates[2], block_coordinates[3]),
                      (color_value[2], color_value[1], color_value[0]), -1)
        block_position += 1

    # Frames get saved as .png files.
    frame_number_to_string = str(frame_number)

    if output_mode == 'video':
        file_name = frame_number_to_string

    else:
        if stream_name_file_output:
            file_name = stream_name + ' - ' + str(frame_number)
        else:
            file_name = stream_sha256 + ' - ' + str(frame_number)

    # save_path = Path(image_output_path / f'{str(file_name)}.png')
    cv2.imwrite(str(Path(image_output_path / f'{str(file_name)}.png')), image)

    # Ensure every bit in payload is accounted for.
    assert frame_payload.len == frame_payload.bitpos

    if save_statistics:
        from bitglitter.config.configfunctions import write_stats_update
        if frame_number != total_frames:
            blocks_wrote = block_height * block_width
        else:
            blocks_wrote = block_position
        write_stats_update(blocks_wrote, 1, int(frame_payload.len / 8))
