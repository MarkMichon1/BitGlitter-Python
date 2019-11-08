import logging
import shutil

from bitglitter.config.config import config
from bitglitter.palettes.paletteutilities import palette_grabber, ValuesToColor


class RenderHandler:
    '''This is where the rendering process is set up, and fed into the appropriate protocol objects and objects.  While
    this may seem like an unnecessary module currently (as of v1.0), I think it's purpose will become more apparent as
    we need a uniform place to handle various future protocols.
    '''

    def __init__(self,

                 # Initializer
                 protocol, block_height, block_width, header_palette_id,

                 # Frame Header
                 stream_sha,

                 # Stream Header - Binary Preamble
                 size_in_bytes, compression_enabled, encryption_enabled, file_mask_enabled, date_created,
                 stream_palette_id,

                 # Stream Header - ASCII Encoded
                 bg_version, stream_name, stream_description, post_encryption_hash,

                 # Render argument
                 pixel_width, output_mode, stream_output_path, frames_per_second,

                 # Misc
                 active_folder, pass_through, output_name
                 ):

        logging.debug('RenderHandler initializing...')

        self.protocol = protocol
        self.block_height = block_height
        self.block_width = block_width

        self.stream_sha = stream_sha

        self.size_in_bytes = size_in_bytes
        self.compression_enabled = compression_enabled
        self.encryption_enabled = encryption_enabled
        self.file_mask_enabled = file_mask_enabled
        self.date_created = date_created

        self.bg_version = bg_version
        self.stream_name = stream_name
        self.stream_description = stream_description
        self.output_name = output_name
        self.post_encryption_hash = post_encryption_hash

        self.pixel_width = pixel_width
        self.output_mode = output_mode
        self.stream_output_path = stream_output_path
        self.frames_per_second = frames_per_second

        self.active_path = active_folder
        self.pass_through = pass_through

        self.header_palette = palette_grabber(header_palette_id)
        self.stream_palette = palette_grabber(stream_palette_id)
        self.initializer_palette = palette_grabber('1')

        self.header_palette_dict = ValuesToColor(self.header_palette, 'header_palette')
        self.stream_palette_dict = ValuesToColor(self.stream_palette, 'stream_palette')
        self.initializer_palette_dict = ValuesToColor(self.initializer_palette, 'initializer_palette')

        self.protocol.begin_session_process(self.active_path, self.pass_through, self.stream_output_path,
                                            self.bg_version, self.output_name, self.initializer_palette,
                                            self.header_palette, self.stream_palette, self.initializer_palette_dict,
                                            self.header_palette_dict, self.stream_palette_dict, self.block_height,
                                            self.block_width, self.pixel_width, self.frames_per_second,
                                            self.output_mode, self.stream_sha, self.size_in_bytes,
                                            self.compression_enabled, self.encryption_enabled, self.file_mask_enabled,
                                            self.date_created, self.stream_name, self.stream_description,
                                            self.post_encryption_hash)

        config.stats_handler.write_update(((self.protocol.total_frames - 1) * (self.block_height * self.block_width) +
                                         self.protocol.remainder_blocks), self.protocol.total_frames,
                                          self.size_in_bytes)

        self.cleanup()


    def cleanup(self):
        '''Removes temporary folder.'''

        logging.debug("Deleting temporary folder....")
        shutil.rmtree(self.active_path)

        config.save_session()
        logging.info('Write process complete!')