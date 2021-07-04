from bitglitter.config.config import engine, SqlBaseClass

class StreamRead(SqlBaseClass):
    # Frame data
    pixel_width = 0
    block_height = 0
    block_width = 0

SqlBaseClass.metadata.create_all(engine)