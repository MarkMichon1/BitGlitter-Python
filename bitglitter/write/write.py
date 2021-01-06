import time

from bitglitter.config.presetmanager import preset_manager
from bitglitter.config.settingsmanager import settings_manager
from bitglitter.config.statisticsmanager import stats_manager
from bitglitter.utilities.filemanipulation import remove_working_folder
from bitglitter.utilities.loggingset import logging_setter
from bitglitter.validation.validatewrite import write_parameter_validate
from bitglitter.write.preprocess.preprocessor import PreProcessor
from bitglitter.write.renderhandler import RenderHandler


def write(

        # Basic setup
        input_path,
        preset_nickname=None,
        stream_name="",
        stream_description="",
        output_path=None,
        output_mode="video",
        output_name="",
        max_cpu_cores=0,

        # Stream configuration
        compression_enabled=True,
        # error_correction=False, -> to be implemented
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

        # Session Data
        save_statistics=False
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
                                 file_mask_enabled, encryption_key, max_cpu_cores, output_mode, compression_enabled, scrypt_n,
                                 scrypt_r, scrypt_p, stream_palette_id, header_palette_id, pixel_width, block_height,
                                 block_width, frames_per_second, preset_used=False)

    # This sets the name of the temporary folder while the file is being written.

    working_dir = settings_manager.WRITE_WORKING_DIR
    default_output_path = settings_manager.DEFAULT_OUTPUT_PATH

    # This is what takes the raw input files and runs them through several processes in preparation for rendering.
    pre_processor = PreProcessor(working_dir, input_path, encryption_key, file_mask_enabled, compression_enabled,
                                 scrypt_n, scrypt_r, scrypt_p)

    render_handler = RenderHandler(stream_name, stream_description, working_dir, default_output_path, encryption_key,
                                   scrypt_n, scrypt_r, scrypt_p, block_height, block_width, pixel_width,
                                   header_palette_id, stream_palette_id, max_cpu_cores, pre_processor.stream_sha,
                                   pre_processor.size_in_bytes, compression_enabled, pre_processor.encryption_enabled,
                                   file_mask_enabled, pre_processor.datetime_started, settings_manager.BG_VERSION,
                                   pre_processor.manifest, settings_manager.PROTOCOL_VERSION, frames_per_second,
                                   output_mode, output_path, output_name)

    #remove_working_folder(working_dir)


    if save_statistics:
        stats_manager.write_update(render_handler.blocks_wrote, render_handler.frames_wrote,
                                   pre_processor.size_in_bytes)

    print(pre_processor.datetime_started)
    print(time.time()) #todo temp
    print(time.time()-pre_processor.datetime_started)
    return pre_processor.stream_sha
