from bitglitter.config.config import session
from bitglitter.config.palettemodels import Palette
from bitglitter.utilities.palette import render_sample_frame
from bitglitter.validation.utilities import proper_string_syntax
from bitglitter.validation.validatepalette import custom_palette_values_validate


def _return_palette(palette_id=None, palette_nickname=None):

    if not palette_id and not palette_nickname:
        raise ValueError('Must include palette_id or palette_nickname to return Palette object.')
    if palette_id:
        palette = session.query(Palette).filter(Palette.palette_id == palette_id).first()
    else:
       palette = session.query(Palette).filter(Palette.nickname == palette_nickname).first()
    if palette:
        return palette
    else:
        raise ValueError('No existing palettes with this palette_id or palette_nickname.')


def add_custom_palette(palette_name, color_set=None, nickname=None, palette_description=None, only_accept_valid=True):


    # TEMP NOTE:
    name_string = str(palette_name)
    description_string = str(palette_description) if palette_description else ''
    nickname_string = str(nickname) if nickname else ''

    proper_string_syntax(name_string)
    if description_string:
        proper_string_syntax(description_string)

    palette_id = None
    return palette_id


def remove_custom_palette(palette_id, nickname):
    """Removes custom palette completely from the database."""

    palette = _return_palette(palette_id, nickname)
    palette.delete()


def edit_nickname_to_custom_palette(palette_id, existing_nickname, new_nickname):
    """This changes the nickname of the given palette to something new, first checking if its valid."""

    palette = _return_palette(palette_id, existing_nickname)
    already_existing_with_nickname = session.query(Palette).filter(Palette.nickname == new_nickname).first()
    if already_existing_with_nickname:
        raise ValueError(f'Palette {already_existing_with_nickname.name} already uses this nickname.')
    else:
        palette.nickname = new_nickname
        palette.save()


def remove_custom_palette_nickname(palette_id, existing_nickname):
    """Removes the palette nickname.  This does not delete the palette, only the nickname."""

    palette = _return_palette(palette_id, existing_nickname)
    palette.nickname = None
    palette.save()


def remove_all_custom_palette_nicknames():
    """Removes all custom palette nicknames, including those included with default data.  This does not delete the
    palettes themselves.
    """

    palettes = session.query(Palette).filter(Palette.is_custom == True)
    for palette in palettes:
        palette.nickname = None
        palette.save()


def return_default_palettes():
    returned_list = session.query(Palette).filter(Palette.is_custom == False)
    return returned_list


def return_custom_palettes():
    returned_list = session.query(Palette).filter(Palette.is_custom == True)
    return returned_list


def remove_all_custom_palettes():
    """Removes all custom palettes from the database."""
    session.query(Palette).filter(Palette.is_custom == True).delete()


def generate_sample_frame(path, palette_id=None, palette_nickname=None, all_palettes=False, include_default=False):
    """Prints a small sample frame of a given palette to give an idea of its appearance in normal rendering, selecting
    random colors from the palette for each of the blocks.  Alternatively, if all_palettes=True, all palettes in the
    database will be generated.  Argument include_default toggles whether default palettes are included as well.
    """

    if not all_palettes:
        palette = _return_palette(palette_id=palette_id, palette_nickname=palette_nickname)
        render_sample_frame(palette.name, palette._convert_colors_to_tuple(), palette.is_24_bit, path)
    else:
        if include_default:
            palettes = session.query(Palette).all()
        else:
            palettes = session.query(Palette).filter(Palette.is_custom == True)
        for palette in palettes:
            render_sample_frame(palette.name, palette._convert_colors_to_tuple(), palette.is_24_bit, path)


def import_palette_base64(base64_string):
    palette = None
    # Validating data to ensure no funny business

    new_palette = Palette()
    return palette


def export_palette_base64(palette_id=None, palette_nickname=None):
    palette = _return_palette(palette_id=palette_id, palette_nickname=palette_nickname)
    assembled_string = ''
    to_b64 = assembled_string
    return to_b64