import logging
import os
import shutil


def refresh_working_folder(active_path):
    """While the temporary folder after write gets automatically deleted, things such as abrupt stops can prevent that
    from happening.  This removes the folder if it is present, and then creates a few one for the next write cycle.
    This runs in the beginning of preProcess.
    """
    active_folder = os.path.join(os.getcwd(), active_path)

    if os.path.isdir(active_path):
        shutil.rmtree(active_path)
        logging.debug(f"active_path folder '{active_path}' already exists.  Deleting...")

    os.mkdir(active_path)
    logging.debug(f"Temp folder '{active_path}' created.")
    return active_folder


def remove_working_folder(working_directory):
    if os.path.isdir(working_directory):
        logging.debug('Deleting temporary working directory for task...')
        shutil.rmtree(working_directory)


def create_default_output_folder(default_output_path):
    if not os.path.isdir(default_output_path):
        logging.debug('Default output directory does not exist.  Creating...')
        os.mkdir(default_output_path)


def return_file_size(file_path):
    """This is taking the final size of the pre-processed file, and this number will be used in the rendering process.
    """

    size = os.path.getsize(file_path)
    return size
