import pickle

from bitglitter.config.basemanager import BaseManager

class PastWriteManager(BaseManager):
    def __init__(self):
        super().__init__()
        self._SAVE_FILE_NAME = 'pastwritemanager'

        self.next_write_id = 1
        self.past_write_dict = {}

        self._save()

    def add_new(self):
        self.past_write_dict[self.next_write_id] = PastWrite() #todo
        self.next_write_id += 1
        self._save()

    def remove_one(self, id):
        del self.past_write_dict[id]
        self._save()

    def clear_all(self):
        self.next_write_id = 1
        self.past_write_dict = {}
        self._save()


class PastWrite:
    def __init__(self):
        pass #todo


try:
    with open('pastwritemanager.bin', 'rb') as unpickler:
        past_write_manager = pickle.load(unpickler)

except:
    past_write_manager = PastWriteManager()
