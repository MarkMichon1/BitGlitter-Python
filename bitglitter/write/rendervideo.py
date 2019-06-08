import logging
import time

import ffmpeg

def render_video(stream_output_path, date_created, image_output_path, frame_number_formatted, frames_per_second):
    '''Taking in whichever arguments, it takes all of the rendered frames, and merges them into an .mp4 .'''
    logging.info('Rendering video...')
    video_output_path = ''
    if stream_output_path:
        video_output_path = stream_output_path + '\\'
    logging.info(f'{video_output_path}{time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(date_created))}.mp4')
    (ffmpeg
     .input(f'{image_output_path}%{len(frame_number_formatted)}d.png', framerate=frames_per_second)
     .output(f'{video_output_path}{time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(date_created))}.mp4')
     .run())