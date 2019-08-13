from os import path
from bitglitter.write.write import write
from bitglitter.read.read import read


class CliArgumentParser(object):
    """
    This class should be responsible
    to parse all CLI args.
    """
    
    # TODO: To check if output path is a valid path and hold
    # possible exceptions that may occur there just like write and read path. 


    @staticmethod
    def read(arguments:dict):
        file = arguments.get('file')
        output_path = arguments.get('o')
        
        if not output_path:
            output_path = False
        
        if path.isfile(file) == True or path.isdir(file) == True:
            read(file_to_input=file)
        else:
            raise FileNotFoundError('Read first argument must be a valid path to a file or folder.')

    
    
    @staticmethod
    def write(arguments:dict):
        file_path = arguments.get('file')
        mode = arguments.get('mode')
        output_path = arguments.get('o')
        stream_name = arguments.get('streamname', '')
        
        if not output_path:
            output_path = False
        
        if not mode:
            mode = 'image'
        
        if path.isfile(file_path) == True or path.isdir(file_path) == True:
            try:
                write(file_list=file_path, stream_name=stream_name, output_mode=mode, output_path=output_path)
            except FileNotFoundError:
                raise FileNotFoundError("ffmpeg is required and wasn't found do you have ffmpeg installed in your local directory ?")
            except TypeError:
                raise TypeError('Please provide -streamname argument.')
            except PermissionError:
                raise PermissionError(f"You don't have the proper permissions to write at {output_path}, \ntry to change output path or run the command with sudo under Linux")
        else:
            raise FileNotFoundError('Write first argument must be a valid path to a file or folder.')