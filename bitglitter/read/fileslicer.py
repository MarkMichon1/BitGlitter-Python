import logging
import os
import shutil

from bitglitter.config.config import config
from bitglitter.config.constants import VALID_VIDEO_FORMATS
from bitglitter.read.decoder import Decoder
from bitglitter.read.videoframepuller import VideoFramePuller

def fileSlicer(fileToInput, activePath, outputPath, blockHeightOverride, blockWidthOverride,
               encryptionKey, scryptN, scryptR, scryptP, configObject, badFrameStrikes):

    # Sets up workspace
    readRoot = os.path.join(os.getcwd(), activePath)
    workingFolder = readRoot + '\\Working Folder'
    if os.path.isdir(workingFolder):
        shutil.rmtree(workingFolder) #todo this may all be unneccessary
    os.makedirs(workingFolder)
    configObject.assembler.workingFolder = readRoot

    # Determines if the multimedia file is an image or a video.
    isVideo = False
    if os.path.splitext(fileToInput)[1] in VALID_VIDEO_FORMATS:
        isVideo = True

    # Begins processing the frame(s).
    frameNumber = 1

    # If there is a serious frame failure, criticalStrikes will increase by one.  If the read is successful, it resets
    # back to zero.  More than five in a row will abort the entire read.  This is to protect against the reader
    # spending a lot of time attempting to read long videos with one failure after the next.
    StrikesInRow = 0 # todo


    decoder = Decoder(isVideo, configObject, scryptN, scryptR, scryptP, blockHeightOverride, blockWidthOverride,
                      outputPath, encryptionKey)

    if isVideo:
        # If there is a serious frame failure, criticalStrikes will increase by one.  If the read is successful, it
        # resets back to zero.  More than five in a row will abort the entire read.  This is to protect against the
        # reader spending a lot of time attempting to read long videos with one failure after the next.
        StrikesInRow = 0

        videoFramePuller = VideoFramePuller(fileToInput, workingFolder)

        for frame in range(videoFramePuller.totalFrames):
            logging.info(f'Processing frame {videoFramePuller.currentFrame} of {videoFramePuller.totalFrames}...')
            activeFrame = videoFramePuller.nextFrame()
            decoder.decodeVideoFrame(activeFrame)
            videoFramePuller.removePreviousFrame()

    #todo have var for next frame --- still needed?  I don't think
    else:
        logging.info("Processing image...")
        checkpointPassed = decoder.decodeImage(fileToInput)

        if checkpointPassed == False:
            logging.debug('Breaking out of fileSlicer(), checkpointPassed == False')
            return False

    config.saveSession()