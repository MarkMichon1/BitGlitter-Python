from bitglitter.utilities.loggingset import logging_setter
from bitglitter.write.preprocessors import PreProcessor
from bitglitter.write.renderhandler import RenderHandler
from bitglitter.write.renderlogic import EncodeFrame
from bitglitter.write.writeparameterverify import verify_write_parameters


def write(  # Basic setup
        file_list,
        stream_name="",
        stream_description="",
        output_path=None,
        output_mode="video",
        output_name="",

        # Stream configuration
        compression_enabled=True,
        file_mask_enabled=False, #todo: revisit in light of new packaging format

        # Encryption
        encryption_key="",
        scrypt_override_n=14,
        scrypt_override_r=8,
        scrypt_override_p=1,

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

    # TODO:
    app_config = AppConfig()

    # Logging initializing.
    logging_setter(logging_level, logging_stdout_output, logging_txt_output)

    # Are all parameters acceptable?
    verify_write_parameters(file_list, stream_name, stream_description, output_path, output_mode,
                            output_name, compression_enabled, file_mask_enabled, scrypt_override_n,
                            scrypt_override_r, scrypt_override_p, stream_palette_id, header_palette_id,
                            pixel_width, block_height, block_width, frames_per_second)

    # This sets the name of the temporary folder while the file is being written.
    active_path = DEFAULT_WRITE_PATH

    # This is what takes the raw input files and runs them through several processes in preparation for rendering.
    pre_process = PreProcessor(active_path, file_list, encryption_key, file_mask_enabled,
                               compression_enabled, scrypt_override_n, scrypt_override_r,
                               scrypt_override_p)

    render_handler = RenderHandler(EncodeFrame(), block_height, block_width, header_palette_id, pre_process.stream_sha,
                                   pre_process.size_in_bytes, compression_enabled, encryption_key != "",
                                   file_mask_enabled, pre_process.date_created, stream_palette_id, BG_VERSION,
                                   stream_name, stream_description, pre_process.post_encryption_hash, pixel_width,
                                   output_mode, output_path, frames_per_second, active_path, pre_process.pass_through,
                                   output_name)

    # config.finish_write(render_handler.statistics, etc) <- todo - update stats after config refactor

    # Returns the SHA of the preprocessed file in string format for optional storage of it.
    return pre_process.stream_sha
