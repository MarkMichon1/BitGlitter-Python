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