import logging
import os

from cv2 import imread

from bitglitter.config.constants import VALID_VIDEO_FORMATS
from bitglitter.read.decoder import Decoder
from bitglitter.read.videoframepuller import VideoFramePuller


def file_slicer(file_to_input, active_path, output_path, block_height_override, block_width_override,
                encryption_key, scrypt_n, scrypt_r, scrypt_p, config_object, bad_frame_strikes, assemble_hold):
    '''This function is responsible for handling the 'physical' frames of the stream, and feeding them into the Decoder
    object.  It also checks to see if various checkpoints are passed, and will abort out of read if critical errors in
    the stream are found.
    '''

    # Sets up workspace
    read_root = os.path.join(os.getcwd(), active_path)
    working_folder = read_root + '\\Working Folder'
    if not os.path.isdir(read_root):
        os.makedirs(read_root)
    config_object.assembler.workingFolder = read_root

    # Determines if the multimedia file is an image or a video.
    is_video = False
    if os.path.splitext(file_to_input)[1] in VALID_VIDEO_FORMATS:
        is_video = True

    decoder = Decoder(is_video, config_object, scrypt_n, scrypt_r, scrypt_p, block_height_override,
                      block_width_override, output_path, encryption_key, assemble_hold)

    if is_video:

        # If there is a serious frame failure, this will increase by one.  If the read is successful, it resets back to
        # zero.  More than five in a row will abort the entire read.  This is to protect against the reader spending a
        # lot of time attempting to read long videos with one failure after the next.
        bad_frames_this_session = 0

        video_frame_puller = VideoFramePuller(file_to_input)

        for frame in range(video_frame_puller.total_frames):

            if decoder.fatal_checkpoint == False:
                break

            if bad_frames_this_session < bad_frame_strikes or bad_frame_strikes == 0:
                logging.info(f'Processing frame {video_frame_puller.current_frame} of '
                             f'{video_frame_puller.total_frames}...')
                active_frame = video_frame_puller.next_frame()

                if decoder.decode_video_frame(active_frame) == False:
                    if decoder.duplicate_frame_read == False:
                        bad_frames_this_session += 1

                        if bad_frame_strikes > 0:
                            logging.warning(f'Bad frame strike {bad_frames_this_session} / {bad_frame_strikes}')

                        else:
                            logging.warning(f'Bad frame strike # {bad_frames_this_session}')

                config_object.save_session()

            else:
                logging.info(f'Breaking out of video after reaching {bad_frame_strikes} bad frame strikes...')
                break

        return True

    else:
        logging.info("Processing image...")
        checkpointPassed = decoder.decode_image(imread(file_to_input))

        if checkpointPassed == False:
            logging.debug('Breaking out of file_slicer(), checkpoint_passed == False')
            return False

        config_object.save_session()
        logging.info("Image successfully processed.")
        return True