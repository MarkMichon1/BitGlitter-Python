import os
import string


def is_valid_directory(argument, path):
    '''Checks whether the inputted directory exists or not.'''
    if not os.path.isdir(path):
        raise ValueError(f'Folder path for {argument} does not exist.')


def is_int_over_zero(argument, some_variable):
    '''Checks if variable is of type int and is greater than zero.'''

    if not isinstance(some_variable, int) or some_variable < 0:
        raise ValueError(f"Argument {argument} must be an integer greater than zero.")


def proper_string_syntax(argument, inputted_string=""):
    '''This exists to verify various inputs are using allowed characters.  One such character that isn't allowed is
    '\\', as that character is what the ASCII part of the stream header uses to divide attributes.
    '''

    acceptable_chars = string.ascii_letters + string.digits + string.punctuation.replace("\\", "") + " "
    if inputted_string:
        for letter in inputted_string:
            if letter not in acceptable_chars:
                raise ValueError(f"Only ASCII characters excluding '\\' are allowed in {argument}.")


def is_bool(argument, variable):
    '''Will raise error if argument isn't type bool.  Used in verifying arguments for read() and write()'''
    if not isinstance(variable, bool):
        raise ValueError(f'Argument {argument} must be type boolean.')