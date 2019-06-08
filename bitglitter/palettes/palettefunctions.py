import os
import time

from bitglitter.config.config import config
from bitglitter.palettes.paletteutilities import _add_custom_palette_direct, color_distance, return_palette_id
from bitglitter.utilities.generalverifyfunctions import proper_string_syntax

# All of these functions are for end users except for _dict_popper.

def _dict_popper(id_or_nick):
    '''This is an internal function used for remove_custom_palette(), edit_nickname_to_custom_palette(), and
    clear_custom_palette_nicknames().  Since a user can either either the palette ID OR it's nickname as an argument,
    first we must check whether that key exists.  If it does, it will check both dictionaries in the ColorHandler object
    for custom colors, custom_palette_list and custom_palette_nickname_list.  It will then delete both dictionary keys
    (if available), and  then return the object to optionally be modified (or otherwise discarded)
    '''

    if id_or_nick in config.color_handler.custom_palette_nickname_list:
        temp_holder = config.color_handler.custom_palette_nickname_list[id_or_nick]
        del config.color_handler.custom_palette_list[temp_holder.id]
        return config.color_handler.custom_palette_nickname_list.pop(id_or_nick)

    elif id_or_nick in config.color_handler.custom_palette_list:
        temp_holder = config.color_handler.custom_palette_list[id_or_nick]
        if temp_holder.nickname in config.color_handler.custom_palette_nickname_list:
            del config.color_handler.custom_palette_nickname_list[temp_holder.nickname]
        return config.color_handler.custom_palette_list.pop(id_or_nick)

    else:
        raise ValueError(f"'{id_or_nick}' does not exist.")


def add_custom_palette(palette_name, palette_description, color_set, optional_nickname =""):
    '''This function allows you to save a custom palette to be used for future writes.  Arguments needed are name,
    description, color set, which is a tuple of tuples, and optionally a nickname.  All other object are attributes are
    added in this process.  Before anything gets added, we need to ensure the arguments are valid.
    '''

    date_created = str(round(time.time()))
    name_string = str(palette_name)
    description_string = str(palette_description)
    nickname_string = str(optional_nickname)

    # Is name, description legal characters?
    proper_string_syntax(name_string)
    proper_string_syntax(description_string)

    # Is nickname legal characters?  Is the name available?
    proper_string_syntax(nickname_string)
    if optional_nickname in config.color_handler.custom_palette_nickname_list or optional_nickname in \
            config.color_handler.custom_palette_list or optional_nickname in config.color_handler.default_palette_list:
        raise ValueError(f"'{optional_nickname}' is already taken, please choose another nickname.")

    # Verifying color set parameters.  2^n length, 3 values per color, values are type int, values are 0-255.  Finally,
    # verify colors aren't overlapping (ie, the same color is used twice).
    if len(color_set) % 2 != 0 or len(color_set) < 2:
        raise ValueError("Length of color set must be 2^n length (2 colors, 4, 8, etc) with a minimum of two colors.")

    for color_tuple in color_set:

        if len(color_tuple) != 3:
            raise ValueError("Each color needs 3 entries, for red green and blue.")

        for color in color_tuple:
            if not isinstance(color, int) or color < 0 or color > 255:
                raise ValueError("For each RGB value, it must be an integer between 0 and 255.")

    min_distance = color_distance(color_set)
    if min_distance == 0:
        raise ValueError("Calculated color distance is 0.  This occurs when you have two identical colors in your"
              "\npalette.  This breaks the communication protocol.  See BitGlitter guide for more information.")

    '''At this point, assuming no errors were raised, we're ready to instantiate the custom color object.  This function
    creates an identification for the object.  For as long as the palette exists, this is a permanent ID that can be
    used as an argument for colorID in write().  This value will get returned at the end of this function.
    '''

    id = return_palette_id(name_string, description_string, date_created, color_set)
    _add_custom_palette_direct(name_string, description_string, color_set, min_distance, date_created, id,
                               nickname_string)
    return id


def remove_custom_palette(id_or_nick):
    '''Removes custom palette completely from the config file.'''

    _dict_popper(id_or_nick)
    config.save_session()


def edit_nickname_to_custom_palette(id_or_nick, new_name):
    '''This changes the nickname of the given palette to something new, first checking if it's valid.'''

    if new_name not in config.color_handler.custom_palette_list \
            and new_name not in config.color_handler.custom_palette_nickname_list \
            and new_name not in config.color_handler.default_palette_list:

        temp_holder = _dict_popper(id_or_nick)
        temp_holder.nickname = new_name
        config.color_handler.custom_palette_list[temp_holder.id] = temp_holder
        config.color_handler.custom_palette_nickname_list[temp_holder.nickname] = temp_holder
        config.save_session()

    else:
        raise ValueError(f"'{new_name}' is already being used, please try another.")


def remove_custom_palette_nickname(id_or_nick):
    '''Removes the palette nickname from the corresponding dictionary.  This does not delete the palette, only the
    nickname.
    '''

    temp_holder = _dict_popper(id_or_nick)
    temp_holder.nickname = ""
    config.color_handler.custom_palette_list[temp_holder.id] = temp_holder
    config.save_session()


def clear_custom_palette_nicknames():
    '''Clears all custom palette nicknames.  This does not delete the palettes themselves.'''

    config.color_handler.custom_palette_nickname_list = {}

    for palette in config.color_handler.custom_palette_list:

        temp_holder = config.color_handler.custom_palette_list.pop(palette)
        temp_holder.nickname = ""
        config.color_handler.custom_palette_list[temp_holder.id] = temp_holder

    config.save_session()


def print_full_palette_list(path):
    '''Writes a text file to a file path outlining available color palettes.'''

    active_path = os.path.join(os.getcwd(), path)

    with open(active_path + '\\BitGlitter Palette List.txt', 'w') as writer:

        writer.write('*' * 21 + '\nDefault Palettes\n' + '*' * 21 + '\n')

        for some_key in config.color_handler.default_palette_list:
            writer.write('\n' + str(config.color_handler.default_palette_list[some_key]) + '\n')

        writer.write('*' * 21 + '\nCustom Palettes\n' + '*' * 21 + '\n')

        if config.color_handler.custom_palette_list:

            for some_key in config.color_handler.custom_palette_list:
                writer.write('\n' + str(config.color_handler.custom_palette_list[some_key]) + '\n')

        else:
            writer.write('\nNo custom palettes (yet)')


def clear_all_custom_palettes():
    '''Removes all custom palettes from both the ID dictionary and nickname dictionary.'''

    config.colorHandler.custom_palette_nickname_list = {}
    config.colorHandler.custom_palette_list = {}
    config.save_session()