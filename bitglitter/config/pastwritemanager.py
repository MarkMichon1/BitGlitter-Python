from bitglitter.config.basemanager import BaseManager

class PastWriteManager(BaseManager):
    def __init__(self):
        super().__init__()
        self._SAVE_FILE_NAME = 'pastwritemanager'

        self.next_write_id = 1
        self.past_write_dict = {}

        self._save()

    def add_new(self):
        pass


class PastWrite:
    def __init__(self):
        pass