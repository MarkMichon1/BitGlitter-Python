import logging
import time

import ffmpeg

def renderVideo(streamOutputPath, dateCreated, imageOutputPath, frameNumberFormatted, framesPerSecond):
    '''Taking in whichever arguments, it takes all of the rendered frames, and merges them into an .mp4 .'''
    logging.info('Rendering video...')
    videoOutputPath = ''
    if streamOutputPath:
        videoOutputPath = streamOutputPath + '\\'
    logging.info(f'{videoOutputPath}{time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(dateCreated))}.mp4')
    (ffmpeg
     .input(f'{imageOutputPath}%{len(frameNumberFormatted)}d.png', framerate=framesPerSecond)
     .output(f'{videoOutputPath}{time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(dateCreated))}.mp4')
     .run())