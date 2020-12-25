import pickle

from bitglitter.config.basemanager import BaseManager


class StatisticsManager(BaseManager):
    """Read and write values are held in this object.  It's attributes are changed through method calls."""

    def __init__(self):
        super().__init__()
        self._SAVE_FILE_NAME = 'statsmanager'

        self.blocks_wrote = 0
        self.frames_wrote = 0
        self.data_wrote = 0

        self.blocks_read = 0
        self.frames_read = 0
        self.data_read = 0

        self._save()

    def __str__(self):  # todo strip?
        """This is used by output_stats() in configfunctions to output a nice formatted text file showing usage
        statistics.
        """

        return ('*' * 21 + '\nStatistics\n' + '*' * 21 + f'\n\nTotal Blocks Wrote: {self.blocks_wrote}'
                                                         f'\nTotal Frames Wrote: {self.frames_wrote}'
                                                         f'\nTotal Data Wrote: {int(self.data_wrote / 8)} B'
                                                         f'\n\nTotal Blocks Read: {self.blocks_read}'
                                                         f'\nTotal Frames Read: {self.frames_read}'
                                                         f'\nTotal Data Read: {int(self.data_read / 8)} B')

    def write_update(self, blocks, frames, data):
        self.blocks_wrote += blocks
        self.frames_wrote += frames
        self.data_wrote += data
        self._save()

    def read_update(self, blocks, frames, data):
        """Deprecated.  May be removed."""

        self.blocks_read += blocks
        self.frames_read += frames
        self.data_read += data
        self._save()

    def clear_stats(self):
        self.blocks_wrote = 0
        self.frames_wrote = 0
        self.data_wrote = 0
        self.blocks_read = 0
        self.frames_read = 0
        self.data_read = 0
        self._save()


try:
    with open('statisticsmanager.bin', 'rb') as unpickler:
        stats_manager = pickle.load(unpickler)

except:
    stats_manager = StatisticsManager()
