import logging
import os
import shutil


def refresh_directory(active_path, delete=True):
    """Used for working (temp) directory, and default directory for read/write.  Optionally removes directory if it
    exists, otherwise it makes sure it is created.
    """
    active_folder = os.path.join(os.getcwd(), active_path)

    if delete:
        if os.path.isdir(active_path):
            shutil.rmtree(active_path)
            logging.debug(f"active_path folder '{active_path}' already exists.  Deleting...")

    if not os.path.isdir(active_path):
        os.makedirs(active_path)
        logging.debug(f"Directory '{active_path}' created.")
    return active_folder


def remove_working_folder(working_directory):
    if os.path.isdir(working_directory):
        logging.debug('Deleting temporary working directory...')
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
