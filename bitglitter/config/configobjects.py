import pickle

from bitglitter.palettes.paletteobjects import DefaultPalette, TwentyFourBitPalette
from bitglitter.read.assembler import Assembler


class Config:
    '''This is the master object that holds all session data.'''

    def __init__(self):

        self.color_handler = PaletteHandler()
        self.stats_handler = Statistics()
        self.assembler = Assembler()
        self.assembler.clear_partial_saves() # Deleting old folder if new config object must be made.

        self.save_session()

    # Reserved for next release, introducing presets
    # preset_dict = {}

    def save_session(self):
        with open('config.pickle', 'wb') as pickleSaver:
            pickle.dump(self, pickleSaver)


class Statistics:
    '''Read and write values are held in this object.  It's attributes are changed through method calls.'''

    def __init__(self):

        self.blocks_wrote = 0
        self.frames_wrote = 0
        self.data_wrote = 0

        self.blocks_read = 0
        self.frames_read = 0
        self.data_read = 0

    def __str__(self):
        '''This is used by output_stats() in configfunctions to output a nice formatted text file showing usage
        statistics.
        '''

        return('*' * 21 + '\nStatistics\n' + '*' * 21 + f'\n\nTotal Blocks Wrote: {self.blocks_wrote}'
                                                                f'\nTotal Frames Wrote: {self.frames_wrote}'
                                                                f'\nTotal Data Wrote: {int(self.data_wrote / 8)} B'
                                                                f'\n\nTotal Blocks Read: {self.blocks_read}'
                                                                f'\nTotal Frames Read: {self.frames_read}'
                                                                f'\nTotal Data Read: {int(self.data_read / 8)} B')

    def write_update(self, blocks, frames, data):
        self.blocks_wrote += blocks
        self.frames_wrote += frames
        self.data_wrote += data


    def read_update(self, blocks, frames, data):
        '''Deprecated.  May be removed.'''

        self.blocks_read += blocks
        self.frames_read += frames
        self.data_read += data

    def clear_stats(self):
        self.blocks_wrote = 0
        self.frames_wrote = 0
        self.data_wrote = 0
        self.blocks_read = 0
        self.frames_read = 0
        self.data_read = 0


class PaletteHandler:
    '''This handles all palettes both default and custom.  Please note that default palettes are created here as well.
    All functions available in palettefunctions module that deal with custom palettes are interfacing with dictionaries
    custom_palette_list and custom_palette_nickname_list in this object.
    '''

    def __init__(self):
        self.default_palette_list = {'1' : DefaultPalette("1 Bit Default",
                            "Two colors, black and white.  While it has the lowest density of one bit of data per "
                            "pixel, it has the highest reliability.", ((0,0,0), (255,255,255)), 441.67, 1),

                            '11' : DefaultPalette("1 Bit Default Alternate",
                            "Uses cyan/magenta instead of white/black.",
                            ((255, 0, 255), (0, 255, 255)), 360.12, 11),

                            '2' : DefaultPalette("2 Bit Default", "Four colors; black, red, green, blue.",
                            ((0,0,0), (255,0,0), (0,255,0), (0,0,255)), 255, 2),

                            '22': DefaultPalette("2 Bit Default Alternate", "Four colors; black, magenta, cyan, yellow.",
                            ((0, 0, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255)), 255, 22),

                            '3' : DefaultPalette("3 Bit Default",
                            "Eight colors.", ((0,0,0), (255,0,0), (0,255,0), (0,0,255), (255,255,0), (0,255,255),
                            (255,0,255), (255,255,255)), 255, 3),

                            '4' : DefaultPalette("4 Bit Default", "Sixteen colors.", ((0,0,0), (128,128,128),
                            (192,192,192), (128,0,0), (255,0,0), (128,128,0), (255,255,0), (0,255,0), (0,128,128),
                            (0,128,0), (0,0,128), (0,0,255), (0,255,255), (128,0,128), (255,0,255), (255,255,255)),
                                                        109.12, 4),

                            '6' : DefaultPalette("6 Bit Default", "Sixty-four colors.", ((0,0,0), (0,0,85),
                            (0,0,170), (0,0,255), (0,85,0), (0,85,85), (0,85,170), (0,85,255), (0,170,0), (0,170,85),
                            (0,170,170), (0,170,255), (0,255,0), (0,255,85), (0,255,170), (0,255,255), (85,0,0),
                            (85,0,85), (85,0,170), (85,0,255), (85,85,0), (85,85,85), (85,85,170), (85,85,255),
                            (85,170,0), (85,170,85), (85,170,170), (85,170,255), (85,255,0), (85,255,85), (85,255,170),
                            (85,255,255), (170,0,0), (170,0,85), (170,0,170), (170,0,255), (170,85,0), (170,85,85),
                            (170,85,170), (170,85,255), (170,170,0), (170,170,85), (170,170,170), (170,170,255),
                            (170,255,0), (170,255,85), (170,255,170), (170,255,255), (255,0,0), (255,0,85), (255,0,170),
                            (255,0,255), (255,85,0), (255,85,85), (255,85,170), (255,85,255), (255,170,0), (255,170,85),
                            (255,170,170), (255,170,255), (255,255,0), (255,255,85), (255,255,170), (255,255,255)), 85,
                            6),

                            '24': TwentyFourBitPalette()
                            }

        self.custom_palette_list = {}
        self.custom_palette_nickname_list = {}
