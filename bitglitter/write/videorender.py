import logging
from pathlib import Path

import ffmpeg


def render_video(stream_output_path, default_output_path, output_name, working_directory, total_frames,
                 frames_per_second, stream_sha):
    """Taking in whichever arguments, it takes all of the rendered frames, and merges them into an .mp4 ."""

    logging.info('Rendering video...')
    if stream_output_path:
        video_output_path = stream_output_path
    else:
        video_output_path = default_output_path
    if output_name:
        video_name = output_name
    else:
        video_name = stream_sha

    formatted_input_path = Path(working_directory / f'%{len(str(total_frames))}d.png')
    save_path = f"{Path(video_output_path / video_name)}.mp4"
    ffmpeg.input(formatted_input_path, framerate=frames_per_second).output(save_path).run()

    logging.info('Rendering video complete.')
    logging.info(f'Video save path: {save_path}')
