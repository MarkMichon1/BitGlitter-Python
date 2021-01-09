import logging
from pathlib import Path

from bitglitter.config.palettemanager import palette_manager
from bitglitter.utilities.display import humanize_file_size
from bitglitter.validation.utilities import is_bool, is_int_over_zero, is_valid_directory, proper_string_syntax, \
    verify_write_params_output_mode, verify_write_params_scrypt
from bitglitter.validation.validatepalette import palette_geometry_verify


def verify_write_params_render_values(stream_palette_id, pixel_width, block_height, block_width, frames_per_second,
                                      output_mode, preset_validation):
    # is stream_palette valid?  We're simultaneously setting up a variable for a geometry just check below.

    if stream_palette_id in palette_manager.DEFAULT_PALETTE_LIST:
        stream_palette = palette_manager.DEFAULT_PALETTE_LIST[stream_palette_id]
    elif stream_palette_id in palette_manager.custom_palette_dict:
        stream_palette = palette_manager.custom_palette_dict[stream_palette_id]
    elif stream_palette_id in palette_manager.custom_palette_nickname_dict:
        stream_palette = palette_manager.custom_palette_nickname_dict[stream_palette_id]
    else:
        raise ValueError(f"Stream palette {stream_palette_id} in write() is not a valid ID or nickname.  Verify that"
                         f" exact value exists.")

    is_int_over_zero('pixel_width', pixel_width)
    is_int_over_zero('block_height', block_height)
    is_int_over_zero('block_width', block_width)
    is_int_over_zero('frames_per_second', frames_per_second)

    if frames_per_second != 30 and frames_per_second != 60:
        raise ValueError("frames_per_second must either be 30 or 60 at this time (we're working on this!)")

    if block_width < 5 or block_height < 5:
        raise ValueError('Frames cannot be less than 5 blocks tall or wide.')

    if block_width * block_height < 1500:
        raise ValueError(f'Frames must have more than 1500 blocks, this current config has'
                         f' {block_width * block_height}')

    # TEMPORARY until issue is fixed
    if output_mode == 'video' and stream_palette_id == '24':
        raise ValueError("24 bit palettes can not be used with videos at this time due to codec issues.  This is"
                         "\nbeing worked on and will be restored soon!  This palette will still work on images.")

    # With the given dimensions and bit length, is it sufficient?
    payload_frame_percentage, bits_available_per_frame, output_per_sec = palette_geometry_verify(
                                                                        stream_palette.bit_length, block_width,
                                                                        block_height, output_mode, frames_per_second)
    if not preset_validation:
        logging.info(f'{humanize_file_size(bits_available_per_frame)}, or ~{payload_frame_percentage}% of payload '
                     f'frames are allocated for the payload itself (higher is better)')

        if output_mode == 'video':
            logging.info(f'As a video, it will effectively be transporting '
                         f'{humanize_file_size(round(output_per_sec / 8))}/sec of data.')
        logging.info('Minimum geometry requirements met.')


def write_parameter_validate(input_path, stream_name, stream_description, stream_output_path, output_name,
                             file_mask_enabled, encryption_key, max_cpu_cores=None, output_mode=None,
                             compression_enabled=None, scrypt_n=None, scrypt_r=None, scrypt_p=None,
                             stream_palette_id=None, pixel_width=None, block_height=None,
                             block_width=None, frames_per_second=None, preset_used=False):
    """This function verifies all write() parameters.  Look at this as the gatekeeper that stops invalid arguments from
     proceeding through the process, potentially breaking the stream (or causing BitGlitter to crash).
    """
    logging.info("Verifying write parameters...")

    path = Path(input_path)
    if not path.is_absolute():
        raise ValueError('Write argument input_path must be an absolute path to the file or directory.')
    if not path.exists():
        raise FileNotFoundError('File or directory for input_path does not exist.')

    if not preset_used:
        verify_write_params_render_values(stream_palette_id, pixel_width, block_height, block_width, frames_per_second,
                                          output_mode, preset_validation=False)
        verify_write_params_output_mode(output_mode)
        is_bool('compression_enabled', compression_enabled)
        verify_write_params_scrypt(scrypt_n, scrypt_r, scrypt_p)

    proper_string_syntax(stream_name, 'stream_name')
    proper_string_syntax(stream_description, 'stream_description')
    proper_string_syntax(output_name, 'output_name')
    is_bool('file_mask_enabled', file_mask_enabled)
    if not encryption_key and file_mask_enabled:
        raise ValueError('file_mask_enabled can only be set to True if an encryption key is provided.')

    if stream_output_path:
        is_valid_directory('stream_output_path', stream_output_path)
    verify_write_params_output_mode(output_mode)
    logging.info("Write parameters validated.")

    if not isinstance(max_cpu_cores, int) or max_cpu_cores < 0:
        raise ValueError('max_cpu_cores must be an integer greater than or equal to 0.')


def write_preset_validate(nickname, output_mode, compression_enabled, scrypt_n, scrypt_r, scrypt_p, max_cpu_cores,
                          stream_palette_id, pixel_width, block_height, block_width, frames_per_second):
    """Validates presets in a nice clean way."""

    if not isinstance(nickname, str):
        raise ValueError('Nickname for preset must be type str.')

    if not isinstance(max_cpu_cores, int):
        raise ValueError('cpu_cores for preset must be type int.')

    is_bool('compression_enabled', compression_enabled)
    verify_write_params_output_mode(output_mode)
    verify_write_params_render_values(stream_palette_id, pixel_width, block_height, block_width,
                                      frames_per_second, output_mode, preset_validation=True)
    verify_write_params_scrypt(scrypt_n, scrypt_r, scrypt_p)
