import pickle

from bitglitter.palettes.paletteobjects import DefaultPalette, TwentyFourBitPalette
from bitglitter.read.assembler import Assembler


class Config:
    '''This is the master object that holds all session data.'''

    def __init__(self):

        self.colorHandler = PaletteHandler()
        self.statsHandler = Statistics()
        self.assembler = Assembler()
        self.assembler.clearPartialSaves() # Deleting old folder if new config object must be made.

        self.saveSession()

    # Reserved for next release, introducing presets
    # presetDict = {}

    def saveSession(self):
        with open('config.pickle', 'wb') as pickleSaver:
            pickle.dump(self, pickleSaver)


class Statistics:
    '''Read and write values are held in this object.  It's attributes are changed through method calls.'''

    def __init__(self):

        self.blocksWrote = 0
        self.framesWrote = 0
        self.dataWrote = 0

        self.blocksRead = 0
        self.framesRead = 0
        self.dataRead = 0

    def __str__(self):
        '''This is used by outputStats() in configfunctions to output a nice formatted text file showing usage
        statistics.
        '''

        return('*' * 21 + '\nStatistics\n' + '*' * 21 + f'\n\nTotal Blocks Wrote: {self.blocksWrote}'
                                                                f'\nTotal Frames Wrote: {self.framesWrote}'
                                                                f'\nTotal Data Wrote: {int(self.dataWrote / 8)} B'
                                                                f'\n\nTotal Blocks Read: {self.blocksRead}'
                                                                f'\nTotal Frames Read: {self.framesRead}'
                                                                f'\nTotal Data Read: {int(self.dataRead / 8)} B')

    def writeUpdate(self, blocks, frames, data):
        self.blocksWrote += blocks
        self.framesWrote += frames
        self.dataWrote += data


    def readUpdate(self, blocks, frames, data):
        self.blocksRead += blocks
        self.framesRead += frames
        self.dataRead += data

    def clearStats(self):
        self.blocksWrote = 0
        self.framesWrote = 0
        self.dataWrote = 0
        self.blocksRead = 0
        self.framesRead = 0
        self.dataRead = 0


class PaletteHandler:
    '''This handles all palettes both default and custom.  Please note that default palettes are created here as well.
    All functions available in palettefunctions module that deal with custom palettes are interfacing with dictionaries
    customPaletteList and customPaletteNicknameList in this object.
    '''

    def __init__(self):
        self.defaultPaletteList = {'1' : DefaultPalette("1 bit default",
                            "Two colors, black and white.  While it has the lowest density of one bit of data per "
                            "pixel, it has the highest reliability.", ((0,0,0), (255,255,255)), 441.67, 1),

                                   '11' : DefaultPalette("1 bit alternate", "Uses cyan/magenta instead of white/black.",
                                                         ((255, 0, 255), (0, 255, 255)), 360.12, 11),

                                   '2' : DefaultPalette("2 bit default", "Four colors; black, red, green, blue.",
                            ((0,0,0), (255,0,0), (0,255,0), (0,0,255)), 255, 2),

                                   '22': DefaultPalette("2 bit alternate", "Four colors; black, magenta, cyan, yellow.",
                                                       ((0, 0, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255)), 255,
                                                        22),

                                   '3' : DefaultPalette("3 bit default",
                            "Eight colors.", ((0,0,0), (255,0,0), (0,255,0), (0,0,255), (255,255,0), (0,255,255),
                            (255,0,255), (255,255,255)), 255, 3),

                                   '4' : DefaultPalette("4 bit default", "Sixteen colors.", ((0,0,0), (128,128,128),
                            (192,192,192), (128,0,0), (255,0,0), (128,128,0), (255,255,0), (0,255,0), (0,128,128),
                            (0,128,0), (0,0,128), (0,0,255), (0,255,255), (128,0,128), (255,0,255), (255,255,255)),
                                                        109.12, 4),

                                   '6' : DefaultPalette("6 bit default", "Sixty-four colors.", ((0,0,0), (0,0,85),
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

        self.customPaletteList = {}
        self.customPaletteNicknameList = {}