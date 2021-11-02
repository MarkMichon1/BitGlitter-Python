from bitstring import ConstBitStream

import logging

from bitglitter.config.configfunctions import read_stats_update
from bitglitter.config.readmodels.readmodels import StreamFrame
from bitglitter.config.readmodels.streamread import StreamRead
from bitglitter.read.decode.headerdecode import frame_header_decode, initializer_header_decode, \
    metadata_header_validate_decode, stream_header_decode
from bitglitter.read.scan.scanvalidate import frame_lock_on, minimum_block_checkpoint
from bitglitter.read.scan.scanhandler import ScanHandler
from bitglitter.utilities.encryption import get_sha256_hash_from_bytes

ERROR_SOFT = {'error': True}
ERROR_FATAL = {'error': True, 'fatal': True}


def frame_process(dict_obj):
    """This is ran each time an individual frame is processed, orchestrating scanning, decoding, validation, and finally
    passing the data to StreamRead for saving and file extraction.  Multiprocessing supports only passing one argument,
    hence all arguments being packaged inside dict_object.
    """

    def _initial_frame_process(dict_obj):
        """Used on the first frame of videos as well as every image frame"""

        frame = dict_obj['frame']

        output_directory = dict_obj['output_directory']
        block_height_override = dict_obj['block_height_override']
        block_width_override = dict_obj['block_width_override']
        encryption_key = dict_obj['encryption_key']
        scrypt_n = dict_obj['scrypt_n']
        scrypt_r = dict_obj['scrypt_r']
        scrypt_p = dict_obj['scrypt_p']
        temp_save_directory = dict_obj['temp_save_directory']
        initializer_palette_a = dict_obj['initializer_palette_a']
        initializer_palette_a_color_set = dict_obj['initializer_palette_a_color_set']
        initializer_palette_b_color_set = dict_obj['initializer_palette_b_color_set']
        initializer_palette_a_dict = dict_obj['initializer_palette_a_dict']
        initializer_palette_b_dict = dict_obj['initializer_palette_b_dict']

        statistics_enabled = dict_obj['statistics_enabled']
        stop_at_metadata_load = dict_obj['stop_at_metadata_load']
        auto_delete_finished_stream = dict_obj['auto_delete_finished_stream']  # todo load in sr+^

        # Statistics
        blocks_read = 0
        data_read_bits = 0

        returned_state = {}



        return returned_state

    def _video_frame_process(dict_obj):
        """Used on every video frame except the first frame (which needs to be treated differently)"""

        stream_read = dict_obj['stream_read']
        frame = dict_obj['frame']

        # Frame Base Geometry
        frame_pixel_height = frame.shape[0]
        frame_pixel_width = frame.shape[1]

        # Statistics
        blocks_read = 0
        data_read_bits = 0

        returned_state = {}

        if not stream_read.stream_header_complete:
            carry_over_bits = dict_obj['dict_object'] #todo get from sr
            # todo: purge carry over bits upon completion

        if not stream_read.metadata_header_complete:
            carry_over_bits = dict_obj['dict_object']

        if not stream_read.palette_header_complete:
            carry_over_bits = dict_obj['dict_object']
            # todo palette ID load if applicable

        # Continuing on to begin processing payload on this frame

        return returned_state

#######################
    if dict_obj['mode'] == 'video':  # First video frame
        if 'stream_read' in dict_obj:  # Frames 2+
            results = _video_frame_process(dict_obj)
        else:  # Frame 1
            results = _initial_frame_process(dict_obj)
    else : # Image scan
        results = _initial_frame_process(dict_obj)

    if 'stream_read' in results:
        if results['stream_read'].test:
            read_stats_update(results['blocks_read'], 1, int(results['bits_read'] / 8))


