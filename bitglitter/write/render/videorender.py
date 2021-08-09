import cv2

import logging
from pathlib import Path


def render_video(stream_output_path, default_output_path, stream_name_file_output, working_directory, total_frames,
                 frames_per_second, stream_sha256, block_width, block_height, pixel_width, stream_name):
    """Taking in whichever arguments, it takes all of the rendered frames, and merges them into an .mp4 ."""

    logging.info('Rendering video...')
    if stream_output_path:
        video_output_path = Path(stream_output_path)
    else:
        video_output_path = Path(default_output_path)
    if stream_name_file_output:
        video_name = stream_name
    else:
        video_name = stream_sha256

    frame_size = (block_width * pixel_width, block_height * pixel_width)
    save_path = f"{Path(video_output_path / video_name)}.mp4"
    output = cv2.VideoWriter(str(save_path), cv2.VideoWriter.fourcc(*'mp4v'), frames_per_second, frame_size)

    for frame in range(total_frames):
        logging.info(f'Rendering video frame {frame + 1} of {total_frames}... '
                     f'({round((((frame + 1) / total_frames) * 100), 2):.2f} %)')
        image = cv2.imread(str(Path(working_directory / f'{frame + 1}.png')))
        output.write(image)

    output.release()
    logging.info('Rendering video complete.')
    logging.info(f'Video save path: {save_path}')
