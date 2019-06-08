import logging

from bitglitter.palettes.paletteutilities import palette_grabber, ColorsToValue, _validate_and_add_palette
from bitglitter.read.decoderassets import minimum_block_checkpoint, read_frame_header, read_initializer, validate_payload
from bitglitter.read.framehandler import FrameHandler
from bitglitter.read.framelockon import frame_lock_on


class Decoder:
    '''The Decoder object is what ultimately handles all higher level processing of each BitGlitter frame, orchestrating
    lower-level behavior.  After frames are locked onto, and information is validated as not corrupt (or not needed,
    as the frames may have already been previously read), that data is then passed onto the Assembler.
    '''

    def __init__(self, is_video, config_object, scrypt_n, scrypt_r, scrypt_p, block_height_override, block_width_override,
                 output_path, encryption_key, assemble_hold):

        # Misc Setup
        self.is_video = is_video
        self.frame_number_of_video = 0
        self.active_frame = None
        self.frame_height = None
        self.frame_width = None
        self.checkpoint_passed = True
        self.fatal_checkpoint = True # Non-recoverable errors that require an immediate break from the loop.
        self.stream_header_cleared = False
        self.duplicate_frame_read = False

        # Input arguments
        self.block_height_override = block_height_override
        self.block_width_override = block_width_override
        self.scrypt_n = scrypt_n
        self.scrypt_r = scrypt_r
        self.scrypt_p = scrypt_p
        self.encryption_key = encryption_key
        self.output_path = output_path
        self.assemble_hold = assemble_hold

        # Lock on Characteristics
        self.pixel_width = None
        self.block_height = None
        self.block_width = None
        self.protocol_version = None

        # Palette Variables
        self.initializer_palette = palette_grabber('1')
        self.initializer_palette_dict = ColorsToValue(self.initializer_palette)
        self.primary_palette = None
        self.primary_palette_dict = None
        self.header_palette = None
        self.header_palette_dict = None
        self.stream_palette = None
        self.stream_palette_dict = None

        # Custom color data used in instantiating new palette
        self.custom_color_name = None
        self.custom_color_description = None
        self.custom_color_date_created = None
        self.custom_color_color_set = None

        # Frame Data
        self.stream_sha = None
        self.frame_sha = None
        self.stream_sha_from_last_frame = None
        self.frame_number_of_stream = None
        self.frame_payload = None
        self.carry_over_bits = None
        self.blocks_to_read = None

        # Auxiliary Components
        self.config_object = config_object
        self.frame_handler = FrameHandler(self.initializer_palette, self.initializer_palette_dict)


    def decode_image(self, file_to_input):
        '''This method is used to decode a single image (jpg, png, bmp).'''

        self.active_frame = file_to_input
        self.frame_height, self.frame_width, unused = self.active_frame.shape
        self.frame_handler.load_new_frame(self.active_frame, True)

        if self._first_frame_setup() == False:
            return False

        if self._image_frame_setup() == False:
            return False

        if self._frame_validation('primary_palette') == False:
            return False

        if self._payload_process('primary_palette') == False:
            return False

        if self.config_object.assembler.save_dict[self.stream_sha].stream_header_ascii_complete == True \
                and self.config_object.assembler.save_dict[self.stream_sha].stream_palette_read == False:
            self._attempt_stream_palette_load()


    def decode_video_frame(self, active_frame):
        '''This is the higher level method that decodes and validates data from each video frame, and then passes it to
        the Assembler object for further processing.
        '''

        self.frame_number_of_video += 1
        self.frame_number_of_stream = None
        self.frame_sha = None
        self.frame_payload = None
        self.carry_over_bits = None
        self.duplicate_frame_read = False

        self.active_frame = active_frame
        self.frame_height, self.frame_width, unused = self.active_frame.shape

        if self.frame_number_of_video == 1:
            self.frame_handler.load_new_frame(self.active_frame, True)

            if self._first_frame_setup() == False:
                return False

            if self._video_first_frame_setup() == False:
                return False

        else:
            self.frame_handler.load_new_frame(self.active_frame, False)

            if self.stream_header_cleared == False:
                self._attempt_stream_palette_load()

                if self.fatal_checkpoint == False:
                    return False

        if self.stream_header_cleared == False: # We are still on header_palette frames.
            if self._frame_validation('header_palette') == False:
                return False

            if self._payload_process('header_palette') == False:
                return False

        else: # It has switched to stream_palette frames.
            if self._frame_validation('stream_palette') == False:
                return False

            if self._payload_process('stream_palette') == False:
                return False


    def _first_frame_setup(self):
        '''This is a series of tasks that must be done for the first frames of both video and images.  The frame is
        locked onto, and the initializer from the frame is validated and loaded.
        '''

        self.checkpoint_passed = minimum_block_checkpoint(self.block_height_override, self.block_width_override,
                                                          self.frame_width, self.frame_height)
        if self.checkpoint_passed == False:
            return False

        self.block_height = self.block_height_override
        self.block_width = self.block_width_override

        self.block_height, self.block_width, self.pixel_width = frame_lock_on(self.active_frame, self.block_height_override,
                                                                              self.block_width_override, self.frame_width,
                                                                              self.frame_height)
        if self.pixel_width == False:
            return False

        self.frame_handler.update_scan_geometry(self.block_height, self.block_width, self.pixel_width)


    def _frame_validation(self, palette_type):
        '''This internal method first validates the frame by checking the frame header, and then checks with the
        Assembler object to see if this frame is needed.  This is ran on every frame.
        '''

        self.frameHeaderBits, self.carry_over_bits = self.frame_handler.return_frame_header(palette_type)

        self.stream_sha, self.frame_sha, self.frame_number_of_stream, self.blocks_to_read = \
            read_frame_header(self.frameHeaderBits)

        if self.stream_sha == False:
            return False

        self.stream_sha_from_last_frame = self.stream_sha
        self.frame_handler.update_blocks_to_read(self.blocks_to_read)

        if self.config_object.assembler.check_if_frame_needed(self.stream_sha, self.frame_number_of_stream) == False:
            self.duplicate_frame_read = True
            if self.is_video == False:
                self.config_object.assembler.save_dict[self.stream_sha]._close_session()

            return False


    def _payload_process(self, palette_type):
        '''If the frame is validated, this method appends any carry-overy bits from reading the frame handler blocks,
        and then passes it on into the Assembler.  This is ran on every frame.
        '''

        self.carry_over_bits.append(self.frame_handler.return_remainder_payload(palette_type))
        self.frame_payload = self.carry_over_bits

        if validate_payload(self.frame_payload, self.frame_sha) == False:
            return False

        self.config_object.assembler.accept_frame(self.stream_sha, self.frame_payload, self.frame_number_of_stream,
                                                  self.scrypt_n, self.scrypt_r, self.scrypt_p, self.output_path,
                                                  self.encryption_key, self.assemble_hold)


    def _attempt_stream_palette_load(self):
        '''The stream header is where the data stating the stream palette used is stated.
        Commonly this will be able to be read on the first frame, but for larger stream headers using custom palettes,
        this may take several frames for it to successfully load, since the full compressed header package must be read
        first.  Assuming the stream palette hasn't loaded yet, this will call the Assembler object to check and see if
        the stream header, along with its ASCII component have been fully read yet.  If so, it is loaded into the proper
        class attributes.
        '''

        logging.debug('Attempting stream palette load...')
        save_object = self.config_object.assembler.save_dict[self.stream_sha_from_last_frame].return_stream_header_id()

        if save_object[0] == True:

            self.stream_header_cleared = True

            # Does stream palette already exist as a custom or default color?
            if save_object[1] in self.config_object.color_handler.custom_palette_list or save_object[1] in \
                    self.config_object.color_handler.default_palette_list:

                self.stream_palette = palette_grabber(save_object[1])
                logging.info(f'Palette ID {save_object[1]} already saved in system... successfully loaded!')

            # This is a new palette which will now be instantiation as a custom palette object.
            else:

                self.fatal_checkpoint =_validate_and_add_palette(save_object[2], save_object[3], save_object[4], save_object[5])

                if self.fatal_checkpoint == False:
                    logging.critical('Palette for this stream cannot be loaded!  This could only be caused by data '
                                     'corrupted during the streams write.  Aborting...')
                    return False

                logging.debug('Custom palette successfully instantiated.')
                self.stream_palette = palette_grabber(save_object[1])

            self.stream_palette_dict = ColorsToValue(self.stream_palette)
            self.frame_handler.update_dictionaries('stream_palette', self.stream_palette_dict, self.stream_palette)
            self.config_object.assembler.save_dict[self.stream_sha].stream_palette_read = True

        else:
            logging.debug('Attempt failed this frame.')


    def _image_frame_setup(self):
        '''This method validates the initializer bit string, as well as loads the primary palette into memory.  The
        reason why this must be a separate method from _video_first_frame_setup is because both images and videos handle
        palettes differently.  Images only need to worry about the "primary palette" or the palette that is being used
        on that particular frame, while videos must intelligently switch between the header palette and the stream
        palette.
        '''

        self.protocol_version, self.primary_palette = read_initializer(self.frame_handler.return_initializer(),
                                                                       self.block_height, self.block_width,
                                                                       self.config_object.color_handler.custom_palette_list,
                                                                       self.config_object.color_handler.default_palette_list)
        if self.protocol_version == False:
            return False
        logging.debug(f'primary_palette ID loaded: {self.primary_palette.id}')

        self.primary_palette_dict = ColorsToValue(self.primary_palette)
        self.frame_handler.primary_palette_bit_length = self.primary_palette.bit_length
        self.frame_handler.update_dictionaries('primary_palette', self.primary_palette_dict, self.primary_palette)


    def _video_first_frame_setup(self):
        '''This method is ran on the first frame of the decoded video, to load in the header palette.  To prevent a
        duplicate explanation, please see _imagePaletteSetup directly above.
        '''

        self.protocol_version, self.header_palette = read_initializer(self.frame_handler.return_initializer(),
                                                                      self.block_height, self.block_width,
                                                                      self.config_object.color_handler.custom_palette_list,
                                                                      self.config_object.color_handler.default_palette_list)
        if self.protocol_version == False:
            return False
        logging.debug(f'header_palette ID loaded: {self.header_palette.id}')

        # Now with header_palette loaded, we can get its color set as well as generate its ColorsToValue dictionary,
        # As well as propagate these values to frame_handler.
        self.header_palette_dict = ColorsToValue(self.header_palette)
        self.frame_handler.update_dictionaries('header_palette', self.header_palette_dict, self.header_palette)