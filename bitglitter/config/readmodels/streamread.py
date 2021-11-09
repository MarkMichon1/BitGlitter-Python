#  This model has its own module because of its large size

from bitstring import BitStream
from sqlalchemy import BLOB, Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

import json
import logging
from pathlib import Path
import time

from bitglitter.config.config import engine, SQLBaseClass


class StreamRead(SQLBaseClass):
    """This serves as the central data container and API for interacting with saved read data."""

    __tablename__ = 'stream_reads'
    __abstract__ = False

    # Core
    time_started = Column(Integer, default=time.time)
    bg_version = Column(String)
    protocol_version = Column(Integer)
    stream_sha256 = Column(String, unique=True, nullable=False)
    stream_is_video = Column(Boolean, nullable=False)
    stream_palette_id = Column(String)
    custom_palette_used = Column(Boolean)
    custom_palette_loaded = Column(Boolean)
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
    metadata_header_hash = Column(String)
    stream_header_complete = Column(Boolean, default=False)
    metadata_header_complete = Column(Boolean, default=False)
    palette_header_complete = Column(Boolean, default=False)
    completed_frames = Column(Integer, default=0)
    highest_consecutive_setup_frame_read = Column(Integer, default=0)  # Important for initial metadata grab
    metadata_header_bytes = Column(BLOB)  # Used when file masking and incorrect key.  Flushed when correct.

    # Operation State
    active_this_session = Column(Boolean, default=True)
    is_complete = Column(Boolean, default=False)

    # Unpackage State
    auto_delete_finished_stream = Column(Boolean)
    auto_unpackage_stream = Column(Boolean)
    stop_at_metadata_load = Column(Boolean)
    metadata_checkpoint_ran = Column(default=False)

    # Geometry
    pixel_width = Column(Integer)
    block_height = Column(Integer)
    block_width = Column(Integer)

    # Crypto
    scrypt_n = Column(Integer)
    scrypt_r = Column(Integer)
    scrypt_p = Column(Integer)
    decryption_key = Column(String)

    # Relationships
    frames = relationship('StreamFrame', back_populates='stream', cascade='all, delete', passive_deletes=True)
    files = relationship('StreamFile', back_populates='stream', cascade='all, delete', passive_deletes=True)
    progress = relationship('StreamDataProgress', back_populates='stream', cascade='all, delete', passive_deletes=True)

    def __str__(self):
        if self.stream_name:
            return f'{self.stream_name} | {self.stream_sha256}'
        else:
            return self.stream_sha256

    def return_state(self, advanced=False):  # todo: do at end w/ all state
        basic_state = {}  # metadata
        advanced_state = {}  # everything else
        return basic_state | advanced_state if advanced else basic_state

    def return_pending_header_bits(self):
        header_bytes = self.carry_over_header_bytes
        header_bits = BitStream(header_bytes)
        trimmed_bits = header_bits.read(header_bits.len - self.carry_over_padding_bits)
        return trimmed_bits

    def session_activity(self, bool_set: bool):  # todo for images upon creation
        self.active_this_session = bool_set
        self.save()

    def stream_palette_load(self, stream_palette):
        self.stream_palette_id = stream_palette.palette_id
        self.custom_palette_used = stream_palette.is_custom
        self.save()

    def stream_header_load(self, size_in_bytes, total_frames, compression_enabled, encryption_enabled,
                           file_masking_enabled, metadata_header_length, metadata_header_hash,
                           custom_palette_header_length, custom_palette_header_hash):
        logging.debug('Steam header load')
        self.size_in_bytes = size_in_bytes
        self.total_frames = total_frames
        self.compression_enabled = compression_enabled
        self.encryption_enabled = encryption_enabled
        self.file_masking_enabled = file_masking_enabled
        self.metadata_header_size_bytes = metadata_header_length
        self.metadata_header_hash = metadata_header_hash
        self.palette_header_size_bytes = custom_palette_header_length
        if not custom_palette_header_length:
            self.palette_header_complete = True
        self.palette_header_hash = custom_palette_header_hash
        self.stream_header_complete = True

        if not encryption_enabled:  # Purging password in DB if not needed
            self.decryption_key = None
        self.save()

    def metadata_header_load(self, bg_version, stream_name, stream_description, time_created, manifest_string):
        logging.debug('Metadata header load')
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
        self.save()

        # Manifest process
        manifest_dict = json.loads(manifest_string)
        manifest_unpack(manifest_dict, self.id, new_output_directory)

    def metadata_checkpoint_return(self):
        """If stop_at_metadata_load is enabled at read() and this hasn't ran previously, this returns a dictionary of
        all stream header and metadata attributes, as well as stream header data if its a learned palette.
        """

        # todo- return palette data if not grabbed yet
        self.metadata_checkpoint_ran = True
        self.save()
        returned_dict = {'stream_name': self.stream_name, 'stream_sha256': self.stream_sha256, 'bg_version':
            self.bg_version, 'stream_description': self.stream_description, 'time_created':
                             self.time_created, 'manifest': None, 'size_in_bytes': self.size_in_bytes, 'total_frames':
                             self.total_frames, 'compression_enabled': self.compression_enabled, 'encryption_enabled':
                             self.encryption_enabled, 'file_masking_enabled': self.file_masking_enabled,
                         'protocol_version':
                             self.protocol_version, 'block_width': self.block_width, 'block_height': self.block_height,
                         'manifest_decrypt_success': None, 'stream_palette_id': self.stream_palette_id}  # <- todo
        return returned_dict

    def new_setup_frame(self, frame_number):
        if frame_number == self.highest_consecutive_setup_frame_read + 1:
            self.highest_consecutive_setup_frame_read += 1
            self.save()

    def completed_frame_count_update(self):
        self.completed_frames = self.frames.filter.count()  # todo...
        self.save()

    def attempt_unpackage(self):
        """Attempts to extract files from the partial or complete decoded data.  Returns a dictionary object giving a
        summary of the results.
        """

        if self.metadata_header_complete and self.manifest_string:
            pass  # attempt ex

        # blob calculate
        # assess existing files (from previous sessions)
        # mark stream AS COMPLETE if so...

        return {}

    def autodelete_attempt(self):
        if self.auto_delete_finished_stream and self.is_complete:
            self.delete()

    def update_config(self):
        pass  # todo rename


# v These need to be at bottom to resolve import/DB relationship issues.  It works but perhaps a better way exists.
import bitglitter.config.readmodels.readmodels
from bitglitter.read.decode.manifest import manifest_unpack

SQLBaseClass.metadata.create_all(engine)
