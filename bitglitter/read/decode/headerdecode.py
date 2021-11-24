import ast
from datetime import datetime
import logging

from bitglitter.config.config import session
from bitglitter.config.configmodels import Constants
from bitglitter.config.palettemodels import Palette
from bitglitter.read.decode.headerutilities import crc_verify
from bitglitter.utilities.compression import decompress_bytes
from bitglitter.utilities.cryptography import decrypt_bytes, get_sha256_hash_from_bytes


def initializer_header_validate_decode(bit_stream, block_height_estimate, block_width_estimate):
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

    if not crc_verify(bit_stream):
        logging.warning('Initializer checksum failure.  Aborting...')
        return False

    bit_stream.pos = 0
    protocol_version = bit_stream.read('uint : 4')
    logging.debug(f'Protocol version: {protocol_version}')
    constants = session.query(Constants).first()
    if str(protocol_version) not in constants.return_supported_protocols():
        logging.warning(f'Protocol v{str(protocol_version)} not supported in v{constants.BG_VERSION} of BitGlitter.'
                        f'  Please update to fix.  Aborting...')
        return False

    decoded_block_height = bit_stream.read('uint : 16')
    decoded_block_width = bit_stream.read('uint : 16')
    if decoded_block_height != block_height_estimate or decoded_block_width != block_width_estimate:
        logging.warning('Geometry assertion failure.  This occurs from corrupted header data, or when frame scanning'
                        ' cannot properly read the calibrator.  Aborting...')
        logging.debug(f'decoded_block_height: {decoded_block_height} block_height_estimate: {block_height_estimate}'
                      f'\ndecoded_block_width: {decoded_block_width} block_width_estimate: {block_width_estimate}')
        return False

    bit_stream.pos += 192
    stream_palette_id = bit_stream.read('uint : 64')

    #  Custom palette used
    if stream_palette_id > 100:
        custom_palette_used = True
        bit_stream.pos -= 256
        stream_palette_id = bit_stream.read('hex : 256')
        stream_palette_id.lower()
        palette = session.query(Palette).filter(Palette.palette_id == stream_palette_id).first()
        if palette is None:
            logging.debug('Unknown custom palette detected, will receive palette data in several headers from now.')
        else:
            logging.info(f'Known custom palette \'{palette.name}\' detected.')

    #  Default palette used
    else:
        custom_palette_used = False
        palette = session.query(Palette).filter(Palette.palette_id == stream_palette_id).first()
        if palette is None:
            logging.warning('This default palette is unknown by this version of BitGlitter.  This could be the case '
                            'if you\'re using an older version.  Aborting...')
            logging.debug(f'stream_palette_id: {stream_palette_id}')
            return False
        else:
            logging.info(f'Default palette \'{palette.name}\' detected.')

    # Get Stream SHA-256
    stream_sha256 = bit_stream.read('hex : 256')

    return {'palette': palette, 'stream_sha256': stream_sha256, 'protocol_version': protocol_version,
            'stream_palette_id': stream_palette_id, 'custom_palette_used': custom_palette_used}


def frame_header_decode(bit_stream):
    """While read_initializer is mostly used for validation of values, this function's purpose is to return values
    needed for the reading process, once verified.  Returns stream_sha, frame_sha, frame_number, and blocks_to_read.
    """

    logging.debug('frame_header_decode running...')
    assert len(bit_stream.bin) == 352

    if not crc_verify(bit_stream):
        logging.warning(f'Frame header checksum failure.  Aborting frame...')
        return False
    bit_stream.pos = 0
    bits_to_read = bit_stream.read('uint : 32')
    frame_number = bit_stream.read('uint : 32')
    frame_sha256 = bit_stream.read('hex : 256')

    logging.debug('frame_header_decode successfully ran.')

    return {'frame_sha256': frame_sha256, 'frame_number': frame_number, 'bits_to_read': bits_to_read}


