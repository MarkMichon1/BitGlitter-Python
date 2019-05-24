import logging
import os

import cv2


class VideoFramePuller:
    '''This object is loads the BitGlitter-encoded video, and returns one frame at a time to be decoded.'''

    def __init__(self, fileToInput, activePath):

        self.activePath = activePath

        self.activeVideo = cv2.VideoCapture(fileToInput)
        logging.debug('Video successfully loaded into VideoFramePuller.')

        self.currentFrame = 1
        self.totalFrames = int(self.activeVideo.get(cv2.CAP_PROP_FRAME_COUNT))
        logging.info(f'{self.totalFrames} frame(s) detected in video.')

    def nextFrame(self):
        '''This method will automatically read the next frame from the video, and return the file path to that image.'''

        self.image = self.activeVideo.read()
        self.activeImagePath = f"{self.activePath}\\frame{self.currentFrame}.png"
        cv2.imwrite(self.activeImagePath, self.image[1])
        return self.activeImagePath


    def removePreviousFrame(self):
        '''After the frame is ran through the decoder, fileslicer will run this method to delete the frame.'''

        os.remove(self.activeImagePath)
        self.currentFrame += 1