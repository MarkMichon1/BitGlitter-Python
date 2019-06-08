import hashlib
import logging
import numpy
import zlib

from bitglitter.palettes.paletteutilities import palette_grabber
from bitglitter.protocols.protocolhandler import protocol_handler


def minimum_block_checkpoint(block_height_override, block_width_override, active_frame_size_width,
                             active_frame_size_height):
    '''If block_height_override and block_width_override have been entered, this checks those values against the height
    and width (in pixels) of the image loaded).  Since the smallest blocks that can be read are one pixels (since that
    is finest detail you can have with an image), any values beyond that are invalid, and stopped here.
    '''

    if block_height_override and block_width_override:
        if active_frame_size_width < block_width_override or active_frame_size_height < \
                block_height_override:
            logging.warning("Block override parameters are too large for a file of these dimensions.  "
                            "Aborting...")
            return False

    return True


def scan_block(image, pixel_width, block_width_position, block_height_position):
    '''This function is what's used to scan the blocks used.  First the scan area is determined, and then each of the
    pixels in that area appended to a list.  An average of those values as type int is returned.
    '''

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

    numpy_output = numpy.flip(image[start_position_y:end_position_y, start_position_x:end_position_x]).mean(axis=(0,1))
    to_list_format = numpy_output.tolist()

    for value in range(3):
        to_list_format[value] = int(to_list_format[value])

    return to_list_format


def read_initializer(bit_stream, blockHeight, block_width, custom_palette_list, default_palette_list):
    '''This function decodes the raw binary data from the initializer header after verifying it's checksum, and will
    emergency stop the read if any of the conditions are met:  If the read checksum differs from the calculated
    checksum, if the read protocol version isn't supported by this BitGlitter version, if the read_block_height or
    read_block_width differ from what frame_lock_on() read, or if the palette ID for the header is unknown (ie, a custom
    color which has not been integrated yet).  Returns protocol_version and header_palette object.
    '''

    # First, we're verifying the initializer is not corrupted by comparing its read checksum with a calculated one from
    # it's contents.  If they match, we continue.  If not, this frame aborts.
    logging.debug('read_initializer running...')

    bit_stream.pos = 0
    full_bit_stream_to_hash = bit_stream.read('bits : 292')
    converted_to_bytes = full_bit_stream_to_hash.tobytes()
    calculated_crc = zlib.crc32(converted_to_bytes)
    read_crc = bit_stream.read('uint : 32')
    if calculated_crc != read_crc:
        logging.warning('Initializer checksum failure.  Aborting...')
        return False, False

    bit_stream.pos = 0
    protocol_version = bit_stream.read('uint : 4')
    logging.debug(f'Protocol version: {protocol_version}')
    if str(protocol_version) not in protocol_handler.available_protocols:
        logging.warning(f'Protocol v{str(protocol_version)} not supported in this version of BitGlitter.  Please update'
                        f' to fix.  Aborting...')
        return False, False

    read_block_height = bit_stream.read('uint : 16')
    read_block_width = bit_stream.read('uint : 16')
    if read_block_height != blockHeight or read_block_width != block_width:
        logging.warning('read_initializer: Geometry assertion failure.  Aborting...')
        logging.debug(f'read_block_height: {read_block_height}\n blockHeight {blockHeight}'
                      f'\n read_block_width {read_block_width}\n block_width {block_width}')

        return False, False

    bit_stream.pos += 232
    frame_palette_id = bit_stream.read('uint : 24')

    if frame_palette_id > 100:

        bit_stream.pos -= 256
        frame_palette_id = bit_stream.read('hex : 256')
        frame_palette_id.lower()

        if frame_palette_id not in custom_palette_list:

            logging.warning('read_initializer: This header palette is unknown, reader cannot proceed until it is '
                            'learned through a \nstream header.  This can occur if the creator of the stream uses a '
                            'non-default palette.  This can also trigger if frames \nare read non-sequentially.  '
                            'Aborting...')
            return False, False

    else:

        if str(frame_palette_id) not in default_palette_list:
            logging.warning('read_initializer: This default palette is unknown by this version of BitGlitter.  This\n'
                            "could be the case if you're using an older version.  Aborting...")
            logging.debug(f'frame_palette_id: {frame_palette_id}\ndefault_palette_list: {default_palette_list}')
            return False, False

    frame_palette = palette_grabber(str(frame_palette_id))
    logging.debug('read_initializer successfully ran.')
    return protocol_version, frame_palette


def read_frame_header(bit_stream):
    '''While read_initializer is mostly used for verification of values, this function's purpose is to return values
    needed for the reading process, once verified.  Returns stream_sha, frame_sha, frame_number, and blocks_to_read.
    '''

    logging.debug('read_frame_header running...')
    full_bit_stream_to_hash = bit_stream.read('bytes : 72')

    calculated_crc = zlib.crc32(full_bit_stream_to_hash)
    read_crc = bit_stream.read('uint : 32')
    if calculated_crc != read_crc:
        logging.warning('frameHeader checksum failure.  Aborting...')
        return False, False, False, False

    bit_stream.pos = 0
    stream_sha = bit_stream.read('hex : 256')
    frame_sha = bit_stream.read('hex : 256')
    frame_number = bit_stream.read('uint : 32')
    blocks_to_read = bit_stream.read('uint : 32')

    logging.debug('read_frame_header successfully ran.')
    return stream_sha, frame_sha, frame_number, blocks_to_read


def validate_payload(payload_bits, read_frame_sha):
    '''Taking all of the frame bits after the frame header, this takes the SHA-256 hash of them, and compares it against
    the frame SHA written in the frame header.  This is the primary mechanism that validates frame data, which either
    allows it to be passed through to the assembler, or discarded.
    '''

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