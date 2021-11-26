from sqlalchemy import Boolean, Column, Integer, String

from multiprocessing import cpu_count
from pathlib import Path

from bitglitter.config.config import engine, session, SQLBaseClass


class Config(SQLBaseClass):
    __abstract__ = False
    __tablename__ = 'config'
    read_path = Column(String, default=str(Path(__file__).resolve().parent.parent / 'Read Output'))
    read_bad_frame_strikes = Column(Integer, default=10)
    enable_bad_frame_strikes = Column(Boolean, default=True)
    write_path = Column(String, default=str(Path(__file__).resolve().parent.parent / 'Write Output'))
    log_txt_dir = Column(String, default=str(Path(__file__).resolve().parent.parent / 'Logs'))
    log_output = Column(Boolean, default=False)
    logging_level = Column(Integer, default=1)
    maximum_cpu_cores = Column(Integer, default=cpu_count())
    MAX_SUPPORTED_CPU_CORES = Column(Integer, default=cpu_count())
    save_statistics = Column(Boolean, default=True)
    output_stream_title = Column(Boolean, default=True)  # App version


class Constants(SQLBaseClass):
    __abstract__ = False
    __tablename__ = 'constants'
    BG_VERSION = Column(String, default='2.0', nullable=False)  # Change as needed
    PROTOCOL_VERSION = Column(Integer, default=1, nullable=False)
    SUPPORTED_PROTOCOLS = Column(String, default='1', nullable=False)

    WORKING_DIR = Column(String, default=str(Path(__file__).resolve().parent.parent / 'Temp'), nullable=False)
    DEFAULT_WRITE_DIR = Column(String, default=str(Path(__file__).resolve().parent.parent / 'Write Output'),
                               nullable=False)
    DEFAULT_READ_DIR = Column(String, default=str(Path(__file__).resolve().parent.parent / 'Read Output'),
                              nullable=False)

    VALID_VIDEO_FORMATS = Column(String, default='.avi|.flv|.mov|.mp4|.wmv', nullable=False)
    VALID_IMAGE_FORMATS = Column(String, default='.bmp|.jpg|.jpeg|.png|.webp', nullable=False)

    def return_supported_protocols(self):
        return self.SUPPORTED_PROTOCOLS.split('|')

    def return_valid_video_formats(self):
        return self.VALID_VIDEO_FORMATS.split('|')

    def return_valid_image_formats(self, glob_format=False):
        if not glob_format:
            return self.VALID_IMAGE_FORMATS.split('|')
        else:
            format_list = self.VALID_IMAGE_FORMATS.split('|')
            return [item.replace('.', '*.') for item in format_list]


class Statistics(SQLBaseClass):
    __abstract__ = False
    __tablename__ = 'statistics'
    blocks_wrote = Column(Integer, default=0)
    frames_wrote = Column(Integer, default=0)
    data_wrote_bits = Column(Integer, default=0)
    blocks_read = Column(Integer, default=0)
    frames_read = Column(Integer, default=0)
    data_read_bits = Column(Integer, default=0)

    def write_update(self, blocks, frames, data):
        self.blocks_wrote += blocks
        self.frames_wrote += frames
        self.data_wrote_bits += data
        self.save()

    def read_update(self, blocks, frames, data):
        self.blocks_read += blocks
        self.frames_read += frames
        self.data_read_bits += data
        self.save()

    def return_stats(self):
        return {
            'blocks_wrote': round(self.data_wrote_bits / 8), 'frames_wrote': self.frames_wrote, 'data_wrote':
                self.data_wrote_bits, 'blocks_read': self.blocks_read, 'frames_read': self.frames_read, 'data_read':
                round(self.data_read_bits),
        }

    def clear_stats(self):
        self.blocks_wrote = 0
        self.frames_wrote = 0
        self.data_wrote_bits = 0
        self.blocks_read = 0
        self.frames_read = 0
        self.data_read_bits = 0
        self.save()


class CurrentJobState(SQLBaseClass):
    """Lightweight singleton object that is queried for every frame read or written when ran with Electron app, to
    indicate if the current job has been cancelled.  This runs at the beginning of each frame.
    """

    __abstract__ = False
    __tablename__ = 'current_job_state'

    active_stream_sha256 = Column(String)
    is_cancelled = Column(Boolean, default=False)

    @classmethod
    def new_task(cls, stream_sha256):
        singleton = session.query(CurrentJobState).first()
        singleton.is_cancelled = False
        singleton.active_stream_sha256 = stream_sha256
        singleton.save()

    @classmethod
    def check_state(cls):
        singleton = session.query(CurrentJobState).first()
        return singleton.active_stream_sha256, singleton.is_cancelled

    @classmethod
    def cancel(cls):
        singleton = session.query(CurrentJobState).first()
        singleton.is_cancelled = True
        singleton.save()

    @classmethod
    def end_task(cls):
        singleton = session.query(CurrentJobState).first()
        singleton.active_stream_sha256 = None
        singleton.is_cancelled = False
        singleton.save()


SQLBaseClass.metadata.create_all(engine)
