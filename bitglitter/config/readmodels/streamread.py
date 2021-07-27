#  This class has its own module because of its large size

from sqlalchemy import Boolean, Column, Integer, String
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
    stream_sha256 = Column(String, unique=True, nullable=False) #req
    stream_is_video = Column(Boolean, nullable=False) #req
    stream_palette = None #todo
    stream_palette_id = None #todo
    custom_palette_used = Column(Boolean)
    number_of_frames = Column(Integer)
    compression_enabled = Column(Boolean)
    encryption_enabled = Column(Boolean)
    file_mask_enabled = Column(Boolean)
    manifest = Column(String) #temporary todo

    # Read State
    payload_offset_bits = Column(Integer) # todo revisit, may need more variables for tracking state
    metadata_headers_ran = Column(Boolean)
    completed_frames = Column(Integer, default=0)

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