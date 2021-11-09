import logging
from multiprocessing import cpu_count, Pool

from bitglitter.config.palettemodels import Palette
from bitglitter.config.readmodels.streamread import StreamRead
from bitglitter.read.readstate.videoframegenerator import video_frame_generator
from bitglitter.read.readstate.imageframeprocessor import ImageFrameProcessor
from bitglitter.read.readstate.multiprocess_state_generator import image_state_generator, video_state_generator
from bitglitter.read.readstate.videoframeprocessor import VideoFrameProcessor


def frame_read_handler(input_path, output_directory, input_type, bad_frame_strikes, max_cpu_cores,
                       block_height_override, block_width_override, decryption_key, scrypt_n, scrypt_r, scrypt_p,
                       temp_save_directory, stop_at_metadata_load, auto_unpackage_stream, auto_delete_finished_stream,
                       save_statistics):
    logging.info(f'Processing {input_path}...')

    #  Initializing variables that will be in all frame_process() calls
    initializer_palette_a = Palette.query.filter(Palette.nickname == '1').first()
    initializer_palette_b = Palette.query.filter(Palette.nickname == '11').first()
    initializer_palette_a_color_set = initializer_palette_a.convert_colors_to_tuple()
    initializer_palette_b_color_set = initializer_palette_b.convert_colors_to_tuple()
    initializer_palette_a_dict = initializer_palette_a.return_decoder()
    initializer_palette_b_dict = initializer_palette_b.return_decoder()

    stream_palette = None
    stream_palette_dict = None
    stream_palette_color_set = None

    initial_state_dict = {'output_directory': output_directory, 'block_height_override': block_height_override,
                          'block_width_override': block_width_override, 'decryption_key': decryption_key, 'scrypt_n':
                          scrypt_n, 'scrypt_r': scrypt_r, 'scrypt_p': scrypt_p, 'temp_save_directory':
                          temp_save_directory, 'initializer_palette_a': initializer_palette_a,
                          'initializer_palette_a_color_set': initializer_palette_a_color_set,
                          'initializer_palette_b_color_set': initializer_palette_b_color_set,
                          'initializer_palette_a_dict': initializer_palette_a_dict, 'initializer_palette_b_dict':
                          initializer_palette_b_dict, 'auto_delete_finished_stream': auto_delete_finished_stream,
                          'stop_at_metadata_load': stop_at_metadata_load, 'save_statistics': save_statistics,
                          'auto_unpackage_stream': auto_unpackage_stream, 'sequential': True}

    # Multicore setup
    if max_cpu_cores == 0 or max_cpu_cores >= cpu_count():
        cpu_pool_size = cpu_count()
    else:
        cpu_pool_size = max_cpu_cores

    frame_strikes_this_session = 0
    frame_read_results = {'active_sessions_this_stream': []}

    if input_type == 'video':

        frame_generator = video_frame_generator(input_path)
        total_video_frames = next(frame_generator)
        initial_state_dict['total_frames'] = total_video_frames
        logging.info(f'{total_video_frames} frame(s) detected in video file.')
        initial_state_dict['mode'] = 'video'

        # Processing frames in a single process until all metadata has been received, then switch to multicore
        logging.info('Starting single core sequential decoding until metadata captured...')
        for frame_data in frame_generator:
            initial_state_dict['frame'] = frame_data['frame']
            initial_state_dict['current_frame_position'] = frame_data['current_frame_position']
            video_frame_processor = VideoFrameProcessor(initial_state_dict)

            # Errors
            if 'error' in video_frame_processor.frame_errors:
                if 'fatal' in video_frame_processor.frame_errors:  # Session-ending error, such as a metadata frame being corrupted
                    logging.warning('Cannot continue.')
                    return {'error': True}
                if bad_frame_strikes:  # Corrupted frame, skipping to next one
                    frame_strikes_this_session += 1
                    logging.warning(f'Bad frame strike {frame_strikes_this_session}/{bad_frame_strikes}')
                    if frame_strikes_this_session >= bad_frame_strikes:
                        logging.warning('Reached frame strike limit.  Aborting...')
                        return {'error': True}

            stream_read = video_frame_processor.stream_read

            # Metadata Return
            if video_frame_processor.metadata and stream_read.stop_at_metadata_load:
                return {'metadata': video_frame_processor.metadata}

            # Headers are decoded, can switch to multiprocessing
            if stream_read.palette_header_complete and stream_read.metadata_header_complete:
                break

            if video_frame_processor.stream_palette and video_frame_processor.stream_palette_loaded_this_frame:
                stream_palette = video_frame_processor.stream_palette
                stream_palette_dict = video_frame_processor.stream_palette_dict
                stream_palette_color_set = video_frame_processor.stream_palette_color_set
                initial_state_dict['stream_palette'] = stream_palette
                initial_state_dict['stream_palette_dict'] = stream_palette_dict
                initial_state_dict['stream_palette_color_set'] = stream_palette_color_set

        # Adding Stream SHA-256 to dict to return #todo...
        frame_read_results['active_sessions_this_stream'] = [stream_read.stream_sha256]

        # Begin multicore frame decode
        with Pool(processes=cpu_pool_size) as worker_pool:
            logging.info(f'Metadata headers fully decoded, now decoding on {cpu_pool_size} CPU core(s)...')
            for frame_read_results in worker_pool.imap(video_frame_process,
                                                       video_state_generator(frame_generator, stream_read,
                                                       save_statistics, initializer_palette_a,
                                                       initializer_palette_a_dict, initializer_palette_a_color_set,
                                                       total_video_frames, stream_palette, stream_palette_dict,
                                                       stream_palette_color_set)):
                if 'error' in frame_read_results:
                    if bad_frame_strikes:  # Corrupted frame, skipping to next one
                        frame_strikes_this_session += 1
                        logging.warning(f'Bad frame strike {frame_strikes_this_session}/{bad_frame_strikes}')
                        if frame_strikes_this_session >= bad_frame_strikes:
                            logging.warning('Reached frame strike limit.  Aborting...')
                            return {'error': True}

    elif input_type == 'image':

        input_list = [input_path] if isinstance(input_path, str) else input_path

        # Begin multicore frame decode
        with Pool(processes=cpu_pool_size) as worker_pool:
            logging.info(f'Decoding on {cpu_pool_size} CPU core(s)...')
            for frame_read_results in worker_pool.imap(image_frame_process, image_state_generator(input_list,
                                                                                                  initial_state_dict)):
                if 'error' in frame_read_results:
                    if bad_frame_strikes:  # Corrupted frame, skipping to next one
                        frame_strikes_this_session += 1
                        logging.warning(f'Bad frame strike {frame_strikes_this_session}/{bad_frame_strikes}')
                        if frame_strikes_this_session >= bad_frame_strikes:
                            logging.warning('Reached frame strike limit.  Aborting...')
                            return {'error': True}

    logging.info('Frame scanning complete.')

    # Closing active sessions and unpackaging streams if its set to:
    # active_reads_this_session = []  # todo active_session = True
    active_reads_this_session = StreamRead.query.filter(StreamRead.active_this_session == True)
    unpackaging_this_session = False
    if active_reads_this_session:
        logging.info(f'{len(active_reads_this_session)} active stream(s) this session.')
        frame_read_results['unpackage_results'] = {}
        for stream_read in active_reads_this_session:
            stream_read.completed_frame_count_update()
            if stream_read.auto_unpackage_stream:
                unpackaging_this_session = True
                logging.info(f'Unpackaging {stream_read.stream_name}...')
                unpackage_results = stream_read.attempt_unpackage()
                frame_read_results['unpackage_results'][stream_read.stream_sha256] = unpackage_results
                stream_read.autodelete_attempt()
            stream_read.session_activity(False)
        if unpackaging_this_session:
            logging.info('File unpackaging complete.')

    # Returns one for video, or all for images
    return {'frame_read_results': frame_read_results}
