from pathlib import Path
import pickle

from bitglitter.config.basemanager import BaseManager
from bitglitter.palettes.palettes import DefaultPalette, TwentyFourBitPalette


class PaletteManager(BaseManager):
    """This handles all palettes both default and custom.  Please note that default palettes are created here as well.
    All functions available in palettefunctions module that deal with custom palettes are interfacing with dictionaries
    custom_palette_list and custom_palette_nickname_list in this object.
    """

    def __init__(self):
        super().__init__()
        self._SAVE_FILE_NAME = 'palettemanager'

        self.DEFAULT_PALETTE_LIST = {'1': DefaultPalette("1 Bit Default",
                                                         "Two colors, black and white.  While it has the lowest "
                                                         "density of one bit of data per "
                                                         "pixel, it has the highest reliability.",
                                                         ((0, 0, 0), (255, 255, 255)), 441.67, 1),

                                     '11': DefaultPalette("1 Bit Default Alternate",
                                                          "Uses cyan/magenta instead of white/black.",
                                                          ((255, 0, 255), (0, 255, 255)), 360.12, 11),

                                     '2': DefaultPalette("2 Bit Default", "Four colors; black, red, green, blue.",
                                                         ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)), 255, 2),

                                     '22': DefaultPalette("2 Bit Default Alternate",
                                                          "Four colors; black, magenta, cyan, yellow.",
                                                          ((0, 0, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255)), 255,
                                                          22),

                                     '3': DefaultPalette("3 Bit Default",
                                                         "Eight colors.", (
                                                         (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255),
                                                         (255, 255, 0), (0, 255, 255),
                                                         (255, 0, 255), (255, 255, 255)), 255, 3),

                                     '4': DefaultPalette("4 Bit Default", "Sixteen colors.",
                                                         ((0, 0, 0), (128, 128, 128),
                                                          (192, 192, 192), (128, 0, 0), (255, 0, 0), (128, 128, 0),
                                                          (255, 255, 0), (0, 255, 0), (0, 128, 128),
                                                          (0, 128, 0), (0, 0, 128), (0, 0, 255), (0, 255, 255),
                                                          (128, 0, 128), (255, 0, 255), (255, 255, 255)),
                                                         109.12, 4),

                                     '6': DefaultPalette("6 Bit Default", "Sixty-four colors.", ((0, 0, 0), (0, 0, 85),
                                                                                                 (0, 0, 170),
                                                                                                 (0, 0, 255),
                                                                                                 (0, 85, 0),
                                                                                                 (0, 85, 85),
                                                                                                 (0, 85, 170),
                                                                                                 (0, 85, 255),
                                                                                                 (0, 170, 0),
                                                                                                 (0, 170, 85),
                                                                                                 (0, 170, 170),
                                                                                                 (0, 170, 255),
                                                                                                 (0, 255, 0),
                                                                                                 (0, 255, 85),
                                                                                                 (0, 255, 170),
                                                                                                 (0, 255, 255),
                                                                                                 (85, 0, 0),
                                                                                                 (85, 0, 85),
                                                                                                 (85, 0, 170),
                                                                                                 (85, 0, 255),
                                                                                                 (85, 85, 0),
                                                                                                 (85, 85, 85),
                                                                                                 (85, 85, 170),
                                                                                                 (85, 85, 255),
                                                                                                 (85, 170, 0),
                                                                                                 (85, 170, 85),
                                                                                                 (85, 170, 170),
                                                                                                 (85, 170, 255),
                                                                                                 (85, 255, 0),
                                                                                                 (85, 255, 85),
                                                                                                 (85, 255, 170),
                                                                                                 (85, 255, 255),
                                                                                                 (170, 0, 0),
                                                                                                 (170, 0, 85),
                                                                                                 (170, 0, 170),
                                                                                                 (170, 0, 255),
                                                                                                 (170, 85, 0),
                                                                                                 (170, 85, 85),
                                                                                                 (170, 85, 170),
                                                                                                 (170, 85, 255),
                                                                                                 (170, 170, 0),
                                                                                                 (170, 170, 85),
                                                                                                 (170, 170, 170),
                                                                                                 (170, 170, 255),
                                                                                                 (170, 255, 0),
                                                                                                 (170, 255, 85),
                                                                                                 (170, 255, 170),
                                                                                                 (170, 255, 255),
                                                                                                 (255, 0, 0),
                                                                                                 (255, 0, 85),
                                                                                                 (255, 0, 170),
                                                                                                 (255, 0, 255),
                                                                                                 (255, 85, 0),
                                                                                                 (255, 85, 85),
                                                                                                 (255, 85, 170),
                                                                                                 (255, 85, 255),
                                                                                                 (255, 170, 0),
                                                                                                 (255, 170, 85),
                                                                                                 (255, 170, 170),
                                                                                                 (255, 170, 255),
                                                                                                 (255, 255, 0),
                                                                                                 (255, 255, 85),
                                                                                                 (255, 255, 170),
                                                                                                 (255, 255, 255)), 85,
                                                         6),

                                     '24': TwentyFourBitPalette()
                                     }

        self.custom_palette_list = {}
        self.custom_palette_nickname_list = {}

        self._save()


try:
    current_directory = Path(__file__).resolve().parent
    pickle_path = current_directory / 'palettemanager.bin'
    with open(pickle_path, 'rb') as unpickler:
        palette_manager = pickle.load(unpickler)

except:
    palette_manager = PaletteManager()
