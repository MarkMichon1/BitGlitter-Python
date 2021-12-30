from sqlalchemy import Boolean, Column, DateTime, Integer, String

from datetime import datetime

from bitglitter.config.config import engine, SQLBaseClass


class Preset(SQLBaseClass):
    __tablename__ = 'presets'
    __abstract__ = False

    nickname = Column(String, unique=True, nullable=False)
    datetime_created = Column(DateTime, default=datetime.now)
    output_mode = Column(String, nullable=False)
    compression_enabled = Column(Boolean, nullable=False)
    scrypt_n = Column(Integer, nullable=False)
    scrypt_r = Column(Integer, nullable=False)
    scrypt_p = Column(Integer, nullable=False)
    cpu_cores = Column(Integer, nullable=False)

    stream_palette_id = Column(String, nullable=False)
    pixel_width = Column(Integer, nullable=False)
    block_height = Column(Integer, nullable=False)
    block_width = Column(Integer, nullable=False)
    frames_per_second = Column(Integer, nullable=False)


SQLBaseClass.metadata.create_all(engine)
