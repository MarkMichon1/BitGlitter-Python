import logging
from multiprocessing import cpu_count

from cv2 import imread

from bitglitter.config.palettemodels import Palette
from read.readstate.videoframegenerator import video_frame_generator
from read.readstate.frameprocess import frame_process


def frame_read_handler(input_path, output_directory, input_type, bad_frame_strikes, max_cpu_cores,
                       block_height_override, block_width_override, encryption_key,
                       scrypt_n, scrypt_r, scrypt_p, temp_save_path, stop_at_metadata_load): #todo <-

    unique_frames_read = None
    blocks_read = None
    data_read = None
    stream_sha256 = None

    logging.info(f'Processing {input_path}...')

    #  Generic setup
    initializer_palette_a = Palette.query.filter(Palette.nickname == '1').first()
    initializer_palette_b = Palette.query.filter(Palette.nickname == '11').first()
    initializer_palette_a_color_set = initializer_palette_a.convert_colors_to_tuple()
    initializer_palette_b_color_set = initializer_palette_b.convert_colors_to_tuple()
    initializer_palette_a_dict = initializer_palette_a.return_decoder()
    initializer_palette_b_dict = initializer_palette_b.return_decoder()
    dict_object = {'output_directory': output_directory, 'block_height_override': block_height_override, 'block_width_override':
                   block_width_override, 'encryption_key': encryption_key, 'scrypt_n': scrypt_n, 'scrypt_r': scrypt_r,
                   'scrypt_p': scrypt_p, 'temp_save_path': temp_save_path, 'initializer_palette_a':
                   initializer_palette_a, 'initializer_palette_a_color_set': initializer_palette_a_color_set,
                   'initializer_palette_b_color_set': initializer_palette_b_color_set,'initializer_palette_b':
                   initializer_palette_b, 'initializer_palette_a_dict': initializer_palette_a_dict,
                   'initializer_palette_b_dict': initializer_palette_b_dict}

    if input_type == 'video':

        # Processing frames in a single process until all metadata has been received, then we'll switch to multicore
        frame_generator = video_frame_generator(input_path)
        frame_strike_count = 0

        #  frame_process dict_object assemble
        dict_object['mode'] = 'video'

        stream_header_termination = False
        while not stream_header_termination:
            if 'total_video_frames' in dict_object:
                if dict_object['current_frame_position'] == dict_object['total_video_frames']: #  Reached end of video
                    return {'unique_frames_read': unique_frames_read, 'blocks_read': blocks_read, 'data_read':
                        data_read, 'stream_sha256': stream_sha256}
            next_frame_data = next(frame_generator)
            dict_object['frame'] = next_frame_data['frame']
            dict_object['current_frame_position'] = next_frame_data['current_frame_position']
            dict_object['total_video_frames'] = next_frame_data['total_video_frames']

            frame_results = frame_process(dict_object)
            if 'abort' in frame_results: #  Errors in these frames are always total aborts, as they have key stream data
                logging.warning('Critical error, cannot continue.')
                return {'abort': True}
            if 'strike' and bad_frame_strikes:  # placeholder todo
                frame_strike_count += 1
                logging.warning(f'Bad frame strike {frame_strike_count}/{bad_frame_strikes}')
                if frame_strike_count >= bad_frame_strikes:
                    logging.warning('Reached frame strike limit.  Aborting...')
                    return {'abort': True}

            #stats add

            #  frame_results processing


        # Begin multicore frame decode
        if max_cpu_cores == 0 or max_cpu_cores >= cpu_count():
            pool_size = cpu_count()
        else:
            pool_size = max_cpu_cores

        # return stat data
        # with Pool(processes=pool_size) as worker_pool:
        #     logging.info('Metadata decoded, switching to multicore..')
        #     for frame_decode in worker_pool.imap(frame_process, decode_multicore_state_generator()):
        #         if frame_decode['strike']:
        #             frame_strike_count += 1
        #         else:
        #             if frame_decode['is_unique_frame']:
        #                 pass
        #             blocks_read += frame_decode['blocks_read']
                # logging.info(f'Processing frame {video_frame_position} of {total_frames}...'
                #              f'({round(((video_frame_position / total_frames) * 100), 2):.2f} %)')

    elif input_type == 'image':
        dict_object['mode'] = 'image'
        dict_object['frame'] = imread(input_path)

        unique_frames_read = 1
        returned_state = frame_process(dict_object)

        if 'abort' not in returned_state:
            unique_frames_read = 1
            blocks_read = returned_state['blocks_read']
            data_read = returned_state['data_read']
        else:
            return {'abort': True}

    logging.info('Post-scan unpackaging starting...')
    #blob calculate
    #file assess ^

    logging.info('Frame decoding complete.')

    return {'unique_frames_read': unique_frames_read, 'blocks_read': blocks_read, 'data_read': data_read,
            'stream_sha256': stream_sha256}
