from bitglitter.config.defaultvalues import DEFAULT_READ_PATH, DEFAULT_BAD_FRAME_STRIKES, DEFAULT_SCRYPT_N, DEFAULT_SCRYPT_R, \
    DEFAULT_SCRYPT_P
from bitglitter.utilities.loggingset import logging_setter
from bitglitter.validation.validate_read import verify_read_parameters

def read(file_to_input,
         output_path = None,
         bad_frame_strikes = DEFAULT_BAD_FRAME_STRIKES,
         assemble_hold = False,

         # Geometry Overrides
         block_height_override = False,
         block_width_override = False,

         # Crypto Input
         encryption_key = None,
         scrypt_n = DEFAULT_SCRYPT_N,
         scrypt_r = DEFAULT_SCRYPT_R,
         scrypt_p = DEFAULT_SCRYPT_P,

         # Logging Settings
         logging_level ='info',
         logging_screen_output = True,
         logging_save_output = False
         ):
    '''This is the high level function that decodes BitGlitter encoded images and video back into the files/folders
    contained within them.  This along with write() are the two primary functions of this library.
    '''

    # Logging initializing.
    logging_setter(logging_level, logging_screen_output, logging_save_output)
    from bitglitter.read.fileslicer import file_slicer
    from bitglitter.config.config import config

    # Are all parameters acceptable?
    verify_read_parameters(file_to_input, output_path, encryption_key, scrypt_n, scrypt_r, scrypt_p,
                           block_width_override, block_width_override, assemble_hold)

    # This sets the name of the temporary folder while screened data from partial saves is being written.
    active_path = DEFAULT_READ_PATH

    # Pull valid frame data from the inputted file.
    checkpoint_passed = file_slicer(file_to_input, active_path, output_path, block_height_override,
                                    block_width_override, encryption_key, scrypt_n, scrypt_r, scrypt_p, config,
                                    bad_frame_strikes, assemble_hold)
    if checkpoint_passed == False:
        return False

    # Now that all frames have been scanned, we'll have the config object check to see if any files are ready for
    # assembly.  If there are, they will be put together and outputted, as well as removed/flushed from partialSaves.
    config.assembler.review_active_sessions()
    config._save_session()
    return True
