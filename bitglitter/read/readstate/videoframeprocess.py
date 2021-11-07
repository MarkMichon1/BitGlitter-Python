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


def video_frame_process(dict_obj):
    ERROR_SOFT = {'error': True}  # Only this frame is cancelled, decoding can continue on next frame
    ERROR_FATAL = {'error': True, 'fatal': True}  # Entire session is cancelled

    frame = dict_obj['frame']
    frame_pixel_height = frame.shape[0]
    frame_pixel_width = frame.shape[1]

    is_sequential = dict_obj['sequential'] if 'sequential' in dict_obj else False
    is_unique_frame = False
    frame_hashable_bits = BitStream()

    logging.info('') #todo

    if 'stream_read' in dict_obj:  # Video frames 2+
        stream_read = dict_obj['stream_read']

        # Scan handler setup

        if is_sequential:  # Sequential frame processing while gathering metadata headers from initial frames
            pass

        else:  # Multicore processing
            pass

    else:  # First video frame

        output_directory = dict_obj['output_directory']
        block_height_override = dict_obj['block_height_override']
        block_width_override = dict_obj['block_width_override']
        decryption_key = dict_obj['decryption_key']
        scrypt_n = dict_obj['scrypt_n']
        scrypt_r = dict_obj['scrypt_r']
        scrypt_p = dict_obj['scrypt_p']
        temp_save_directory = dict_obj['temp_save_directory']
        initializer_palette_a = dict_obj['initializer_palette_a']
        initializer_palette_a_color_set = dict_obj['initializer_palette_a_color_set']
        initializer_palette_b_color_set = dict_obj['initializer_palette_b_color_set']
        initializer_palette_a_dict = dict_obj['initializer_palette_a_dict']
        initializer_palette_b_dict = dict_obj['initializer_palette_b_dict']

        auto_delete_finished_stream = dict_obj['auto_delete_finished_stream']
        auto_unpackage_stream = dict_obj['auto_unpackage_stream']
        stop_at_metadata_load = dict_obj['stop_at_metadata_load']

        frame_blocks_left = True

        # Geometry override checkpoint
        if not geometry_override_checkpoint(block_height_override, block_width_override, frame_pixel_height,
                                            frame_pixel_width):
            return ERROR_FATAL

        # Frame lock on
        lock_on_results = frame_lock_on(frame, block_height_override, block_width_override, frame_pixel_height,
                                        frame_pixel_width, initializer_palette_a_color_set,
                                        initializer_palette_b_color_set, initializer_palette_a_dict,
                                        initializer_palette_b_dict)
        if not lock_on_results:
            return ERROR_FATAL
        block_height = lock_on_results['block_height']
        block_width = lock_on_results['block_width']
        pixel_width = lock_on_results['pixel_width']

        # Now we passed minimum frame validation, moving to ScanHandler setup
        scan_handler = ScanHandler(frame, True, initializer_palette_a, initializer_palette_a_dict,
                                   initializer_palette_a_color_set)
        scan_handler.set_scan_geometry(block_height, block_width, pixel_width)

        #  Initializer scan and decode
        initializer_results = scan_handler.return_initializer_bits()
        if 'error' in initializer_results:
            return ERROR_FATAL
        initializer_bits_raw = initializer_results['bits']
        initializer_decode_results = initializer_header_validate_decode(initializer_bits_raw, block_height, block_width)
        if 'error' in initializer_decode_results:
            return ERROR_FATAL

        protocol_version = initializer_decode_results['protocol_version']
        stream_sha256 = initializer_decode_results['stream_sha256']

        stream_palette = None
        palette_header_complete = False
        if 'palette' in initializer_decode_results:  # Palette already stored in db, not pending in future header
            stream_palette = initializer_decode_results['palette']
            stream_palette_dict = stream_palette.return_decoder()
            stream_palette_color_set = stream_palette.convert_colors_to_tuple()
            scan_handler.set_stream_palette(stream_palette, stream_palette_dict, stream_palette_color_set)
            palette_header_complete = True

        # Blacklist check
        blacklisted_hash = StreamSHA256Blacklist.query.filter(StreamSHA256Blacklist == stream_sha256).first()
        if blacklisted_hash:
            logging.warning(f'Hash {stream_sha256} is on your blacklist.  Aborting stream...')
            return ERROR_FATAL

        # Loading or creating StreamRead instance
        stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
        if stream_read:
            if stream_read.is_complete:
                logging.info(f'{stream_read.stream_name} -- {stream_sha256} is complete.  Aborting...')
                return ERROR_FATAL
            logging.info(f'Existing stream read found: {stream_read}')
        else:
            logging.info(f'New stream: {stream_sha256}')
            stream_read = StreamRead.create(temp_directory=str(temp_save_directory / stream_sha256),
                                            stream_sha256=stream_sha256, stream_is_video=True,
                                            protocol_version=protocol_version, output_directory=output_directory,
                                            decryption_key=decryption_key, scrypt_n=scrypt_n, scrypt_r=scrypt_r,
                                            scrypt_p=scrypt_p, auto_delete_finished_stream=auto_delete_finished_stream,
                                            stop_at_metadata_load=stop_at_metadata_load, palette_header_complete=
                                            palette_header_complete, auto_unpackage_stream=auto_unpackage_stream,
                                            block_height=block_height, block_width=block_width, pixel_width=pixel_width)
            if stream_palette:
                stream_read.stream_palette_load(stream_palette)

        # Frame header scan and decode
        frame_header_bits_raw = scan_handler.return_frame_header_bits(is_initializer_palette=True)['bits']
        frame_header_decode_results = frame_header_decode(frame_header_bits_raw)
        if not frame_header_decode_results:
            return ERROR_FATAL
        frame_sha256 = frame_header_decode_results['frame_sha256']
        frame_number = frame_header_decode_results['frame_number']
        bits_to_read = frame_header_decode_results['bits_to_read']
        scan_handler.set_bits_to_read(bits_to_read)

        # Checking if frame exists
        stream_frame = StreamFrame.query.filter(StreamFrame.stream_id == stream_read.id) \
            .filter(StreamFrame.frame_number == frame_number).first()
        if stream_frame:  # Frame already loaded, skipping
            if stream_frame.is_complete:  # Current frame is fully validated and saved
                logging.debug(f'Frame is already complete: {frame_number}')
            else:  # Current frame is being actively processed by another process
                logging.debug(f'Pending active frame in another process: {frame_number}')
            frame_blocks_left = False
        else:  # New frame
            stream_frame = StreamFrame.create(stream_id=stream_read.id, frame_number=frame_number)
            logging.debug(f'New frame: #{frame_number}')
            is_unique_frame = True

        # Stream header process and decode
        if frame_blocks_left:
            stream_header_results = scan_handler.return_stream_header_bits(is_initializer_palette=True)
            if not stream_header_results['complete_request']:  # Couldn't fit in this frame, moving to the next
                # todo return carry over bits
                frame_blocks_left = False
            else:
                stream_header_bits_raw = stream_header_results['bits']
                frame_hashable_bits += stream_header_results['bits']
                stream_header_decode_results = stream_header_decode(stream_header_bits_raw)
                if not stream_header_decode_results:
                    return ERROR_FATAL
                size_in_bytes = stream_header_decode_results['size_in_bytes']
                total_frames = stream_header_decode_results['total_frames']
                compression_enabled = stream_header_decode_results['compression_enabled']
                encryption_enabled = stream_header_decode_results['encryption_enabled']
                file_masking_enabled = stream_header_decode_results['file_masking_enabled']
                metadata_header_length = stream_header_decode_results['metadata_header_length']
                metadata_header_hash = stream_header_decode_results['metadata_header_hash']
                custom_palette_header_length = stream_header_decode_results['custom_palette_header_length']
                custom_palette_header_hash = stream_header_decode_results['custom_palette_header_hash']
                stream_read.stream_header_load(size_in_bytes, total_frames, compression_enabled, encryption_enabled,
                                               file_masking_enabled, metadata_header_length, metadata_header_hash,
                                               custom_palette_header_length, custom_palette_header_hash)

        # Metadata header process and decode
        if frame_blocks_left:
            metadata_header_results = scan_handler.return_bits(metadata_header_length, is_initializer_palette=True,
                                                               is_payload=True, byte_input=True)
            if not metadata_header_results['complete_request']:
                # todo return carry over bits
                frame_blocks_left = False
            metadata_header_bytes = metadata_header_results['bits'].bytes
            frame_hashable_bits += metadata_header_bytes
            metadata_header_decode_results = metadata_header_validate_decode(metadata_header_bytes,
                                                                             metadata_header_hash, decryption_key,
                                                                             encryption_enabled, scrypt_n, scrypt_r,
                                                                             scrypt_p)
            if not metadata_header_decode_results:
                return ERROR_FATAL
            bg_version = metadata_header_decode_results['bg_version']
            stream_name = metadata_header_decode_results['stream_name']
            stream_description = metadata_header_decode_results['stream_description']
            time_created = metadata_header_decode_results['time_created']
            manifest_string = metadata_header_decode_results['manifest_string']
            stream_read.metadata_header_load(bg_version, stream_name, stream_description, time_created, manifest_string)

        # Palette header process and decode (if custom palette is)
        if frame_blocks_left and stream_read.custom_palette_used:
            pass
            # if palette id is in db scan_handler.skip_frames(len) else normal read
        #todo hashable bits
        #todo skip processing if palette ID is in DB

        # Payload process and decode
        payload_in_frame = False
        stream_payload_bits = BitStream()
        if frame_blocks_left:
            stream_payload_bits = scan_handler.return_payload_bits()['bits']
            payload_in_frame = True

        returned_dict = {'stream_read': stream_read}

        # Frame Validation
        if is_unique_frame:
            frame_hashable_bytes = (frame_hashable_bits + stream_payload_bits).tobytes()
            if frame_sha256 != get_sha256_hash_from_bytes(frame_hashable_bytes):
                logging.warning('Setup frame corrupted.  Aborting stream...')
                return ERROR_FATAL

            # Marking frame as complete, moving on to next frame
            if payload_in_frame:
                stream_frame.finalize_frame(stream_payload_bits)
            else:
                stream_frame.finalize_frame()
            if is_sequential:
                stream_read.new_setup_frame(frame_number)

            # Metadata checkpoint if enabled
            if stream_read.stop_at_metadata_load:
                logging.info(f'Returning metadata from {stream_read}')
                returned_dict['metadata'] = stream_read.metadata_checkpoint_return()

    # Statistics Update
    if dict_obj['save_statistics']:
        read_stats_update(scan_handler.block_position, 1, int(scan_handler.bits_read / 8))

    return returned_dict

    logging.debug('Successful video frame process cycle')