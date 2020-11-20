import logging

from bitglitter.validation.utilities import is_bool, is_valid_directory, proper_string_syntax, \
    verify_write_params_output_mode, verify_write_params_render_values, verify_write_params_scrypt


def write_parameter_validate(file_list, stream_name, stream_description, stream_output_path, output_name,
                             file_mask_enabled, output_mode=None, compression_enabled=None,  scrypt_n=None,
                             scrypt_r=None, scrypt_p=None, stream_palette_id=None, header_palette_id=None,
                             pixel_width=None, block_height=None, block_width=None, frames_per_second=None,
                             preset_used=False):
    """This function verifies all write() parameters.  Look at this as the gatekeeper that stops invalid arguments from
     proceeding through the process, potentially breaking the stream (or causing BitGlitter to crash).
    """

    logging.info("Verifying write parameters...")

    if not file_list:
        raise FileNotFoundError("A minimum of one file or folder is required for stream creation for argument file_list"
                                " in write().")

    if not preset_used:
        verify_write_params_render_values(header_palette_id, stream_palette_id, pixel_width, block_height, block_width,
                                          frames_per_second, output_mode, preset_validation=False)
        verify_write_params_output_mode(output_mode)
        is_bool('compression_enabled', compression_enabled)
        verify_write_params_scrypt(scrypt_n, scrypt_r, scrypt_p)

    proper_string_syntax(stream_name, 'stream_name')
    proper_string_syntax(stream_description, 'stream_description')
    proper_string_syntax(output_name, 'output_name')
    is_bool('file_mask_enabled', file_mask_enabled)

    if stream_output_path:
        is_valid_directory('stream_output_path', stream_output_path)
    verify_write_params_output_mode(output_mode)
    logging.info("Write parameters validated.")


def write_preset_validate(nickname, output_mode, compression_enabled, scrypt_n, scrypt_r, scrypt_p, stream_palette_id,
                          header_palette_id, pixel_width, block_height, block_width, frames_per_second):
    """Validates presets in a nice clean way."""
    if not isinstance(nickname, str):
        raise ValueError('Nickname for preset must be type str.')

    is_bool('compression_enabled', compression_enabled)
    verify_write_params_output_mode(output_mode)
    verify_write_params_render_values(header_palette_id, stream_palette_id, pixel_width, block_height, block_width,
                                      frames_per_second, output_mode, preset_validation=True)
    verify_write_params_scrypt(scrypt_n, scrypt_r, scrypt_p)