#  This class has its own module because of its large size

from sqlalchemy import BLOB, Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

import time

from bitglitter.config.config import engine, session, SqlBaseClass


class StreamRead(SqlBaseClass):
    """This serves as the central data container and API for interacting with saved read data."""

    __tablename__ = 'stream_reads'
    __abstract__ = False

    # Core
    time_started = Column(Integer, default=time.time)
    bg_version = Column(String)
    protocol_version = Column(Integer)
    stream_sha256 = Column(String, unique=True, nullable=False)  # req
    stream_is_video = Column(Boolean, nullable=False)  # req
    stream_palette = None  # todo
    stream_palette_id = None  # todo
    custom_palette_used = Column(Boolean)
    number_of_frames = Column(Integer)
    compression_enabled = Column(Boolean)
    encryption_enabled = Column(Boolean)
    file_mask_enabled = Column(Boolean)
    manifest = Column(String)  # temporary todo

    # Read State
    remaining_pre_payload_bits = Column(Integer)
    carry_over_header_bytes = Column(BLOB)
    carry_over_padding_bits = Column(Integer)
    payload_start_frame = Column(Integer)
    payload_first_frame_bits = Column(Integer)
    payload_bits_per_standard_frame = Column(Integer)
    metadata_headers_ran = Column(Boolean)
    completed_frames = Column(Integer, default=0)
    aborted = Column(Boolean, default=False)

    # Geometry
    pixel_width = Column(Integer)
    block_height = Column(Integer)
    block_width = Column(Integer)

    # Metadata
    stream_name = Column(String)
    stream_description = Column(String)
    time_created = Column(Integer)
    size_in_bytes = Column(Integer)

    # Crypto
    scrypt_n = Column(Integer)
    scrypt_r = Column(Integer)
    scrypt_p = Column(Integer)
    crypto_key = Column(String)

    # Relationships
    frames = relationship('StreamFrame', back_populates='stream', cascade='all, delete', passive_deletes=True)
    directories = relationship('StreamDirectory', back_populates='stream', cascade='all, delete', passive_deletes=True)
    files = relationship('StreamFile', back_populates='stream', cascade='all, delete', passive_deletes=True)
    progress = relationship('StreamDataProgress', back_populates='stream', cascade='all, delete', passive_deletes=True)

    def __str__(self):
        return f'{self.stream_name} - {self.stream_sha256}'

    def manifest_load(self):
        pass

    def geometry_load(self):
        pass

    def accept_frame(self, payload_bits, frame_number):
        pass

    # User control
    def _delete_data_folder(self):
        pass

    def _delete_stream(self):
        self.delete()


# v This needs to be at bottom to resolve import/DB relationship issues.
import bitglitter.config.readmodels.readmodels

SqlBaseClass.metadata.create_all(engine)


#todo: MULTIPLE CLASSES: merge with above model and integrate applicable stuff into readfunctions

