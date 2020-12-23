import logging
import os
import string

from bitglitter.config.palettemanager import palette_manager
from bitglitter.utilities.display import humanize_file_size
from bitglitter.validation.validatepalette import palette_verify

def is_valid_directory(argument, path):
    '''Checks whether the inputted directory exists or not.'''
    if not os.path.isdir(path):
        raise ValueError(f'Folder path for {argument} does not exist.')


def is_int_over_zero(argument, some_variable):
    '''Checks if variable is of type int and is greater than zero.'''

    if not isinstance(some_variable, int) or some_variable < 0:
        raise ValueError(f"Argument {argument} must be an integer greater than zero.")


def proper_string_syntax(argument, inputted_string=""):
    '''This exists to verify various inputs are using allowed characters.  One such character that isn't allowed is
    '\\', as that character is what the ASCII part of the stream header uses to divide attributes.
    '''

    acceptable_chars = string.ascii_letters + string.digits + string.punctuation.replace("\\", "") + " "
    if inputted_string:
        for letter in inputted_string:
            if letter not in acceptable_chars:
                raise ValueError(f"Only ASCII characters excluding '\\' are allowed in {argument}.")


def is_bool(argument, variable):
    '''Will raise error if argument isn't type bool.  Used in verifying arguments for read() and write()'''
    if not isinstance(variable, bool):
        raise ValueError(f'Argument {argument} must be type boolean.')


def verify_write_params_output_mode(output_mode):
    if output_mode != 'video' and output_mode != 'image':
        raise ValueError("Argument output_mode in write() only accepts 'video' or 'image'.")


def verify_write_params_scrypt(scrypt_n, scrypt_r, scrypt_p):
    """Used both during """

    is_int_over_zero('scrypt_n', scrypt_n)
    is_int_over_zero('scrypt_r', scrypt_r)
    is_int_over_zero('scrypt_p', scrypt_p)


def verify_write_params_render_values(header_palette_id, stream_palette_id, pixel_width, block_height, block_width,
                                      frames_per_second, output_mode, preset_validation):

    # is stream_palette valid?  We're simultaneously setting up a variable for a geometry just check below.
    def does_palette_exist(palette, palette_type):
        if palette in palette_manager.DEFAULT_PALETTE_LIST:
            palette_to_return = palette_manager.DEFAULT_PALETTE_LIST[palette]
        elif palette in palette_manager.custom_palette_list:
            palette_to_return = palette_manager.custom_palette_list[palette]
        elif palette in palette_manager.custom_palette_nickname_list:
            palette_to_return = palette_manager.custom_palette_nickname_list[palette]
        else:
            raise ValueError(f"Argument {palette_type} in write() is not a valid ID or nickname.  Verify that exact "
                             f"value exists.")
        return palette_to_return

    active_header_palette = does_palette_exist(header_palette_id, 'header_palette')
    active_stream_palette = does_palette_exist(stream_palette_id, 'stream_palette')

    is_int_over_zero('pixel_width', pixel_width)
    is_int_over_zero('block_height', block_height)
    is_int_over_zero('block_width', block_width)
    is_int_over_zero('frames_per_second', frames_per_second)

    if frames_per_second != 30 and frames_per_second != 60:
        raise ValueError("frames_per_second must either be 30 or 60 at this time (we're working on this!)")

    if block_width < 17 or block_height < 17:
        raise ValueError('Minimum block dimensions are 17 width x 17 height.')

    # TEMPORARY until issue is fixed
    if output_mode == 'video':
        if header_palette_id == '24' or stream_palette_id == '24':
            raise ValueError("24 bit palettes can not be used with videos at this time due to codec issues.  This is"
                             "\nbeing worked on and will be restored soon!  This palette will still work on images.")

    # With the given dimensions and bit length, is it sufficient?
    returned_header_values = palette_verify('header_palette', active_header_palette.bit_length, block_width,
                                            block_height, output_mode, frames_per_second)
    logging.info(f'{returned_header_values[0]}% of the frame for initial header is allocated for frame payload (higher '
                 f'is better)')

    returned_stream_values = palette_verify('stream_palette', active_stream_palette.bit_length, block_width,
                                            block_height, output_mode, frames_per_second)
    if not preset_validation:
        logging.info(f'{humanize_file_size(returned_stream_values[1])}, or {returned_stream_values[0]}% of subsequent '
                     f'frames is allocated for frame payload (higher is better)')

        if output_mode == 'video':
            logging.info(f'As a video, it will effectively be transporting '
                         f'{humanize_file_size(round(returned_stream_values[2] / 8))}/sec of data.')
        logging.info('Minimum geometry requirements met.')


def logging_config_validate(logging_level, logging_stdout_output, logging_txt_output):
    acceptable_level_words = [False, 'debug', 'info']
    if logging_level not in acceptable_level_words:
        raise ValueError(f"{logging_level} is not a valid input for logging_level.  Only 'info', 'debug', and False are"
                         f" allowed.")

    if not isinstance(logging_stdout_output, bool):
        raise ValueError("Only booleans are allowed for logging_stdout_output.")

    if not isinstance(logging_txt_output, bool):
        raise ValueError("Only booleans are allowed for logging_txt_output.")