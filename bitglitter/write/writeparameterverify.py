import logging
from math import ceil

from bitglitter.config.config import config
from bitglitter.utilities.generalverifyfunctions import is_bool, is_valid_directory, is_int_over_zero, \
    proper_string_syntax

def palette_verify(header_type, bit_length, block_width, block_height, output_type, fps=0):
    '''This function calculates the necessary overhead for both images and videos for subsequent frames after 1.  It
    returns a number between 0-100%, for what percentage the overhead occupies.  The lower the value, the higher the
    frame efficiency.
    '''

    total_blocks = block_width * block_height

    block_overhead = block_height + block_width + 323
    frame_header_in_bits = 608

    blocks_needed = 0

    if header_type == 'header_palette' or output_type == 'image':
        blocks_needed += block_overhead

    bits_available = (total_blocks - blocks_needed) * bit_length
    bits_available -= frame_header_in_bits
    occupied_blocks = blocks_needed + ceil(frame_header_in_bits / bit_length)

    if occupied_blocks > total_blocks:
        raise ValueError(f"{header_type} has {occupied_blocks - total_blocks} too few blocks with this configuration."
                         f"\nPlease fix this by using a palette with a larger bitlength or use more blocks per frame.")

    output_per_sec = None
    if output_type == 'video' and header_type == 'stream_palette':
        output_per_sec = bits_available * fps

    return ((round(100 - (occupied_blocks / total_blocks * 100), 2)), bits_available, output_per_sec)


def verify_write_parameters(file_list, stream_name, stream_description, stream_output_path, output_mode, output_name,
                            compression_enabled, file_mask_enabled, scrypt_n, scrypt_r, scrypt_p, stream_palette,
                            header_palette, pixel_width, block_height, block_width, frames_per_second):
    '''This function verifies all write() parameters for Protocol v1.  Look at this as the gatekeeper that stops
    invalid arguments from proceeding through the process, potentially breaking the stream (or causing BitGlitter to
    crash).
    '''

    logging.info("Verifying write parameters...")

    if not file_list:
        raise FileNotFoundError("A minimum of one file or folder is required for stream creation for argument file_list"
                                " in write().")

    # TEMPORARY until issue is fixed
    if output_mode == 'video':
        if header_palette == '24' or stream_palette == '24':
            raise ValueError("24 bit palettes can not be used with videos at this time due to codec issues.  This is"
                             "\nbeing worked on and will be restored soon!  This palette will still work on images.")


    proper_string_syntax(stream_name, 'stream_name')
    proper_string_syntax(stream_description, 'stream_description')
    proper_string_syntax(output_name, 'output_name')

    if stream_output_path:
        is_valid_directory('stream_output_path', stream_output_path)

    if output_mode != 'video' and output_mode != 'image':
        raise ValueError("Argument output_mode in write() only accepts 'video' or 'image'.")

    is_bool('compression_enabled', compression_enabled)
    is_bool('file_mask_enabled', file_mask_enabled)

    is_int_over_zero('scrypt_n', scrypt_n)
    is_int_over_zero('scrypt_r', scrypt_r)
    is_int_over_zero('scrypt_p', scrypt_p)

    # is stream_palette valid?  We're simultaneously setting up a variable for a geometry just check below.
    def does_palette_exist(palette, type):
        if palette in config.color_handler.default_palette_list:
            palette_to_return = config.color_handler.default_palette_list[palette]
        elif palette in config.color_handler.custom_palette_list:
            palette_to_return = config.color_handler.custom_palette_list[palette]
        elif palette in config.color_handler.custom_palette_nickname_list:
            palette_to_return = config.color_handler.custom_palette_nickname_list[palette]
        else:
            raise ValueError(f"Argument {type} in write() is not a valid ID or nickname.  Verify that exact value "
                             "exists.")
        return palette_to_return

    active_header_palette = does_palette_exist(header_palette, 'header_palette')
    active_stream_palette = does_palette_exist(stream_palette, 'stream_palette')

    is_int_over_zero('pixel_width', pixel_width)
    is_int_over_zero('block_height', block_height)
    is_int_over_zero('block_width', block_width)
    is_int_over_zero('frames_per_second', frames_per_second)

    if frames_per_second != 30 and frames_per_second != 60:
        raise ValueError("frames_per_second must either be 30 or 60 at this time (we're working on this!)")

    if block_width < 17 or block_height < 17:
        raise ValueError('Minimum block dimensions for Protocol 1 are 17 x 17.')

    # With the given dimensions and bit length, is it sufficient?
    returned_header_values = palette_verify('header_palette', active_header_palette.bit_length, block_width,
                                            block_height, output_mode, frames_per_second)
    logging.info(f'{returned_header_values[0]}% of the frame for initial header is allocated for frame payload (higher '
                 f'is better)')

    returned_stream_values = palette_verify('stream_palette', active_stream_palette.bit_length, block_width,
                                            block_height, output_mode, frames_per_second)
    logging.info(f'{returned_stream_values[1]} B, or {returned_stream_values[0]}% of subsequent frames is allocated for'
                 f' frame payload (higher is better)')

    if output_mode == 'video':
        logging.info(f'As a video, it will effectively be transporting {round(returned_stream_values[2] / 8)} B/sec of'
                     f' data.')

    logging.info('Minimum geometry requirements met.')
    logging.info("Write parameters validated.")