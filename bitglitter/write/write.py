from bitglitter.config.presetmanager import preset_manager
from bitglitter.config.settingsmanager import settings_manager

from bitglitter.utilities.loggingset import logging_setter
from bitglitter.validation.validate_write import write_parameter_validate


def write(  # Basic setup
        input_path,
        preset_nickname=None,
        stream_name="",
        stream_description="",
        output_path=None,
        output_mode="video",
        output_name="",

        # Stream configuration
        compression_enabled=True,
        file_mask_enabled=False,

        # Encryption
        encryption_key="",
        scrypt_n=14,
        scrypt_r=8,
        scrypt_p=1,

        # Stream geometry, color, general config
        header_palette_id='6',
        stream_palette_id='6',
        pixel_width=24,
        block_height=45,
        block_width=80,

        # Video rendering
        frames_per_second=30,

        # Logging
        logging_level='info',
        logging_stdout_output=True,
        logging_txt_output=False,
):
    """This is the primary function in creating BitGlitter streams from files.  Please see Wiki page for more
    information.
    """

    # Initializing logging, must be up front for logging to work properly.
    logging_setter(logging_level, logging_stdout_output, logging_txt_output)

    if preset_nickname:
        write_parameter_validate(input_path, stream_name, stream_description, output_path, output_name,
                                 file_mask_enabled, encryption_key, preset_used=True)

        preset = preset_manager.return_preset(preset_nickname)
        output_mode = preset.output_mode
        compression_enabled = preset.compression_enabled
        scrypt_n = preset.scrypt_n
        scrypt_r = preset.scrypt_r
        scrypt_p = preset.scrypt_p
        header_palette_id = preset.header_palette_id
        stream_palette_id = preset.stream_palette_id
        pixel_width = preset.pixel_width
        block_height = preset.block_height
        block_width = preset.block_width
        frames_per_second = preset.frames_per_second

    else:
        write_parameter_validate(input_path, stream_name, stream_description, output_path, output_name,
                                 file_mask_enabled, encryption_key, output_mode, compression_enabled, scrypt_n,
                                 scrypt_r, scrypt_p, stream_palette_id, header_palette_id, pixel_width, block_height,
                                 block_width, frames_per_second, preset_used=False)

    # This sets the name of the temporary folder while the file is being written.
    working_dir = settings_manager.WRITE_WORKING_DIR

    # This is what takes the raw input files and runs them through several processes in preparation for rendering.
    # pre_processor = PreProcessor(temp_write_path, file_list, encryption_key, file_mask_enabled,
    #                            compression_enabled, scrypt_override_n, scrypt_override_r,
    #                            scrypt_override_p)
    #
    # render_handler = RenderHandler(EncodeFrame(), block_height, block_width, header_palette_id, pre_processor.stream_sha,
    #                                pre_processor.size_in_bytes, compression_enabled, encryption_key != "",
    #                                file_mask_enabled, pre_processor.date_created, stream_palette_id, BG_VERSION,
    #                                stream_name, stream_description, pre_processor.post_encryption_hash, pixel_width,
    #                                output_mode, output_path, frames_per_second, temp_write_path, pre_processor.pass_through,
    #                                output_name)
    #
    # new_render = None

    # config.finish_write(render_handler.statistics, etc) <- todo - update stats after config refactor
    #

    # Returns the SHA of the preprocessed file in string format for optional storage of it.
    # return pre_processor.stream_sha
    return {} #eventually dict with write data
