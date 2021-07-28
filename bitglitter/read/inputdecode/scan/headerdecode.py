from bitstring import ConstBitStream

import ast
import logging
import zlib

from bitglitter.config.config import session
from bitglitter.config.configmodels import Constants
from bitglitter.config.palettemodels import Palette

# todo- normalize logging messages, should all be debug except initializer

#  When there is an integrity error in these functions, two tiers of errors can be returned:
FRAME_FAILURE_RETURN = {'abort': True}  # Failures that invalidate the frame, but the stream can continue.
STREAM_FAILURE_RETURN = {'abort': True, 'complete': True}  # The stream stops after these


def initializer_header_decode(bit_stream, block_height_estimate, block_width_estimate):
    """This decodes the raw binary data from the initializer header after verifying its CRC checksum, and will
    stop the read if any of these conditions are met:  If the read checksum differs from the calculated checksum, if the
    read protocol version isn't supported by this BitGlitter version, if the decoded block height or block width differ
    from what the frame lockon read, or if the there is a default palette used which isn't recognized by this version of
    BitGlitter.  Returns either 'failure' messages (see variables directly above), or the loaded stream palette.
    """

    # First, we're verifying the initializer is not corrupted by comparing its read checksum with a calculated one from
    # it's contents.  If they match, we continue.  If not, this frame aborts.

    logging.debug('initializer_header_decode running...')
    assert len(bit_stream.bin) == 580

    #TODO TEMP:
    bit_stream = ConstBitStream(bit_stream)

    bit_stream.pos = 0
    full_bit_stream_to_hash = bit_stream.read('bits : 548')
    converted_to_bytes = full_bit_stream_to_hash.tobytes()
    calculated_crc = zlib.crc32(converted_to_bytes)
    read_crc = bit_stream.read('uint : 32')
    if calculated_crc != read_crc:
        logging.warning('Initializer checksum failure.  Aborting...')
        return STREAM_FAILURE_RETURN

    bit_stream.pos = 0
    protocol_version = bit_stream.read('uint : 4')
    logging.debug(f'Protocol version: {protocol_version}')
    constants = session.query(Constants).first()
    if str(protocol_version) not in constants.return_supported_protocols():
        logging.warning(f'Protocol v{str(protocol_version)} not supported in v{constants.BG_VERSION} of BitGlitter.'
                        f'  Please update to fix.  Aborting...')
        return STREAM_FAILURE_RETURN

    decoded_block_height = bit_stream.read('uint : 16')
    decoded_block_width = bit_stream.read('uint : 16')
    if decoded_block_height != block_height_estimate or decoded_block_width != block_width_estimate:
        logging.warning('Geometry assertion failure.  This occurs from corrupted header data, or when frame scanning'
                        'cannot properly read the calibrator.  Aborting...')
        logging.debug(f'decoded_block_height: {decoded_block_height} block_height_estimate: {block_height_estimate}'
                      f'\ndecoded_block_width: {decoded_block_width} block_width_estimate: {block_width_estimate}')
        return STREAM_FAILURE_RETURN

    bit_stream.pos += 192
    stream_palette_id = bit_stream.read('uint : 64')

    #  custom palette used
    if stream_palette_id > 100:
        bit_stream.pos -= 256
        stream_palette_id = bit_stream.read('hex : 256')
        stream_palette_id.lower()
        palette = session.query(Palette).filter(Palette.palette_id == stream_palette_id).first()
        if palette is None:
            logging.debug('Unknown custom palette detected, will receive palette data in several headers from now.')
            return {}
        else:
            logging.info(f'Known custom palette \'{palette.name}\' detected.')
            return {'palette': palette}

    #  default palette used
    else:
        palette = session.query(Palette).filter(Palette.palette_id == stream_palette_id).first()
        if palette is None:
            logging.warning('This default palette is unknown by this version of BitGlitter.  This could be the case '
                            'if you\'re using an older version.  Aborting...')
            logging.debug(f'stream_palette_id: {stream_palette_id}')
            return STREAM_FAILURE_RETURN
        else:
            logging.info(f'Default palette \'{palette.name}\' detected.')
            return {'palette': palette}


