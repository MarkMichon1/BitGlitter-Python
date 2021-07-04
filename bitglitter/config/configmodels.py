from sqlalchemy import Boolean, Column, Integer, String

from multiprocessing import cpu_count
from pathlib import Path

from bitglitter.config.config import engine, SqlBaseClass


class Config(SqlBaseClass):
    __abstract__ = False
    __tablename__ = 'config'
    decoded_files_output_path = Column(String, default=str(Path(__file__).resolve().parent.parent / 'Decoded Files'))
    read_bad_frame_strikes = Column(Integer, default=10)
    write_path = Column(String, default=str(Path(__file__).resolve().parent.parent / 'Render Output'))
    log_txt_path = Column(String, default=str(Path(__file__).resolve().parent.parent / 'Logs'))
    log_output = Column(Boolean, default=False)
    maximum_cpu_cores = Column(Integer, default=cpu_count())
    save_statistics = Column(Boolean, default=True)


class Constants(SqlBaseClass):
    __abstract__ = False
    __tablename__ = 'constants'
    BG_VERSION = Column(String, default='2.0', nullable=False)
    PROTOCOL_VERSION = Column(Integer, default=1, nullable=False)
    SUPPORTED_PROTOCOLS = Column(String, default='1', nullable=False)
    WRITE_WORKING_DIR = Column(String, default=str(Path(__file__).resolve().parent.parent / 'Temp'), nullable=False)
    DEFAULT_OUTPUT_PATH = Column(String, default=str(Path(__file__).resolve().parent.parent / 'Render Output'),
                                 nullable=False)
    DEFAULT_PARTIAL_SAVE_DATA_PATH = Column(String, default=str(Path(__file__).resolve().parent.parent /
                                                                'Partial Stream Data'), nullable=False)
    VALID_VIDEO_FORMATS = Column(String, default='.avi|.flv|.mov|.mp4|.wmv', nullable=False)
    VALID_IMAGE_FORMATS = Column(String, default='.bmp|.jpg|.png', nullable=False)

    def return_supported_protocols(self):
        return self.SUPPORTED_PROTOCOLS.split('|')

    def return_valid_video_formats(self):
        return self.VALID_VIDEO_FORMATS.split('|')

    def return_valid_image_formats(self):
        return self.VALID_IMAGE_FORMATS.split('|')


class Statistics(SqlBaseClass):
    __abstract__ = False
    __tablename__ = 'statistics'
    blocks_wrote = Column(Integer, default=0)
    frames_wrote = Column(Integer, default=0)
    data_wrote = Column(Integer, default=0)
    blocks_read = Column(Integer, default=0)
    frames_read = Column(Integer, default=0)
    data_read = Column(Integer, default=0)

    def write_update(self, blocks, frames, data):
        self.blocks_wrote += blocks
        self.frames_wrote += frames
        self.data_wrote += data
        self.save()

    def read_update(self, blocks, frames, data):
        self.blocks_read += blocks
        self.frames_read += frames
        self.data_read += data
        self.save()

    def return_stats(self):
        return {
            'blocks_wrote': self.blocks_wrote, 'frames_wrote': self.frames_wrote, 'data_wrote': self.data_wrote,
            'blocks_read': self.blocks_read, 'frames_read': self.frames_read, 'data_read': self.data_read,
        }

    def clear_stats(self):
        self.blocks_wrote = 0
        self.frames_wrote = 0
        self.data_wrote = 0
        self.blocks_read = 0
        self.frames_read = 0
        self.data_read = 0
        self.save()


SqlBaseClass.metadata.create_all(engine)
