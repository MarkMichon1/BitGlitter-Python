from bitstring import BitStream

import math

from bitglitter.read.scan.scanutilities import color_snap, scan_block


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
        self.x_range = 0
        self.y_range = 0
        self.x_position = 0
        self.y_position = 0
        self.next_block_to_scan = None
        self.block_position = 0
        self.remaining_blocks = 0
        self.bits_to_read = 0
        self.payload_bits_read = 0
        self.bits_read = 0
        self.leftover_bits = BitStream()

        # Class state before last action
        self.prior_leftover_bits = BitStream()
        self.prior_x_position = 0
        self.prior_y_position = 0
        self.prior_number_of_bits = 0 #?
        self.prior_remaining_blocks = 0

        #  Additional setup if we have more starting data
        if self.block_height and self.block_width and self.pixel_width:
            self._geometry_setup()
            self.next_block_to_scan = self._frame_coordinate_generator()

    def _geometry_setup(self):
        self.x_range = self.block_width - int(self.has_initializer)
        self.y_range = self.block_height - int(self.has_initializer)
        self.remaining_blocks = self.x_range * self.y_range

    def _undo_last_task(self):
        """Moves coordinates in generator back before the last task was executed."""
        self.leftover_bits = self.prior_leftover_bits
        self.x_position = self.prior_x_position
        self.y_position = self.prior_y_position
        self.remaining_blocks = self.prior_remaining_blocks

    def _frame_coordinate_generator(self):
        """Creates a generator that outputs the correct block coordinates for scan_block to utilize.  This depends on
         whether an initializer is used in this frame or not.
        """

        while self.y_position < self.y_range:
            yield self.x_position + int(self.has_initializer), self.y_position + int(self.has_initializer)
            self.x_position += 1
            if self.x_position == self.x_range:
                self.x_position = 0
                self.y_position += 1

    def return_bits(self, number_of_bits, is_initializer_palette, is_payload, byte_input=False, redo=False, test=False):

        # Saving state before execution
        self.prior_leftover_bits = self.leftover_bits
        self.prior_x_position = self.x_position
        self.prior_y_position = self.y_position
        self.prior_remaining_blocks = self.remaining_blocks

        if redo:
            self._undo_last_task()

        if byte_input:
            number_of_bits = number_of_bits * 8

        if is_payload:
            self.payload_bits_read += number_of_bits

        if test:
            pass
            # print(f'{self.leftover_bits=} {self.x_position=} {self.y_position=} {self.bits_to_read=} {self.remaining_blocks=} {self.payload_bits_read=}')

        if is_initializer_palette:
            active_color_set = self.initializer_color_set
            active_color_dict = self.initializer_palette_dict
            active_bit_length = self.initializer_palette.bit_length
        else:
            active_color_set = self.stream_palette_color_set
            active_color_dict = self.stream_palette_dict
            active_bit_length = self.stream_palette.bit_length

        complete_request = True
        if number_of_bits:  # Set amount of bits to scan
            number_of_blocks = int(math.ceil((number_of_bits - self.leftover_bits.len) / active_bit_length))
            if number_of_blocks > self.remaining_blocks:
                number_of_blocks = self.remaining_blocks
                complete_request = False
        else:  # If 0, scans the rest of the frame
            number_of_blocks = self.remaining_blocks

        bits = self.leftover_bits if self.leftover_bits.len > 0 else BitStream()

        for block in range(number_of_blocks):
            block_coordinates = next(self.next_block_to_scan)
            average_rgb = scan_block(self.frame, self.pixel_width, block_coordinates[0], block_coordinates[1])

            if active_color_set:  # Non-24 bit palette
                bits.append(active_color_dict.get_value(color_snap(average_rgb, active_color_set)))
            else:  # 24 bit palette
                bits.append(active_color_dict.get_value(average_rgb))
        self.remaining_blocks -= number_of_blocks

        bits = BitStream(bits)
        if bits.len > number_of_bits:
            bits.pos = number_of_bits
            self.leftover_bits = bits.read(bits.len - number_of_bits)
            bits.pos = 0
            bits = bits.read(number_of_bits)
        if complete_request:
            assert bits.len == number_of_bits

        # Statistics update
        self.block_position += number_of_blocks
        self.bits_read += number_of_bits

        return {'bits': bits, 'complete_request': complete_request}

    def set_scan_geometry(self, block_height, block_width, pixel_width):
        self.block_height = block_height
        self.block_width = block_width
        self.pixel_width = pixel_width
        self._geometry_setup()
        self.next_block_to_scan = self._frame_coordinate_generator()

    def set_stream_palette(self, stream_palette, stream_palette_dict, stream_palette_color_set):
        self.stream_palette = stream_palette
        self.stream_palette_dict = stream_palette_dict
        self.stream_palette_color_set = stream_palette_color_set

    def set_bits_to_read(self, number_of_bits):
        self.bits_to_read = number_of_bits

    def return_initializer_bits(self):
        """returns the initializer bitstring for the frame."""
        return self.return_bits(580, True, is_payload=False)

    def return_frame_header_bits(self, is_initializer_palette, redo=False):
        return self.return_bits(352, is_initializer_palette, is_payload=False, redo=redo, test=True)

    def return_stream_header_bits(self, is_initializer_palette):
        return self.return_bits(685, is_initializer_palette, is_payload=True)

    def return_payload_bits(self):
        """Returns the remainder payload bits on the frame."""
        remainder_bits = self.bits_to_read - self.payload_bits_read
        ding = self.return_bits(remainder_bits, is_initializer_palette=False, is_payload=True)
        return ding
