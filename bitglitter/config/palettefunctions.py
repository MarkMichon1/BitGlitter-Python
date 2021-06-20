from bitglitter.config.palettes import palette_manager


def add_custom_palette(palette_name, palette_description, color_set, optional_nickname=""):

    id = palette_manager.add_custom_palette(palette_name, palette_description, color_set, optional_nickname)
    return id


def remove_custom_palette(id_or_nick):
    """Removes custom palette completely from the config file."""

    palette_manager.remove_custom_palette(id_or_nick)


def edit_nickname_to_custom_palette(id_or_nick, new_name):
    """This changes the nickname of the given palette to something new, first checking if it's valid."""

    palette_manager.edit_nickname_to_custom_palette(id_or_nick, new_name)


def remove_custom_palette_nickname(id_or_nick):
    """Removes the palette nickname from the corresponding dictionary.  This does not delete the palette, only the
    nickname.
    """

    palette_manager.remove_custom_palette_nickname(id_or_nick)


def remove_all_custom_palette_nicknames():
    """Removes all custom palette nicknames.  This does not delete the palettes themselves."""

    palette_manager.remove_all_custom_palette_nicknames()


def return_default_palettes():
    returned_list = palette_manager.return_default_palettes()
    return returned_list


def return_custom_palettes():
    returned_list = palette_manager.return_custom_palettes()
    return returned_list


def remove_all_custom_palettes():
    """Removes all custom palettes from both the ID dictionary and nickname dictionary."""

    palette_manager.remove_all_custom_palettes()
