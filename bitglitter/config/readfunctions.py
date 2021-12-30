import json
import logging
from pathlib import Path

import cv2

from bitglitter.config.config import session
from bitglitter.config.configmodels import Constants
from bitglitter.config.palettemodels import Palette
from bitglitter.config.readmodels.readmodels import StreamFrame, StreamSHA256Blacklist
from bitglitter.config.readmodels.streamread import StreamRead
from bitglitter.read.decode.headerdecode import initializer_header_validate_decode, metadata_header_validate_decode
from bitglitter.read.scan.scanhandler import ScanHandler
from bitglitter.read.scan.scanvalidate import frame_lock_on
from bitglitter.utilities.filemanipulation import refresh_directory, remove_working_folder
from bitglitter.utilities.loggingset import logging_setter

logging_setter(logging_level='info', logging_stdout_output=True, logging_txt_output=False)


def unpackage(stream_sha256):
    """Attempt to unpackage as much of the file as possible.  Returns None if stream doesn't exist, returns False if
    there is a decryption error.
    """

    stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return False
    constants = session.query(Constants).first()
    working_directory = Path(constants.WORKING_DIR)
    refresh_directory(working_directory)
    results = stream_read.attempt_unpackage(working_directory)
    stream_read.autodelete_attempt()
    remove_working_folder(working_directory)
    return results


def return_all_read_information(advanced=False):
    stream_reads = StreamRead.query.all()
    returned_list = []
    for stream_read in stream_reads:
        returned_list.append(stream_read.return_state(advanced))
    return returned_list


def return_single_read_information(stream_sha256, advanced=False):
    stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return False
    else:
        return stream_read.return_state(advanced)


def update_decrypt_values(stream_sha256, decryption_key=None, scrypt_n=None, scrypt_r=None, scrypt_p=None):
    stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return False
    if not stream_read.encryption_enabled:
        return True

    if decryption_key:
        stream_read.decryption_key = decryption_key
    if scrypt_n:
        stream_read.scrypt_n = scrypt_n
    if scrypt_r:
        stream_read.scrypt_r = scrypt_r
    if scrypt_p:
        stream_read.scrypt_p = scrypt_p
    stream_read.toggle_eligibility_calculations(True)
    return True


def attempt_metadata_decrypt(stream_sha256):
    stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return False
    if not stream_read.file_masking_enabled:
        return {'error': 'File masking not enabled'}
    if not stream_read.decryption_key:
        return {'error': 'No decryption key '}
    if stream_read.manifest_string:
        return {'error': 'Metadata has already been decrypted'}

    results = metadata_header_validate_decode(stream_read.encrypted_metadata_header_bytes, None,
                                              stream_read.decryption_key, True, stream_read.file_masking_enabled,
                                              stream_read.scrypt_n, stream_read.scrypt_r, stream_read.scrypt_p,
                                              frame_processor=False)

    if 'bg_version' in results:
        bg_version = results['bg_version']
        stream_name = results['stream_name']
        stream_description = results['stream_description']
        time_created = results['time_created']
        manifest_string = results['manifest_string']
        stream_read.metadata_header_load(bg_version, stream_name, stream_description, time_created, manifest_string)
        return {'metadata': stream_read.metadata_checkpoint_return()}
    else:
        return {'error': 'Incorrect decryption value(s)'}


def return_stream_manifest(stream_sha256, return_as_json=False):
    stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return False
    if not stream_read.manifest_string:
        return {'error': 'Metadata header not decoded yet'}
    if stream_read.encrypted_metadata_header_bytes:
        return {'error': 'Metadata not decrypted yet'}
    if return_as_json:
        return stream_read.manifest_string
    else:
        return json.loads(stream_read.manifest_string)


def remove_partial_save(stream_sha256):
    stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return False
    stream_read.delete()
    return True


def remove_all_partial_save_data():
    """Removes all data for partial saves, both files and metadata within some internal classes."""
    session.query(StreamRead).delete()
    session.commit()
    return True


def update_stream_read(stream_sha256, auto_delete_finished_stream=None, auto_unpackage_stream=None):
    """Will get larger as more config options are added; general settings about the stream are changed with this."""

    stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return False
    if isinstance(auto_delete_finished_stream, bool):
        stream_read.auto_delete_finished_stream = auto_delete_finished_stream
    if isinstance(auto_unpackage_stream, bool):
        stream_read.auto_unpackage_stream = auto_unpackage_stream
    stream_read.save()
    return True


