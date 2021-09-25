from bitstring import BitArray, ConstBitStream
from numpy import flip

import hashlib
import logging

from bitglitter.read.scan.scanutilities import color_snap, return_distance, scan_block
from bitglitter.utilities.palette import ColorsToBits


def minimum_block_checkpoint(block_height_override, block_width_override, active_frame_size_height,
                             active_frame_size_width):
    """If block_height_override and block_width_override have been entered, this checks those values against the height
    and width (in pixels) of the image loaded).  Since the smallest blocks that can be read are one pixels (since that
    is finest detail you can have with an image), any values beyond that are invalid, and stopped here.
    """

    if block_height_override and block_width_override:
        if active_frame_size_width < block_width_override or active_frame_size_height < \
                block_height_override:
            logging.warning("Block override parameters are too large for a file of these dimensions.  "
                            "Aborting...")
            return False

    return True


def frame_lock_on(frame, block_height_override, block_width_override, frame_pixel_height, frame_pixel_width,
                  initializer_palette_a_color_set, initializer_palette_b_color_set, initializer_palette_a_dict,
                  initializer_palette_b_dict):
    """This function is used to lock onto the frame.  If override values are present, these will be used.  Otherwise,
    it will attempt to extract the correct values from the X and Y calibrator on the initial frame."""

    logging.debug('Calibrator lock on...')
    combined_colors = initializer_palette_a_color_set + initializer_palette_b_color_set

    if block_height_override and block_width_override:  # Jump straight to validation
        logging.info("block_height_override and block_width_override parameters detected.  Attempting to lock with "
                     "these values...")
        pixel_width = ((frame_pixel_width / block_width_override) + (frame_pixel_height / block_height_override)) / 2

        checkpoint = verify_blocks_x(frame, pixel_width, block_width_override, combined_colors,
                                     initializer_palette_a_dict, initializer_palette_b_dict, override=True)
        if not checkpoint:
            return {'abort': True}

        checkpoint = verify_blocks_y(frame, pixel_width, block_height_override, combined_colors,
                                     initializer_palette_a_dict, initializer_palette_b_dict, override=True)
        if not checkpoint:
            return {'abort': True}

        block_width, block_height = block_width_override, block_height_override

    else:
        # First checkpoint.  Does pixel 0,0 have color_distance value of under 100 for black (0,0,0)?
        if return_distance(frame[0, 0], (0, 0, 0)) > 100:
            logging.warning('Frame lock fail!  Initial pixel value exceeds maximum color distance allowed for a '
                            'reliable lock.')
            return {'abort': True}

        pixel_width, block_dimension_guess = pixel_creep(frame, initializer_palette_a_color_set, initializer_palette_b_color_set,
                                                         combined_colors, initializer_palette_a_dict,
                                                         initializer_palette_b_dict, frame_pixel_width, frame_pixel_height,
                                                         width=True)
        checkpoint = verify_blocks_x(frame, pixel_width, block_dimension_guess, combined_colors,
                                     initializer_palette_a_dict, initializer_palette_b_dict)
        if not checkpoint:
            return {'abort': True}

        block_width = block_dimension_guess
        pixel_width, block_dimension_guess = pixel_creep(frame, initializer_palette_a_color_set, initializer_palette_b_color_set,
                                                         combined_colors, initializer_palette_a_dict,
                                                         initializer_palette_b_dict, frame_pixel_width, frame_pixel_height,
                                                         width=False)
        checkpoint = verify_blocks_y(frame, pixel_width, block_dimension_guess, combined_colors,
                                     initializer_palette_a_dict, initializer_palette_b_dict)

        if not checkpoint:
            return {'abort': True}
        block_height = block_dimension_guess

    logging.debug(f'Lockon successful.\npixel_width: {pixel_width}\nblock_height: {block_height}\nblock_width: '
                  f'{block_width}')
    return {'block_height': block_height, 'block_width': block_width, 'pixel_width': pixel_width}


