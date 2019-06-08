import logging
import math

from bitstring import BitStream

from bitglitter.read.coloranalysis import color_snap
from bitglitter.read.decoderassets import scan_block
from bitglitter.config.config import config


class FrameHandler:
    '''FrameHandler object is what traverses the actual frame, and returns bit data.  It's designed as an easy to use
    API, hiding much of the moving parts behind the scenes of a frame scan.
    '''

    def __init__(self, initializer_palette, initializer_palette_dict):

        # Setup
        self.image = None
        self.block_height = None
        self.block_width = None
        self.pixel_width = None

        # Palette Variables
        self.initializer_palette = initializer_palette
        self.initializer_palette_dict = initializer_palette_dict
        self.header_palette = None
        self.header_palette_dict = None
        self.stream_palette = None
        self.stream_palette_dict = None
        self.primary_palette = None
        self.primary_palette_dict = None

        # Dictionaries
        self.palette_dict = {'initializer_palette': self.initializer_palette,
                            'primary_palette': self.primary_palette,
                            'header_palette': self.header_palette,
                            'stream_palette': self.stream_palette}
        self.palette_conversion_dict = {'initializer_palette' : self.initializer_palette_dict,
                                      'primary_palette': self.primary_palette_dict,
                                      'header_palette' : self.header_palette_dict,
                                      'stream_palette' : self.stream_palette_dict}

        # Scan State
        self.is_first_frame = True
        self.non_calibrator_blocks = 0
        self.next_block = 0
        self.block_position = 0


    def _setup_frame_grid(self, has_initializer):
        '''Ran on initialization, this creates a generator that outputs the correct block coordinates for scan_block
        to utilize.  This depends on whether an initializer is used in this frame or not.
        '''

        for y_block in range(self.block_height - int(has_initializer)):
            for x_block in range(self.block_width - int(has_initializer)):
                yield x_block + int(has_initializer), y_block + int(has_initializer)


    def _blocks_to_bits(self, how_many, palette_type):
        '''This is an internal method that, based on how many blocks it was told to scan as well as the palette type
        used, will scan that amount on the image and return those converted bits.
        '''

        bit_string = BitStream()
        active_color_set = self.palette_dict[palette_type].color_set
        active_palette_dict = self.palette_conversion_dict[palette_type]

        for block in range(how_many):
            block_coords = next(self.next_block)
            raw_rgb = scan_block(self.image, self.pixel_width, block_coords[0], block_coords[1])
            if active_color_set:
                bit_string.append(active_palette_dict.get_value(color_snap(raw_rgb, active_color_set)))

            else:
                bit_string.append(active_palette_dict.get_value(raw_rgb))

        self.block_position += how_many
        config.stats_handler.blocks_read += how_many

        return bit_string


    def return_initializer(self):
        '''This returns the initializer bitstring for the frame.'''

        return self._blocks_to_bits(324, 'initializer_palette')


    def return_frame_header(self, palette_type):
        '''This method returns the bits carrying the frame header for the frame, as well as the "carry over" bits, which
        were the excess capacity within those blocks, assuming there was extra space.
        '''

        # always 608 bits, plus whatever remainder bits that may be present in the final block.  Protocol v1 only!
        if palette_type != 'stream_palette' and palette_type != 'header_palette' and palette_type != 'primary_palette':
            raise ValueError("FrameHandler.return_frame_header: invalid palette_type argument.")

        full_block_data = self._blocks_to_bits(math.ceil(608 / self.palette_dict[palette_type].bit_length),
                                               f'{palette_type}')
        carry_over_bits = BitStream()

        if full_block_data.len > 608:

            full_block_data.pos = 608
            carry_over_bits.append(full_block_data.read(f'bits : {full_block_data.len - 608}'))
            full_block_data.pos = 0

        config.stats_handler.data_read += carry_over_bits.len
        return full_block_data.read('bits : 608'), carry_over_bits


    def return_remainder_payload(self, palette_type):
        '''With the other parts of the frame already scanned (initializer if applicable, and frame header), based on how
        many blocks are left, it will scan those and return the bit string.
        '''


        if palette_type != 'stream_palette' and palette_type != 'header_palette' and palette_type != 'primary_palette':
            raise ValueError("FrameHandler.return_remainder_payload: invalid palette_type argument.")

        remainder_payload = self._blocks_to_bits(self.non_calibrator_blocks - self.block_position, f'{palette_type}')
        config.stats_handler.data_read += remainder_payload.len

        return remainder_payload


    def update_scan_geometry(self, block_height, block_width, pixel_width):
        '''FrameHandler is a persistent object between frames, held by Decoder.  Because of it's instantiation at
        Decoder's instantiation, scan geometry cannot be loaded into it immediately.  This function does that.
        '''

        self.block_height = block_height
        self.block_width = block_width
        self.pixel_width = pixel_width

        self.non_calibrator_blocks = (self.block_height - int(self.is_first_frame)) * \
                                     (self.block_width - int(self.is_first_frame))


    def update_dictionaries(self, palette_type, palette_dict, palette):
        '''As the stream is setting up, its not possible to instantiate this object with everything at once.  This
        method allows for an easy way to inject new palette objects into the dictionaries used for retrieving values.
        '''

        if palette_type == 'header_palette':
            self.palette_conversion_dict['header_palette'] = palette_dict
            self.palette_dict['header_palette'] = palette
        elif palette_type == 'stream_palette':
            self.palette_conversion_dict['stream_palette'] = palette_dict
            self.palette_dict['stream_palette'] = palette
        elif palette_type == 'primary_palette':
            self.palette_conversion_dict['primary_palette'] = palette_dict
            self.palette_dict['primary_palette'] = palette
        else:
            raise ValueError('FrameHandler.updateDictionary: invalid palette_type argument.')


    def update_blocks_to_read(self, blocks_to_read):
        '''After the frame header bit string is successfully read by read_frame_header(), this updates how many total
        blocks must be read on this frame.  Until that is known, FrameHandler will simply 'blindly' read the full frame,
        as it is instructed to in pieces.
        '''


        if blocks_to_read < self.non_calibrator_blocks:
            logging.debug(f'Last frame detected, {blocks_to_read} to scan.')
        else:
            logging.debug('Full frame detected.')

        self.non_calibrator_blocks = blocks_to_read


    def load_new_frame(self, image, has_initializer):
        '''This method loads in the new image, as well as resets the parameters from the previous frame.'''

        self.image = image
        self.is_first_frame = has_initializer
        self.next_block = self._setup_frame_grid(has_initializer)
        self.block_position = 0

        # This will only fail once, as geometry is not immediately known on the loading of the first frame.
        try:
            self.non_calibrator_blocks = (self.block_height - int(has_initializer)) * \
                                         (self.block_width - int(has_initializer))
        except:
            pass

        config.stats_handler.frames_read += 1