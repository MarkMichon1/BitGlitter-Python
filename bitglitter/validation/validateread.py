import logging
import os
from pathlib import Path

from bitglitter.config.config import session
from bitglitter.config.configmodels import Constants
from bitglitter.validation.utilities import is_valid_directory, is_int_over_zero, proper_string_syntax, \
    is_bool


def _file_path_validate(file_path, type_requirement, video_formats, image_formats):
    path = Path(file_path)
    if not path.is_absolute():
        raise ValueError('Write argument input_path must be an absolute path to the file or directory.')
    if not os.path.isfile(file_path):
        raise ValueError(f'file_to_input argument {file_path} must be a file.')

    file_format = os.path.splitext(file_path)[1]

    if file_format in video_formats:
        if type_requirement == 'image':
            raise ValueError('Lists can only accept image files for input_file, videos must be decoded one at a time,'
                             ' using type string.')
        logging.debug(f'Video detected: {file_format}')
        input_type = 'video'
    elif file_format in image_formats:
        logging.debug(f'Image detected: {file_format}')
        input_type = 'image'
    else:
        if type_requirement == 'all':
            raise ValueError(f'input_file value {file_path} is not a valid format.  Only the following are allowed: '
                             f'{video_formats}, and {image_formats}')
        elif type_requirement == 'image':
            raise ValueError(f'input_file value {file_path} is not a valid format.  Only the following are allowed for'
                             f'lists: {image_formats}')

    return input_type


def validate_read_parameters(file_path, output_path, encryption_key, scrypt_n, scrypt_r, scrypt_p,
                             block_height_override, block_width_override, max_cpu_cores, save_statistics,
                             bad_frame_strikes, stop_at_metadata_load, auto_unpackage_stream,
                             auto_delete_finished_stream):
    """This function verifies the arguments going into read() to ensure they comform with the required format for
    processing.
    """

    logging.debug("Validating read parameters...")
    constants = session.query(Constants).first()

    valid_video_formats = constants.return_valid_video_formats()
    valid_image_formats = constants.return_valid_image_formats()

    if isinstance(file_path, str):  # Single video or image file to decode
        path = Path(file_path)
        if not path.is_dir():
            input_type = _file_path_validate(file_path, 'all', valid_video_formats, valid_image_formats)
        else:
            input_type = 'image'
    elif isinstance(file_path, list):  # Multiple images
        for path in file_path:
            input_type = _file_path_validate(path, 'image', valid_video_formats, valid_image_formats)
    else:
        raise ValueError('file_path can only accept strings for single video file or a directory (with images inside), '
                         'or list of string for image frames.')

    if output_path:
        is_valid_directory('file_to_input', output_path)

    proper_string_syntax('encryption_key', encryption_key)

    is_int_over_zero('bad_frame_strikes', bad_frame_strikes)

    is_int_over_zero('scrypt_n', scrypt_n)
    is_int_over_zero('scrypt_r', scrypt_r)
    is_int_over_zero('scrypt_p', scrypt_p)

    is_int_over_zero('block_height_override', block_height_override)
    is_int_over_zero('block_width_override', block_width_override)

    if not isinstance(max_cpu_cores, int) or max_cpu_cores < 0:
        raise ValueError('max_cpu_cores must be an integer greater than or equal to 0.')

    is_bool('save_statistics', save_statistics)
    is_bool('stop_at_metadata_load', stop_at_metadata_load)
    is_bool('auto_unpackage_stream', auto_unpackage_stream)
    is_bool('auto_delete_finished_stream', auto_delete_finished_stream)
    logging.debug("Read parameters validated.")

    return input_type
