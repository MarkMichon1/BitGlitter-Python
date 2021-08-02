def multiprocess_state_generator(video_frame_generator, stream_sha256):
    """Returns a packaged dict object for use in frame_process"""

    for frame in video_frame_generator:
        yield {'mode': 'video', 'main_sequence': True}