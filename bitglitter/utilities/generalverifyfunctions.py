import os
import string


def isValidDirectory(argument, path):
    '''Checks whether the inputted directory exists or not.'''
    if not os.path.isdir(path):
        raise ValueError(f'Folder path for {argument} does not exist.')


def isIntOverZero(argument, someVariable):
    '''Checks if variable is of type int and is greater than zero.'''

    if not isinstance(someVariable, int) or someVariable < 0:
        raise ValueError(f"Argument {argument} must be an integer greater than zero.")


def properStringSyntax(argument, inputtedString=""):
    '''This exists to verify various inputs are using allowed characters.  One such character that isn't allowed is
    '\\', as that character is what the ASCII part of the stream header uses to divide attributes.
    '''

    acceptableChars = string.ascii_letters + string.digits + string.punctuation.replace("\\", "") + " "
    if inputtedString:
        for letter in inputtedString:
            if letter not in acceptableChars:
                raise ValueError(f"Only ASCII characters excluding '\\' are allowed in {argument}.")


def isBool(argument, variable):
    '''Will raise error if argument isn't type bool.  Used in verifying arguments for read() and write()'''
    if not isinstance(variable, bool):
        raise ValueError(f'Argument {argument} must be type boolean.')