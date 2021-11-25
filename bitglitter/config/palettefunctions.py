import ast
import base64
import logging
import time

from bitglitter.config.config import session
from bitglitter.config.palettemodels import Palette
from bitglitter.utilities.palette import get_palette_id_from_hash, render_sample_frame
from bitglitter.validation.utilities import proper_string_syntax
from bitglitter.validation.validatepalette import custom_palette_values_validate


def _convert_palette_to_dict(palette):
    """Minimizing duplicate code"""
    return {'is_24_bit': palette.is_24_bit, 'is_custom': palette.is_custom, 'is_included_with_repo':
            palette.is_included_with_repo, 'palette_id': palette.palette_id, 'name': palette.name, 'description':
            palette.description, 'nickname': palette.nickname, 'color_set': palette.convert_colors_to_tuple(),
            'color_distance': palette.color_distance, 'number_of_colors': palette.number_of_colors, 'bit_length':
            palette.bit_length, 'time_created': palette.time_created, 'base64_string': palette.base64_string}


def _return_palette(palette_id=None, palette_nickname=None):
    """Internal function for returning the actual palette model.  The function below is to return an end-user friendly
    dictionary model.
    """
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


def return_palette(palette_id=None, palette_nickname=None):
    palette = _return_palette(palette_id, palette_nickname)
    if palette:
        return _convert_palette_to_dict(palette)
    else:
        return None


def add_custom_palette(palette_name, color_set, nickname=None, palette_description=''):
    custom_palette_values_validate(palette_name, palette_description, color_set)

    proper_string_syntax(palette_name)
    if palette_description:
        proper_string_syntax(palette_description)

    palette = session.query(Palette).filter(Palette.name == palette_name).first()
    if palette:
        raise ValueError(f'Name {palette_name} is already taken, please choose another.')

    if nickname:
        proper_string_syntax(nickname)
        palette = session.query(Palette).filter(Palette.nickname == nickname).first()
        if palette:
            raise ValueError(f"Nickname '{nickname}' is already taken, please choose another.")

    new_palette = Palette.create(is_valid=True, is_custom=True, name=palette_name, palette_id='', nickname=nickname,
                                 description=palette_description, time_created=int(time.time()), color_set=color_set)

    return new_palette.palette_id


def remove_custom_palette(palette_id=None, nickname=None):
    """Removes custom palette completely from the database."""

    palette = _return_palette(palette_id, nickname)
    palette.delete()


def edit_nickname_to_custom_palette(palette_id=None, existing_nickname=None, new_nickname=None):
    """This changes the nickname of the given palette to something new, first checking if its valid."""

    if not new_nickname:
        raise ValueError('Must include a new nickname')

    palette = _return_palette(palette_id, existing_nickname)
    already_existing_with_nickname = session.query(Palette).filter(Palette.nickname == new_nickname).first()
    if already_existing_with_nickname:
        raise ValueError(f'Palette {already_existing_with_nickname.name} already uses this nickname.')
    else:
        palette.nickname = new_nickname
        palette.save()


def remove_custom_palette_nickname(palette_id=None, existing_nickname=None):
    """Removes the palette nickname.  This does not delete the palette, only the nickname."""

    palette = _return_palette(palette_id, existing_nickname)
    palette.nickname = None
    palette.save()


def remove_all_custom_palette_nicknames():
    """Removes all custom palette nicknames, including those included with default data.  This does not delete the
    palettes themselves.
    """

    palettes = session.query(Palette).filter(Palette.is_custom)
    for palette in palettes:
        palette.nickname = None
        palette.save()


def return_all_palettes():
    palettes = session.query(Palette).all()
    returned_list = []
    for palette in palettes:
        returned_list.append(_convert_palette_to_dict(palette))
    return returned_list


def return_default_palettes():
    palettes = session.query(Palette).filter(Palette.is_custom == False)
    returned_list = []
    for palette in palettes:
        returned_list.append(_convert_palette_to_dict(palette))
    return returned_list


