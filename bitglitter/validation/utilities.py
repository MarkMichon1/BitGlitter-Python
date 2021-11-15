import os
import string


def is_valid_directory(argument, path):
    """Checks whether the inputted directory exists or not."""
    if not os.path.isdir(path):
        raise ValueError(f'Folder path "{path}" for {argument} does not exist.')


def is_int_over_zero(argument, some_variable):
    """Checks if variable is of type int and is greater than zero."""

    if not isinstance(some_variable, int) or some_variable < 0:
        raise ValueError(f"Argument {argument} must be an integer greater than zero, {some_variable} was provided")


def proper_string_syntax(argument, inputted_string="", posix=False):
    """This exists to verify various inputs are using allowed characters.  One such character that isn't allowed is
    '\\', as that character is what the ASCII part of the stream header uses to divide attributes.
    """

    if posix:
        acceptable_chars = string.ascii_letters + string.digits + string.punctuation.replace("\\", "") + " "
    else:
        acceptable_chars = string.ascii_letters + string.digits + '._-'

    if posix:
        if inputted_string[0] == ' ' or inputted_string[-1] == ' ':
            raise ValueError('Cannot start or end string with space')

    if inputted_string:
        for letter in inputted_string:
            if letter not in acceptable_chars:
                if posix:
                    raise ValueError(f'Can only use these characters for {argument}: {acceptable_chars}')
                else:
                    raise ValueError(f"Only ASCII characters excluding '\\' are allowed in {argument}.")


def is_bool(argument, variable):
    """Will raise error if argument isn't type bool.  Used in verifying arguments for read() and write()"""
    if not isinstance(variable, bool):
        raise ValueError(f'Argument {argument} must be type boolean.')


def verify_write_params_output_mode(output_mode):
    if output_mode != 'video' and output_mode != 'image':
        raise ValueError("Argument output_mode in write() only accepts 'video' or 'image'.")


def verify_write_params_scrypt(scrypt_n, scrypt_r, scrypt_p):
    """Used both during """

    is_int_over_zero('scrypt_n', scrypt_n)
    is_int_over_zero('scrypt_r', scrypt_r)
    is_int_over_zero('scrypt_p', scrypt_p)


def logging_config_validate(logging_level, logging_stdout_output, logging_txt_output):
    acceptable_level_words = [False, 'debug', 'info']
    if logging_level not in acceptable_level_words:
        raise ValueError(f"{logging_level} is not a valid input for logging_level.  Only 'info', 'debug', and False are"
                         f" allowed.")

    if not isinstance(logging_stdout_output, bool):
        raise ValueError("Only booleans are allowed for logging_stdout_output.")

    if not isinstance(logging_txt_output, bool):
        raise ValueError("Only booleans are allowed for logging_txt_output.")
