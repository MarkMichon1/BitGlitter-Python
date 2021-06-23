import logging
import os
from pathlib import Path

from bitglitter.config.del_pending_palettes import palette_manager
from bitglitter.config.settingsmanager import settings_manager
from bitglitter.validation.utilities import is_valid_directory, is_int_over_zero, proper_string_syntax, \
    is_bool


def verify_read_parameters(file_path, output_path, encryption_key, scrypt_n, scrypt_r, scrypt_p,
                           block_height_override, block_width_override, max_cpu_cores, stream_palette_id_override,
                           save_statistics):
    """This function verifies the arguments going into read() to ensure they comform with the required format for
    processing.
    """

    logging.info("Verifying read parameters...")

    path = Path(file_path)
    if not path.is_absolute():
        raise ValueError('Write argument input_path must be an absolute path to the file or directory.')
    if not os.path.isfile(file_path):
        raise ValueError(f'file_to_input argument {file_path} must be a file.')

    file_format = os.path.splitext(file_path)[1]
    if file_format in settings_manager.VALID_VIDEO_FORMATS:
        logging.debug(f'Video detected: {file_format}')
        input_type = 'video'
    elif file_format in settings_manager.VALID_IMAGE_FORMATS:
        logging.debug(f'Image detected: {file_format}')
        input_type = 'image'
    else:
        raise ValueError(f'input_file value {file_path} is not a valid format.  Only the following are '
                         f'allowed: {settings_manager.VALID_VIDEO_FORMATS}, and {settings_manager.VALID_IMAGE_FORMATS}')

    if output_path:
        is_valid_directory('file_to_input', output_path)

    proper_string_syntax('encryption_key', encryption_key)

    is_int_over_zero('scryptOverrideN', scrypt_n)
    is_int_over_zero('scryptOverrideR', scrypt_r)
    is_int_over_zero('scryptOverrideP', scrypt_p)

    is_int_over_zero('block_height_override', block_height_override)
    is_int_over_zero('block_width_override', block_width_override)

    if not isinstance(max_cpu_cores, int) or max_cpu_cores < 0:
        raise ValueError('max_cpu_cores must be an integer greater than or equal to 0.')

    if stream_palette_id_override:
        palette_manager.does_palette_exist(stream_palette_id_override)

    is_bool('save_statistics', save_statistics)

    logging.info("Read parameters validated.")
    return input_type