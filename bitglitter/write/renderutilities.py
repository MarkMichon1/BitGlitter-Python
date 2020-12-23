import logging
import math

def total_frames_estimator(block_height, block_width, text_header, size_in_bytes, stream_palette, header_palette,
                           output_mode):
    '''This method returns how many frames will be required to complete the rendering process.'''

    logging.debug("Calculating how many frames to render...")

    total_blocks = block_height * block_width
    stream_header_overhead_in_bits = 678 + (len(text_header) * 8)
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


def loop_generator(block_height, block_width, pixel_width, initializer_enabled):
    '''This generator yields the coordinates for each of the blocks used, depending on the geometry of the frame.'''

    for yRange in range(block_height - int(initializer_enabled)):
        for xRange in range(block_width - int(initializer_enabled)):
            yield ((pixel_width * int(initializer_enabled)) + (pixel_width * xRange),
                   (pixel_width * int(initializer_enabled)) + (pixel_width * yRange),
                   (pixel_width * int(initializer_enabled)) + (pixel_width * (xRange + 1) - 1),
                   (pixel_width * int(initializer_enabled)) + (pixel_width * (yRange + 1) - 1))