def verify_blocks_x(image, pixel_width, block_width_estimate, combined_colors, initializer_palette_a_dict,
                    initializer_palette_b_dict, override=False):
    """This is a function used within frame_lock_on().  It verifies the correct values for the X axis."""

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
        if override:
            logging.warning('block_width_override is not equal to what was read on calibrator.  Aborting...')

        else:
            logging.warning('block_width validation does not match initial read.  This could be the result of \n'
                            'sufficiently distorted frames.  Aborting...')

        return False

    if read_calibrator_x.read('bool'):
        logging.warning('0,0 block unexpected value.  Aborting...')
        return False

    if override:
        logging.info('block_width_override successfully verified.')

    else:
        logging.debug('block_width successfully verified.')

    return True


def verify_blocks_y(image, pixel_width, block_height_estimate, combined_colors, initializer_palette_a_dict,
                    initializer_palette_b_dict, override=False):
    """This is a function used within frame_lock_on().  It verifies the correct values for the Y axis."""

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
        if override:
            logging.warning('block_height_override is not equal to what was read on calibrator.  Aborting...')

        else:
            logging.warning('block_height validation does not match initial read.  This could be the result of \n'
                            'sufficiently distorted frames.  Aborting...')

        return False

    if read_calibrator_y.read('bool'):
        logging.warning('0,0 block unexpected value.  Aborting...')
        return False

    if override:
        logging.info('block_height_override successfully verified.')

    else:
        logging.debug('block_height successfully verified.')

    return True


def pixel_creep(image, initializer_palette_a_color_set, initializer_palette_b_color_set, combined_colors,
                initializer_palette_a_dict, initializer_palette_b_dict, image_width, image_height, width):
    """This function moves across the calibrator on the top and left of the frame one pixel at a time, and after
    'snapping' the colors, decodes an unsigned integer from each axis, which if read correctly, is the block width and
    block height of the frame.
    """

    calibrator_bits = BitArray()
    snapped_values = []
    active_color = (0, 0, 0)
    pixel_on_dimension = 1
    palette_a_is_active = False

    if width:
        axis_analyzed = image_width

    else:
        axis_analyzed = image_height

    for value in range(16):
        while True:
            if width:
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
                if not palette_a_is_active:
                    active_palette = initializer_palette_b_color_set

                else:
                    active_palette = initializer_palette_a_color_set

                for color in active_palette:
                    active_distance = return_distance(active_scan, color)

                    if active_distance < 100:
                        palette_a_is_active = not palette_a_is_active
                        new_palette_locked = True
                        break

                    else:
                        continue

            if new_palette_locked:
                break

        active_color = color_snap(active_scan, combined_colors)
        snapped_values.append(active_color)

        if value % 2 != 0:
            calibrator_bits.append(initializer_palette_a_dict.get_value(active_color))

        else:
            calibrator_bits.append(initializer_palette_b_dict.get_value(active_color))

    calibrator_bits.reverse()
    read_calibrator_bits = ConstBitStream(calibrator_bits)
    block_dimension_guess = read_calibrator_bits.read('uint:16')
    pixel_width = axis_analyzed / block_dimension_guess

    return pixel_width, block_dimension_guess


def validate_payload(payload_bits, read_frame_sha):
    """Taking all of the frame bits after the frame header, this takes the SHA-256 hash of them, and compares it against
    the frame SHA written in the frame header.  This is the primary mechanism that validates frame data, which either
    allows it to be passed through to the assembler, or discarded.
    """

    sha_hasher = hashlib.sha256()
    sha_hasher.update(payload_bits.tobytes())
    string_output = sha_hasher.hexdigest()
    logging.debug(f'length of payload_bits: {payload_bits.len}')

    if string_output != read_frame_sha:
        logging.warning('validate_payload: read_frame_sha does not match calculated one.  Aborting...')
        logging.debug(f'Read from frameHeader: {read_frame_sha}\nCalculated just now: {string_output}')
        return False

    logging.debug('Payload validated this frame.')
    return True
