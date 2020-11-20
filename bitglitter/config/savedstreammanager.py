import pickle

from bitglitter.config.basemanager import BaseManager

#TODO- Assembler refactor?  + old Config _initted_ it.
class SavedStreamManager(BaseManager):
    """Acts as an API to Assembler."""

    def __init__(self):
        super().__init__()
        self._SAVE_FILE_NAME = 'savedstreammanager'

        self._delete_save_folder()
        self._save()

    def _delete_save_folder(self):
        pass  # todo


try:
    with open('savedstreammanager.bin', 'rb') as unpickler:
        saved_stream_manager = pickle.load(unpickler)

except:
    saved_stream_manager = SavedStreamManager()
