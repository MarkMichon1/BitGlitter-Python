def video_state_generator(video_frame_generator, stream_read):
    """Returns a dict object for frame_process to use when switching to multiprocessing"""

    for frame in video_frame_generator:
        yield {'mode': 'video', 'stream_read': stream_read}


def image_state_generator():
    for image in temp:
        pass
