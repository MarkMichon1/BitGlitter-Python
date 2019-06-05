import os
import sys
from bitglitter.write.write import write
from .args import parser
from .utilities import (
    validate_args, list_get
)

class CliArgumentParser(object):
    """
    This class should keep responsible
    to parse all CLI args.
    """
    def __init__(self, arguments_dict={}):  
        self.arguments = validate_args(arguments_dict.parse_args())

    def __contains__(self, attr):
        if attr in self.arguments:
            return True
        else:
            False

    def print_args(self):
        print(self.arguments)
    
    # Implementation of write argument for CLI
    # Where first argument must me the path to 
    # a file or folder and de second argument must
    # be output mode i.e image or video
    def write(self):
        write_arg = self.arguments.get('write')
        file_path = list_get(write_arg, 0)
        out_mode = list_get(write_arg, 1, default='video')

        if os.path.isfile(file_path) == True or os.path.isdir(file_path) == True:
            write(file_path, outputMode=out_mode)
        else:
            # TODO: Create exceptions
            sys.exit('--write first argument must be a valid path to a file or folder.')