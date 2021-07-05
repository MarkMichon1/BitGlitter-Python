from bitglitter.config.config import engine, SqlBaseClass

class StreamRead(SqlBaseClass):
    __tablename__ = 'stream_reads'
    __abstract__ = False

    pixel_width = 0
    block_height = 0
    block_width = 0

    def _delete_data_folder(self):
        pass

    def _delete_stream(self):
        pass

SqlBaseClass.metadata.create_all(engine)