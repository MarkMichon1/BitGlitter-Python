import logging

from bitstring import BitArray, ConstBitStream
from numpy import flip

from bitglitter.read.coloranalysis import color_snap, return_distance
from bitglitter.read.decoderassets import scan_block
from bitglitter.palettes.paletteutilities import palette_grabber, ColorsToValue


def frame_lock_on(image, block_height_override, block_width_override, frame_width, frame_height):
    '''This function is used to lock onto the frame.  If override values are present, these will be used.  Otherwise,
    it will attempt to extract the correct values from the X and Y calibrator on the initial frame.'''

    logging.debug('Locking onto frame...')
    initializer_palette_a = palette_grabber('1')
    initializer_palette_b = palette_grabber('11')
    initializer_palette_a_dict = ColorsToValue(initializer_palette_a)
    initializer_palette_b_dict = ColorsToValue(initializer_palette_b)
    combined_colors = initializer_palette_a.color_set + initializer_palette_b.color_set

    if block_height_override and block_width_override: # Jump straight to verification
        logging.info("block_height_override and block_width_override parameters detected.  Attempting to lock with "
                     "these values...")
        pixel_width = ((frame_width / block_width_override) + (frame_height / block_height_override)) / 2

        checkpoint = verify_blocks_x(image, pixel_width, block_width_override, combined_colors,
                                     initializer_palette_a_dict, initializer_palette_b_dict, override=True)
        if checkpoint == False:
                return False, False, False

        checkpoint = verify_blocks_y(image, pixel_width, block_height_override, combined_colors,
                                     initializer_palette_a_dict, initializer_palette_b_dict, override=True)
        if checkpoint == False:
                return False, False, False

        block_width, block_height = block_width_override, block_height_override

    else:
        # First checkpoint.  Does pixel 0,0 have color_distance value of under 100 for black (0,0,0)?
        if return_distance(image[0, 0], (0, 0, 0)) > 100:
            logging.warning('Frame lock fail!  Initial pixel value exceeds maximum color distance allowed for a '
                            'reliable lock.')
            return False, False, False

        pixel_width, block_dimension_guess = pixel_creep(image, initializer_palette_a, initializer_palette_b,
                                                         combined_colors, initializer_palette_a_dict,
                                                         initializer_palette_b_dict, frame_width, frame_height,
                                                         width=True)
        checkpoint = verify_blocks_x(image, pixel_width, block_dimension_guess, combined_colors,
                                     initializer_palette_a_dict, initializer_palette_b_dict)
        if checkpoint == False:
            return False, False, False

        block_width = block_dimension_guess
        pixel_width, block_dimension_guess = pixel_creep(image, initializer_palette_a, initializer_palette_b,
                                                         combined_colors, initializer_palette_a_dict,
                                                         initializer_palette_b_dict, frame_width, frame_height,
                                                         width=False)
        checkpoint = verify_blocks_y(image, pixel_width, block_dimension_guess, combined_colors,
                                     initializer_palette_a_dict, initializer_palette_b_dict)

        if checkpoint == False:
            return False, False, False
        block_height = block_dimension_guess

    logging.debug(f'Lockon successful.\npixel_width: {pixel_width}\nblock_height: {block_height}\nblock_width: '
                  f'{block_width}')
    return block_height, block_width, pixel_width


def verify_blocks_x(image, pixel_width, block_width_estimate, combined_colors, initializer_palette_a_dict,
                    initializer_palette_b_dict, override = False):
    '''This is a function used within frame_lock_on().  It verifies the correct values for the X axis.'''

    calibrator_bits_x = BitArray()
    for x_block in range(17):
        snapped_value = color_snap(scan_block(image, pixel_width, x_block, 0), combined_colors)

        if x_block % 2 == 0:
            calibrator_bits_x.append(initializer_palette_a_dict.get_value(snapped_value))

        else:
            calibrator_bits_x.append(initializer_palette_b_dict.get_value(snapped_value))

    calibrator_bits_x.reverse()
    read_calibrator_x = ConstBitStream(calibrator_bits_x)

    if read_calibrator_x.read('uint:16') != block_width_estimate:
        if override == True:
            logging.warning('block_width_override is not equal to what was read on calibrator.  Aborting...')

        else:
            logging.warning('block_width verification does not match initial read.  This could be the result of \n'
                            'sufficiently distorted frames.  Aborting...')

        return False

    if read_calibrator_x.read('bool') != False:
        logging.warning('0,0 block unexpected value.  Aborting...')
        return False

    if override == True:
        logging.info('block_width_override successfully verified.')

    else:
        logging.debug('block_width successfully verified.')

    return True


