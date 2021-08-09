import logging

from bitstring import BitStream, ConstBitStream

from bitglitter.read.inputdecode.scanutilities import color_snap, scan_block


class ScanHandler:
    """This performs the low level scanning of the frame, and returns the raw bit/byte data for further validating and
    processing.
    """

    def __init__(self, frame, has_initializer, initializer_palette, initializer_palette_dict, initializer_color_set,
                 block_height=None, block_width=None, pixel_width=None, stream_palette=None, stream_palette_dict=None,
                 stream_palette_color_set=None):
        #  Core
        self.frame = frame
        self.has_initializer = has_initializer
        self.block_height = block_height
        self.block_width = block_width
        self.pixel_width = pixel_width

        #  Palette
        self.initializer_palette = initializer_palette
        self.initializer_palette_dict = initializer_palette_dict
        self.initializer_color_set = initializer_color_set

        self.stream_palette = stream_palette
        self.stream_palette_dict = stream_palette_dict
        self.stream_palette_color_set = stream_palette_color_set

        #  Scan state
        self.next_block = None
        self.block_position = 0
        self.remaining_blocks = 0
        self.payload_bits_this_frame = 0
        self.leftover_bits = BitStream()

        #  Additional setup if we have more starting data
        if self.block_height and self.block_width and self.pixel_width:
            self.next_block = self._setup_frame_grid()

    def _setup_frame_grid(self):
        """Creates a generator that outputs the correct block coordinates for scan_block to utilize.  This depends on
         whether an initializer is used in this frame or not.
        """
        x_range = self.block_width - int(self.has_initializer)
        y_range = self.block_height - int(self.has_initializer)
        self.remaining_blocks = x_range * y_range

        for y_block in range(y_range):
            for x_block in range(x_range):
                yield x_block + int(self.has_initializer), y_block + int(self.has_initializer)

    def _return_bits(self, number_of_bits, is_initializer_palette):
        if is_initializer_palette:
            active_color_set = self.initializer_color_set
            active_color_dict = self.initializer_palette_dict
            active_bit_length = self.initializer_palette.bit_length
        else:
            active_color_set = self.stream_palette_color_set
            active_color_dict = self.stream_palette_dict
            active_bit_length = self.stream_palette.bit_length

        if number_of_bits:  # Set amount of bits to scan
            number_of_blocks = (number_of_bits - self.leftover_bits.len) // active_bit_length
        else:  # If 0, scans the rest of the frame
            number_of_blocks = self.remaining_blocks

        bits = self.leftover_bits if self.leftover_bits.len > 0 else BitStream()

        for block in range(number_of_blocks):
            block_coordinates = next(self.next_block)
            average_rgb = scan_block(self.frame, self.pixel_width, block_coordinates[0], block_coordinates[1])

            if active_color_set:  # Non-24 bit palette
                bits.append(active_color_dict.get_value(color_snap(average_rgb, active_color_set)))
            else:  # 24 bit palette
                bits.append(active_color_dict.get_value(average_rgb))
        self.remaining_blocks =- number_of_blocks

        bits = ConstBitStream(bits)
        if bits.len > number_of_bits:
            bits.pos = number_of_bits
            self.leftover_bits = bits.read(bits.len - number_of_bits)
            bits.pos = 0
        assert bits.len == number_of_bits
        return {'blocks_read': number_of_blocks, 'bits': bits}

    def set_scan_geometry(self, block_height, block_width, pixel_width):
        self.block_height = block_height
        self.block_width = block_width
        self.pixel_width = pixel_width
        self.next_block = self._setup_frame_grid()

    def set_stream_palette(self, stream_palette, stream_palette_dict, stream_palette_color_set):
        self.stream_palette = stream_palette
        self.stream_palette_dict = stream_palette_dict
        self.stream_palette_color_set = stream_palette_color_set

    def set_bits_to_read(self, number_of_bits):
        pass

    def return_initializer_bits(self):
        """returns the initializer bitstring for the frame."""
        return self._return_bits(580, True)

    def return_frame_header_bytes(self):
        pass  # 352

    def return_payload_bits(self):
        pass


#     def update_blocks_to_read(self, blocks_to_read):
#         '''After the frame header bit string is successfully read by read_frame_header(), this updates how many total
#         blocks must be read on this frame.  Until that is known, FrameHandler will simply 'blindly' read the full frame,
#         as it is instructed to in pieces.
#         '''
#
#
#         if blocks_to_read < self.non_calibrator_blocks:
#             logging.debug(f'Last frame detected, {blocks_to_read} to scan.')
#         else:
#             logging.debug('Full frame detected.')
#
#         self.non_calibrator_blocks = blocks_to_read