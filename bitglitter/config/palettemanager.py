from pathlib import Path
import pickle
import time

from bitglitter.config.basemanager import BaseManager
from bitglitter.palettes.palettes import CustomPalette, DefaultPalette, TwentyFourBitPalette
from bitglitter.palettes.utilities import get_color_distance, get_palette_id_from_hash
from bitglitter.validation.utilities import proper_string_syntax


class PaletteManager(BaseManager):
    """This handles all palettes both default and custom.  Please note that default palettes are created here as well.
    All functions available in palettefunctions module that deal with custom palettes are interfacing with dictionaries
    custom_palette_list and custom_palette_nickname_list in this object.
    """

    def __init__(self):
        super().__init__()
        self._SAVE_FILE_NAME = 'palette_state'

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

        self.custom_palette_dict = {}
        self.custom_palette_nickname_dict = {}
        self._save()

    def _return_popped_palette(self, id_or_nick):

        if id_or_nick in self.custom_palette_dict:
            palette = self.custom_palette_dict.pop(id_or_nick)
            if palette.nickname in self.custom_palette_nickname_dict:
                del self.custom_palette_nickname_dict[palette.nickname]
            self._save()
            return palette

        elif id_or_nick in self.custom_palette_nickname_dict:
            palette = self.custom_palette_nickname_dict.pop(id_or_nick)
            del self.custom_palette_dict[palette.palette_id]
            self._save()
            return palette

        else:
            raise ValueError(f"'{id_or_nick}' does not exist.")

    def add_custom_palette(self, name, description, color_set, optional_nickname):
        """Validates and then adds custom palette."""

        date_created = str(round(time.time()))
        name_string = str(name)
        description_string = str(description)
        nickname_string = str(optional_nickname)

        proper_string_syntax(name_string)
        proper_string_syntax(description_string)

        if len(name_string) > 50:
            raise ValueError('Custom palette names cannot exceed 50 characters.')
        if len(description_string) > 100:
            raise ValueError('Custom palette descriptions cannot exceed 50 characters.')
        if len(color_set) > 256:
            raise ValueError('Custom palettes cannot exceed 256 colors.')

        proper_string_syntax(nickname_string)
        if optional_nickname in palette_manager.custom_palette_nickname_dict or optional_nickname in \
                palette_manager.custom_palette_dict or optional_nickname in palette_manager.DEFAULT_PALETTE_LIST:
            raise ValueError(f"'{optional_nickname}' is already taken, please choose another nickname.")

        # Verifying color set parameters.  2^n length, 3 values per color, values are type int, values are 0-255.
        # Finally, verify colors aren't overlapping (ie, the same color is used twice).
        if len(color_set) % 2 != 0 or len(color_set) < 2:
            raise ValueError(
                "Length of color set must be 2^n length (2 colors, 4, 8, etc) with a minimum of two colors.")

        for color_tuple in color_set:

            if len(color_tuple) != 3:
                raise ValueError("Each color needs 3 entries, for red green and blue.")

            for color in color_tuple:
                if not isinstance(color, int) or color < 0 or color > 255:
                    raise ValueError("For each RGB value, it must be an integer between 0 and 255.")

        min_distance = get_color_distance(color_set)
        if min_distance == 0:
            raise ValueError("Calculated color distance is 0.  This occurs when you have two identical colors in your"
                             "\npalette.  This breaks the communication protocol.  See BitGlitter guide for more "
                             "information.")

        palette_id = get_palette_id_from_hash(name_string, description_string, date_created, color_set)

        new_palette = CustomPalette(name_string, description_string, color_set, min_distance, date_created, palette_id,
                                    nickname_string)
        self.custom_palette_dict[palette_id] = new_palette
        if nickname_string:
            self.custom_palette_nickname_dict[nickname_string] = new_palette
        self._save()

        return palette_id

    def edit_nickname_to_custom_palette(self, id_or_nick, new_nickname):
        if new_nickname not in self.custom_palette_dict \
                and new_nickname not in self.custom_palette_nickname_dict \
                and new_nickname not in self.DEFAULT_PALETTE_LIST:

            palette = self._return_popped_palette(id_or_nick)
            palette.nickname = new_nickname
            self.custom_palette_dict[palette.palette_id] = palette
            self.custom_palette_nickname_dict[palette.nickname] = palette
            self._save()

        else:
            raise ValueError(f"'{new_nickname}' is already being used, please try another.")

    def remove_custom_palette_nickname(self, id_or_nick):
        palette = self._return_popped_palette(id_or_nick)
        palette.nickname = ""
        self.custom_palette_dict[palette.palette_id] = palette
        self._save()

    def remove_all_custom_palette_nicknames(self):

        self.custom_palette_nickname_dict = {}

        for palette in self.custom_palette_dict:
            returned_palette = self.custom_palette_dict.pop(palette)
            returned_palette.nickname = ""
            self.custom_palette_dict[returned_palette.palette_id] = returned_palette

        self._save()

    def remove_custom_palette(self, id_or_nick):
        self._return_popped_palette(id_or_nick)
        self._save()

    def remove_all_custom_palettes(self):
        self.custom_palette_dict = {}
        self.custom_palette_nickname_dict = {}
        self._save()

    def return_default_palettes(self):
        returned_list = []
        for palette in self.DEFAULT_PALETTE_LIST.values():
            returned_list.append(palette.return_as_dict())
        return returned_list

    def return_custom_palettes(self):
        returned_list = []
        for palette in self.custom_palette_dict.values():
            returned_list.append(palette.return_as_dict())
        return returned_list

    def return_selected_palette(self, id_or_nickname):
        """Goes through each of the dictionaries to return the color object."""

        if id_or_nickname in self.DEFAULT_PALETTE_LIST:
            return self.DEFAULT_PALETTE_LIST[id_or_nickname]
        elif id_or_nickname in self.custom_palette_dict:
            return self.custom_palette_dict[id_or_nickname]
        elif id_or_nickname in self.custom_palette_nickname_dict:
            return self.custom_palette_nickname_dict[id_or_nickname]
        else:
            raise ValueError(f'No palettes exist with ID or nickname \'{id_or_nickname}\'.')

    def does_palette_exist(self, id_or_nickname):
        if id_or_nickname not in self.DEFAULT_PALETTE_LIST and id_or_nickname not in self.custom_palette_dict and \
                id_or_nickname not in self.custom_palette_nickname_dict:
            raise ValueError(f"Stream palette {id_or_nickname} is not a valid ID or nickname.  Verify that exact value"
                             f" exists.")


try:
    current_directory = Path(__file__).resolve().parent
    pickle_path = current_directory / 'palette_state.bin'
    with open(pickle_path, 'rb') as unpickler:
        palette_manager = pickle.load(unpickler)

except FileNotFoundError:
    palette_manager = PaletteManager()
