import cv2

from bitglitter.config.palettemodels import Palette


def video_state_generator(video_frame_generator, stream_read, save_statistics, initializer_palette,
                          initializer_palette_dict, initializer_color_set, total_video_frames, stream_palette=None,
                          stream_palette_dict=None, stream_palette_color_set=None):
    """Returns a dict object for frame_process to use when switching to multiprocessing"""

    if not stream_palette:
        stream_palette = Palette.query.filter(Palette.palette_id == stream_read.stream_palette_id).first()
        stream_palette_dict = stream_palette.return_decoder()
        stream_palette_color_set = stream_palette.convert_colors_to_tuple()

    for returned_state in video_frame_generator:
        yield {'mode': 'video', 'stream_read': stream_read, 'frame': returned_state['frame'], 'save_statistics':
                save_statistics, 'initializer_palette_a': initializer_palette, 'initializer_palette_a_dict':
                initializer_palette_dict, 'initializer_palette_a_color_set': initializer_color_set,
                'current_frame_position': returned_state['current_frame_position'], 'total_frames': total_video_frames,
                'stream_palette': stream_palette, 'stream_palette_dict': stream_palette_dict,
                'stream_palette_color_set': stream_palette_color_set, 'sequential': False}


def image_state_generator(input_list, initial_state_dict):
    """Used for all image decoding regardless of placement, since they need to be approached with an empty slate in
    terms of state.
    """

    total_frames = len(input_list)
    count = 1
    for image_path in input_list:
        frame = cv2.imread(image_path)
        yield {'mode': 'image', 'frame': frame, 'current_frame_position': count, 'total_frames': total_frames,
               'dict_obj': initial_state_dict}
        count += 1
