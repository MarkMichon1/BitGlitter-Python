from bitglitter.utilities.palette import get_color_distance
from bitglitter.validation.utilities import proper_string_syntax


def palette_geometry_verify(stream_palette_bit_length, block_width, block_height, output_type, fps=0):
    """This function calculates the necessary overhead for both images and videos for subsequent frames after 1.  It
    returns a number between 0-100%, for what percentage the overhead occupies.  The lower the value, the higher the
    frame efficiency.
    """

    total_blocks = block_width * block_height

    INITIALIZER_OVERHEAD = block_height + block_width + 579
    FRAME_HEADER_BITS = 352
    occupied_blocks = 0

    if output_type == 'image':
        total_blocks -= INITIALIZER_OVERHEAD
        occupied_blocks += INITIALIZER_OVERHEAD
    bits_available_per_frame = (total_blocks * stream_palette_bit_length) - FRAME_HEADER_BITS
    occupied_blocks += int(FRAME_HEADER_BITS / stream_palette_bit_length)

    payload_frame_percentage = round((((total_blocks - occupied_blocks) / total_blocks) * 100), 2)

    output_per_sec = 0
    if output_type == 'video':
        output_per_sec = bits_available_per_frame * fps

    return payload_frame_percentage, bits_available_per_frame, output_per_sec


def custom_palette_values_validate(name_string, description_string, color_set, read_mode=False):

    proper_string_syntax(name_string)
    proper_string_syntax(description_string)

    if len(name_string) > 50:
        if read_mode:
            return False
        raise ValueError('Custom palette names cannot exceed 50 characters.')
    if len(description_string) > 100:
        if read_mode:
            return False
        raise ValueError('Custom palette descriptions cannot exceed 100 characters.')
    if len(color_set) > 256:
        if read_mode:
            return False
        raise ValueError('Custom palettes cannot exceed 256 colors.')

    # Verifying color set parameters.  2^n length, 3 values per color, values are type int, values are 0-255.
    if len(color_set) % 2 != 0 or len(color_set) < 2:
        if read_mode:
            return False
        raise ValueError(
            "Length of color set must be 2^n length (2 colors, 4, 8, etc) with a minimum of two colors.")

    for color_tuple in color_set:

        if len(color_tuple) != 3:
            if read_mode:
                return False
            raise ValueError("Each color needs 3 entries, for red green and blue.")

        for color in color_tuple:
            if not isinstance(color, int) or color < 0 or color > 255:
                if read_mode:
                    return False
                raise ValueError("For each RGB value, it must be an integer between 0 and 255.")

    # Finally, verify colors aren't overlapping (ie, the same color is used twice).
    min_distance = get_color_distance(color_set)
    if min_distance == 0:
        if read_mode:
            return False
        raise ValueError("Calculated color distance is 0.  This occurs when you have two identical colors in your"
                         "palette.  This breaks the communication protocol.  See BitGlitter guide for more "
                         "information.")

    return True
