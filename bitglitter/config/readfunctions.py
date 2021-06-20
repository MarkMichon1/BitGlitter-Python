def return_all_read_information():
    pass


def return_single_read(stream_sha):
    pass


def attempt_password(stream_sha, encryption_key):
    pass


def configure(some_args):
    pass  # tba


def return_stream_manifest(stream_sha):
    pass


def change_decoded_files_save_path(folder_path):
    """This changes the folder where files that have been successfully pulled from the stream get written to."""
    pass


def remove_partial_save(stream_sha):
    pass


def remove_all_partial_save_data():
    """Removes all data for partial saves, both files and metadata within some internal classes."""
    pass


def update_partial_save():
    pass

    # def update_partial_save(stream_sha, reattempt_assembly=True, password_update=None, scrypt_n=None,
    #                         scrypt_r=None, scrypt_p=None, change_output_directory=None):
    #     '''This function will update the PartialSave object with the parameters provided, once they've been verified.'''
    #
    #     if password_update:
    #         proper_string_syntax('password_update', password_update)
    #     if scrypt_n:
    #         is_int_over_zero('scrypt_n', scrypt_n)
    #     if scrypt_r:
    #         is_int_over_zero('scrypt_r', scrypt_r)
    #     if scrypt_p:
    #         is_int_over_zero('scrypt_p', scrypt_p)
    #     if change_output_path:
    #         is_valid_directory('change_output_path', change_output_path)
    #
    #     config.assembler.save_dict[stream_sha].user_input_update(password_update, scrypt_n, scrypt_r, scrypt_p,
    #                                                              change_output_path)