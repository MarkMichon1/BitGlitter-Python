import logging

from bitglitter.protocols.protocol_one.write.protocol_one_renderassets import ascii_header_process, how_many_frames
from bitglitter.protocols.protocol_one.write.protocol_one_renderloop import render_loop
from bitglitter.write.rendervideo import render_video

class EncodeFrame:
    '''This object takes what has already been processed from pre_processing, renders that data into images.'''

    def __init__(self):

        logging.debug('EncodeFrame initializing...')

        self.PROTOCOL_VERSION = 1

        self.active_path = None
        self.pass_through = None
        self.stream_output_path = None
        self.bg_version = None

        self.header_palette = None
        self.initializer_palette = None
        self.stream_palette = None

        self.initializer_palette_dict = None
        self.header_palette_dict = None
        self.stream_palette_dict = None

        self.block_height = None
        self.block_width = None
        self.pixel_width = None
        self.frames_per_second = None
        self.output_mode = None

        self.stream_sha = None

        # Stream header data to encode
        self.size_in_bytes = None
        self.total_frames = None
        self.compression_enabled = None
        self.encryption_enabled = None
        self.file_mask_enabled = None
        self.date_created = None
        self.stream_name = None
        self.stream_description = None
        self.post_encryption_hash = None

        self.total_frames = 0


    def begin_session_process(self,

                              # General- Path and Protocol
                              active_path, pass_through, stream_output_path, bg_version, output_name,

                              # Palettes
                              initializer_palette, header_palette, stream_palette,

                              # Color Dictionaries
                              initializer_palette_dict, header_palette_dict, stream_palette_dict,

                              # Geometry & General Render Configuration
                              block_height, block_width, pixel_width, frames_per_second, output_mode,

                              # Frame Header
                              stream_sha,

                              # Stream Header - Binary Preamble
                              size_in_bytes, compression_enabled, encryption_enabled, file_mask_enabled,
                              date_created,

                              # Stream Header - ASCII Encoded
                              stream_name, stream_description, pre_encryption_hash

                              ):

        #Load arguments
        self.active_path = active_path
        self.pass_through = pass_through
        self.stream_output_path = stream_output_path
        self.bg_version = bg_version
        self.output_name = output_name

        self.header_palette = header_palette
        self.initializer_palette = initializer_palette
        self.stream_palette = stream_palette

        self.initializer_palette_dict = initializer_palette_dict
        self.header_palette_dict = header_palette_dict
        self.stream_palette_dict = stream_palette_dict

        self.block_height = block_height
        self.block_width = block_width
        self.pixel_width = pixel_width
        self.frames_per_second = frames_per_second
        self.output_mode = output_mode

        self.stream_sha = stream_sha

        self.size_in_bytes = size_in_bytes
        self.compression_enabled = compression_enabled
        self.encryption_enabled = encryption_enabled
        self.file_mask_enabled = file_mask_enabled
        self.date_created = date_created

        self.stream_name = stream_name
        self.stream_description = stream_description
        self.post_encryption_hash = pre_encryption_hash

        self.ascii_compressed = ascii_header_process(self.file_mask_enabled, self.active_path,
                                                     self.stream_palette, self.bg_version, self.stream_name,
                                                     self.stream_description, self.post_encryption_hash,
                                                     self.encryption_enabled)

        self.total_frames = how_many_frames(self.block_height, self.block_width, len(self.ascii_compressed),
                                            self.size_in_bytes, self.stream_palette, self.header_palette,
                                            self.output_mode)

        self.remainder_blocks, self.image_output_path, self.frame_number_formatted = render_loop(self.block_height,
                                                    self.block_width, self.pixel_width, self.PROTOCOL_VERSION,
                                                    self.initializer_palette, self.header_palette, self.stream_palette,
                                                    self.output_mode, self.stream_output_path, self.output_name,
                                                    self.active_path, self.pass_through, self.size_in_bytes,
                                                    self.total_frames, self.compression_enabled,
                                                    self.encryption_enabled, self.file_mask_enabled, self.date_created,
                                                    self.ascii_compressed, self.stream_sha,
                                                    self.initializer_palette_dict, self.header_palette_dict,
                                                    self.stream_palette_dict)

        if output_mode == 'video':
            render_video(self.stream_output_path, self.output_name, self.date_created, self.image_output_path,
                         self.frame_number_formatted, self.frames_per_second)