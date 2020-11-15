import pickle

from bitglitter.read.assembler import Assembler
from bitglitter.config.components.components_to_split_up import PaletteHandler, Statistics


class AppConfig:
    '''This is the master object that holds all session data.'''

    def __init__(self):

        self.color_handler = PaletteHandler()
        self.stats_handler = Statistics()
        self.save_handler = None
        self.assembler = Assembler() #todo delegate to^^^^
        self.assembler.clear_partial_saves() # Deleting old folder if new config object must be made.

        self.save_session()

    # Reserved for next release, introducing presets
    # preset_dict = {}

    def save_session(self):
        with open('config.pickle', 'wb') as pickleSaver:
            pickle.dump(self, pickleSaver)

    def ffmpeg_verify(self):
        """At the beginning of each config load, check to see if ffmpeg binary is present.  If not, download."""
        pass

#todo: move this into __init__
try:
    with open ('config.bin', 'rb') as pickleLoad:
        config = pickle.load(pickleLoad)

except:
    config = AppConfig()