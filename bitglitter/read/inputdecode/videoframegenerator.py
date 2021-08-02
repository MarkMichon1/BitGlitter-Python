import cv2
import logging


def video_frame_generator(video_input_path):
    """Opens the video file and yields one frame a"""

    active_video = cv2.VideoCapture(video_input_path)
    total_video_frames = int(active_video.get(cv2.CAP_PROP_FRAME_COUNT))
    logging.info(f'{total_video_frames} frame(s) detected in video file.')
    current_frame_position = 1

    for frame in range(total_video_frames):
        yield {'frame': active_video.read()[1], 'current_frame_position': current_frame_position, 'total_video_frames':
               total_video_frames}
        current_frame_position += 1
