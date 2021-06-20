from pathlib import Path
import pickle

class BaseManager:
    """Saving a few repetitive lines of code in all of the manager objects."""

    def __init__(self):
        self._SAVE_FILE_NAME = None

    def _save(self):
        pass
        # current_directory = Path(__file__).resolve().parent
        # write_path = current_directory / f'{self._SAVE_FILE_NAME}.bin'
        # with open(write_path, 'wb') as pickler:
        #     pickle.dump(self, pickler)