# class SavedStream:
#     '''PartialSave objects are essentially containers for the state of streams as they are being read, frame by frame.
#     This mainly interacts through the Assembler object.  All of the functionality needed to convert raw frame data back
#     into the original package is done through it's contained methods.
#     '''
#
#     def __init__(self, stream_sha, working_folder, scrypt_n, scrypt_r, scrypt_p, output_path, encryption_key,
#                  assemble_hold):
#
#         # Core object state data
#         self.save_folder = working_folder + f'\\{stream_sha}'
#         self.stream_sha = stream_sha
#         self.assembled_sha = stream_sha
#         self.frames_ingested = 0
#
#         self.stream_header_preamble_complete = False
#         self.stream_header_ascii_complete = False
#         self.stream_header_preamble_buffer = BitStream()
#         self.stream_header_ascii_buffer = BitStream()
#
#         self.next_stream_header_sequential_frame = 1
#         self.payload_begins_this_frame = None
#         self.active_this_session = True
#         self.is_assembled = False # Did the frames successfully merge into a single binary?
#         self.post_processor_decrypted = False # Was the stream successfully decrypted?
#         self.frame_reference_table = None
#         self.frames_prior_to_binary_preamble = []
#         self.stream_palette_read = False
#         self.assemble_hold = assemble_hold
#
#
#         # Stream Setup Header
#         self.size_in_bytes = None
#         self.total_frames = '???'
#         self.compression_enabled = None
#         self.encryption_enabled = None
#         self.masking_enabled = None
#         self.custom_palette_used = None
#         self.date_created = None
#         self.stream_palette_id = None
#         self.ascii_header_byte_size = None
#
#         # Stream Metadata
#         self.bg_version = None
#         self.stream_name = None
#         self.stream_description = None
#         self.file_list = None
#
#         # Metadata Header Fields
#         self.custom_color_name = None
#         self.custom_color_description = None
#         self.custom_color_date_created = None
#         self.custom_color_palette = None
#         self.post_compression_sha = None
#
#         manifest = None
#
#         # Changeable Postprocessing Arguments
#         self.encryption_key = encryption_key
#         self.scrypt_n = scrypt_n
#         self.scrypt_r = scrypt_r
#         self.scrypt_p = scrypt_p
#         self.output_path = output_path
#
#         os.mkdir(self.save_folder)
#         logging.info(f'New partial save! Stream SHA-256: {self.stream_sha}')
#
#
#     def load_frame_data(self, frame_data, frame_number, is_recursive = False):
#         '''After being validated in the decoder, this method blindly accepts the frame_data as a piece, saving it within
#         the appropriate folder, and adding the frame number to the list.
#         '''
#
#         # This makes the count increase only when this function isn't ran recursively.  This prevents revisited frames
#         # from increasing the count.
#         if is_recursive == False:
#             self.frames_ingested += 1
#
#         if self.stream_header_ascii_complete == False and frame_number == self.next_stream_header_sequential_frame:
#             frame_data = self._stream_header_assembly(frame_data, frame_number)
#
#         if frame_data.len > 0:
#             self._write_file(frame_data, f'frame{frame_number}')
#
#         self.active_this_session = True
#
#         if self.stream_header_preamble_complete == True:
#             self.frame_reference_table.set(True, frame_number - 1)
#
#         else:
#             self.frames_prior_to_binary_preamble.append(frame_number)
#
#         logging.debug(f"Frame {frame_number} for stream {self.stream_sha} successfully saved!")
#
#         if self.stream_header_ascii_complete == False \
#             and self.is_frame_needed(self.next_stream_header_sequential_frame) == False:
#             frame_data = self._read_file(f'frame{self.next_stream_header_sequential_frame}')
#             self.load_frame_data(frame_data, self.next_stream_header_sequential_frame, is_recursive= True)
#
#     #todo: add frame block byte file to signify processing on given frame
#
#     def user_input_update(self, password_update, scrypt_n, scrypt_r, scrypt_p, change_output_path):
#         '''This method changes user related configurations such as password, scrypt parameters, and save location.
#         These arguments are blindly accepted from update_partial_save() in savedfilefunctions, as the inputs are
#         validated there.
#         '''
#
#         if password_update:
#             self.encryption_key = password_update
#
#         if scrypt_n:
#             self.scrypt_n = scrypt_n
#         if scrypt_r:
#             self.scrypt_r = scrypt_r
#         if scrypt_p:
#             self.scrypt_p = scrypt_p
#
#         if change_output_path:
#             self.output_path = change_output_path
#
#
#     def _attempt_assembly(self):
#         '''This method will check to see if all frames for the stream have been read.  If so, they will be assembled
#         into a single binary, it's hash will be validated, and then it will be ran through post-processing,
#         which is what ultimately yields the original files encoded in the stream.
#         '''
#
#         if self.is_assembled == False: # If false, assembly will be attempted.  Otherwise, we skip to postprocessing.
#
#             if self.total_frames == self.frames_ingested:
#                 logging.info(f'All frame(s) loaded for {self.stream_sha}, attempting assembly...')
#                 data_left = self.size_in_bytes * 8
#                 assembled_path = f'{self.save_folder}\\assembled.bin'
#                 inter_frame_bit_buffer = BitStream()
#
#                 with open(assembled_path, 'ab') as assemble_package:
#
#                     for frame in range(self.total_frames - self.payload_begins_this_frame + 1):
#
#                         frame_number = frame + self.payload_begins_this_frame
#                         logging.debug(f'Assembling {frame_number}/{self.total_frames}')
#                         active_frame = self._read_file(f'frame{frame_number}')
#
#                         if frame_number != self.total_frames: # All frames except the last one.
#                             bit_merge = BitStream(inter_frame_bit_buffer + active_frame)
#                             data_holder = bit_merge.read(f'bytes: {bit_merge.len // 8}')
#
#                             if bit_merge.len - bit_merge.pos > 0:
#                                 inter_frame_bit_buffer = bit_merge.read(f'bits : {bit_merge.len - bit_merge.pos}')
#
#                             else:
#                                 inter_frame_bit_buffer = BitStream()
#
#                             if isinstance(data_holder, bytes):
#                                 logging.debug('was bytes this frame!')
#                                 assemble_package.write(data_holder)
#
#                             else:
#                                 logging.debug('bits to bytes this frame')
#                                 to_byte_type = data_holder.tobytes()
#                                 assemble_package.write(to_byte_type)
#                             data_left -= active_frame.len
#
#                         else: #This is the last frame
#                             bit_merge = inter_frame_bit_buffer + active_frame.read(f'bits : {data_left}')
#                             to_byte_type = bit_merge.tobytes()
#                             assemble_package.write(to_byte_type)
#
#                 if get_hash_from_file(assembled_path) != self.assembled_sha:
#                     logging.critical(f'Assembled frames do not match self.packageSHA.  Cannot continue.')
#                     return False
#
#                 logging.debug(f'Successfully assembled.')
#                 self.is_assembled = True
#
#             else:
#                 logging.info(f'{self.frames_ingested} / {self.total_frames}  frames have been loaded for '
#                              f'{self.stream_sha}\n so far, cannot assemble yet.')
#                 return False
#
#         post_process_attempt = PostProcessor(self.output_path, self.stream_sha, self.save_folder,
#                                            self.encryption_enabled, self.encryption_key, self.scrypt_n,
#                                            self.scrypt_r, self.scrypt_p, self.compression_enabled)
#
#         # Did all three stages of PostProcess successfully run?
#         if post_process_attempt.fully_assembled != True:
#             return False
#
#         return True
#
#
#     def _create_frame_reference_table(self):
#         '''This creates a file inside of the object's folder to keep track of which frames have been ingested.  Bit
#         positions correspond to frame number (-1 so position 0 is frame 1, etc).
#         '''
#
#         self.frame_reference_table = BitStream(length=self.total_frames)
#
#         for position in self.frames_prior_to_binary_preamble:
#             self.frame_reference_table.set(True, position - 1)
#
#         self.frames_prior_to_binary_preamble = []
#
#
#     def _stream_header_assembly(self, frame_data, frame_number):
#         '''Stream headers may span over numerous frames, and could be read non-sequentially.  This function manages this
#         aspect.  Both stream headers are stripped from the raw frame data, returning payload data (if applicable).
#         '''
#
#         logging.debug('_stream_header_assembly running...')
#         self.next_stream_header_sequential_frame += 1
#
#         if self.stream_header_preamble_complete == False:
#
#             # Preamble header uses all of this frame.
#             if 422 - self.stream_header_preamble_buffer.len >= frame_data.len:
#
#                 logging.debug('Preamble header uses all of this frame.')
#                 read_length = frame_data.len
#
#             # Preamble terminates on this frame.
#             else:
#
#                 logging.debug('Preamble terminates on this frame.')
#                 read_length = 422 - self.stream_header_preamble_buffer.len
#
#             self.stream_header_preamble_buffer.append(frame_data.read(f'bits:{read_length}'))
#
#             if self.stream_header_preamble_buffer.len == 422:
#                 self.read_stream_header_binary_preamble()
#
#         if self.stream_header_ascii_complete == False and frame_data.len - frame_data.bitpos > 0:
#             # ASCII header rolls over to the next frame.
#             if self.ascii_header_byte_size * 8 - self.stream_header_ascii_buffer.len >= frame_data.len \
#                     - frame_data.bitpos:
#
#                 logging.debug('ASCII header rolls over to another frame.')
#                 read_length = frame_data.len - frame_data.bitpos
#
#             # ASCII header terminates on this frame.
#             else:
#                 logging.debug('ASCII header terminates on this frame.')
#                 read_length = self.ascii_header_byte_size * 8 - self.stream_header_ascii_buffer.len
#
#             self.stream_header_ascii_buffer.append(frame_data.read(f'bits:{read_length}'))
#
#             if self.stream_header_ascii_buffer.len == self.ascii_header_byte_size * 8:
#                 self.payload_begins_this_frame = frame_number
#                 self.read_stream_header_ascii_compressed()
#
#             if frame_data.len - frame_data.bitpos > 0:
#                 return frame_data.read(f'bits:{frame_data.len - frame_data.bitpos}')
#
#         return BitStream()
#
#
#     def _write_file(self, data, file_name, to_compress=False):
#         '''This is an internal method used to write data to the object's folder.  Since we are dealing with bits and not
#         bytes (which is the smallest size operating systems can work with), there is a special five-byte header that
#         decodes as an unsigned integer which is the amount of bits to read.
#         '''
#
#         bits_appendage = BitStream(uint=data.len, length=40)
#         bits_appendage_to_bytes = bits_appendage.tobytes()
#         data_to_bytes = data.tobytes()
#
#         if to_compress == True:
#             temp_name = self.save_folder + '\\temp.bin'
#             with open(temp_name, 'wb') as write_data:
#                 write_data.write(bits_appendage_to_bytes)
#                 write_data.write(data_to_bytes)
#
#             compress_file(temp_name, self.save_folder + f'\\{file_name}.bin')
#
#         else:
#             with open(self.save_folder + f'\\{file_name}.bin', 'wb') as write_data:
#                 write_data.write(bits_appendage_to_bytes)
#                 write_data.write(data_to_bytes)
#
#
#     def _read_file(self, file_name, to_decompress=False):
#         '''This internal method reads the file with the file_name according to how many bits it is, deletes the file,
#         and then returns the BitStream object.
#         '''
#
#         file_path = self.save_folder + f'\\{file_name}.bin'
#
#         if to_decompress == False:
#             with open(file_path, 'rb') as readData:
#                 file_to_bits = BitStream(readData)
#                 bits_to_read = file_to_bits.read('uint:40')
#                 retrieved_file = file_to_bits.read(f'bits:{bits_to_read}')
#             os.remove(file_path)
#
#         else:
#             decompress_file(file_path, self.save_folder + '\\temp.bin')
#             with open(self.save_folder + '\\temp.bin', 'rb') as readData:
#                 file_to_bits = BitStream(readData)
#                 bits_to_read = file_to_bits.read('uint:40')
#                 retrieved_file = file_to_bits.read(f'bits:{bits_to_read}')
#             os.remove(self.save_folder + '\\temp.bin')
#
#         return retrieved_file
#
#
#     def read_stream_header_binary_preamble(self):
#         '''This method converts the raw full binary preamble into the various PartialSave attributes.'''
#
#         self.size_in_bytes, self.total_frames, self.compression_enabled, self.encryption_enabled, self.masking_enabled,\
#         self.custom_palette_used, self.date_created, self.stream_palette_id, self.ascii_header_byte_size = \
#             decode_stream_header(self.stream_header_preamble_buffer)
#         self.stream_header_preamble_buffer = None
#         self.date_created = datetime.datetime.fromtimestamp(int(self.date_created)).strftime('%Y-%m-%d %H:%M:%S')
#
#         logging.info(f'*** Part 1/2 of header decoded for {self.stream_sha}: ***\nPayload size: {self.size_in_bytes} B'
#                      f'\nTotal frames: {self.total_frames}\nCompression enabled: {self.compression_enabled}'
#                      f'\nEncryption Enabled: {self.encryption_enabled}\nFile masking enabled: {self.masking_enabled}'
#                      f'\nCustom Palette Used: {self.custom_palette_used}\nDate created: {self.date_created}'
#                      f'\nStream palette ID: {self.stream_palette_id}')
#         logging.debug(f'ASCII header byte size: {self.ascii_header_byte_size} B')
#
#         self._create_frame_reference_table()
#         self.stream_header_preamble_complete = True
#
#
#     def read_stream_header_ascii_compressed(self):
#         '''This method converts the raw full ASCII stream header into the various PartialSave attributes.'''
#
#         self.bg_version, self.stream_name, self.stream_description, self.file_list, self.custom_color_name, \
#         self.custom_color_description, self.custom_color_date_created, self.custom_color_palette, \
#         self.post_compression_sha = \
#          decode_text_header(self.stream_header_ascii_buffer, self.custom_palette_used,
#                             self.encryption_enabled)
#         self.stream_header_ascii_buffer = None
#
#         if self.masking_enabled == True:
#             self.file_list = "Cannot display, file masking enabled for this stream!"
#
#         else:
#             self.file_list = format_file_list(self.file_list)
#
#         logging.info(f'*** Part 2/2 of header decoded for {self.stream_sha}: ***\nProgram version of sender: '
#                      f'v{self.bg_version}\nStream name: {self.stream_name}\nStream description: '
#                      f'{self.stream_description} \nFile list: {self.file_list}')
#
#         if self.custom_palette_used == True:
#             logging.info(f'\nCustom color name: {self.custom_color_name}\nCustom color description: '
#                          f'{self.custom_color_description}\nCustom color date created: '
#                     f'{datetime.datetime.fromtimestamp(int(self.custom_color_date_created)).strftime("%Y-%m-%d %H:%M:%S")}'
#                          f'\nCustom color palette: {self.custom_color_palette}')
#
#         if self.encryption_enabled == True:
#             logging.info(f'Post-compression hash: {self.post_compression_sha}')
#             self.assembled_sha = self.post_compression_sha
#
#         self.stream_header_ascii_complete = True
#
#
#     def is_frame_needed(self, frame_number):
#         '''This determines whether a given frame is needed for this stream or not.'''
#
#         # Is the stream already assembled?  If so, no more frames need to be accepted.
#         if self.is_assembled == True:
#             return False
#
#         # The stream is not assembled.
#         else:
#
#             # If the stream header binary preamble isn't loaded yet, then by default we accept the frame, unless that
#             # frame number is already in self.frames_prior_to_binary_preamble, which is a list of processed frames prior
#             # to the binary preamble being read.
#             if self.stream_header_preamble_complete == False:
#                 if frame_number not in self.frames_prior_to_binary_preamble:
#                     return True
#
#                 else:
#                     return False
#
#             # The preamble has been loaded, checking the reference table.
#             else:
#
#                 # Frame reference table is not in memory and must be loaded.
#                 if self.frame_reference_table == None:
#
#                     self.frame_reference_table = BitStream(self._read_file('\\frame_reference_table',
#                                                                            to_decompress=True))
#
#                 self.frame_reference_table.bitpos = frame_number - 1
#                 isFrameLoaded = self.frame_reference_table.read('bool')
#                 return not isFrameLoaded
#
#
#     def _close_session(self):
#         '''Called by the Assembler object, this will flush self.frame_reference_table back to disk, as well as flag it as
#         an inactive session.
#         '''
#
#         self.active_this_session = False
#
#         if self.stream_header_preamble_complete == True:
#             self._write_file(self.frame_reference_table, '\\frame_reference_table', to_compress=True)
#
#         self.frame_reference_table = None
#         logging.debug(f'Closing session for {self.stream_sha}')
#
#
#     def return_status(self, debug_data): # todo: convert into dict return
#         '''This is used in print_full_save_list in savedfunctions module; it returns the state of the object, as well as
#         various information read from the reader.  __str__ is not used, as debug_data controls what level of data is
#         returned, whether for end users, or debugging purposes.
#         '''
#
#         temp_holder = f"{'*' * 8} {self.stream_sha} {'*' * 8}" \
#             f"\n\n{self.frames_ingested} / {self.total_frames} frames saved" \
#             f"\n\nStream header complete: {self.stream_header_ascii_complete}" \
#             f"\nIs assembled: {self.is_assembled}" \
#             f"\n\nStream name: {self.stream_name}" \
#             f"\nStream Description: {self.stream_description}" \
#             f"\nDate Created: {self.date_created}" \
#             f"\nSize in bytes: {self.size_in_bytes} B" \
#             f"\nCompression enabled: {self.compression_enabled}" \
#             f"\nEncryption enabled: {self.encryption_enabled}" \
#             f"\nFile masking enabled: {self.masking_enabled}" \
#             f"\n\nEncryption key: {self.encryption_key} " \
#             f"\nScrypt N: {self.scrypt_n}" \
#             f"\nScrypt R: {self.scrypt_r}" \
#             f"\nScrypt P: {self.scrypt_p}" \
#             f"\nOutput path upon assembly: {self.output_path}" \
#             f"\n\nFile list: {self.file_list}"
#
#         if debug_data == True:
#             temp_holder += f"\n\n{'*' * 3} {'DEBUG'} {'*' * 3}" \
#                 f"\nBG version: {self.bg_version}" \
#                 f"\nASCII header byte size: {self.ascii_header_byte_size}" \
#                 f"\nPost compression SHA: {self.post_compression_sha}" \
#                 f"\nStream Palette ID: {self.stream_palette_id}" \
#                 f"\n\nCustom color data (if applicable)" \
#                 f"\nCustom color name: {self.custom_color_name}" \
#                 f"\nCustom color description: {self.custom_color_description}" \
#                 f"\nCustom color date created: {self.custom_color_date_created}" \
#                 f"\nCustom color palette: {self.custom_color_palette}"
#
#         return temp_holder
#
#
#     def return_stream_header_id(self):
#         '''This method releases the stream_palette ID (and custom color data if applicable) for the Decoder to use to
#         create the palette.
#         '''
#
#         return self.stream_header_ascii_complete, self.stream_palette_id, self.custom_color_name, \
#                self.custom_color_description,  self.custom_color_date_created, self.custom_color_palette