def frame_header_decode(bit_stream):
    """While read_initializer is mostly used for validation of values, this function's purpose is to return values
    needed for the reading process, once verified.  Returns stream_sha, frame_sha, frame_number, and blocks_to_read.
    """

    logging.debug('frame_header_decode running...')
    assert len(bit_stream.bin) == 352

    full_bit_stream_to_hash = bit_stream.read('bytes : 72')
    calculated_crc = zlib.crc32(full_bit_stream_to_hash)
    read_crc = bit_stream.read('uint : 32')
    if calculated_crc != read_crc:
        logging.warning('Frame header checksum failure!  Aborting...')
        return False, False, False, False

    bit_stream.pos = 0
    stream_sha = bit_stream.read('hex : 256')
    frame_sha = bit_stream.read('hex : 256')
    frame_number = bit_stream.read('uint : 32')
    blocks_to_read = bit_stream.read('uint : 32')

    logging.debug('read_frame_header successfully ran.')
    return stream_sha, frame_sha, frame_number, blocks_to_read


def stream_header_decode(bit_stream):
    """This function takes the raw bit string taken from the frame(s) and extracts stream data from it."""

    logging.debug('stream_header_decode running...')
    # TODO TEMP:
    bit_stream = ConstBitStream(bit_stream)
    assert len(bit_stream.bin) == 685

    size_in_bytes = bit_stream.read('uint : 64')
    total_frames = bit_stream.read('uint : 32')
    compression_enabled = bit_stream.read('bool')
    encryption_enabled = bit_stream.read('bool')
    file_masking_enabled = bit_stream.read('bool')
    is_custom_palette = bit_stream.read('bool')
    date_created = bit_stream.read('uint : 34')

    if not is_custom_palette:
        stream_palette_id = str(bit_stream.read('uint : 256'))

    else:
        stream_palette_id = str(bit_stream.read('hex : 256'))

    ascii_header_compressed_in_bytes = bit_stream.read('uint : 32')

    return size_in_bytes, total_frames, compression_enabled, encryption_enabled, file_masking_enabled, \
           is_custom_palette, date_created, stream_palette_id, ascii_header_compressed_in_bytes


def metadata_header_decode(bit_stream):
    logging.debug('metadata_header_decode running...')


def custom_palette_header_decode(bit_stream):
    logging.debug('custom_palette_header_decode running...')


# todo....?
def decode_text_header(bitstream, custom_color_enabled, encryption_enabled):
    """This function encodes the raw bit string taken from the frame(s) back into ASCII, and returns the split
    managers inside of it.
    """

    logging.debug('Reading stream header...')
    custom_color_name = None
    custom_color_description = None
    custom_color_date_created = None
    custom_color_palette = None
    post_compression_sha = None

    to_bytes = bitstream.tobytes()
    logging.debug(f'ASCII header byte size inputted to read function: {int(len(bitstream) / 8)} B')
    uncompressed_string = zlib.decompress(to_bytes).decode()
    string_broken_into_parts = uncompressed_string.split('\\\\')[1:-1]
    bg_version = string_broken_into_parts[0]
    stream_name = string_broken_into_parts[1]
    stream_description = string_broken_into_parts[2]
    file_list = string_broken_into_parts[3]

    index_bump = 0
    if custom_color_enabled:
        custom_color_name = string_broken_into_parts[4]
        custom_color_description = string_broken_into_parts[5]
        custom_color_date_created = string_broken_into_parts[6]
        custom_color_palette = ast.literal_eval(string_broken_into_parts[7])
        index_bump += 4

    if encryption_enabled:
        post_compression_sha = string_broken_into_parts[4 + index_bump]

    logging.debug('Stream header ASCII part successfully read.')

    return bg_version, stream_name, stream_description, file_list, custom_color_name, custom_color_description, \
           custom_color_date_created, custom_color_palette, post_compression_sha
