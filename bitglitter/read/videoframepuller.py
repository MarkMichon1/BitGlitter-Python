import logging

import cv2


class VideoFramePuller:
    '''This object is loads the BitGlitter-encoded video, and returns one frame at a time to be decoded.'''

    def __init__(self, file_to_input):

        self.active_video = cv2.VideoCapture(file_to_input)
        logging.debug('Video successfully loaded into VideoFramePuller.')
        self.total_frames = int(self.active_video.get(cv2.CAP_PROP_FRAME_COUNT))
        logging.info(f'{self.total_frames} frame(s) detected in video.')
        self.current_frame = 1


    def next_frame(self):
        '''This method will automatically read the next frame from the video, and return the file path to that image.'''

        self.current_frame += 1
        return self.active_video.read()[1]