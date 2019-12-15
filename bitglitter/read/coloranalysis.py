import math

def return_distance(raw_frame_rgb, expected_value):
    return math.sqrt(((raw_frame_rgb[0] - expected_value[0]) ** 2) + ((raw_frame_rgb[1] - expected_value[1]) ** 2) +
                     ((raw_frame_rgb[2] - expected_value[2]) ** 2))

def color_snap(raw_frame_rgb, palette_color_list):

    closest_match = None
    closest_distance = 500
    for color in palette_color_list:

        active_distance = return_distance(raw_frame_rgb, color)
        if active_distance < closest_distance:
            closest_match = color
            closest_distance = active_distance
    return closest_match