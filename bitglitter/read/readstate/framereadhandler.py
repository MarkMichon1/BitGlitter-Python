import logging
from multiprocessing import cpu_count

from cv2 import imread

from bitglitter.config.configfunctions import _read_update
from bitglitter.config.palettemodels import Palette
from bitglitter.read.readstate.videoframegenerator import video_frame_generator
from bitglitter.read.readstate.frameprocess import frame_process
from bitglitter.read.readstate.multiprocess_state_generator import image_state_generator, video_state_generator


def frame_read_handler(input_path, output_directory, input_type, bad_frame_strikes, max_cpu_cores,
                       block_height_override, block_width_override, encryption_key, scrypt_n, scrypt_r, scrypt_p,
                       temp_save_directory, stop_at_metadata_load, unpackage_files, auto_delete_finished_stream,
                       save_statistics):

    frame_read_results = {}
    logging.info(f'Processing {input_path}...')

    #  Initializing variables that will be in all frame_process() calls
    initializer_palette_a = Palette.query.filter(Palette.nickname == '1').first()
    initializer_palette_b = Palette.query.filter(Palette.nickname == '11').first()
    initializer_palette_a_color_set = initializer_palette_a.convert_colors_to_tuple()
    initializer_palette_b_color_set = initializer_palette_b.convert_colors_to_tuple()
    initializer_palette_a_dict = initializer_palette_a.return_decoder()
    initializer_palette_b_dict = initializer_palette_b.return_decoder()
    # todo clean up when finalized vvv
    process_state_dict = {'output_directory': output_directory, 'block_height_override': block_height_override,
                      'block_width_override':
                   block_width_override, 'encryption_key': encryption_key, 'scrypt_n': scrypt_n, 'scrypt_r': scrypt_r,
                   'scrypt_p': scrypt_p, 'temp_save_directory': temp_save_directory, 'initializer_palette_a':
                   initializer_palette_a, 'initializer_palette_a_color_set': initializer_palette_a_color_set,
                   'initializer_palette_b_color_set': initializer_palette_b_color_set, 'initializer_palette_a_dict':
                   initializer_palette_a_dict, 'initializer_palette_b_dict': initializer_palette_b_dict,
                   'auto_delete_finished_stream': auto_delete_finished_stream, 'stop_at_metadata_load':
                              stop_at_metadata_load}

    if input_type == 'video':

        frame_generator = video_frame_generator(input_path)
        total_video_frames = next(frame_generator)
        logging.info(f'{total_video_frames} frame(s) detected in video file.')

        frame_strikes_this_session = 0
        process_state_dict['mode'] = 'video'

        # Processing frames in a single process until all metadata has been received, then switch to multicore
        for frame_data in frame_generator:
            current_frame_position = frame_data['current_frame_position']
            percentage_string = f'{round(((current_frame_position / total_video_frames) * 100), 2):.2f}'
            logging.info(f'Scanning frame {current_frame_position} of {total_video_frames}... ({percentage_string} %)')

            process_state_dict['frame'] = frame_data['frame']
            frame_results = frame_process(process_state_dict)
            stream_read = frame_results['stream_read']

            # Stats
            if save_statistics:
                _read_update(frame_results['blocks_read'], 1, frame_results['data_read'])

            # Errors
            if 'error' in frame_results:
                if 'fatal' in frame_results:  # Session-ending error, such as a metadata frame being corrupted
                    logging.warning('Critical error, cannot continue.')
                    return {'something': True} #todo
                elif 'corrupted' in frame_results:  # Corrupted frame, skipping to next one
                    if bad_frame_strikes:
                        frame_strikes_this_session += 1
                        logging.warning(f'Bad frame strike {frame_strikes_this_session}/{bad_frame_strikes}')
                        if frame_strikes_this_session >= bad_frame_strikes:
                            logging.warning('Reached frame strike limit.  Aborting...')
                            pass #todo reached strike limit

            # Metadata Return
            if 'metadata' in frame_results and stream_read.stop_at_metadata_load:
                pass

        # Adding Stream SHA-256 to dict to return
        frame_read_results['active_sessions_this_stream'] = [stream_read.stream_sha256]

        # Begin multicore frame decode
        if max_cpu_cores == 0 or max_cpu_cores >= cpu_count():
            pool_size = cpu_count()
        else:
            pool_size = max_cpu_cores

        # Priming state generator
        video_state_generator(frame_generator, stream_read)

        # return stat data
        # with Pool(processes=pool_size) as worker_pool:
        #     logging.info(f'Metadata fully decoded, now decoding on {max_cpu_cores} core(s)...')
        #     for frame_decode in worker_pool.imap(frame_process, decode_multicore_state_generator()):
        #         if frame_decode['strike']:
        #             frame_strikes_this_session += 1
        #         else:
        #             if frame_decode['is_unique_frame']:
        #                 pass
        #             blocks_read += frame_decode['blocks_read']
        #         percentage_string = 0
        #         logging.info(f'Scanning frame {current_frame_position}/{total_video_frames}...') #todo
        #         logging.info(f'Processing frame {video_frame_position} of {total_frames}...'
        #                      f'({round(((video_frame_position / total_frames) * 100), 2):.2f} %)')
        logging.info('Frame decoding complete.')

    elif input_type == 'image':

        input_list = [input_path] if isinstance(input_path, str) else input_path

        process_state_dict['mode'] = 'image'
        process_state_dict['frame'] = imread(input_list) #todo move to generator

        frames_read = 1
        returned_state = frame_process(process_state_dict)

        #mc integrate

        # Stats
        # frames_read += 1 #todo: integrate into mp return
        # blocks_read = returned_state['blocks_read']
        # data_read = returned_state['data_read']

        #Errors todo mp return
        return {'abort': True}


    if unpackage_files:
        active_reads_this_session = [] #todo query unpackage_files = True, active_session = True
        if active_reads_this_session:
            logging.info(f'{len(active_reads_this_session)} active stream(s) this session.')
            frame_read_results['unpackage_results'] = {}
            for stream_read in active_reads_this_session:
                logging.info(f'Unpackaging {stream_read.stream_name}...')
                unpackage_results = stream_read.attempt_unpackage()
                frame_read_results['unpackage_results'][stream_read.stream_sha256] = unpackage_results

    logging.info('Frame decoding complete.')

    # Returns one for video, or all for images #todo
    return {'stream_sha256': stream_sha256}
