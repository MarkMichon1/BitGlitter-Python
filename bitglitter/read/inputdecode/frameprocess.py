import logging

from bitglitter.config.readmodels.streamread import StreamRead
from bitglitter.read.inputdecode.headerdecode import custom_palette_header_validate_decode, frame_header_decode, \
    initializer_header_decode, metadata_header_validate_decode, stream_header_decode
from bitglitter.read.inputdecode.scanvalidate import frame_lock_on, minimum_block_checkpoint
from bitglitter.read.inputdecode.scanhandler import ScanHandler


def frame_process(dict_object):
    """This is ran each time an individual frame is processed, orchestrating scanning, decoding, validation, and finally
    passing the data to StreamRead for saving and file extraction.  Multiprocessing supports only passing one argument,
    hence all arguments being packaged inside dict_object.
    """

    #  Unpackaging generic variables from dict_object, these are consistent across conditions this function is used
    frame = dict_object['frame']
    mode = dict_object['mode']
    output_path = dict_object['output_path']
    block_height_override = dict_object['block_height_override']
    block_width_override = dict_object['block_width_override']
    encryption_key = dict_object['encryption_key']
    scrypt_n = dict_object['scrypt_n']
    scrypt_r = dict_object['scrypt_r']
    scrypt_p = dict_object['scrypt_p']
    temp_save_path = dict_object['temp_save_path']
    live_payload_unpackaging = dict_object['live_payload_unpackaging']
    initializer_palette_a = dict_object['initializer_palette_a']
    initializer_palette_b = dict_object['initializer_palette_b']
    initializer_palette_a_color_set = dict_object['initializer_palette_a_color_set']
    initializer_palette_b_color_set = dict_object['initializer_palette_b_color_set']
    initializer_palette_a_dict = dict_object['initializer_palette_a_dict']
    initializer_palette_b_dict = dict_object['initializer_palette_b_dict']

    frame_pixel_height = frame.shape[0]
    frame_pixel_width = frame.shape[1]

    blocks_read = 0
    data_read_bits = 0

    if mode == 'video':
        current_frame_position = dict_object['current_frame_position']
        total_video_frames = dict_object['total_video_frames']
        logging.info(f'Scanning frame {current_frame_position}/{total_video_frames}') #todo- put outside if out of order w/ mp, add %

        if current_frame_position != 1:
            pass

            #todo- check bool in streamread
            if '123' in 'placeholder':  # Continued initializer frames
                pass

            else:  #  Standard sequence (pure payload frames, including termination)
                pass
                #  Multiprocessing setup

        else:  #  First frame

            #  Ensuring override parameters (if given) don't exceed frame pixel dimensions
            if not minimum_block_checkpoint(block_height_override, block_width_override, frame_pixel_height,
                                               frame_pixel_width):
                return {'abort': True}

            #  Frame lock on
            lock_on_results = frame_lock_on(frame, block_height_override, block_width_override, frame_pixel_height,
                                            frame_pixel_width, initializer_palette_a_color_set,
                                            initializer_palette_b_color_set, initializer_palette_a_dict,
                                            initializer_palette_b_dict)
            if 'abort' in lock_on_results:
                logging.warning('Frame lock fail.  Aborting...')
                return {'abort': True}
            block_height = lock_on_results['block_height']
            block_width = lock_on_results['block_width']
            pixel_width = lock_on_results['pixel_width']

            #  Now we passed minimum frame validation, moving to ScanHandler setup
            scan_handler = ScanHandler(frame, True, initializer_palette_a, initializer_palette_a_dict,
                                       initializer_palette_a_color_set)
            scan_handler.set_scan_geometry(block_height, block_width, pixel_width)

            #  Initializer scan and decode
            results = scan_handler.return_initializer_bits()
            initializer_bits = results['bits']
            blocks_read += results['blocks_read']
            data_read_bits += results['blocks_read']
            results = initializer_header_decode(initializer_bits, block_height, block_width)
            if 'abort' in results:
                return {'abort': True}
            stream_palette = None
            if 'palette' in results:  # We already have palette stored in db, and not pending in future palette header
                stream_palette = results['palette']
                stream_palette_dict = stream_palette.return_decoder()
                stream_palette_color_set = stream_palette.convert_colors_to_tuple()
                scan_handler.set_stream_palette(stream_palette, stream_palette_dict, stream_palette_color_set)

            # Loading or creating StreamRead instance
            stream_sha256 = results['stream_sha256']
            stream_read = StreamRead.query.filter(StreamRead.stream_sha256 == stream_sha256).first()
            if stream_read:
                if stream_read.stream_name:
                    logging.info(f'Existing stream read found for {stream_read.stream_name} -- {stream_sha256}')
                else:
                    logging.info(f'Existing stream read found: {stream_sha256}')
            else:
                logging.info(f'New stream: {stream_sha256}')
                stream_read = StreamRead.create(stream_sha256=stream_sha256, stream_is_video=True)




    elif mode == 'image':
        pass

    else:
        raise ValueError('Invalid mode for frame_process()')



    # # Setting ScanHandler state #todo- load from generator or not
    # if mode == 'image' or frame_number == 1:
    #     scan_handler = ScanHandler(frame, is_calibrator_frame=True)
    # else:
    #     scan_handler = ScanHandler(frame, is_calibrator_frame=False)
    # if block_height and block_width and pixel_width:
    #     scan_handler.set_scan_geometry(block_height, block_width, pixel_width)

    if live_payload_unpackaging:
        pass  # call streamread and check progress

    # todo- return state data, failures, and carry over bits

    # if mode == 'image':
    #     pass #todo last
    #     """
    #     first frame setup
    #     image frame setup
    #     frame validation
    #     payload process

    # todo: return stream read, stream palette, bW, bH

    return {'final_meta_frame': bool, 'total_blocks': 0, 'is_unique_frame': bool} #todo
