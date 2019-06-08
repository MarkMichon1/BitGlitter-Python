import os

from bitglitter.config.config import config
from bitglitter.utilities.generalverifyfunctions import is_int_over_zero, is_valid_directory, proper_string_syntax

# These functions are for end users.

def print_full_save_list(path, debug_data = False):
    '''This function will output a text file displaying the current status of all of the partial saves in BitGlitter.
    Path specifies the folder path it will be outputted to.  Argument debug_data will show various debug information
    pertaining to the partial save, that the normal user has no need to see.
    '''

    active_path = os.path.join(os.getcwd(), path)

    with open(active_path + '\\BitGlitter Partial Saves.txt', 'w') as writer:
        writer.write('*' * 21 + '\nPartial Saves\n' + '*' * 21 + '\n')

        if config.assembler.save_dict:
            temp_holder = ''

            for partial_save in config.assembler.save_dict:
                temp_holder += ('\n' + config.assembler.save_dict[partial_save].return_status(debug_data) + '\n\n')
            writer.write(temp_holder)

        else:
            writer.write('\nNo partial saves (yet!)')


def update_partial_save(stream_sha, reattempt_assembly = True, password_update = None, scrypt_n =  None,
                        scrypt_r = None, scrypt_p = None, change_output_path = None):
    '''This function will update the PartialSave object with the parameters provided, once they've been verified.'''

    if password_update:
        proper_string_syntax('password_update', password_update)
    if scrypt_n:
        is_int_over_zero('scrypt_n', scrypt_n)
    if scrypt_r:
        is_int_over_zero('scrypt_r', scrypt_r)
    if scrypt_p:
        is_int_over_zero('scrypt_p', scrypt_p)
    if change_output_path:
        is_valid_directory('change_output_path', change_output_path)

    config.assembler.save_dict[stream_sha].user_input_update(password_update, scrypt_n, scrypt_r, scrypt_p,
                                                             change_output_path)

    if reattempt_assembly == True:
        if config.assembler.save_dict[stream_sha]._attempt_assembly() == True:
            config.assembler.remove_partial_save(stream_sha)

    config.save_session()


def remove_partial_save(stream_sha):
    '''Taking the stream SHA as an argument, this function will remove the partial save object, and well as remove any
    temporary data BitGlitter may have had with it.
    '''

    config.assembler.remove_partial_save(stream_sha)
    config.save_session()


def begin_assembly(stream_sha):
    '''This function exists to initiate assembly of a package at a later time, rather than doing so immediately for
    whatever reason.
    '''

    if config.assembler.save_dict[stream_sha]._attempt_assembly() == True:
        config.assembler.remove_partial_save(stream_sha)
    config.save_session()


def remove_all_partial_saves():
    '''This removes all partial save objects saved, as well as any temporary data.'''

    config.assembler.clear_partial_saves()
    config.save_session()