def verify_blocks_y(image, pixel_width, block_height_estimate, combined_colors, initializer_palette_a_dict,
                    initializer_palette_b_dict, override = False):
    '''This is a function used within frame_lock_on().  It verifies the correct values for the Y axis.'''

    calibrator_bits_y = BitArray()
    for y_block in range(17):
        snapped_value = color_snap(scan_block(image, pixel_width, 0, y_block), combined_colors)

        if y_block % 2 == 0:
            calibrator_bits_y.append(initializer_palette_a_dict.get_value(snapped_value))

        else:
            calibrator_bits_y.append(initializer_palette_b_dict.get_value(snapped_value))

    calibrator_bits_y.reverse()
    read_calibrator_y = ConstBitStream(calibrator_bits_y)

    if read_calibrator_y.read('uint:16') != block_height_estimate:
        if override == True:
            logging.warning('block_height_override is not equal to what was read on calibrator.  Aborting...')

        else:
            logging.warning('block_height verification does not match initial read.  This could be the result of \n'
                            'sufficiently distorted frames.  Aborting...')

        return False

    if read_calibrator_y.read('bool') != False:
        logging.warning('0,0 block unexpected value.  Aborting...')
        return False

    if override == True:
        logging.info('block_height_override successfully verified.')

    else:
        logging.debug('block_height successfully verified.')

    return True


def pixel_creep(image, initializer_palette_a, initializer_palette_b, combined_colors, initializer_palette_a_dict,
                initializer_palette_b_dict, image_width, image_height, width):
    '''This function moves across the calibrator on the top and left of the frame one pixel at a time, and after
    'snapping' the colors, decodes an unsigned integer from each axis, which if read correctly, is the block width and
    block height of the frame.
    '''

    calibrator_bits = BitArray()
    snapped_values = []
    active_color = (0, 0, 0)
    active_distance = 0
    pixel_on_dimension = 1
    palette_a_is_active = False

    if width == True:
        axis_on_image = pixel_on_dimension, 0
        axis_analyzed = image_width

    else:
        axis_on_image = 0, pixel_on_dimension
        axis_analyzed = image_height

    for value in range(16):
        while True:
            if width == True:
                axis_on_image = 0, pixel_on_dimension
                axis_analyzed = image_width

            else:
                axis_on_image = pixel_on_dimension, 0
                axis_analyzed = image_height

            new_palette_locked = False
            active_scan = flip(image[axis_on_image])
            active_distance = return_distance(active_scan, active_color)

            pixel_on_dimension += 1
            if active_distance < 100:  # Iterating over same colored blocks, until distance exceeds 100.
                continue

            else:  # We are determining if we are within < 100 dist of a new color, or are in fuzzy space.
                if palette_a_is_active == False:
                    active_palette = initializer_palette_b.color_set

                else:
                    active_palette = initializer_palette_a.color_set

                for color in active_palette:
                    active_distance = return_distance(active_scan, color)

                    if active_distance < 100:
                        palette_a_is_active = not palette_a_is_active
                        new_palette_locked = True
                        break

                    else:
                        continue

            if new_palette_locked == True:
                break

        active_color = color_snap(active_scan, combined_colors)
        snapped_values.append(active_color)

        if value % 2 != 0:
            calibrator_bits.append(initializer_palette_a_dict.get_value(active_color))

        else:
            calibrator_bits.append(initializer_palette_b_dict.get_value(active_color))

        active_distance = 0

    calibrator_bits.reverse()
    read_calibrator_bits = ConstBitStream(calibrator_bits)
    block_dimension_guess = read_calibrator_bits.read('uint:16')
    pixel_width = axis_analyzed / block_dimension_guess

    return pixel_width, block_dimension_guess