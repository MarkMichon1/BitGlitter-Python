from pathlib import Path
import pickle

from bitglitter.config.basemanager import BaseManager


class ReadManager(BaseManager):
    """Acts as an API to Assembler."""

    def __init__(self):
        super().__init__()
        self._SAVE_FILE_NAME = 'save_state'

        self._delete_save_folder()
        self._save()

    def _delete_save_folder(self):
        pass  # todo

    def delete_stream(self):
        pass

    def delete_all_streams(self):
        pass  # tied into remove_session

    def try_password(self):
        pass


try:
    current_directory = Path(__file__).resolve().parent
    pickle_path = current_directory / 'read_state.bin'
    with open(pickle_path, 'rb') as unpickler:
        read_manager = pickle.load(unpickler)

except FileNotFoundError:
    read_manager = ReadManager()
