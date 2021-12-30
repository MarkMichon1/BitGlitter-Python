from bitstring import BitArray, ConstBitStream
import cv2
import numpy

import hashlib
import itertools
import logging
import math
from pathlib import Path
from random import choice, randint

from bitglitter.write.render.renderutilities import render_coords_generator


class BitsToColor:
    """This generates a dictionary linking a string binary value to an RGB value.  This is how binary data gets directly
    converted to colors.  This step required more than a dictionary, as additional logic was required to switch between
    a standard dictionary used by default and custom palettes, and 24 bit palettes.  They both convert data to colors in
    different ways, and this provides a single clean interface for that.
    """

    def __init__(self, color_set_tupled, bit_length, palette_name):

        logging.debug(f'Generating encoder for {palette_name}...')
        self.color_set_tupled = color_set_tupled
        self.bit_length = bit_length
        self.return_value = self.generate_dictionary()

    @staticmethod
    def twenty_four_bit_values(bit_value):

        red_channel = bit_value.read('uint : 8')
        green_channel = bit_value.read('uint : 8')
        blue_channel = bit_value.read('uint : 8')
        return red_channel, green_channel, blue_channel

    def generate_dictionary(self):

        color_dict = {}
        if self.bit_length != 24:

            for value in range(len(self.color_set_tupled)):
                temp_bin_holder = str(BitArray(uint=value, length=self.bit_length))
                temp_bin_holder = ConstBitStream(temp_bin_holder)
                color_dict[temp_bin_holder] = self.color_set_tupled[value]
            return color_dict

        else:
            return self.twenty_four_bit_values

    def get_color(self, value):

        if self.bit_length != 24:
            return self.return_value[value]
        else:
            return self.return_value(value)


class ColorsToBits:
    """This class does the exact opposite as BitsToColor.  This first generates a dictionary linking colors to
    specific bit values, and then get_value() accomplishes that.  It is worth noting that 24 bit color functions
    differently than the other color palettes, in that it doesn't use a dictionary, but rather converts each byte into
    an unsigned integer for each of it's three color channels, and then returns that color.
    """

    def __init__(self, color_set_tupled, bit_length, palette_name):
        logging.debug(f'Generating decoder for {palette_name}...')
        self.color_set_tupled = color_set_tupled
        self.bit_length = bit_length
        self.return_value = self.generate_dictionary()

    @staticmethod
    def twenty_four_bit_values(color):
        outgoing_data = BitArray()
        for color_channel in color:
            outgoing_data.append(BitArray(uint=color_channel, length=8))
        return outgoing_data

    def generate_dictionary(self):
        value_dict = {}

        if self.bit_length != 24:
            for value in range(len(self.color_set_tupled)):
                temp_bin_holder = str(BitArray(uint=value, length=self.bit_length))
                temp_bin_holder = ConstBitStream(temp_bin_holder)
                value_dict[self.color_set_tupled[value]] = temp_bin_holder
            return value_dict
        else:
            return self.twenty_four_bit_values

    def get_value(self, color):
        if self.bit_length != 24:
            return self.return_value[color]
        else:
            return self.return_value(color)


def convert_hex_to_rgb(color_set):
    """Takes the palette color set, converts any hex values into tuples, and returns a integer tuple of the R/G/B
    color channels.
    """

    returned_list = []
    for color in color_set:
        if isinstance(color, str):  # is hex code
            stripped = color.replace('#', '')
            returned_list.append(tuple(int(stripped[i:i + 2], 16) for i in (0, 2, 4)))
        else:  # Does nothing if already a tuple, simply adds it back to list to be returned.
            returned_list.append(color)
    return returned_list


def get_color_distance(color_set):
    """This function takes in the set of tuples in a palette, and calculates their proximity to each other in RGB space.
    Higher number denote 'safer' palettes to use in the field, as they are less prone to errors in the field.  Getting 0
    returned means you have at least a single pair of identical RGB values.  All colors must be unique!
    """

    min_distance = None
    for pair in itertools.combinations(color_set, 2):
        first_color, second_color = pair

        red_distance = (second_color[0] - first_color[0]) ** 2
        green_distance = (second_color[1] - first_color[1]) ** 2
        blue_distance = (second_color[2] - first_color[2]) ** 2

        sum_of_distances = math.sqrt(red_distance + green_distance + blue_distance)

        if min_distance is not None:
            if sum_of_distances < min_distance:
                min_distance = sum_of_distances
        else:
            min_distance = sum_of_distances

    return round(min_distance, 3)


def get_palette_id_from_hash(name, description, time_created, color_set):
    """Taking in the various parameters, this creates a unique ID for the custom palettes."""

    # Normalizes list brackets to tuples to ensure consistent hashing across context/usage
    color_set_string = str(color_set)
    color_set_string.replace('[', '(')
    color_set_string.replace(']', ')')

    hasher = hashlib.sha256(str(name + description + str(time_created) + color_set_string).encode())
    return hasher.hexdigest()


def render_sample_frame(palette_name, palette_colors_rgb_tuple, is_24_bit, save_path, block_width, block_height,
                        pixel_width):

    image = numpy.zeros((pixel_width * block_height, pixel_width * block_width, 3), dtype='uint8')
    next_coordinates = render_coords_generator(block_height, block_width, pixel_width, False)
    for i in range(block_width * block_height):
        if not is_24_bit:
            chosen_color = choice(palette_colors_rgb_tuple)
        else:
            chosen_color = (randint(0, 255), randint(0, 255), randint(0, 255))
        block_coordinates = next(next_coordinates)
        cv2.rectangle(image, (block_coordinates[0], block_coordinates[1]), (block_coordinates[2], block_coordinates[3]),
                      (chosen_color[2], chosen_color[1], chosen_color[0]), -1)

    save_directory = Path(save_path)
    save_path = save_directory / f'{palette_name}.png'
    cv2.imwrite(str(save_path), image)