##########################

            #  Ensuring override parameters (if given) don't exceed frame pixel dimensions
            # if not minimum_block_checkpoint(block_height_override, block_width_override, frame_pixel_height,
            #                                    frame_pixel_width):
            #     return {'error': True}
            #
            # #  Frame lock on
            # lock_on_results = frame_lock_on(frame, block_height_override, block_width_override, frame_pixel_height,
            #                                 frame_pixel_width, initializer_palette_a_color_set,
            #                                 initializer_palette_b_color_set, initializer_palette_a_dict,
            #                                 initializer_palette_b_dict)
            # if 'error' in lock_on_results:
            #     logging.warning('Frame lock fail.  Aborting...')
            #     return {'abort': True}
            # block_height = lock_on_results['block_height']
            # block_width = lock_on_results['block_width']
            # pixel_width = lock_on_results['pixel_width']
            #
            # #  Now we passed minimum frame validation, moving to ScanHandler setup
            # scan_handler = ScanHandler(frame, True, initializer_palette_a, initializer_palette_a_dict,
            #                            initializer_palette_a_color_set)
            # scan_handler.set_scan_geometry(block_height, block_width, pixel_width)
            #
            # #  Initializer scan and decode
            # results = scan_handler.return_initializer_bits()
            # initializer_bits = results['bits']
            # blocks_read += results['blocks_read']
            # data_read_bits += results['blocks_read']
            # results = initializer_header_decode(initializer_bits, block_height, block_width)
            # if 'abort' in results:
            #     return {'abort': True}
            # protocol_version = results['protocol_version']
            # stream_palette = None
            # if 'palette' in results:  # We already have palette stored in db, and not pending in future palette header
            #     stream_palette = results['palette']
            #     stream_palette_dict = stream_palette.return_decoder()
            #     stream_palette_color_set = stream_palette.convert_colors_to_tuple()
            #     scan_handler.set_stream_palette(stream_palette, stream_palette_dict, stream_palette_color_set)
            #
            # # Loading or creating StreamRead instance
            # stream_sha256 = results['stream_sha256']
            # stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
            # if stream_read:
            #     if stream_read.stream_name:
            #         logging.info(f'Existing stream read found for {stream_read.stream_name} -- {stream_sha256}')
            #     else:
            #         logging.info(f'Existing stream read found: {stream_sha256}')
            # else:
            #     logging.info(f'New stream: {stream_sha256}')
            #     stream_read = StreamRead.create(temp_directory=str(temp_save_directory / stream_sha256),
            #                                     stream_sha256=stream_sha256, stream_is_video=True,
            #                                     protocol_version=protocol_version, output_directory=output_directory,
            #                                     encryption_key=encryption_key, scrypt_n=scrypt_n, scrypt_r=scrypt_r,
            #                                     scrypt_p=scrypt_p, auto_delete_finished_stream=
            #                                     auto_delete_finished_stream)
            #     stream_read.geometry_load(block_height, block_width, pixel_width)
            #     if stream_palette:
            #         stream_read.stream_palette_id_load(stream_palette.palette_id)
            #
            # # Frame header read and decode
            # results = scan_handler.return_frame_header_bits(is_initializer_palette=True)
            # frame_header_bits = results['bits']
            # blocks_read += results['blocks_read']
            # data_read_bits += results['blocks_read']
            # results = frame_header_decode(frame_header_bits)
            # frame_sha256 = results['frame_sha256']
            # frame_number = results['frame_number']
            # bits_to_read = results['bits_to_read']
            # scan_handler.set_bits_to_read(bits_to_read)
            #
            # # Checking if frame exists
            # stream_frame = StreamFrame.query.filter(StreamFrame.stream_id == stream_read.id)\
            #     .filter(StreamFrame.frame_number == frame_number).first()
            # if stream_frame:  # Frame already loaded, skipping
            #     if stream_frame.is_complete:  # Current frame is fully validated and saved
            #         logging.debug(f'Complete frame: {frame_number}')
            #     else:  # Current frame is being actively processed by another process
            #         logging.debug(f'Pending active frame in another process: {frame_number}')
            #     return {} #todo
            # else:  # New frame
            #     logging.debug(f'New frame: {frame_number}')
            #     stream_frame = StreamFrame.create(stream_id=stream_read.id, frame_number=frame_number)
            #
            # # Stream header process and decode
            # results = scan_handler.return_stream_header_bits(is_initializer_palette=True)
            # if not results['complete_request']:  # Couldn't fit in this frame, moving to the next
            #     return #todo return carry over bits
            # stream_header_bits = results['bits']
            # hashable_bits = stream_header_bits
            # blocks_read += results['blocks_read']
            # data_read_bits += results['blocks_read']
            #
            # results = stream_header_decode(stream_header_bits)
            # if 'abort' in results:
            #     return #todo stream failure somehow
            # size_in_bytes = results['size_in_bytes']
            # total_frames = results['total_frames']
            # compression_enabled = results['compression_enabled']
            # encryption_enabled = results['encryption_enabled']
            # file_masking_enabled = results['file_masking_enabled']
            # metadata_header_length = results['metadata_header_length']
            # metadata_header_hash = results['metadata_header_hash']
            # custom_palette_header_length = results['custom_palette_header_length']
            # custom_palette_header_hash = results['custom_palette_header_hash']
            # stream_read.stream_header_load(size_in_bytes, total_frames, compression_enabled, encryption_enabled,
            #                                file_masking_enabled, metadata_header_length, metadata_header_hash,
            #                                custom_palette_header_length, custom_palette_header_hash)
            #
            # # Palette header read if need be
            # if not stream_read.palette_header_complete:
            #     pass # todo palette ID load if applicable
            #     # results = scan_handler.return_bits(metadata_header_length * 8, is_initializer_palette=True, is_payload=True)
            #     # hashable_bits += palette_header_bits
            #     # + hashable bits
            #
            # # Metadata header process and decode
            # results = scan_handler.return_bits(metadata_header_length * 8, is_initializer_palette=True, is_payload=True)
            # if not results['complete_request']:  # Couldn't fit in this frame, moving to the next
            #     return #todo return carry over bits
            # metadata_header_bytes = results['bits'].bytes
            # hashable_bits +=  metadata_header_bytes
            #
            # blocks_read += results['blocks_read']
            # data_read_bits += results['blocks_read']
            # results = metadata_header_validate_decode(metadata_header_bytes, metadata_header_hash, encryption_key,
            #                                           encryption_enabled, scrypt_n, scrypt_r, scrypt_p)
            # if 'abort' in results:
            #     if 'complete' in results:
            #         return #todo- fatal failure
            # else:
            #     stream_read.metadata_header_load(results['bg_version'], results['stream_name'],
            #                                      results['stream_description'], results['time_created'],
            #                                      results['manifest_string'])
            #
            # # Payload process and decode
            # results = scan_handler.return_payload_bits()
            # stream_payload_bits = results['bits']
            # hashable_bytes = (hashable_bits + stream_payload_bits).tobytes()
            # blocks_read += results['blocks_read']
            # data_read_bits += results['blocks_read']
            # # Validating frame as a whole
            # if frame_sha256 != get_sha256_hash_from_bytes(hashable_bytes):
            #     logging.debug('Frame payload corrupted.  Aborting frame...')
            #     return {}  # bad frame strike todo
            #
            # # Marking frame as complete, moving on to the next frame
            # stream_frame.finalize_frame(stream_payload_bits)
            # return {} #todo- return anything if fine?


    return results
