import logging
import os

from cv2 import imread

from bitglitter.config.constants import VALID_VIDEO_FORMATS
from bitglitter.read.decoder import Decoder
from bitglitter.read.videoframepuller import VideoFramePuller


def fileSlicer(fileToInput, activePath, outputPath, blockHeightOverride, blockWidthOverride,
               encryptionKey, scryptN, scryptR, scryptP, configObject, badFrameStrikes, assembleHold):
    '''This function is responsible for handling the 'physical' frames of the stream, and feeding them into the Decoder
    object.  It also checks to see if various checkpoints are passed, and will abort out of read if critical errors in
    the stream are found.
    '''

    # Sets up workspace
    readRoot = os.path.join(os.getcwd(), activePath)
    workingFolder = readRoot + '\\Working Folder'
    if not os.path.isdir(readRoot):
        os.makedirs(readRoot)
    configObject.assembler.workingFolder = readRoot

    # Determines if the multimedia file is an image or a video.
    isVideo = False
    if os.path.splitext(fileToInput)[1] in VALID_VIDEO_FORMATS:
        isVideo = True

    decoder = Decoder(isVideo, configObject, scryptN, scryptR, scryptP, blockHeightOverride, blockWidthOverride,
                      outputPath, encryptionKey, assembleHold)

    if isVideo:

        # If there is a serious frame failure, this will increase by one.  If the read is successful, it resets back to
        # zero.  More than five in a row will abort the entire read.  This is to protect against the reader spending a
        # lot of time attempting to read long videos with one failure after the next.
        badFramesThisSession = 0

        videoFramePuller = VideoFramePuller(fileToInput)

        for frame in range(videoFramePuller.totalFrames):

            if decoder.fatalCheckpoint == False:
                break

            if badFramesThisSession < badFrameStrikes or badFrameStrikes == 0:
                logging.info(f'Processing frame {videoFramePuller.currentFrame} of {videoFramePuller.totalFrames}...')
                activeFrame = videoFramePuller.nextFrame()

                if decoder.decodeVideoFrame(activeFrame) == False:
                    if decoder.duplicateFrameRead == False:
                        badFramesThisSession += 1

                        if badFrameStrikes > 0:
                            logging.warning(f'Bad frame strike {badFramesThisSession} / {badFrameStrikes}')

                        else:
                            logging.warning(f'Bad frame strike # {badFramesThisSession}')

                configObject.saveSession()

            else:
                logging.info(f'Breaking out of video after reaching {badFrameStrikes} bad frame strikes...')
                break

        return True

    else:
        logging.info("Processing image...")
        checkpointPassed = decoder.decodeImage(imread(fileToInput))

        if checkpointPassed == False:
            logging.debug('Breaking out of fileSlicer(), checkpointPassed == False')
            return False

        configObject.saveSession()
        logging.info("Image successfully processed.")
        return True