def stream_header_decode(bit_stream):
    """This function takes the raw bit string taken from the frame(s) and extracts stream data from it."""

    logging.debug('stream_header_decode running...')
    assert len(bit_stream.bin) == 685

    if not crc_verify(bit_stream):
        logging.warning('Stream header checksum failure!  Aborting...')
        return False

    bit_stream.pos = 0
    size_in_bytes = bit_stream.read('uint : 64')
    total_frames = bit_stream.read('uint : 32')
    compression_enabled = bit_stream.read('bool')
    encryption_enabled = bit_stream.read('bool')
    file_masking_enabled = bit_stream.read('bool')

    metadata_header_length = bit_stream.read('uint : 32')
    metadata_header_hash = bit_stream.read('hex : 256')
    custom_palette_header_length = bit_stream.read('uint : 10')
    custom_palette_header_hash = bit_stream.read('hex : 256')

    return {'size_in_bytes': size_in_bytes, 'total_frames': total_frames, 'compression_enabled': compression_enabled,
            'encryption_enabled': encryption_enabled, 'file_masking_enabled': file_masking_enabled,
            'metadata_header_length': metadata_header_length, 'metadata_header_hash': metadata_header_hash,
            'custom_palette_header_length': custom_palette_header_length, 'custom_palette_header_hash':
                custom_palette_header_hash}


def metadata_header_validate_decode(header_bytes, read_sha256, crypto_key, encryption_enabled, file_mask_enabled,
                                    scrypt_n=14, scrypt_r=8, scrypt_p=1, frame_processor=True):
    logging.debug('metadata_header_decode running...')

    #  Attempt decryption if encryption enabled
    decrypted_bytes = None
    if encryption_enabled and file_mask_enabled:
        decrypted_bytes = decrypt_bytes(header_bytes, crypto_key, scrypt_n, scrypt_r, scrypt_p)
        if decrypted_bytes:
            logging.info('Successful decryption.')
        else:  # Signalling there was a decryption failure
            logging.warning('Provided decryption values (key, scrypt_n, scrypt_r, scrypt_p) invalid.  Cannot extract'
                            ' files until correct parameters received.')
            return None

    decompressed_bytes = decompress_bytes(decrypted_bytes if encryption_enabled and file_mask_enabled else header_bytes)

    #  Integrity check
    if frame_processor:
        calculated_sha256 = get_sha256_hash_from_bytes(decompressed_bytes)
        if calculated_sha256 != read_sha256:  # Shouldn't be possible but here nonetheless to ensure data integrity.
            logging.warning('Read Stream SHA-256 does not match calculated.  This should never (in theory) be seen'
                            'from the other layers of integrity checks.  Aborting...')
            return False

    decoded = decompressed_bytes.decode()
    bg_version, stream_name, stream_description, time_created, manifest_string = decoded.split('\\\\')
    time_created = int(time_created)
    time_datetime = datetime.fromtimestamp(time_created)
    logging.info(f"Metadata successfully decoded:\nStream name: {stream_name}\nStream description: "
                 f"{stream_description}\nTime created: {time_datetime.strftime('%b %d, %Y %I:%M:%S %p')}")
    return {'bg_version': bg_version, 'stream_name': stream_name, 'stream_description': stream_description,
            'time_created': time_created, 'manifest_string': manifest_string}


def custom_palette_header_validate_decode(header_bytes, read_sha256):
    logging.debug('custom_palette_header_decode running...')
    decompressed_bytes = decompress_bytes(header_bytes)

    #  Integrity check
    calculated_sha256 = get_sha256_hash_from_bytes(decompressed_bytes)
    if calculated_sha256 != read_sha256:  # Shouldn't be possible but here nonetheless to ensure data integrity.
        logging.warning('Read palette header SHA-256 does not match calculated.  This should never (in theory) be seen'
                        ' from the other layers of integrity checks.  Aborting...')
        return False
    palette_id, palette_name, palette_description, time_created, number_of_colors, color_list = \
        decompressed_bytes.decode().split('\\\\')
    time_created = int(time_created)
    number_of_colors = int(number_of_colors)
    color_list = ast.literal_eval(color_list)  # Revisit in future.  Safer way?
    if isinstance(color_list, list) or isinstance(color_list, tuple):
        return {'palette_id': palette_id, 'palette_name': palette_name, 'palette_description': palette_description,
                'time_created': time_created, 'number_of_colors': number_of_colors, 'color_list': color_list}
    else:
        raise ValueError('Emergency stop- returned string was not a list or tuple.')
