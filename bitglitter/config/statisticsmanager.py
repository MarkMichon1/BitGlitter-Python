import logging
from pathlib import Path
import pickle

from bitglitter.config.basemanager import BaseManager
from bitglitter.utilities.display import humanize_file_size


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

    def __str__(self):
        """This is used by output_stats() in configfunctions to output a nice formatted text file showing usage
        statistics.
        """

        return ('*' * 21 + '\nStatistics\n' + '*' * 21 + f'\n\nTotal Blocks Wrote: {self.blocks_wrote}'
                                                         f'\nTotal Frames Wrote: {self.frames_wrote}'
                                                         f'\nTotal Data Wrote: {humanize_file_size(self.data_wrote)}'
                                                         f'\n\nTotal Blocks Read: {self.blocks_read}'
                                                         f'\nTotal Frames Read: {self.frames_read}'
                                                         f'\nTotal Data Read: {int(self.data_read / 8)} B')

    def write_update(self, blocks, frames, data):
        self.blocks_wrote += blocks
        self.frames_wrote += frames
        self.data_wrote += data
        self._save()
        logging.debug(f'Write stats update:\n{blocks} new blocks, {frames} frames, {humanize_file_size(data)} data ->'
                      f' {self.blocks_wrote} total blocks, {self.frames_wrote} frames, '
                      f'{humanize_file_size(self.data_wrote)} data.')

    def read_update(self, blocks, frames, data):
        self.blocks_read += blocks  # todo add this to read
        self.frames_read += frames
        self.data_read += data
        self._save()
        logging.debug(f'Read stats update:\n{blocks} new blocks, {frames} frames, {humanize_file_size(data)} data ->'
                      f' {self.blocks_read} total blocks, {self.frames_read} frames,'
                      f' {humanize_file_size(self.data_read)} data.')

    def clear_stats(self):
        self.blocks_wrote = 0
        self.frames_wrote = 0
        self.data_wrote = 0
        self.blocks_read = 0
        self.frames_read = 0
        self.data_read = 0
        self._save()

    def return_stats(self):
        return {
            'blocks_wrote': self.blocks_wrote, 'frames_wrote': self.frames_wrote, 'data_wrote': self.data_wrote,
            'blocks_read': self.blocks_read, 'frames_read': self.frames_read, 'data_read': self.data_read,
        }


try:
    current_directory = Path(__file__).resolve().parent
    pickle_path = current_directory / 'statsmanager.bin'
    with open(pickle_path, 'rb') as unpickler:
        stats_manager = pickle.load(unpickler)

except FileNotFoundError:
    stats_manager = StatisticsManager()
