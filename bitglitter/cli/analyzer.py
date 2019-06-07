import os
import sys
from bitglitter.write.write import write


class CliArgumentParser(object):
    """
    This class should be responsible
    to parse all CLI args.
    """
    
    # Implementation of write argument for CLI
    # Where first argument must me the path to 
    # a file or folder and de second argument must
    # be output mode i.e image or video
    @staticmethod
    def write(arguments):
        file_path = arguments.get('file')
        mode = arguments.get('mode', 'video')
        stream_name = arguments.get('streamname', '')
        if os.path.isfile(file_path) == True or os.path.isdir(file_path) == True:
            write(fileList=file_path, streamName=stream_name, outputMode=mode)
        else:
            # TODO: Create exceptions
            sys.exit('--write first argument must be a valid path to a file or folder.')
