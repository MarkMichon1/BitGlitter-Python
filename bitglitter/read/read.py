import logging
from pathlib import Path

from bitglitter.config.config import session
from bitglitter.config.configfunctions import _read_update
from bitglitter.config.configmodels import Config, Constants
from bitglitter.read.inputdecode.framereadhandler import FrameReadHandler
from bitglitter.utilities.loggingset import logging_setter
from bitglitter.validation.validateread import verify_read_parameters


def read(file_path,
         output_directory=False,
         bad_frame_strikes=25,
         max_cpu_cores=0,
         live_payload_unpackaging=False,

         # Overrides
         block_height_override=False,
         block_width_override=False,
         stream_palette_id_override=False,

         # Crypto Input
         encryption_key=None,
         scrypt_n=14,
         scrypt_r=8,
         scrypt_p=1,

         # Logging Settings
         logging_level='info',
         logging_screen_output=True,
         logging_save_output=False,

         # Session Data
         save_statistics=False,
         _app_mode = False #overrides some configs if ran from Electron app
         ):

    """This is the high level function that decodes BitGlitter encoded images and video back into the files/folders
    contained within them.  This along with write() are the two primary functions of this library.
    """

    config = session.query(Config).first()
    constants = session.query(Constants).first()

    # Logging initializing.
    logging_setter(logging_level, logging_screen_output, logging_save_output, Path(config.log_txt_path))
    logging.info('Beginning read...')

    # Are all parameters acceptable?
    input_type = verify_read_parameters(file_path, output_directory, encryption_key, scrypt_n, scrypt_r, scrypt_p,
                                        block_height_override, block_width_override, max_cpu_cores,
                                        stream_palette_id_override, save_statistics)

    # This sets the name of the temporary folder while screened data from partial saves is being written.
    partial_save_path = Path(constants.DEFAULT_PARTIAL_SAVE_DATA_PATH)


    # Pull valid frame data from the inputted file.
    decode_handler = FrameReadHandler(file_path, output_directory, input_type, bad_frame_strikes, max_cpu_cores,
                                      block_height_override, block_width_override, stream_palette_id_override,
                                      encryption_key, scrypt_n, scrypt_r, scrypt_p, save_statistics, partial_save_path)

    # Review decoded data to check if any files can be extracted.
    #todo- merge decode_handler.review_data()

    # Save statistics if enabled.
    if save_statistics:
        _read_update(decode_handler.blocks_read, decode_handler.unique_frames_read, decode_handler.data_read)
