import logging
import os

from bitglitter.config.constants import VALID_IMAGE_FORMATS, VALID_VIDEO_FORMATS
from bitglitter.utilities.generalverifyfunctions import is_valid_directory, is_int_over_zero, proper_string_syntax, \
    is_bool


def verify_read_parameters(file_to_input, output_path, encryption_key, scrypt_n, scrypt_r, scrypt_p,
                           block_height_override, block_width_override, assemble_hold):
    '''This function verifies the arguments going into read() to ensure they comform with the required format for
    processing.
    '''

    logging.info("Verifying read parameters...")

    if not os.path.isfile(file_to_input):
        raise ValueError(f'file_to_input argument {file_to_input} must be a file.')

    if os.path.splitext(file_to_input)[1] not in VALID_VIDEO_FORMATS and \
            os.path.splitext(file_to_input)[1] not in VALID_IMAGE_FORMATS:
        raise ValueError(f'file_to_input argument {file_to_input} is not a valid format.  Only the following are '
                         f'allowed: {VALID_IMAGE_FORMATS}, and {VALID_VIDEO_FORMATS}')

    if output_path:
        is_valid_directory('file_to_input', output_path)

    proper_string_syntax('encryption_key', encryption_key)

    is_int_over_zero('scryptOverrideN', scrypt_n)
    is_int_over_zero('scryptOverrideR', scrypt_r)
    is_int_over_zero('scryptOverrideP', scrypt_p)

    is_int_over_zero('block_height_override', block_height_override)
    is_int_over_zero('block_width_override', block_width_override)

    is_bool('assemble_hold', assemble_hold)

    logging.info("All read parameters within acceptable range.")