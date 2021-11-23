from bitstring import BitStream

import logging

from bitglitter.config.configfunctions import read_stats_update
from bitglitter.config.palettefunctions import import_custom_palette_from_header
from bitglitter.config.readmodels.streamread import StreamRead
from bitglitter.config.readmodels.readmodels import StreamFrame, StreamSHA256Blacklist
from bitglitter.read.decode.headerdecode import custom_palette_header_validate_decode, frame_header_decode, \
    initializer_header_validate_decode, metadata_header_validate_decode, stream_header_decode
from bitglitter.read.scan.scanvalidate import frame_lock_on, geometry_override_checkpoint
from bitglitter.read.scan.scanhandler import ScanHandler
from bitglitter.utilities.cryptography import get_sha256_hash_from_bytes


class ImageFrameProcessor:
    def __init__(self, dict_obj):
        frame_position = dict_obj['current_frame_position']
        total_frames = dict_obj['total_frames']
        file_name = dict_obj['file_name']
        percentage_string = f'{round(((frame_position / total_frames) * 100), 2):.2f}'
        logging.info(f"Processing \"{file_name}\" - {frame_position} of {total_frames}... {percentage_string} %")

        self.starting_state = dict_obj['starting_state']

        self.ERROR_SOFT = {'error': True}  # Only this frame is cancelled, decoding can continue on next frame
        self.ERROR_BREAK = {'break': True}  # Not corruption related, some condition that requires skipping instead
        self.frame_errors = {}

        # State
        self.is_unique_frame = False
        self.frame_hashable_bits = BitStream()
        self.stream_payload_bits = BitStream()
        self.frame_blocks_left = True
        self.payload_in_frame = False
        self.setup_headers_end_this_frame = False
        self.save_statistics = self.starting_state['save_statistics']

        self.stream_read = None
        self.scan_handler = None #setup when
        self.stream_frame = None
        self.stream_sha256 = None
        self.frame_sha256 = None
        self.frame_number = None
        self.metadata = None
        self.metadata_header_bytes = None
        self.palette_header_bytes = None
        self.bits_to_read = None

        # Setup
        self.frame = dict_obj['frame']
        self.frame_pixel_height = self.frame.shape[0]
        self.frame_pixel_width = self.frame.shape[1]
        self.initializer_palette_a = self.starting_state['initializer_palette_a']
        self.initializer_palette_a_color_set = self.starting_state['initializer_palette_a_color_set']
        self.initializer_palette_a_dict = self.starting_state['initializer_palette_a_dict']
        self.initializer_palette_b_color_set = self.starting_state['initializer_palette_b_color_set']
        self.initializer_palette_b_dict = self.starting_state['initializer_palette_b_dict']

        self.output_directory = self.starting_state['output_directory']
        self.block_height_override = self.starting_state['block_height_override']
        self.block_width_override = self.starting_state['block_width_override']
        self.decryption_key = self.starting_state['decryption_key']
        self.scrypt_n = self.starting_state['scrypt_n']
        self.scrypt_r = self.starting_state['scrypt_r']
        self.scrypt_p = self.starting_state['scrypt_p']
        self.temp_save_directory = self.starting_state['temp_save_directory']
        self.auto_delete_finished_stream = self.starting_state['auto_delete_finished_stream']
        self.auto_unpackage_stream = self.starting_state['auto_unpackage_stream']
        self.stop_at_metadata_load = self.starting_state['stop_at_metadata_load']

        self.block_height = None
        self.block_width = None
        self.pixel_width = None

        self.stream_palette = None
        self.stream_palette_id = None
        self.stream_palette_dict = None
        self.stream_palette_color_set = None

        self._initial_frame_setup()
        self._frame_header_process()
        if self.frame_number == 1:
            self._stream_header_process()
        if self.stream_read and self.frame_number:
            if not self.stream_read.is_payload_ready() and \
                    self.frame_number - 1 == self.stream_read.highest_consecutive_setup_frame_read:
                if not self.stream_read.metadata_header_complete:
                    self._metadata_header_process_attempt()
                if not self.stream_read.palette_header_complete:
                    self._palette_header_process_attempt()
        self._payload_process()
        self._frame_validation()
        self._metadata_checkpoint()
        self._run_statistics()
        self.scan_handler = None  # Keep as is, multiprocessing cannot return its internal generator and crashes
        logging.debug('Frame decode cycle complete.')

    def _initial_frame_setup(self):
        # Geometry override checkpoint
        if not geometry_override_checkpoint(self.block_height_override, self.block_width_override,
                                            self.frame_pixel_height, self.frame_pixel_width):
            self.frame_errors = self.ERROR_SOFT
            return

        # Geometry override checkpoint
        if not geometry_override_checkpoint(self.block_height_override, self.block_width_override,
                                            self.frame_pixel_height, self.frame_pixel_width):
            self.frame_errors = self.ERROR_SOFT
            return

        # Frame lock on
        lock_on_results = frame_lock_on(self.frame, self.block_height_override, self.block_width_override,
                                        self.frame_pixel_height, self.frame_pixel_width,
                                        self.initializer_palette_a_color_set, self.initializer_palette_b_color_set,
                                        self.initializer_palette_a_dict, self.initializer_palette_b_dict)
        if not lock_on_results:
            self.frame_errors = self.ERROR_SOFT
            return
        self.block_height = lock_on_results['block_height']
        self.block_width = lock_on_results['block_width']
        self.pixel_width = lock_on_results['pixel_width']

        # Now we passed minimum frame validation, moving to ScanHandler setup
        self.scan_handler = ScanHandler(self.frame, True, self.initializer_palette_a, self.initializer_palette_a_dict,
                                        self.initializer_palette_a_color_set, self.block_height, self.block_width,
                                        self.pixel_width)

        #  Initializer scan and decode
        initializer_results = self.scan_handler.return_initializer_bits()
        if 'error' in initializer_results:
            self.frame_errors = self.ERROR_SOFT
            return
        initializer_bits_raw = initializer_results['bits']
        initializer_decode_results = initializer_header_validate_decode(initializer_bits_raw, self.block_height,
                                                                        self.block_width)
        if 'error' in initializer_decode_results:
            self.frame_errors = self.ERROR_SOFT
            return

        protocol_version = initializer_decode_results['protocol_version']
        custom_palette_used = initializer_decode_results['custom_palette_used']
        self.stream_sha256 = initializer_decode_results['stream_sha256']

        self.palette_header_complete = False
        if initializer_decode_results['palette']:  # Palette already stored in db, not pending in future header
            self.stream_palette = initializer_decode_results['palette']
            self.stream_palette_dict = self.stream_palette.return_decoder()
            self.stream_palette_color_set = self.stream_palette.convert_colors_to_tuple()
            self.scan_handler.set_stream_palette(self.stream_palette, self.stream_palette_dict,
                                                 self.stream_palette_color_set)
            self.palette_header_complete = not custom_palette_used
            self.stream_palette_loaded_this_frame = True
            custom_palette_loaded = True
        else:
            self.stream_palette_id = initializer_decode_results['stream_palette_id']
            custom_palette_loaded = False

        # Blacklist check
        blacklisted_hash = StreamSHA256Blacklist.query.filter(StreamSHA256Blacklist == self.stream_sha256).first()
        if blacklisted_hash:
            logging.warning(f'Hash {self.stream_sha256} is on your blacklist.  Aborting...')
            self.frame_errors = self.ERROR_SOFT
            return

        # Loading or creating StreamRead instance
        self.stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == self.stream_sha256).first()
        if self.stream_read:
            if self.stream_read.is_complete:
                logging.info(f'{self.stream_read.stream_name} -- {self.stream_sha256} is complete.  Aborting...')
                self.frame_errors = self.ERROR_BREAK
                return
            else:
                self.stream_read.session_activity(True, save=False)
                self.stream_read.toggle_eligibility_calculations(True)
            logging.info(f'Existing stream read found: {self.stream_read}')
            if self.stream_read.all_frames_accounted_for:
                logging.info('All frames accounted for, skipping video frame processing...')
                self.frame_errors = self.ERROR_SOFT
                return

        else:
            logging.info(f'New stream: {self.stream_sha256}')
            self.stream_read = StreamRead.create(stream_sha256=self.stream_sha256, stream_is_video=False,
                                                 protocol_version=protocol_version, output_directory=
                                                 self.output_directory, decryption_key=self.decryption_key, scrypt_n=
                                                 self.scrypt_n, scrypt_r=self.scrypt_r, scrypt_p=self.scrypt_p,
                                                 auto_delete_finished_stream=self.auto_delete_finished_stream,
                                                 stop_at_metadata_load=self.stop_at_metadata_load,
                                                 palette_header_complete=self.palette_header_complete,
                                                 auto_unpackage_stream=self.auto_unpackage_stream, block_height=
                                                 self.block_height, block_width=self.block_width, pixel_width=
                                                 self.pixel_width, stream_palette_id=self.stream_palette_id,
                                                 custom_palette_used=custom_palette_used, custom_palette_loaded=
                                                 custom_palette_loaded)
            if self.stream_palette:
                self.stream_read.stream_palette_load(self.stream_palette)

    def _frame_header_process(self):

        if self.frame_errors:
            return

        if self.stream_read.is_payload_ready():
            is_initializer_palette = False
        else:
            is_initializer_palette = True

        frame_header_bits_raw = self.scan_handler.return_frame_header_bits(is_initializer_palette=
                                                                           is_initializer_palette)['bits']
        frame_header_decode_results = frame_header_decode(frame_header_bits_raw)
        if not frame_header_decode_results:
            self.frame_errors = self.ERROR_SOFT
            return
        self.frame_sha256 = frame_header_decode_results['frame_sha256']
        self.frame_number = frame_header_decode_results['frame_number']
        self.bits_to_read = frame_header_decode_results['bits_to_read']
        self.scan_handler.set_bits_to_read(self.bits_to_read)

        # Breaking out of frame if non-sequential frame while setting up stream, and a custom palette is used not in DB
        if not self.stream_read.is_payload_ready() and self.stream_read.custom_palette_used and \
            not self.stream_read.custom_palette_loaded:
            if self.frame_number - 1 != self.stream_read.highest_consecutive_setup_frame_read:
                logging.warning('Cannot read frame, as palette header (in the first few frames) hasn\' yet been'
                                'read/decoded.  Aborting frame...')
                self.frame_errors = self.ERROR_SOFT
                return

        # Checking if frame exists
        self.stream_frame = StreamFrame.query.filter(StreamFrame.stream_id == self.stream_read.id) \
            .filter(StreamFrame.frame_number == self.frame_number).first()
        if self.stream_frame:  # Frame already loaded, skipping
            if self.stream_frame.is_complete:  # Current frame is fully validated and saved
                logging.info(f'Frame {self.frame_number} is already complete')
            else:  # Current frame is being actively processed by another process
                logging.debug(f'Pending active frame in another process: {self.frame_number}')
            self.frame_blocks_left = False
        else:  # New frame
            self.stream_frame = StreamFrame.create(stream_id=self.stream_read.id, frame_number=self.frame_number)
            logging.debug(f'New frame: #{self.frame_number}')
            self.is_unique_frame = True

    def _stream_header_process(self):
        if self.frame_errors:
            return
        if self.frame_blocks_left:
            stream_header_results = self.scan_handler.return_stream_header_bits(is_initializer_palette=True)

            # Note- stream header always fits in first frame with current protocol, hence the missing carry over logic.
            stream_header_bits_raw = stream_header_results['bits']
            self.frame_hashable_bits += stream_header_results['bits']
            stream_header_decode_results = stream_header_decode(stream_header_bits_raw)
            if not stream_header_decode_results:
                self.frame_errors = self.ERROR_SOFT
                return
            logging.info(stream_header_decode_results)
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

    def _metadata_header_process_attempt(self):
        def _metadata_header_decode():
            """Actual header processing once all bytes are accounted for."""

            metadata_header_decode_results = metadata_header_validate_decode(self.metadata_header_bytes,
                                                                             self.stream_read.metadata_header_sha256_raw,
                                                                             self.stream_read.decryption_key,
                                                                             self.stream_read.encryption_enabled,
                                                                             self.stream_read.file_masking_enabled,
                                                                             self.stream_read.scrypt_n,
                                                                             self.stream_read.scrypt_r,
                                                                             self.stream_read.scrypt_p)

            # Incorrect decryption key, storing header bytes in stream read
            if metadata_header_decode_results == None:
                self.stream_read.accept_encrypted_metadata_bytes(self.metadata_header_bytes)

            # Corrupted header
            elif metadata_header_decode_results == False:
                self.frame_errors = self.ERROR_SOFT
                return

            # Successful and decode (and successful decryption if applicable)
            elif 'bg_version' in metadata_header_decode_results:
                bg_version = metadata_header_decode_results['bg_version']
                stream_name = metadata_header_decode_results['stream_name']
                stream_description = metadata_header_decode_results['stream_description']
                time_created = metadata_header_decode_results['time_created']
                manifest_string = metadata_header_decode_results['manifest_string']
                self.stream_read.metadata_header_load(bg_version, stream_name, stream_description, time_created,
                                                      manifest_string)

        if self.frame_errors:
            return
        if self.frame_blocks_left:

            if self.stream_read.carry_over_header_bytes:  # Loading in previous bytes from last frame to re-attempt
                metadata_header_bits = self.stream_read.return_pending_header_bits()
                scan_length = (self.stream_read.metadata_header_size_bytes * 8) - metadata_header_bits.len
                metadata_scan_results = self.scan_handler.return_bits(scan_length, is_initializer_palette=True,
                                                                      is_payload=True, byte_input=False)
                metadata_header_bits += metadata_scan_results['bits']

                if metadata_scan_results['complete_request']:  # Header terminates here
                    logging.debug('Metadata header terminates this frame.')
                    self.metadata_header_bytes = metadata_header_bits.tobytes()
                    self.frame_hashable_bits += metadata_scan_results['bits']
                    self.setup_headers_end_this_frame = True if not self.stream_read.custom_palette_used else False
                    if self.stream_read.decryption_key and self.stream_read.file_masking_enabled or \
                            not self.stream_read.file_masking_enabled:
                        _metadata_header_decode()
                        self.stream_read.set_pending_header_bits()
                    else:
                        logging.info('This stream has file masking enabled, and no decryption key was provided.  Cannot'
                                     ' open metadata header until a decryption key (and a proper one) is provided!')
                        self.stream_read.accept_encrypted_metadata_bytes(self.metadata_header_bytes)
                        return
                else:  # Header carries over into next frame
                    logging.debug('Metadata header rolling over to next frame...')
                    self.stream_read.set_pending_header_bits(metadata_header_bits)
                    self.frame_blocks_left = False
                    self.frame_hashable_bits += metadata_scan_results['bits']
                    return

            else:  # First frame
                metadata_scan_results = self.scan_handler.return_bits(self.stream_read.metadata_header_size_bytes,
                                                                      is_initializer_palette=True, is_payload=True,
                                                                      byte_input=True)
                metadata_header_bits = metadata_scan_results['bits']
                if not metadata_scan_results['complete_request']:
                    logging.debug('Metadata header rolling over to next frame...')
                    self.stream_read.set_pending_header_bits(metadata_header_bits)
                    self.frame_blocks_left = False
                    self.frame_hashable_bits += metadata_header_bits
                    return
                self.metadata_header_bytes = metadata_header_bits.tobytes()
                self.frame_hashable_bits += self.metadata_header_bytes
                _metadata_header_decode()
                self.setup_headers_end_this_frame = True if not self.stream_read.custom_palette_used else False

    def _palette_header_process_attempt(self):
        def _palette_header_decode():
            """Actual header processing once all bytes are accounted for."""
            self.stream_read.palette_header_complete = True
            self.stream_read.save()

            if self.stream_read.custom_palette_loaded or not self.stream_read.custom_palette_used:
                return

            palette_header_decode_results = custom_palette_header_validate_decode(self.palette_header_bytes,
                                                                                  self.stream_read.palette_header_sha256)

            # Header integrity error
            if palette_header_decode_results == False:
                self.frame_errors = self.ERROR_SOFT
                return

            # Successfully decoded
            elif 'palette_id' in palette_header_decode_results:
                palette_id = palette_header_decode_results['palette_id']
                palette_name = palette_header_decode_results['palette_name']
                palette_description = palette_header_decode_results['palette_description']
                time_created = palette_header_decode_results['time_created']
                number_of_colors = palette_header_decode_results['number_of_colors']
                color_list = palette_header_decode_results['color_list']

                results = import_custom_palette_from_header(palette_id, self.stream_read.stream_palette_id,
                                                            palette_name, palette_description, time_created,
                                                            number_of_colors, color_list)

                # Failure
                if results == False:
                    self.frame_errors = self.ERROR_SOFT
                    return

                self.stream_palette = results['palette']
                self.stream_read.stream_palette_load(self.stream_palette)
                self.stream_palette_dict = self.stream_palette.return_decoder()
                self.stream_palette_color_set = self.stream_palette.convert_colors_to_tuple()
                self.scan_handler.set_stream_palette(self.stream_palette, self.stream_palette_dict,
                                                     self.stream_palette_color_set)
                self.stream_palette_loaded_this_frame = True

        if self.frame_errors:
            return
        if self.frame_blocks_left and self.stream_read.custom_palette_used:

            if self.stream_read.carry_over_header_bytes:
                palette_header_bits = self.stream_read.return_pending_header_bits()
                scan_length = (self.stream_read.palette_header_size_bytes * 8) - palette_header_bits.len
                palette_scan_results = self.scan_handler.return_bits(scan_length, is_initializer_palette=True,
                                                                     is_payload=True, byte_input=False)
                palette_header_bits += palette_scan_results['bits']

                if palette_scan_results['complete_request']:
                    logging.debug('Custom palette header terminates this frame')
                    self.palette_header_bytes = palette_header_bits.tobytes()
                    self.frame_hashable_bits += palette_scan_results['bits']
                    _palette_header_decode()

                    self.stream_read.set_pending_header_bits()

                else:
                    logging.debug('Palette header rolling over to next frame...')
                    self.stream_read.set_pending_header_bits(palette_header_bits)
                    self.frame_blocks_left = False
                    self.frame_hashable_bits += palette_scan_results['bits']
                    return

            else:
                palette_scan_results = self.scan_handler.return_bits(self.stream_read.palette_header_size_bytes,
                                                                     is_initializer_palette=True, is_payload=True,
                                                                     byte_input=True)
                palette_header_bits = palette_scan_results['bits']
                if not palette_scan_results['complete_request']:
                    logging.debug('Palette header rolling over to next frame...')
                    self.stream_read.set_pending_header_bits(palette_header_bits)
                    self.frame_blocks_left = False
                    self.frame_hashable_bits += palette_header_bits
                    return
                self.palette_header_bytes = palette_header_bits.tobytes()
                self.frame_hashable_bits += self.palette_header_bytes
                _palette_header_decode()

    def _payload_process(self):
        if self.frame_errors:
            return
        if self.frame_blocks_left:
            self.stream_payload_bits = self.scan_handler.return_payload_bits()['bits']
            self.payload_in_frame = True

    def _frame_validation(self):
        if self.frame_errors:
            return
        if self.is_unique_frame:
            frame_hashable_bytes = (self.frame_hashable_bits + self.stream_payload_bits).tobytes()
            assert self.frame_hashable_bits.len + self.stream_payload_bits.len == self.bits_to_read
            if self.frame_sha256 != get_sha256_hash_from_bytes(frame_hashable_bytes):
                logging.warning('Frame corrupted.  Aborting frame...')
                self.frame_errors = self.ERROR_SOFT
                return

            # Marking frame as complete, moving on to next frame
            if self.payload_in_frame:
                self.stream_frame.finalize_frame(self.stream_payload_bits)

                # First frame with payload in it
                if self.setup_headers_end_this_frame:
                    print('HERE')
                    self.stream_read.set_payload_start_data(self.frame_number, self.stream_payload_bits.len)
            else:
                self.stream_frame.finalize_frame()
            if self.frame_number - 1 == self.stream_read.highest_consecutive_setup_frame_read:
                self.stream_read.new_setup_frame(self.frame_number)

    def _metadata_checkpoint(self):
        if self.stream_read.stop_at_metadata_load and not self.stream_read.metadata_checkpoint_ran:
            logging.info(f'Returning metadata from {self.stream_read}')
            self.metadata = self.stream_read.metadata_checkpoint_return()

    def _run_statistics(self):
        if self.save_statistics:
            read_stats_update(self.scan_handler.block_position, 1, self.scan_handler.payload_bits_read)