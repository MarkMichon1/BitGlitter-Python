import logging
from pathlib import Path

from bitglitter.config.config import session
from bitglitter.config.configfunctions import _read_update
from bitglitter.config.configmodels import Config, Constants
from bitglitter.config.readmodels.readmodels import StreamFrame
from bitglitter.read.inputdecode.framereadhandler import frame_read_handler
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
         _app_mode=False  # overrides some configs if ran from Electron app
         ):
    """This is the high level function that decodes BitGlitter encoded images and video back into the files/folders
    contained within them.  This along with write() are the two primary functions of this library.
    """

    config = session.query(Config).first()
    constants = session.query(Constants).first()

    # This sets the name of the temporary folder while screened data from partial saves is being written.
    temp_save_path = Path(constants.DEFAULT_TEMP_SAVE_DATA_PATH)

    # Logging initializing.
    logging_setter(logging_level, logging_screen_output, logging_save_output, Path(config.log_txt_path))
    logging.info('Beginning read...')

    # Are all parameters acceptable?
    input_type = verify_read_parameters(file_path, output_directory, encryption_key, scrypt_n, scrypt_r, scrypt_p,
                                        block_height_override, block_width_override, max_cpu_cores, save_statistics,
                                        live_payload_unpackaging, bad_frame_strikes)

    # Pull valid frame data from the inputted file.
    returned = frame_read_handler(file_path, output_directory, input_type, bad_frame_strikes, max_cpu_cores,
                                  block_height_override, block_width_override, encryption_key, scrypt_n, scrypt_r,
                                  scrypt_p, temp_save_path, live_payload_unpackaging)

    #  Remove incomplete frames from db
    session.query(StreamFrame).filter(not StreamFrame.is_complete).delete()
    session.commit()

    # Save statistics if enabled.
    if save_statistics and 'abort' not in returned:
        _read_update(returned['blocks_read'], returned['unique_frames_read'], returned['data_read'])

    return returned['stream_sha256'] if 'stream_sha256' in returned else None
