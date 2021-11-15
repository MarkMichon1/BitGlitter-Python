from pathlib import Path

from bitglitter.config.config import session
from bitglitter.config.configmodels import Config, Constants
from bitglitter.config.presetfunctions import return_preset
from bitglitter.utilities.filemanipulation import refresh_directory, remove_working_folder
from bitglitter.utilities.loggingset import logging_setter
from bitglitter.validation.validatewrite import write_parameter_validate
from bitglitter.write.preprocess.preprocessor import PreProcessor
from bitglitter.write.render.renderhandler import RenderHandler
from bitglitter.write.render.videorender import render_video


def write(

        # Basic setup
        input_path,
        preset_nickname=None,
        stream_name="",
        stream_description="",
        output_directory=None,
        output_mode="video",
        stream_name_file_output=False,
        max_cpu_cores=0,

        # Stream configuration
        compression_enabled=True,
        # error_correction=False, -> Pending further research for viability

        # Encryption
        encryption_key="",
        file_mask_enabled=False,
        scrypt_n=14,
        scrypt_r=8,
        scrypt_p=1,

        # Stream geometry, color, general config
        stream_palette_id='6',
        stream_palette_nickname=None,
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
        save_statistics=False,
):
    """Creates BitGlitter streams from files/directories.  See repo readme for more information."""

    config = session.query(Config).first()
    constants = session.query(Constants).first()

    # This sets the name of the temporary folder while the file is being written, as well as the default output path.
    working_directory = Path(constants.WORKING_DIR)
    refresh_directory(working_directory)

    # Setting save path for stream
    if output_directory:
        output_directory = Path(output_directory)
    else:
        output_directory = Path(config.write_path)
        refresh_directory(output_directory, delete=False)

    print(output_directory)

    # Initializing logging, must be up front for logging to work properly.
    logging_setter(logging_level, logging_stdout_output, logging_txt_output, Path(config.log_txt_dir))

    # Loading preset (if given), and validating any other parameters before continuing with the rendering process.
    if preset_nickname:
        write_parameter_validate(input_path, stream_name, stream_description, output_directory, stream_name_file_output,
                                 file_mask_enabled, encryption_key, preset_used=True)
        preset = return_preset(preset_nickname)
        output_mode = preset.output_mode
        compression_enabled = preset.compression_enabled
        scrypt_n = preset.scrypt_n
        scrypt_r = preset.scrypt_r
        scrypt_p = preset.scrypt_p
        max_cpu_cores = preset.max_cpu_cores
        stream_palette_id = preset.stream_palette_id
        pixel_width = preset.pixel_width
        block_height = preset.block_height
        block_width = preset.block_width
        frames_per_second = preset.frames_per_second
    else:
        write_parameter_validate(input_path, stream_name, stream_description, output_directory, stream_name_file_output,
                                 file_mask_enabled, encryption_key, max_cpu_cores, output_mode, compression_enabled,
                                 scrypt_n, scrypt_r, scrypt_p, stream_palette_id, stream_palette_nickname, pixel_width,
                                 block_height, block_width, frames_per_second, preset_used=False)

    # This is what takes the raw input files and runs them through several processes in preparation for rendering.
    pre_processor = PreProcessor(working_directory, input_path, encryption_key, compression_enabled, scrypt_n, scrypt_r,
                                 scrypt_p, stream_name)

    # This is where the final steps leading up to frame generation as well as generation itself takes place.
    render_handler = RenderHandler(stream_name, stream_description, working_directory, output_directory, encryption_key,
                                   scrypt_n, scrypt_r, scrypt_p, block_height, block_width, pixel_width,
                                   stream_palette_id, max_cpu_cores, pre_processor.stream_sha256,
                                   pre_processor.size_in_bytes, compression_enabled, pre_processor.encryption_enabled,
                                   file_mask_enabled, pre_processor.datetime_started, constants.BG_VERSION,
                                   pre_processor.manifest, constants.PROTOCOL_VERSION, output_mode, output_directory,
                                   stream_name_file_output, save_statistics)

    # Video render
    if output_mode == 'video':
        render_video(output_directory, stream_name_file_output, working_directory, render_handler.total_frames,
                     frames_per_second, pre_processor.stream_sha256, block_width, block_height, pixel_width,
                     stream_name, render_handler.total_operations)

    # Removing temporary files
    remove_working_folder(working_directory)

    return pre_processor.stream_sha256
