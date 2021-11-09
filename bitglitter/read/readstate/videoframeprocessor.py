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


class VideoFrameProcessor:
    def __init__(self, dict_obj):
        frame_position = dict_obj['current_frame_position']
        total_frames = dict_obj['total_frames']
        percentage_string = f'{round(((frame_position / total_frames) * 100), 2):.2f}'
        logging.info(f"Processing video frame {frame_position} of {total_frames}... {percentage_string} %")

        self.dict_obj = dict_obj

        self.ERROR_SOFT = {'error': True}  # Only this frame is cancelled, decoding can continue on next frame
        self.ERROR_FATAL = {'error': True, 'fatal': True}  # Entire session is cancelled
        self.frame_errors = {}

        self.frame = self.dict_obj['frame']
        self.frame_pixel_height = self.frame.shape[0]
        self.frame_pixel_width = self.frame.shape[1]

        self.initializer_palette_a = self.dict_obj['initializer_palette_a_color_set']
        self.initializer_palette_a_color_set = self.dict_obj['initializer_palette_a_color_set']
        self.initializer_palette_a_dict = self.dict_obj['initializer_palette_a_dict']

        self.stream_palette = None
        self.stream_palette_dict = None
        self.stream_palette_color_set = None
        self.stream_palette_loaded_this_frame = False #todo

        # State
        self.is_sequential = self.dict_obj['sequential']
        self.is_unique_frame = False
        self.frame_hashable_bits = BitStream()
        self.stream_payload_bits = BitStream()
        self.frame_blocks_left = True
        self.payload_in_frame = False #todo
        self.save_statistics = self.dict_obj['save_statistics']

        self.stream_read = None
        self.scan_handler = None
        self.stream_frame = None
        self.frame_sha256 = None
        self.frame_number = None
        self.metadata = None

        # First frame variables
        self.output_directory = None
        self.block_height_override = None
        self.block_width_override = None
        self.decryption_key = None
        self.scrypt_n = None
        self.scrypt_r = None
        self.scrypt_p = None
        self.temp_save_directory = None
        self.initializer_palette_b_color_set = None
        self.initializer_palette_b_dict = None
        self.auto_delete_finished_stream = None
        self.auto_unpackage_stream = None
        self.stop_at_metadata_load = None
        self.block_height = None
        self.block_width = None
        self.pixel_width = None

        # Video frames 2+
        if 'stream_read' in self.dict_obj:
            self._second_frame_onwards_setup()

            # Still grabbing setup headers in this frame
            if self.is_sequential:
                if not self.stream_read.stream_header_complete:
                    if not self._stream_header_process_attempt():
                        self.frame_errors = self.ERROR_FATAL
                if not self.frame_errors:
                    pass


            # Multiprocessing
            else:
                pass

        else:
            if not self._initial_frame_setup():
                self.frame_errors = self.ERROR_FATAL
            if not self.frame_errors:
                if not self._frame_header_process(first_frame=True):
                    self.frame_errors = self.ERROR_FATAL
            if not self.frame_errors:
                if not self._stream_header_process_attempt():
                    self.frame_errors = self.ERROR_FATAL
            if not self.frame_errors:
                if not self._metadata_header_process_attempt():
                    self.frame_errors = self.ERROR_FATAL
            if not self.frame_errors:
                if not self._palette_header_attempt():
                    self.frame_errors = self.ERROR_FATAL
            self._run_statistics()

    def _initial_frame_setup(self):
        self.output_directory = self.dict_obj['output_directory']
        self.block_height_override = self.dict_obj['block_height_override']
        self.block_width_override = self.dict_obj['block_width_override']
        self.decryption_key = self.dict_obj['decryption_key']
        self.scrypt_n = self.dict_obj['scrypt_n']
        self.scrypt_r = self.dict_obj['scrypt_r']
        self.scrypt_p = self.dict_obj['scrypt_p']
        self.temp_save_directory = self.dict_obj['temp_save_directory']
        self.initializer_palette_b_color_set = self.dict_obj['initializer_palette_b_color_set']
        self.initializer_palette_b_dict = self.dict_obj['initializer_palette_b_dict']
        self.auto_delete_finished_stream = self.dict_obj['auto_delete_finished_stream']
        self.auto_unpackage_stream = self.dict_obj['auto_unpackage_stream']
        self.stop_at_metadata_load = self.dict_obj['stop_at_metadata_load']

        # Geometry override checkpoint
        if not geometry_override_checkpoint(self.block_height_override, self.block_width_override,
                                            self.frame_pixel_height, self.frame_pixel_width):
            return False

        # Frame lock on
        lock_on_results = frame_lock_on(self.frame, self.block_height_override, self.block_width_override,
                                        self.frame_pixel_height, self.frame_pixel_width,
                                        self.initializer_palette_a_color_set, self.initializer_palette_b_color_set,
                                        self.initializer_palette_a_dict, self.initializer_palette_b_dict)
        if not lock_on_results:
            return False
        self.block_height = lock_on_results['block_height']
        self.block_width = lock_on_results['block_width']
        self.pixel_width = lock_on_results['pixel_width']

        # Now we passed minimum frame validation, moving to ScanHandler setup
        self.scan_handler = ScanHandler(self.frame, True, self.initializer_palette_a, self.initializer_palette_a_dict,
                                        self.initializer_palette_a_color_set)
        self.scan_handler.set_scan_geometry(self.block_height, self.block_width, self.pixel_width)

        #  Initializer scan and decode
        initializer_results = self.scan_handler.return_initializer_bits()
        if 'error' in initializer_results:
            return False
        initializer_bits_raw = initializer_results['bits']
        initializer_decode_results = initializer_header_validate_decode(initializer_bits_raw, self.block_height,
                                                                        self.block_width)
        if 'error' in initializer_decode_results:
            return False

        protocol_version = initializer_decode_results['protocol_version']
        self.stream_sha256 = initializer_decode_results['stream_sha256']

        self.stream_palette = None
        self.palette_header_complete = False
        if 'palette' in initializer_decode_results:  # Palette already stored in db, not pending in future header
            self.stream_palette = initializer_decode_results['palette']
            self.stream_palette_dict = self.stream_palette.return_decoder()
            self.stream_palette_color_set = self.stream_palette.convert_colors_to_tuple()
            self.scan_handler.set_stream_palette(self.stream_palette, self.stream_palette_dict,
                                                 self.stream_palette_color_set)
            self.palette_header_complete = True
            self.stream_palette_loaded_this_frame = True

        # Blacklist check
        blacklisted_hash = StreamSHA256Blacklist.query.filter(StreamSHA256Blacklist == self.stream_sha256).first()
        if blacklisted_hash:
            logging.warning(f'Hash {self.stream_sha256} is on your blacklist.  Aborting stream...')
            return False

        # Loading or creating StreamRead instance
        self.stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == self.stream_sha256).first()
        if self.stream_read:
            if self.stream_read.is_complete:
                logging.info(f'{self.stream_read.stream_name} -- {self.stream_sha256} is complete.  Aborting...')
                return False
            else:
                self.stream_read.session_activity(True)
            logging.info(f'Existing stream read found: {self.stream_read}')

        else:
            logging.info(f'New stream: {self.stream_sha256}')
            self.stream_read = StreamRead.create(stream_sha256=self.stream_sha256, stream_is_video=True,
                                                 protocol_version=protocol_version, output_directory=
                                                 self.output_directory, decryption_key=self.decryption_key, scrypt_n=
                                                 self.scrypt_n, scrypt_r=self.scrypt_r, scrypt_p=self.scrypt_p,
                                                 auto_delete_finished_stream=self.auto_delete_finished_stream,
                                                 stop_at_metadata_load=self.stop_at_metadata_load,
                                                 palette_header_complete=self.palette_header_complete,
                                                 auto_unpackage_stream=self.auto_unpackage_stream, block_height=
                                                 self.block_height, block_width=self.block_width, pixel_width=
                                                 self.pixel_width)
            if self.stream_palette:
                self.stream_read.stream_palette_load(self.stream_palette)

        return True

    def _frame_header_process(self, first_frame: bool):
        # Frame header process and decode
        frame_header_bits_raw = self.scan_handler.return_frame_header_bits(is_initializer_palette=first_frame)['bits']
        frame_header_decode_results = frame_header_decode(frame_header_bits_raw)
        if not frame_header_decode_results:
            return False
        self.frame_sha256 = frame_header_decode_results['frame_sha256']
        self.frame_number = frame_header_decode_results['frame_number']
        bits_to_read = frame_header_decode_results['bits_to_read']
        self.scan_handler.set_bits_to_read(bits_to_read)

        # Checking if frame exists
        self.stream_frame = StreamFrame.query.filter(StreamFrame.stream_id == self.stream_read.id) \
            .filter(StreamFrame.frame_number == self.frame_number).first()
        if self.stream_frame:  # Frame already loaded, skipping
            if self.stream_frame.is_complete:  # Current frame is fully validated and saved
                logging.debug(f'Frame is already complete: {self.frame_number}')
            else:  # Current frame is being actively processed by another process
                logging.debug(f'Pending active frame in another process: {self.frame_number}')
            self.frame_blocks_left = False
        else:  # New frame
            self.stream_frame = StreamFrame.create(stream_id=self.stream_read.id, frame_number=self.frame_number)
            logging.debug(f'New frame: #{self.frame_number}')
            self.is_unique_frame = True

    def _stream_header_process_attempt(self):
        if self.frame_blocks_left:
            stream_header_results = self.scan_handler.return_stream_header_bits(is_initializer_palette=True)
            if not stream_header_results['complete_request']:  # Couldn't fit in this frame, moving to the next
                # todo return carry over bits
                self.frame_blocks_left = False
            else:
                stream_header_bits_raw = stream_header_results['bits']
                self.frame_hashable_bits += stream_header_results['bits']
                stream_header_decode_results = stream_header_decode(stream_header_bits_raw)
                if not stream_header_decode_results:
                    return False
                size_in_bytes = stream_header_decode_results['size_in_bytes']
                total_frames = stream_header_decode_results['total_frames']
                compression_enabled = stream_header_decode_results['compression_enabled']
                encryption_enabled = stream_header_decode_results['encryption_enabled']
                file_masking_enabled = stream_header_decode_results['file_masking_enabled']
                metadata_header_length = stream_header_decode_results['metadata_header_length']
                metadata_header_hash = stream_header_decode_results['metadata_header_hash']
                custom_palette_header_length = stream_header_decode_results['custom_palette_header_length']
                custom_palette_header_hash = stream_header_decode_results['custom_palette_header_hash']
                self.stream_read.stream_header_load(size_in_bytes, total_frames, compression_enabled,
                                                    encryption_enabled, file_masking_enabled, metadata_header_length,
                                                    metadata_header_hash, custom_palette_header_length,
                                                    custom_palette_header_hash)
        return True

    def _metadata_header_process_attempt(self):
        if self.frame_blocks_left:
            metadata_header_results = self.scan_handler.return_bits(self.stream_read.metadata_header_length,
                                                                    is_initializer_palette=True, is_payload=True,
                                                                    byte_input=True)
            if not metadata_header_results['complete_request']:
                # todo return carry over bits
                self.frame_blocks_left = False
                return #todo- not failure, but ok -> next frame state
            metadata_header_bytes = metadata_header_results['bits'].bytes
            self.frame_hashable_bits += metadata_header_bytes
            metadata_header_decode_results = metadata_header_validate_decode(metadata_header_bytes,
                                                                             self.stream_read.metadata_header_hash,
                                                                             self.stream_read.decryption_key,
                                                                             self.stream_read.encryption_enabled,
                                                                             self.stream_read.scrypt_n,
                                                                             self.stream_read.scrypt_r,
                                                                             self.stream_read.scrypt_p)
            if not metadata_header_decode_results:
                return False
            bg_version = metadata_header_decode_results['bg_version']
            stream_name = metadata_header_decode_results['stream_name']
            stream_description = metadata_header_decode_results['stream_description']
            time_created = metadata_header_decode_results['time_created']
            manifest_string = metadata_header_decode_results['manifest_string']
            self.stream_read.metadata_header_load(bg_version, stream_name, stream_description, time_created,
                                                  manifest_string)
        return True

    def _palette_header_attempt(self):
        if self.frame_blocks_left and self.stream_read.custom_palette_used:
            pass
            # if palette id is in db scan_handler.skip_frames(len) else normal read
            #todo hashable bits
            #todo skip processing if palette ID is in DB
        return True

    def _payload_process(self):
        if self.frame_blocks_left:
            self.stream_payload_bits = self.scan_handler.return_payload_bits()['bits']
            self.payload_in_frame = True

    def _frame_validation(self):
        if self.is_unique_frame:
            frame_hashable_bytes = (self.frame_hashable_bits + self.stream_payload_bits).tobytes()
            if self.frame_sha256 != get_sha256_hash_from_bytes(frame_hashable_bytes):
                logging.warning('Setup frame corrupted.  Aborting stream...')
                return False

            # Marking frame as complete, moving on to next frame
            if self.payload_in_frame:
                self.stream_frame.finalize_frame(self.stream_payload_bits)
            else:
                self.stream_frame.finalize_frame()
            if self.is_sequential:
                self.stream_read.new_setup_frame(self.frame_number)

    def _metadata_checkpoint(self):
        if self.stream_read.stop_at_metadata_load and not self.stream_read.metadata_checkpoint_ran:
            logging.info(f'Returning metadata from {self.stream_read}')
            self.metadata = self.stream_read.metadata_checkpoint_return()


    def _run_statistics(self):
        if self.save_statistics:
            read_stats_update(self.scan_handler.block_position, 1, int(self.scan_handler.bits_read / 8))

    def _second_frame_onwards_setup(self):
        self.stream_read = self.dict_obj['stream_read']
        self.scan_handler = ScanHandler(self.frame, False, self.initializer_palette_a, self.initializer_palette_a_dict,
                                        self.initializer_palette_a_color_set, block_height=
                                        self.stream_read.block_height, block_width=self.stream_read.block_width,
                                        pixel_width=self.stream_read.pixel_width)
        if 'stream_palette' in self.dict_obj:
            self.scan_handler.set_stream_palette(self.dict_obj['stream_palette'], self.dict_obj['stream_palette_dict'],
                                            self.dict_obj['stream_palette_color_set'])
