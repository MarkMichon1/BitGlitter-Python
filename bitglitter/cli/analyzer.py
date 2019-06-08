from os import path
from bitglitter.write.write import write
from bitglitter.read.read import read


class CliArgumentParser(object):
    """
    This class should be responsible
    to parse all CLI args.
    """
    
    @staticmethod
    def read(arguments:dict):
        file = arguments.get('file')
        if path.isfile(file) == True or path.isdir(file) == True:
            read(fileToInput=file)
        else:
            raise FileNotFoundError('Read first argument must be a valid path to a file or folder.')

    
    @staticmethod
    def write(arguments:dict):
        print(arguments)
        file_path = arguments.get('file')
        mode = arguments.get('mode')
        if not mode:
            mode = 'image'
        stream_name = arguments.get('streamname', '')
        if path.isfile(file_path) == True or path.isdir(file_path) == True:
            try:
                write(fileList=file_path, streamName=stream_name, outputMode=mode)
            except FileNotFoundError:
                raise FileNotFoundError("ffmpeg is required and wasn't found do you have ffmpeg installed in your local directory ?")
            except TypeError:
                raise TypeError('Please provide -streamname argument.')
        else:
            raise FileNotFoundError('Write first argument must be a valid path to a file or folder.')