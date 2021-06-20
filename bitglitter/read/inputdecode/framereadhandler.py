import logging
from multiprocessing import cpu_count, Pool

from cv2 import imread

from bitglitter.read.inputdecode.decodestatemanagement import decode_video_multicore_state_generator, initial_video_stream_lockon
from bitglitter.read.inputdecode.frameprocess import frame_process


class FrameReadHandler:  # look at render handler
    def __init__(self, input_path, output_path, input_type, bad_frame_strikes, max_cpu_cores, block_height_override,
                 block_width_override, stream_palette_id_override, encryption_key, scrypt_n, scrypt_r, scrypt_p,
                 save_statistics, partial_save_path):

        self.unique_frames_read = 0
        self.blocks_read = 0
        self.data_read = 0

        logging.info(f'Processing {input_path}')

        if input_type == 'video':
            # Single process metadata decode until into pure payload frames
            state = initial_video_stream_lockon(input_path, output_path, input_type, bad_frame_strikes, block_height_override,
                                                block_width_override, stream_palette_id_override, encryption_key, scrypt_n,
                                                scrypt_r, scrypt_p, save_statistics, partial_save_path)
            # todo include stats
            video_frame_position = 1
            strikes = bad_frame_strikes
            is_header_termination_frame = False
            #todo load variables
            # while not is_header_termination_frame:
            #     frame_process()

            # breaking out of video after reaching {bad_frame_strikes} bad frame strikes, or comparable message for img

            # Begin multicore frame decode

            #


            if max_cpu_cores == 0 or max_cpu_cores >= cpu_count():
                pool_size = cpu_count()
            else:
                pool_size = max_cpu_cores

            # with Pool(processes=pool_size) as worker_pool:
            #     logging.info('Metadata decoded, switching to multicore..')
            #     for frame_decode in worker_pool.imap(frame_process, decode_multicore_state_generator()):
            #         if frame_decode['strike']:
            #             strikes += 1
            #         else:
            #             if frame_decode['is_unique_frame']:
            #                 self.
            #             self.blocks_read += frame_decode['blocks_read']
            #         logging.info(f'Processing frame {video_frame_position} of {total_frames}...'
            #                      f'({round(((video_frame_position / total_frames) * 100), 2):.2f} %)')

        elif input_type == 'image':
            returned_state = frame_process(imread(input_path))

        logging.info('Frame decoding complete.')

    def review_data(self):
        logging.info('Reviewing decoded data...')

        # readmanager call
        # read_manager.review_active_state
