import logging
from pathlib import Path

from bitglitter.config.config import session
from bitglitter.config.configmodels import Config, Constants
from bitglitter.config.readmodels.readmodels import StreamFrame
from bitglitter.read.readstate.framereadhandler import frame_read_handler
from bitglitter.utilities.loggingset import logging_setter
from bitglitter.validation.validateread import verify_read_parameters


def read(file_path,
         stop_at_metadata_load=True,
         auto_unpackage_stream=True,
         auto_delete_finished_stream=True,
         output_directory=None,
         bad_frame_strikes=25,
         max_cpu_cores=0,

         # Overrides
         block_height_override=False,
         block_width_override=False,

         # Crypto Input
         decryption_key=None,
         scrypt_n=14,
         scrypt_r=8,
         scrypt_p=1,

         # Logging Settings
         logging_level='info',
         logging_screen_output=True,
         logging_save_output=False,

         # Session Data
         save_statistics=False,
         ):
    """This is the high level function that decodes BitGlitter encoded images and video back into the files/folders
    contained within them.  This along with write() are the two primary functions of this library.
    """

    config = session.query(Config).first()
    constants = session.query(Constants).first()

    # This sets the name of the temporary folder while screened data from partial saves is being written.
    temp_save_directory = Path(constants.DEFAULT_TEMP_SAVE_DIR)

    # Setting save path for stream
    if output_directory:
        output_directory = output_directory
    else:
        output_directory = config.write_path

    # Logging initializing.
    logging_setter(logging_level, logging_screen_output, logging_save_output, Path(config.log_txt_dir))
    logging.info('Starting read...')

    # Are all parameters acceptable?
    input_type = verify_read_parameters(file_path, output_directory, decryption_key, scrypt_n, scrypt_r, scrypt_p,
                                        block_height_override, block_width_override, max_cpu_cores, save_statistics,
                                        bad_frame_strikes)

    # Pull valid frame data from the inputted file.
    frame_read_results = frame_read_handler(file_path, output_directory, input_type, bad_frame_strikes, max_cpu_cores,
                                            block_height_override, block_width_override, decryption_key, scrypt_n,
                                            scrypt_r, scrypt_p, temp_save_directory, stop_at_metadata_load,
                                            auto_unpackage_stream, auto_delete_finished_stream, save_statistics)

    #  Remove incomplete frames from db
    session.query(StreamFrame).filter(not StreamFrame.is_complete).delete()
    session.commit()

    # Return metadata if conditions are met
    if 'metadata' in frame_read_results:
        return frame_read_results['metadata']

    logging.info('Read cycle complete.')
    return frame_read_results['stream_sha256'] if 'stream_sha256' in frame_read_results else None