# class Assembler:
#     '''This object holds PartialSave objects, which holds the state of the file being read until it is fully assembled
#     and complete, which then purges the record.
#     '''
#
#     def __init__(self):
#         self.working_folder = DEFAULT_READ_PATH
#         self.save_dict = {}
#         self.active_session_hashes = []
#
#
#     def check_if_frame_needed(self, stream_sha, frame_number):
#
#         if stream_sha not in self.save_dict:
#             return True
#         else:
#             if self.save_dict[stream_sha].is_frame_needed(frame_number) == False:
#                 logging.info(f'Frame # {frame_number} / {self.save_dict[stream_sha].total_frames} for stream SHA '
#                              f'{stream_sha} is already saved!  Skipping...')
#             else:
#                 return True
#         return False
#
#
#     def create_partial_save(self, stream_sha, scrypt_n, scrypt_r, scrypt_p, output_path, encryption_key, assemble_hold):
#         self.save_dict[stream_sha] = SavedStream(stream_sha, self.working_folder, scrypt_n, scrypt_r, scrypt_p, output_path,
#                                                  encryption_key, assemble_hold)
#
#
#     def save_frame_into_partial_save(self, stream_sha, payload, frame_number):
#         logging.info(f'Frame # {frame_number} / {self.save_dict[stream_sha].total_frames} for stream SHA {stream_sha} '
#                      f'saved!')
#         self.save_dict[stream_sha].load_frame_data(payload, frame_number)
#
#
#     def accept_frame(self, stream_sha, payload, frame_number, scrypt_n, scrypt_r, scrypt_p, output_path, encryption_key,
#                      assemble_hold):
#         '''This method accepts a validated frame.'''
#
#         if stream_sha not in self.save_dict:
#             self.create_partial_save(stream_sha, scrypt_n, scrypt_r, scrypt_p, output_path, encryption_key, assemble_hold)
#
#         if stream_sha not in self.active_session_hashes:
#             self.active_session_hashes.append(stream_sha)
#
#         self.save_frame_into_partial_save(stream_sha, payload, frame_number)
#
#
#     def review_active_sessions(self):
#         '''This method will go over all stream_sha's that were read in this read session, and will check to see if
#         check if frames_ingested == total_frames AND the frame reference table is displaying all frames are present.  This
#         only runs if there is at least one active session.
#         '''
#
#         if self.active_session_hashes:
#             logging.info('Reviewing active sessions and attempting assembly...')
#             for partial_save in self.active_session_hashes:
#
#                 # Not ready to be assembled this session.
#                 if self.save_dict[partial_save]._attempt_assembly() == False \
#                         and self.save_dict[partial_save].assemble_hold == False:
#                     self.save_dict[partial_save]._close_session()
#
#                 # Assembled, temporary files pending deletion.
#                 else:
#                     logging.info(f'{partial_save} fully read!  Deleting temporary files...')
#                     self.remove_partial_save(partial_save)
#
#             self.active_session_hashes = []
#
#
#     def remove_partial_save(self, stream_sha):
#         '''Removes PartialSave from dictionary.  Is used either through direct user argument, or by read() once a stream
#         is successfully converted back into a file.
#         '''
#
#         del self.save_dict[stream_sha]
#         shutil.rmtree(self.working_folder + f'\\{stream_sha}')
#         logging.debug(f'Temporary files successfully removed.')
#
#
#     def clear_partial_saves(self):
#         '''This removes all save data.  Called by user function remove_all_partial_saves() in savedfilefunctions.'''
#
#         try:
#             shutil.rmtree(self.working_folder)
#         except:
#             pass
#
#         self.save_dict = {}


