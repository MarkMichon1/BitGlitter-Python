from bitstring import BitStream

import logging

from bitglitter.config.configfunctions import read_stats_update
from bitglitter.config.readmodels.streamread import StreamRead
from bitglitter.config.readmodels.readmodels import StreamFrame, StreamSHA256Blacklist
from bitglitter.read.decode.headerdecode import frame_header_decode, initializer_header_validate_decode, \
    metadata_header_validate_decode, stream_header_decode
from bitglitter.read.scan.scanvalidate import frame_lock_on, geometry_override_checkpoint
from bitglitter.read.scan.scanhandler import ScanHandler
from bitglitter.utilities.encryption import get_sha256_hash_from_bytes


class ImageFrameProcessor:
    def __init__(self, dict_obj):
        frame_position = dict_obj['current_frame_position']
        total_frames = dict_obj['total_frames']
        percentage_string = f'{round(((frame_position / total_frames) * 100), 2):.2f}'
        logging.info(f"Processing image {frame_position} of {total_frames}... {percentage_string} %")

        self.dict_obj = dict_obj

import logging

from bitglitter.config.configfunctions import read_stats_update
from bitglitter.read.scan.scanvalidate import frame_lock_on, geometry_override_checkpoint


# def image_frame_process(dict_obj):
#     ERROR_SOFT = {'error': True}  # Only this frame is cancelled, decoding can continue on next frame
#
#     frame = dict_obj['frame']
#     frame_pixel_height = frame.shape[0]
#     frame_pixel_width = frame.shape[1]
#
#     output_directory = dict_obj['output_directory']
#     block_height_override = dict_obj['block_height_override']
#     block_width_override = dict_obj['block_width_override']
#     decryption_key = dict_obj['decryption_key']
#     scrypt_n = dict_obj['scrypt_n']
#     scrypt_r = dict_obj['scrypt_r']
#     scrypt_p = dict_obj['scrypt_p']
#     temp_save_directory = dict_obj['temp_save_directory']
#     initializer_palette_a = dict_obj['initializer_palette_a']
#     initializer_palette_a_color_set = dict_obj['initializer_palette_a_color_set']
#     initializer_palette_b_color_set = dict_obj['initializer_palette_b_color_set']
#     initializer_palette_a_dict = dict_obj['initializer_palette_a_dict']
#     initializer_palette_b_dict = dict_obj['initializer_palette_b_dict']
#
#     auto_delete_finished_stream = dict_obj['auto_delete_finished_stream']
#     auto_unpackage_stream = dict_obj['auto_unpackage_stream']
#     stop_at_metadata_load = dict_obj['stop_at_metadata_load']
#
#     # Geometry override checkpoint
#     if not geometry_override_checkpoint(block_height_override, block_width_override, frame_pixel_height,
#                                         frame_pixel_width):
#         return ERROR_SOFT
#
#     # Frame lock on
#     lock_on_results = frame_lock_on(frame, block_height_override, block_width_override, frame_pixel_height,
#                                     frame_pixel_width, initializer_palette_a_color_set,
#                                     initializer_palette_b_color_set, initializer_palette_a_dict,
#                                     initializer_palette_b_dict)
#
#     # Statistics Update
#     if dict_obj['save_statistics']:
#         read_stats_update(scan_handler.block_position, 1, int(scan_handler.bits_read / 8))
#
#     logging.debug(f'Successful video frame process cycle')

#self.scan_handler = None # Keep as is, multiprocessing cannot return its internal generator and crashes