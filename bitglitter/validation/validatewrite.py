import logging
from pathlib import Path

from bitglitter.config.palettefunctions import _return_palette
from bitglitter.utilities.display import humanize_file_size
from bitglitter.validation.utilities import is_bool, is_int_over_zero, is_valid_directory, proper_string_syntax, \
    verify_write_params_output_mode, verify_write_params_scrypt
from bitglitter.validation.validatepalette import palette_geometry_verify


def verify_write_params_render_values(stream_palette_id, stream_palette_nickname, pixel_width, block_height,
                                      block_width, frames_per_second, output_mode, preset_validation):
    palette = _return_palette(palette_id=stream_palette_id, palette_nickname=stream_palette_nickname)
    if not palette.is_valid:
        raise Exception('Custom palette provided cannot currently be used.  This can be from a color distance of 0, or '
                        'if the number of colors in the palette is not 2^n (2, 4, 8, etc).  Please edit the palette\'s '
                        'color set or use a different palette.')

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
    if output_mode == 'video' and palette.is_24_bit:
        raise ValueError("24 bit palettes can not be used with videos at this time due to codec issues.  This is"
                         "\nbeing worked on and will be restored soon!  This palette will still work on images.")

    # With the given dimensions and bit length, is it sufficient?
    payload_frame_percentage, bits_available_per_frame, output_per_sec = palette_geometry_verify(
                                                                        palette.bit_length, block_width,
                                                                        block_height, output_mode, frames_per_second)
    if not preset_validation:
        logging.info(f'{humanize_file_size(bits_available_per_frame)}/frame, or ~{payload_frame_percentage}% of'
                     f' frames are allocated for the payload itself (higher is better)')

        if output_mode == 'video':
            logging.info(f'As a video, it will effectively be transporting '
                         f'{humanize_file_size(round(output_per_sec / 8))}/sec of data.')
        logging.info('Minimum geometry requirements met.')


def write_parameter_validate(input_path, stream_name, stream_description, stream_output_path, output_name,
                             file_mask_enabled, encryption_key, max_cpu_cores=None, output_mode=None,
                             compression_enabled=None, scrypt_n=None, scrypt_r=None, scrypt_p=None,
                             stream_palette_id=None, stream_palette_nickname=None, pixel_width=None, block_height=None,
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
        verify_write_params_render_values(stream_palette_id, stream_palette_nickname, pixel_width, block_height,
                                          block_width, frames_per_second, output_mode, preset_validation=False)
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