# class Decryptor:
#     '''This is the first step of the post-processing once assembly is complete.  This will take the assembled binary,
#     and, if encryption was enabled on this stream, will attempt to decrypt it with the AES key provided.
#     '''
#
#     def __init__(self, working_folder, encryption_enabled, encryption_key, scrypt_n, scrypt_r, scrypt_p, stream_sha):
#
#         input_file = working_folder + '\\assembled.bin'
#         self.pass_through = input_file
#         self.is_satisfied = False
#
#         if encryption_enabled:
#
#             if encryption_key:
#
#                 logging.info('Attempting to decrypt with provided key...')
#                 logging.debug(f'Trying with key {encryption_key}')
#                 self.pass_through = working_folder + '\\decrypted.bin'
#                 decrypt_file(input_file, self.pass_through, encryption_key, scrypt_n, scrypt_r, scrypt_p,
#                              remove_input=False)
#
#                 # Checking if password is valid
#                 if stream_sha == get_hash_from_file(self.pass_through):
#
#                     logging.info('Successfully decrypted.')
#                     self.is_satisfied = True
#
#                 else:
#
#                     logging.info("Password incorrect, cannot continue.")
#                     os.remove(self.pass_through)
#
#             else:
#
#                 logging.warning(f'Decryption key missing from input argument, cannot continue.')
#
#         else:
#
#             logging.info('Encryption was not enabled on this stream.  Skipping step...')
#             self.is_satisfied = True
#
#
# class Decompressor:
#     '''If compression was enabled on this stream, this object will decompress it.'''
#
#     def __init__(self, working_folder, pass_through, compression_enabled):
#
#         self.pass_through = pass_through
#
#         if compression_enabled:
#             new_path = working_folder + "\\decompressed.dat"
#             logging.info('Decompressing file...')
#             decompress_file(self.pass_through, new_path)
#             self.pass_through = new_path
#             logging.info('Successfully decompressed.')
#
#         else:
#             logging.info('Compression was not enabled on this stream.  Skipping step...')
#
#
# class Unpackager:
#     '''This object takes the decompressed binary and 'unpackages' it into the files and/or folders embedded in it.'''
#
#     def __init__(self, pass_through, output_path, stream_sha):
#
#         if output_path == None:
#             printed_save_location = 'program run folder'
#
#         else:
#             printed_save_location = output_path
#
#         logging.info(f'Unpackaging file(s) at {printed_save_location}...')
#
#         unpackage(pass_through, output_path, stream_sha)
#         logging.info('File(s) successfully unpackaged.')