def return_custom_palettes():
    palettes = session.query(Palette).filter(Palette.is_custom == True)
    returned_list = []
    for palette in palettes:
        returned_list.append(_convert_palette_to_dict(palette))

    return returned_list


def remove_all_custom_palettes():
    """Removes all custom palettes from the database."""
    session.query(Palette).filter(Palette.is_custom).delete()
    session.commit()
    return True


def generate_sample_frame(directory_path, palette_id=None, palette_nickname=None, all_palettes=False,
                          include_default=False, pixel_width=20, block_height=20, block_width=20):
    """Prints a small sample frame of a given palette to give an idea of its appearance in normal rendering, selecting
    random colors from the palette for each of the blocks.  Alternatively, if all_palettes=True, all palettes in the
    database will be generated.  Argument include_default toggles whether default palettes are included as well.  Can
    optionally control the size of the sample frames with the last 3 arguments.
    """

    if not all_palettes:
        palette = _return_palette(palette_id=palette_id, palette_nickname=palette_nickname)
        render_sample_frame(palette.name, palette.convert_colors_to_tuple(), palette.is_24_bit, directory_path,
                            block_width, block_height, pixel_width)
    else:
        if include_default:
            palettes = session.query(Palette).all()
        else:
            palettes = session.query(Palette).filter(Palette.is_custom)
        for palette in palettes:
            render_sample_frame(palette.name, palette.convert_colors_to_tuple(), palette.is_24_bit, directory_path,
                                block_width, block_height, pixel_width)


def import_palette_base64(base64_string):
    decoded_string = base64.b64decode(base64_string.encode()).decode()
    returned_list = decoded_string.split('\\\\')
    palette_id = returned_list[0]
    palette_name = returned_list[1]
    palette_description = returned_list[2]
    time_created = returned_list[3]
    color_set_str = returned_list[4]
    invalid_characters = returned_list[5]
    if invalid_characters != '':
        raise ValueError('Corrupted string.  Please ensure you have the full b64 string and try again.')

    # Validating data to ensure no funny business
    calculated_hash = get_palette_id_from_hash(palette_name, palette_description, time_created, color_set_str)
    if calculated_hash != palette_id:
        raise ValueError('Corrupted string.  Please ensure you have the full b64 string and try again.')

    palette = session.query(Palette).filter(Palette.palette_id == palette_id).first()
    if palette:
        raise ValueError('Palette already exists locally!')
    palette = session.query(Palette).filter(Palette.name == palette_name).first()
    if palette:
        raise ValueError('Palette with this name already exists.')

    color_set_list = ast.literal_eval(color_set_str)
    custom_palette_values_validate(palette_name, palette_description, color_set_list)

    palette = Palette.create(palette_id=palette_id, is_valid=True, is_custom=True, name=palette_name,
                             description=palette_description, time_created=time_created, color_set=color_set_list)

    return palette.palette_id


def export_palette_base64(palette_id=None, palette_nickname=None):
    palette = _return_palette(palette_id=palette_id, palette_nickname=palette_nickname)
    if not palette.is_valid:
        raise ValueError('Cannot export invalid palettes')

    return palette.base64_string


def import_custom_palette_from_header(palette_id, stream_header_palette_id, palette_name, palette_description,
                                      time_created, number_of_colors, color_list):
    """Validates values, and creates and returns palette."""
    if palette_id != stream_header_palette_id:
        logging.warning('Corrupted data in palette header, cannot continue.  Aborting...')
        return False

    calculated_id = get_palette_id_from_hash(palette_name, palette_description, time_created, str(color_list))
    if calculated_id != stream_header_palette_id:
        logging.warning('Calculated palette ID / Stream header palette ID mismatch, cannot continue.  Aborting...')
        return False

    if custom_palette_values_validate(palette_name, palette_description, color_list) == False or \
            len(color_list) != number_of_colors:
        logging.warning('Corrupted palette header values, cannot continue.  Aborting...')
        return False

    palette = Palette.create(palette_id=palette_id, is_valid=True, is_custom=True, name=palette_name,
                             description=palette_description, time_created=time_created, color_set=color_list)
    return {'palette': palette}
