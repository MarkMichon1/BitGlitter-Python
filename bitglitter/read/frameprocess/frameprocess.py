from bitglitter.read.framescan.scanhandler import ScanHandler

def frame_process(frame, mode, frame_number, stream_sha=None, stream_palette=None, block_width=None, block_height=None,
                  pixel_width=None, meta_mode=False, meta_length=None, meta_consumed=0): # meta_length
    """Processes frames to extract the data in a wide variety of ways, depending on context."""
    # var instantiation

    scan_handler = ScanHandler(frame)
    frame_height, frame_width, unused = frame.shape

    if mode == 'image':
        pass #todo last
        """
        first frame setup
        image frame setup
        frame validation
        payload process
        """
    elif mode == 'video':
        if frame_number == 1:
            pass


    # validate overrides- stream palette AND geometry

    # strikeout

    # accept frame

    # todo- check if initializer protocol is in supported protocols in settings manager

    return {'final_meta_frame': bool, 'total_blocks': 0, 'is_unique_frame': bool} #todo

    # ^ stream palette, block width, block height