def blacklist_stream_sha256(stream_sha256):
    if not isinstance(stream_sha256, str):
        raise ValueError('Must be type str')
    if len(stream_sha256) != 64:
        raise ValueError('Stream IDs are 64 characters long')
    hex_characters = '1234567890abcdef'
    sha256_lowercase = stream_sha256.lower()
    for character in sha256_lowercase:
        if character not in hex_characters:
            raise ValueError('Not a valid stream ID')
    existing_blacklist = StreamSHA256Blacklist.query \
        .filter(StreamSHA256Blacklist.stream_sha256 == sha256_lowercase).first()
    if existing_blacklist:
        raise ValueError('Blacklisted stream is already in database')

    stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == sha256_lowercase).first()
    if stream_read:
        stream_read.delete()
    StreamSHA256Blacklist.create(stream_sha256=sha256_lowercase)
    return True


def return_all_blacklist_sha256():
    returned_list = []
    blacklisted_streams = StreamSHA256Blacklist.query.all()
    for blacklisted_item in blacklisted_streams:
        returned_list.append(blacklisted_item.stream_sha256)
    return returned_list


def remove_blacklist_sha256(stream_sha256):
    blacklist = StreamSHA256Blacklist.query.filter(StreamSHA256Blacklist.stream_sha256 == stream_sha256) \
        .first()
    if not blacklist:
        return False
    blacklist.delete()
    return True


def remove_all_blacklist_sha256():
    session.query(StreamSHA256Blacklist).delete()
    session.commit()
    return True


def return_stream_frame_data(stream_sha256):
    stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return False

    frames = stream_read.frames.order_by(StreamFrame.frame_number.asc()).all()
    returned_list = []
    for frame in frames:
        returned_list.append({'is_complete': frame.is_complete, 'added_to_progress': frame.added_to_progress,
                              'payload_bits': frame.payload_bits, 'frame_number': frame.frame_number})

    return returned_list


def return_stream_file_data(stream_sha256, advanced=False):
    stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return False
    files = stream_read.files.all()
    returned_list = []
    for file in files:
        returned_list.append(file.return_state(advanced))

    return returned_list


def return_stream_progress_data(stream_sha256):
    stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
    if not stream_read:
        return False
    progress = stream_read.progress.all()
    returned_list = []
    for progress_group in progress:
        returned_list.append({'bit_start_position': progress_group.bit_start_position, 'bit_end_position':
                             progress_group.bit_end_position})

    return returned_list


def verify_is_bitglitter_file(file_path: str):
    """Returns True or False depending on if the image or first video frame is detected as valid.  It does this through
    testing if it can lock onto the frame, and read the initializer."""

    # Disabling log messages in the other functions; we just want a simple True or False returned.
    logger = logging.getLogger()
    logger.disabled = True

    constants = session.query(Constants).first()
    valid_image_formats = constants.return_valid_image_formats()
    valid_video_formats = constants.return_valid_video_formats()
    path = Path(file_path)
    if path.suffix not in valid_image_formats + valid_video_formats:
        return False

    if path.suffix in valid_image_formats:
        frame = cv2.imread(file_path)
    else:
        active_video = cv2.VideoCapture(file_path)
        frame = active_video.read()[1]

    frame_pixel_width = frame.shape[1]
    frame_pixel_height = frame.shape[0]

    initializer_palette_a = Palette.query.filter(Palette.palette_id == '1').first()
    initializer_palette_b = Palette.query.filter(Palette.palette_id == '11').first()
    initializer_palette_a_color_set = initializer_palette_a.convert_colors_to_tuple()
    initializer_palette_b_color_set = initializer_palette_b.convert_colors_to_tuple()
    initializer_palette_a_dict = initializer_palette_a.return_decoder()
    initializer_palette_b_dict = initializer_palette_b.return_decoder()

    lock_on_results = frame_lock_on(frame, None, None, frame_pixel_height, frame_pixel_width,
                                    initializer_palette_a_color_set, initializer_palette_b_color_set,
                                    initializer_palette_a_dict, initializer_palette_b_dict)
    if not lock_on_results:
        return False
    block_height = lock_on_results['block_height']
    block_width = lock_on_results['block_width']
    pixel_width = lock_on_results['pixel_width']


    scan_handler = ScanHandler(frame, True, initializer_palette_a, initializer_palette_a_dict,
                               initializer_palette_a_color_set, block_height, block_width, pixel_width)

    initializer_bits = scan_handler.return_initializer_bits()['bits']

    if not initializer_header_validate_decode(initializer_bits, block_height, block_width):
        return False

    return True