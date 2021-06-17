import ast
import logging
import zlib

from bitglitter.config.palettemanager import palette_manager
from bitglitter.config.settingsmanager import settings_manager

# test
def read_initializer(bit_stream, blockHeight, block_width, custom_palette_list, default_palette_list):
    """This function decodes the raw binary data from the initializer header after verifying it's checksum, and will
    emergency stop the read if any of the conditions are met:  If the read checksum differs from the calculated
    checksum, if the read protocol version isn't supported by this BitGlitter version, if the read_block_height or
    read_block_width differ from what frame_lock_on() read, or if the palette ID for the header is unknown (ie, a custom
    color which has not been integrated yet).  Returns protocol_version and header_palette object.
    """

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
    if str(protocol_version) not in settings_manager.SUPPORTED_PROTOCOLS:
        logging.warning(f'Protocol v{str(protocol_version)} not supported in this version of BitGlitter'
                        f' (v{settings_manager.BG_VERSION}).  Please update to fix.  Aborting...')
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

    frame_palette = palette_manager.return_selected_palette(str(frame_palette_id))
    logging.debug('read_initializer successfully ran.')
    return protocol_version, frame_palette


def read_frame_header(bit_stream):
    """While read_initializer is mostly used for validation of values, this function's purpose is to return values
    needed for the reading process, once verified.  Returns stream_sha, frame_sha, frame_number, and blocks_to_read.
    """

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


def decode_stream_header(bit_stream):
    """This function takes the raw bit string taken from the frame(s) and extracts stream data from it."""

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
