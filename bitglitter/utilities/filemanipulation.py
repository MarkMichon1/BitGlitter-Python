import logging
import os
import shutil


def refresh_working_folder(active_path):
    '''While the temporary folder after write gets automatically deleted, things such as abrupt stops can prevent that
    from happening.  This removes the folder if it is present, and then creates a few one for the next write cycle.
    This runs in the beginning of preProcess.
    '''
    activeFolder = os.path.join(os.getcwd(), active_path)

    if os.path.isdir(active_path):
        shutil.rmtree(active_path)
        logging.debug(f"active_path folder '{active_path}' already exists.  Deleting...")

    os.mkdir(active_path)
    logging.debug(f"Temp folder '{active_path}' created.")
    return activeFolder


def return_file_size(file_path):
    '''This is taking the final size of the pre-processed file, and this number will be used in the rendering process.
    '''

    size = os.path.getsize(file_path)
    return size