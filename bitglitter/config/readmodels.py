from bitglitter.config.config import engine, SqlBaseClass


class StreamRead(SqlBaseClass): #todo- merge old v1.x class with these models
    __tablename__ = 'stream_reads'
    __abstract__ = False

    # Core
    stream_sha = None
    stream_palette_id = None
    number_of_frames = None
    compression_enabled = None
    encryption_enabled = None

    # Geometry
    pixel_width = 0
    block_height = 0
    block_width = 0

    # Crypto
    scrypt_n = 0
    scrypt_r = 0
    scrypt_p = 0

    def _delete_data_folder(self):
        pass

    def _delete_stream(self):
        pass


class StreamFrame(SqlBaseClass):
    __tablename__ = 'stream_frames'
    __abstract__ = False

    stream = None
    frame_number = None

    is_scanned = False


class FileMap(SqlBaseClass):
    __tablename__ = 'file_maps'
    __abstract__ = False


SqlBaseClass.metadata.create_all(engine)
