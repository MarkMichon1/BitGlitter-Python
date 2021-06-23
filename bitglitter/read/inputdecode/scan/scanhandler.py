from bitglitter.config.del_pending_palettes import palette_manager
from bitglitter.palettes.utilities import ColorsToBits


class ScanHandler:
    def __init__(self, frame, is_calibrator_frame):
        self.frame = frame
        self.is_calibrator_frame = is_calibrator_frame
        self.block_height = None
        self.block_width = None
        self.pixel_width = None

        self.initializer_palette = palette_manager.return_selected_palette('1')
        self.initializer_palette_dict = ColorsToBits(self.initializer_palette)
        stream_palette = None
        stream_palette_palette_dict = None

        self.non_calibrator_blocks = 0

    def set_scan_geometry(self, block_height, block_width, pixel_width):
        self.block_height = block_height
        self.block_width = block_width
        self.pixel_width = pixel_width

        self.non_calibrator_blocks = (self.block_height - int(self.is_calibrator_frame)) * \
                                         (self.block_width - int(self.is_calibrator_frame))