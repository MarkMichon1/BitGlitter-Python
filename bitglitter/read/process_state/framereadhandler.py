from sqlalchemy.exc import InvalidRequestError

import logging
from multiprocessing import cpu_count, Pool
from pathlib import Path

from bitglitter.config.palettemodels import Palette
from bitglitter.config.readmodels.streamread import StreamRead
from bitglitter.read.process_state.videoframegenerator import video_frame_generator
from bitglitter.read.process_state.imageframeprocessor import ImageFrameProcessor
from bitglitter.read.process_state.multiprocess_state_generator import image_state_generator, video_state_generator
from bitglitter.read.process_state.videoframeprocessor import VideoFrameProcessor
from bitglitter.utilities.read import flush_inactive_frames


def frame_read_handler(input_path, output_directory, input_type, bad_frame_strikes, max_cpu_cores,
                       block_height_override, block_width_override, decryption_key, scrypt_n, scrypt_r, scrypt_p,
                       temp_save_directory, stop_at_metadata_load, auto_unpackage_stream, auto_delete_finished_stream,
                       save_statistics, valid_image_formats):
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
    image_strike_limit_hit = False
    image_metadata_checkpoint_data = None
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

            # Skip if all frames completed
            if video_frame_processor.skip_process:
                frame_read_results['active_sessions_this_stream'].append(video_frame_processor.stream_sha256)
                break

            # Errors
            if 'error' in video_frame_processor.frame_errors:
                # Session-ending error, such as a metadata frame being corrupted
                if 'fatal' in video_frame_processor.frame_errors:
                    logging.warning('Cannot continue.')
                    return {'error': True}
                if bad_frame_strikes:  # Corrupted frame, skipping to next one
                    frame_strikes_this_session += 1
                    logging.warning(f'Bad frame strike {frame_strikes_this_session}/{bad_frame_strikes}')
                    if frame_strikes_this_session >= bad_frame_strikes:
                        logging.warning('Reached frame strike limit.  Aborting...')
                        return {'error': True}

            if frame_data['current_frame_position'] == 1:
                stream_read = video_frame_processor.stream_read
                initial_state_dict['stream_read'] = stream_read

            # Metadata return
            if video_frame_processor.metadata and stream_read.stop_at_metadata_load:
                return {'metadata': video_frame_processor.metadata}

            # Stream palette load
            if video_frame_processor.stream_palette and video_frame_processor.stream_palette_loaded_this_frame:
                stream_palette = video_frame_processor.stream_palette
                stream_palette_dict = video_frame_processor.stream_palette_dict
                stream_palette_color_set = video_frame_processor.stream_palette_color_set
                initial_state_dict['stream_palette'] = stream_palette
                initial_state_dict['stream_palette_dict'] = stream_palette_dict
                initial_state_dict['stream_palette_color_set'] = stream_palette_color_set

            # Headers are decoded, can switch to multiprocessing
            if stream_read.palette_header_complete and stream_read.metadata_header_complete:
                frame_read_results['active_sessions_this_stream']\
                    .append(video_frame_processor.stream_read.stream_sha256)
                break

        # Begin multicore frame decode
        if not video_frame_processor.skip_process:
            with Pool(processes=cpu_pool_size) as worker_pool:
                logging.info(f'Metadata headers fully decoded, now decoding on {cpu_pool_size} CPU core(s)...')
                for multicore_read_results in worker_pool.imap(VideoFrameProcessor,
                                                           video_state_generator(frame_generator, stream_read,
                                                           save_statistics, initializer_palette_a,
                                                           initializer_palette_a_dict, initializer_palette_a_color_set,
                                                           total_video_frames, stream_palette, stream_palette_dict,
                                                           stream_palette_color_set)):

                    if 'error' in multicore_read_results.frame_errors:
                        if bad_frame_strikes:  # Corrupted frame, skipping to next one
                            frame_strikes_this_session += 1
                            logging.warning(f'Bad frame strike {frame_strikes_this_session}/{bad_frame_strikes}')
                            if frame_strikes_this_session >= bad_frame_strikes:
                                logging.warning('Reached frame strike limit.  Aborting...')
                                return {'error': True}

    elif input_type == 'image':

        # Normalizing the different forms of input path into a common list format format
        if isinstance(input_path, list):
            input_list = input_path
        elif isinstance(input_path, str):
            path = Path(input_path)
            if path.is_dir():
                input_list = []
                for file_format in valid_image_formats:
                    for whitelisted_file in path.rglob(file_format):
                        input_list.append(str(whitelisted_file))
            else:
                input_list = [input_path]

        # Begin multicore frame decode
        image_metadata_checkpoint_data = None
        image_strike_limit_hit = False
        with Pool(processes=cpu_pool_size) as worker_pool:
            logging.info(f'Decoding on {cpu_pool_size} CPU core(s)...')
            for multicore_read_results in worker_pool.imap(ImageFrameProcessor, image_state_generator(input_list,
                                                                                                  initial_state_dict)):
                if 'error' in multicore_read_results.frame_errors:
                    if bad_frame_strikes:  # Corrupted frame, skipping to next one
                        frame_strikes_this_session += 1
                        logging.warning(f'Bad frame strike {frame_strikes_this_session}/{bad_frame_strikes}'
                                        f' ({multicore_read_results.file_name})')
                        if frame_strikes_this_session >= bad_frame_strikes:
                            logging.warning('Reached frame strike limit.  Aborting...')
                            image_strike_limit_hit = True
                            break

                if multicore_read_results.stream_sha256:
                    if multicore_read_results.stream_sha256 not in frame_read_results['active_sessions_this_stream']:
                        frame_read_results['active_sessions_this_stream'].append(multicore_read_results.stream_sha256)

                if multicore_read_results.metadata and multicore_read_results.stream_read.stop_at_metadata_load:
                    image_metadata_checkpoint_data = multicore_read_results.metadata
                    break

    # Outside the scope of image multiprocessing to work properly
    if image_strike_limit_hit:
        return {'error': True}
    if image_metadata_checkpoint_data:
        return {'metadata': image_metadata_checkpoint_data}

    logging.info('Frame scanning complete.')

    #  Remove incomplete frames from db
    flush_inactive_frames()

    # Closing active sessions and unpackaging streams if its set to:
    active_reads_this_session = StreamRead.query.filter(StreamRead.active_this_session == True).all()
    unpackaging_this_session = False
    if active_reads_this_session:
        logging.info(f'{len(active_reads_this_session)} active stream(s) this session.')
        frame_read_results['unpackage_results'] = {}
        for stream_read in active_reads_this_session:
            stream_read.completed_frame_count_update()
            if stream_read.auto_unpackage_stream:
                unpackaging_this_session = True
                unpackage_results = stream_read.attempt_unpackage(temp_save_directory)
                frame_read_results['unpackage_results'][stream_read.stream_sha256] = unpackage_results
                stream_read.autodelete_attempt()
            else:
                stream_read.check_file_eligibility()
            try:
                stream_read.session_activity(False)
            except InvalidRequestError:
                pass
        if unpackaging_this_session:
            logging.info('File unpackaging complete.')

    return {'frame_read_results': frame_read_results}
