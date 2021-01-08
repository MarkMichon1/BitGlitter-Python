import logging

from bitglitter.config.settingsmanager import settings_manager
from bitglitter.read.framedecode.fileslicer import file_slicer
from bitglitter.utilities.loggingset import logging_setter
from bitglitter.validation.validateread import verify_read_parameters


def read(input_path,
         output_path=False,
         bad_frame_strikes=25,
         max_cpu_cores=0,

         # Overrides
         block_height_override=False,
         block_width_override=False,
         header_palette_id_override=False,
         stream_palette_id_override=False,

         # Crypto Input
         encryption_key=None,
         scrypt_n=14,
         scrypt_r=8,
         scrypt_p=1,

         # Logging Settings
         logging_level='info',
         logging_screen_output=True,
         logging_save_output=False
         ):

    """This is the high level function that decodes BitGlitter encoded images and video back into the files/folders
    contained within them.  This along with write() are the two primary functions of this library.
    """

    # Logging initializing.
    logging_setter(logging_level, logging_screen_output, logging_save_output, settings_manager.log_txt_path)
    logging.info('Beginning read...')

    # Are all parameters acceptable?
    verify_read_parameters(input_path, output_path, encryption_key, scrypt_n, scrypt_r, scrypt_p,
                           block_width_override, block_width_override, max_cpu_cores)

    # This sets the name of the temporary folder while screened data from partial saves is being written.
    partial_save_path = settings_manager


    # Pull valid frame data from the inputted file.
    checkpoint_passed = file_slicer(input_path, partial_save_path, output_path, block_height_override,
                                    block_width_override, encryption_key, scrypt_n, scrypt_r, scrypt_p,
                                    bad_frame_strikes)
    if not checkpoint_passed:
        return

    # Now that all frames have been scanned, we'll have the config object check to see if any files are ready for
    # assembly.  If there are, they will be put together and outputted, as well as removed/flushed from partialSaves.
    config.assembler.review_active_sessions()
    config._save_session()
