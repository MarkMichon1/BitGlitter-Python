import cv2
import logging

from bitglitter.read.framescan.frameprocess import frame_process


def initial_video_stream_lockon(video_input_path, output_path, bad_frame_strikes, block_height_override,
                                block_width_override, stream_palette_id_override, encryption_key, scrypt_n, scrypt_r,
                                scrypt_p, save_statistics, partial_save_path):
    """Used to """

    active_video = cv2.VideoCapture(video_input_path)
    total_frames = int(active_video.get(cv2.CAP_PROP_FRAME_COUNT))
    logging.info(f'{total_frames} frame(s) detected in video file.')


    final_meta_frame = False
    frame_strikes = 0

    while not final_meta_frame:
        returned_state = frame_process()
        if returned_state['strike']:
            frame_strikes += 1
            if frame_strikes == bad_frame_strikes:
                pass # do something to break out of loop

        else:
            final_meta_frame = returned_state['final_meta_frame']

    strikes = 0

    return {'strikeout': bool, 'next_frame': None}


def decode_video_multicore_state_generator(video_input_path):
    active_video = cv2.VideoCapture(video_input_path)
    total_frames = int(active_video.get(cv2.CAP_PROP_FRAME_COUNT))
    current_frame = 1

    for frame in range(total_frames):
        yield {'frame': active_video.read()[1], 'current_frame_position': current_frame}

# For reference until confirmed working ^

# class VideoFramePuller:
#     """This object is loads the BitGlitter-encoded video, and returns one frame at a time to be decoded."""
#
#     def __init__(self, file_to_input):
#         self.active_video = cv2.VideoCapture(file_to_input)
#         logging.debug('Video successfully loaded into VideoFramePuller.')
#         self.total_frames = int(self.active_video.get(cv2.CAP_PROP_FRAME_COUNT))
#         logging.info(f'{self.total_frames} frame(s) detected in video.')
#         self.current_frame = 1
#
#     def next_frame(self):
#         """This method will automatically read the next frame from the video, and return the file path to that image."""
#
#         self.current_frame += 1
#         return self.active_video.read()[1]
