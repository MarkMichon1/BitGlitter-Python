#  This model has its own module because of its large size

from bitstring import BitStream
from sqlalchemy import BLOB, Boolean, Column, Float, func, Integer, String
from sqlalchemy.orm import relationship

import json
import logging
import math
from pathlib import Path
import time

from bitglitter.config.config import engine, SQLBaseClass, session
from bitglitter.config.palettemodels import Palette
from bitglitter.read.decode.manifest import manifest_unpack
from bitglitter.config.readmodels.readmodels import StreamFrame, StreamFile, StreamDataProgress


class StreamRead(SQLBaseClass):
    """This serves as the central data container and API for interacting with saved read data."""

    __tablename__ = 'stream_reads'
    __abstract__ = False

    # Core Metadata (App)
    time_started = Column(Integer, default=time.time)
    bg_version = Column(String)
    protocol_version = Column(Integer)
    stream_sha256 = Column(String, unique=True, nullable=False)
    stream_is_video = Column(Boolean, nullable=False)
    stream_palette_id = Column(String)
    custom_palette_used = Column(Boolean)
    custom_palette_loaded = Column(Boolean, default=False)
    total_frames = Column(Integer)
    compression_enabled = Column(Boolean)
    encryption_enabled = Column(Boolean)
    file_masking_enabled = Column(Boolean)
    stream_name = Column(String)
    stream_description = Column(String)
    time_created = Column(Integer)
    size_in_bytes = Column(Integer)
    output_directory = Column(String)
    manifest_string = Column(String)

    # Header Management
    remaining_pre_payload_bits = Column(Integer)
    carry_over_header_bytes = Column(BLOB)
    carry_over_padding_bits = Column(Integer)

    # Read State
    payload_start_frame = Column(Integer)
    payload_first_frame_bits = Column(Integer)
    payload_bits_per_standard_frame = Column(Integer)
    palette_header_size_bytes = Column(Integer)
    palette_header_hash = Column(String)
    metadata_header_size_bytes = Column(Integer)
    metadata_header_sha256 = Column(String)
    stream_header_complete = Column(Boolean, default=False)
    metadata_header_complete = Column(Boolean, default=False)
    palette_header_complete = Column(Boolean, default=False)
    completed_frames = Column(Integer, default=0)
    highest_consecutive_setup_frame_read = Column(Integer, default=0)  # Important for initial metadata grab
    encrypted_metadata_header_bytes = Column(BLOB)  # Used when file masking and incorrect key.  Flushed when correct.

    # Operation State
    active_this_session = Column(Boolean, default=True)
    recalculate_eligibility = Column(Boolean, default=True) # Toggles file eligibility stuff if new data (or not)
    all_frames_accounted_for = Column(Boolean, default=False)  # all frames are saved in DB
    total_files = Column(Integer)
    completed_files = Column(Integer, default=0)
    is_complete = Column(Boolean, default=False)  # is unpackaged

    # Unpackage State
    stop_at_metadata_load = Column(Boolean)
    auto_unpackage_stream = Column(Boolean)
    auto_delete_frames = Column(Boolean) #todo
    auto_delete_finished_stream = Column(Boolean)
    metadata_checkpoint_ran = Column(Boolean, default=False)
    highest_processed_frame = Column(Integer)
    progress_complete = Column(Boolean, default=False)

    # Geometry
    pixel_width = Column(Float)
    block_height = Column(Integer)
    block_width = Column(Integer)

    # Crypto
    scrypt_n = Column(Integer)
    scrypt_r = Column(Integer)
    scrypt_p = Column(Integer)
    decryption_key = Column(String)
    metadata_is_decrypted = Column(Boolean, default=False)

    # Relationships
    frames = relationship('StreamFrame', back_populates='stream', cascade='all, delete', passive_deletes=True,
                          lazy='dynamic')
    files = relationship('StreamFile', back_populates='stream', cascade='all, delete', passive_deletes=True,
                         lazy='dynamic')
    progress = relationship('StreamDataProgress', back_populates='stream', cascade='all, delete', passive_deletes=True,
                            lazy='dynamic')

    def __str__(self):
        if self.stream_name:
            return f'{self.stream_name} | {self.stream_sha256}'
        else:
            return self.stream_sha256

    def _refresh_save_directory(self):
        save_directory = Path(self.output_directory)
        if not save_directory.exists():
            logging.debug('Directory for read doesn\'t exist, creating...')
            save_directory.mkdir()


    def return_state(self, advanced=False):
        palette_name = None
        if self.custom_palette_loaded and self.custom_palette_used or not self.custom_palette_used:
            palette = Palette.query.filter(Palette.palette_id == self.stream_palette_id)
            palette_name = palette.name
        basic_state = {'time_started': self.time_started, 'bg_version': self.bg_version, 'protocol_version':
                       self.protocol_version, 'stream_sha256': self.stream_sha256, 'stream_is_video':
                       self.stream_is_video, 'stream_palette_id': self.stream_palette_id, 'palette_name': palette_name,
                       'custom_palette_used': self.custom_palette_used, 'total_frames': self.total_frames,
                       'compression_enabled': self.compression_enabled, 'encryption_enabled': self.encryption_enabled,
                       'file_masking_enabled': self.file_masking_enabled, 'stream_name': self.stream_name,
                       'stream_description': self.stream_description, 'time_created': self.time_created,
                       'size_in_bytes': self.size_in_bytes, 'output_directory': self.output_directory, 'pixel_width':
                       self.pixel_width, 'block_height': self.block_height, 'block_width': self.block_width,
                       'scrypt_n': self.scrypt_n, 'scrypt_r': self.scrypt_r, 'scrypt_p': self.scrypt_p,
                       'decryption_key': self.decryption_key, 'metadata_is_decrypted': self.metadata_is_decrypted}
        advanced_state = {}  # everything else # todo
        return basic_state | advanced_state if advanced else basic_state

    def return_pending_header_bits(self):
        header_bytes = self.carry_over_header_bytes
        header_bits = BitStream(header_bytes)
        trimmed_bits = header_bits.read(header_bits.len - self.carry_over_padding_bits)
        return trimmed_bits

    def session_activity(self, state: bool, save=True):
        self.active_this_session = state
        if save:
            self.save()

    def toggle_eligibility_calculations(self, state: bool, save=True):
        self.recalculate_eligibility = state
        if save:
            self.save()

    def _calculate_payload_bits_per_frame(self, stream_palette_bit_length):
        FRAME_HEADER_LENGTH_BITS = 352
        self.payload_bits_per_standard_frame = ((self.block_width - int(not self.stream_is_video)) *
                                                (self.block_height - int(not self.stream_is_video))) \
                                               * stream_palette_bit_length - FRAME_HEADER_LENGTH_BITS

    def stream_palette_load(self, stream_palette):
        self.stream_palette_id = stream_palette.palette_id
        self.custom_palette_used = stream_palette.is_custom
        self.custom_palette_loaded = True
        self._calculate_payload_bits_per_frame(stream_palette.bit_length)
        self.save()

    def stream_header_load(self, size_in_bytes, total_frames, compression_enabled, encryption_enabled,
                           file_masking_enabled, metadata_header_length, metadata_header_hash,
                           custom_palette_header_length, custom_palette_header_hash):
        logging.debug('Stream read- stream header load')
        self.size_in_bytes = size_in_bytes
        self.total_frames = total_frames
        self.compression_enabled = compression_enabled
        self.encryption_enabled = encryption_enabled
        self.file_masking_enabled = file_masking_enabled
        if not encryption_enabled or encryption_enabled and not file_masking_enabled:
            self.metadata_is_decrypted = True
        self.metadata_header_size_bytes = metadata_header_length
        self.metadata_header_sha256 = metadata_header_hash
        self.palette_header_size_bytes = custom_palette_header_length
        if not custom_palette_header_length:
            self.palette_header_complete = True
        self.palette_header_hash = custom_palette_header_hash
        self.stream_header_complete = True

        if not encryption_enabled:  # Purging password in DB if not needed
            self.decryption_key = None
        self.save()

    def metadata_header_load(self, bg_version, stream_name, stream_description, time_created, manifest_string):
        logging.debug('Stream read- metadata header load')
        self.metadata_is_decrypted = True
        self.bg_version = bg_version
        self.stream_name = stream_name
        self.stream_description = stream_description
        self.time_created = time_created
        self.manifest_string = manifest_string
        self.metadata_header_complete = True

        # Set output directory
        new_output_directory = Path(self.output_directory)
        new_output_directory = new_output_directory / stream_name
        self.output_directory = str(new_output_directory)

        # Manifest process
        manifest_dict = json.loads(manifest_string)
        manifest_unpack(manifest_dict, self.id, new_output_directory)
        self.total_files = self.files.count()

        # Purging encrypted header bytes and decryption key from DB (if applicable)
        self.encrypted_metadata_header_bytes = None
        self.decryption_key = None

        self.save()

    def metadata_checkpoint_return(self):
        """If stop_at_metadata_load is enabled at read() and this hasn't ran previously, this returns a dictionary of
        all stream header and metadata attributes, as well as stream header data if its a learned palette.
        """

        self.metadata_checkpoint_ran = True
        self.save()
        palette_name = None
        if self.custom_palette_loaded and self.custom_palette_used or not self.custom_palette_used:
            palette = Palette.query.filter(Palette.palette_id == self.stream_palette_id).first()
            palette_name = palette.name
        manifest_decrypt_success = True if self.manifest_string else False
        returned_dict = {'stream_name': self.stream_name, 'stream_sha256': self.stream_sha256, 'bg_version':
                        self.bg_version, 'stream_description': self.stream_description, 'time_created':
                        self.time_created, 'manifest': None, 'size_in_bytes': self.size_in_bytes, 'total_frames':
                        self.total_frames, 'compression_enabled': self.compression_enabled, 'encryption_enabled':
                        self.encryption_enabled, 'file_masking_enabled': self.file_masking_enabled, 'protocol_version':
                        self.protocol_version, 'block_width': self.block_width, 'block_height': self.block_height,
                        'manifest_decrypt_success': manifest_decrypt_success, 'stream_palette_id':
                        self.stream_palette_id, 'palette_name': palette_name}
        return returned_dict

    def accept_encrypted_metadata_bytes(self, encrypted_metadata_bytes):
        """If file masking is enabled on the stream and incorrect decryption values are used, this adds the encrypted
        header to the database until it is decrypted"""
        self.encrypted_metadata_header_bytes = encrypted_metadata_bytes
        self.save()

    def new_setup_frame(self, frame_number):
        if frame_number == self.highest_consecutive_setup_frame_read + 1:
            self.highest_consecutive_setup_frame_read += 1
            self.save()

    def completed_frame_count_update(self):
        self.completed_frames = self.frames.filter(StreamFrame.is_complete == True).count()
        if self.completed_frames == self.total_frames:
            logging.info(f'All {self.total_frames} frame(s) have been decoded and are accounted for in stream'
                         f' {self.stream_name}')
            self.all_frames_accounted_for = True
        self.save()

    def check_file_eligibility(self):
        """Assesses and flags what files can be unpackaged through calculating the decoded bit indexes from finalized
        frames.
        """

        # Metadata header itself hasn't been read from frames yet
        if not self.metadata_header_complete and not self.manifest_string:
            logging.info('Cannot unpackage, metadata header has not been read from frames yet.')
            return {'failure': 'Metadata not read from frames yet.'}

        # Header has been decoded but not decrypted
        if not self.metadata_is_decrypted and self.file_masking_enabled:
            logging.info('Cannot unpackage, correct decryption key has\'nt been provided.')
            return {'failure': 'Metadata '}

        if not self.recalculate_eligibility:
            return {}

        # Progress calculate
        self.highest_processed_frame = session.query(func.max(StreamFrame.frame_number)) \
            .filter(StreamFrame.stream_id == self.id).one()[0]

        # Bypass these calculations
        if self.all_frames_accounted_for:
            if not self.progress_complete:
                self.progress.delete()
                self.frames.update({StreamFrame.added_to_progress: True})
                StreamDataProgress.create(self.id, 0, (self.size_in_bytes * 8) - 1)
                self.progress_complete = True

        # Incomplete stream, calculating progress
        else:
            for index_range in range(math.ceil(self.highest_processed_frame / 100)):
                frame_group = StreamFrame.query.filter(StreamFrame.frame_number < (index_range + 1) * 100) \
                    .filter(StreamFrame.frame_number >= index_range * 100).filter(StreamFrame.stream_id == self.id)\
                    .filter(StreamFrame.added_to_progress == False).all()
                for frame in frame_group:
                    bit_start, bit_end = frame.get_bit_index(self.payload_start_frame, self.payload_first_frame_bits,
                                                             self.payload_bits_per_standard_frame)
                    StreamDataProgress.create(self.id, bit_start, bit_end)
                    frame.progress_calculated()

        # What files are eligible to be unpackaged that 'fit' inside of the finished data
        if self.all_frames_accounted_for:
            self.files.filter(StreamFile.is_eligible == False) \
                .update({StreamFile.is_eligible: True})
        else:
            for progress_cluster in self.progress:
                self.files.filter(StreamFile.is_eligible == False)\
                    .filter(StreamFile.is_processed == False) \
                    .filter(StreamFile.start_bit_position >= progress_cluster.bit_start_position) \
                    .filter(StreamFile.end_bit_position <= progress_cluster.bit_end_position) \
                    .update({StreamFile.is_eligible: True})

        self.toggle_eligibility_calculations(False)
        return {}

    def attempt_unpackage(self):
        """Attempts to extract files from the partial or complete decoded data.  Returns a dictionary object giving a
        summary of the results.
        """
        logging.info(f'Unpackaging {str(self)}...')

        #metadata header/manifest logic here (unpackage -> check first)
        # return {'failure': }

        elibility_results = self.check_file_eligibility()
        if 'failure' in elibility_results:
            return elibility_results

        self._refresh_save_directory()

        # File extract
        pending_extraction = self.files.filter(StreamFile.is_eligible == True).filter(StreamFile.is_processed == False)

        returned_list = []
        for file in pending_extraction:
            extract_results = file.extract(self.payload_start_frame, self.payload_first_frame_bits,
                                           self.payload_bits_per_standard_frame, self.total_frames, self.size_in_bytes)
            returned_list.append(extract_results)
            if extract_results['results'] == 'Cannot decrypt':
                logging.warning('Incorrect decryption values provided for stream.  Please change values and try again.'
                                '  Aborting...')
                break

        # Is stream complete?
        self.completed_files = self.files.filter(StreamFile.is_processed == True).count()
        if self.completed_files == self.total_files:
            self.is_complete = True
        self.save()

        return returned_list

    def autodelete_attempt(self):
        if self.auto_delete_finished_stream and self.is_complete:
            self.delete()

    def set_payload_start_data(self, payload_start_frame, payload_first_frame_bits):
        self.payload_start_frame = payload_start_frame
        self.payload_first_frame_bits = payload_first_frame_bits
        self.save()


SQLBaseClass.metadata.create_all(engine)
