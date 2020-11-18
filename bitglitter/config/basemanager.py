import pickle

class BaseManager:
    """Saving a few repetitive lines of code in all of the manager objects."""

    def __init__(self):
        self._SAVE_FILE_NAME = None

    def _save(self):
        with open(f'{self._SAVE_FILE_NAME}.bin', 'wb') as pickler:
            pickle.dump(self, pickler)