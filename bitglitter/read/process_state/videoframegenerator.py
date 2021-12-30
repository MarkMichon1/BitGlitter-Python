import cv2


def video_frame_generator(video_input_path):
    """Opens the video file and yields one frame at a time for decoding"""

    active_video = cv2.VideoCapture(video_input_path)
    total_video_frames = int(active_video.get(cv2.CAP_PROP_FRAME_COUNT))
    current_frame_position = 1

    yield total_video_frames

    for frame in range(total_video_frames):
        yield {'frame': active_video.read()[1], 'current_frame_position': current_frame_position}
        current_frame_position += 1
