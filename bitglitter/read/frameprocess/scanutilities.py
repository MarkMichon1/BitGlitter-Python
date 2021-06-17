import math

import numpy


def return_distance(raw_frame_rgb, expected_value):
    return math.sqrt(((raw_frame_rgb[0] - expected_value[0]) ** 2) + ((raw_frame_rgb[1] - expected_value[1]) ** 2) +
                     ((raw_frame_rgb[2] - expected_value[2]) ** 2))


def color_snap(raw_frame_rgb, palette_color_list):
    closest_palette_match = None
    closest_distance = 500
    for palette in palette_color_list:
        active_distance = return_distance(raw_frame_rgb, palette)
        if active_distance < closest_distance:
            closest_palette_match = palette
            closest_distance = active_distance
    return closest_palette_match


def scan_block(image, pixel_width, block_width_position, block_height_position):
    """This function is what's used to scan the blocks used.  First the scan area is determined, and then each of the
    pixels in that area appended to a list.  An average of those values as type int is returned.
    """

    if pixel_width < 5:
        start_position_x = int(block_width_position * pixel_width)
        end_position_x = int((block_width_position * pixel_width) + pixel_width - 1)
        start_position_y = int(block_height_position * pixel_width)
        end_position_y = int((block_height_position * pixel_width) + pixel_width - 1)

    else:
        start_position_x = int(round((block_width_position * pixel_width) + (pixel_width * .25), 1))
        end_position_x = int(round(start_position_x + (pixel_width * .5), 1))
        start_position_y = int(round((block_height_position * pixel_width) + (pixel_width * .25), 1))
        end_position_y = int(round(start_position_y + (pixel_width * .5), 1))

    numpy_output = numpy.flip(image[start_position_y:end_position_y, start_position_x:end_position_x]).mean(axis=(0, 1))
    to_list_format = numpy_output.tolist()

    for value in range(3):
        to_list_format[value] = int(to_list_format[value])

    return to_list_format
