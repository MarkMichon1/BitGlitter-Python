import logging
from pathlib import Path

from bitglitter.config.settingsmanager import settings_manager
from bitglitter.validation.utilities import is_valid_directory, is_int_over_zero, proper_string_syntax, \
    is_bool


def verify_read_parameters(input_path, output_path, encryption_key, scrypt_n, scrypt_r, scrypt_p,
                           block_height_override, block_width_override, max_cpu_cores):
    """This function verifies the arguments going into read() to ensure they comform with the required format for
    processing.
    """

    logging.info("Verifying read parameters...")

    path = Path(input_path)
    if not path.is_absolute():
        raise ValueError('Write argument input_path must be an absolute path to the file or directory.')
    if not os.path.isfile(input_path):
        raise ValueError(f'file_to_input argument {input_path} must be a file.')

    if os.path.splitext(input_path)[1] not in VALID_VIDEO_FORMATS and \
            os.path.splitext(input_path)[1] not in VALID_IMAGE_FORMATS:
        raise ValueError(f'file_to_input argument {input_path} is not a valid format.  Only the following are '
                         f'allowed: {VALID_IMAGE_FORMATS}, and {VALID_VIDEO_FORMATS}')

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

    logging.info("Read parameters validated.")
