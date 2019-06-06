import logging

import cv2


class VideoFramePuller:
    '''This object is loads the BitGlitter-encoded video, and returns one frame at a time to be decoded.'''

    def __init__(self, fileToInput):

        self.activeVideo = cv2.VideoCapture(fileToInput)
        logging.debug('Video successfully loaded into VideoFramePuller.')
        self.totalFrames = int(self.activeVideo.get(cv2.CAP_PROP_FRAME_COUNT))
        logging.info(f'{self.totalFrames} frame(s) detected in video.')
        self.currentFrame = 1


    def nextFrame(self):
        '''This method will automatically read the next frame from the video, and return the file path to that image.'''

        self.currentFrame += 1
        return self.activeVideo.read()[1]