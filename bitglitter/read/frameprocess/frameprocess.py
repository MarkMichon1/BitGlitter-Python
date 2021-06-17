from bitglitter.read.frameprocess.framevalidation import frame_lock_on, minimum_block_checkpoint
from bitglitter.read.frameprocess.scanhandler import ScanHandler

def frame_process(frame, mode, frame_number, block_height_override=None, block_width_override=None, stream_sha=None,
                  stream_palette=None, block_width=None, block_height=None,
                  pixel_width=None, meta_mode=False, meta_length=None, meta_consumed=0): # meta_length
    """Processes frames to extract the data in a wide variety of ways, depending on context."""
    # var instantiation

    # Setting ScanHandler state
    if mode == 'image' or frame_number == 1:
        scan_handler = ScanHandler(frame, is_calibrator_frame=True)
    else:
        scan_handler = ScanHandler(frame, is_calibrator_frame=False)
    if block_height and block_width and pixel_width:
        scan_handler.set_scan_geometry(block_height, block_width, pixel_width)

    frame_pixel_height, frame_pixel_width, unused = frame.shape

    def first_frame_setup():
        """This is a series of tasks that must be done for the first frames of video and image frames.  The frame is
        locked onto, and the frame's initializer is validated and loaded.
        """
        checkpoint_passed = minimum_block_checkpoint(block_height_override, block_width_override,
                                                                  frame_pixel_width, frame_pixel_height)
        if not checkpoint_passed:
            return False

        block_height, block_width, pixel_width = frame_lock_on(frame, block_height_override, block_width_override,
                                                               frame_pixel_width, frame_pixel_height)
        if not pixel_width:
            return False

        scan_handler.set_scan_geometry(block_height, block_width, pixel_width)



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
        else:
            pass

        def test():
            pass


    # validate overrides- stream palette AND geometry

    # strikeout

    # accept frame

    # todo- check if initializer protocol is in supported protocols in settings manager

    return {'final_meta_frame': bool, 'total_blocks': 0, 'is_unique_frame': bool} #todo

    # ^ stream palette, block width, block height

