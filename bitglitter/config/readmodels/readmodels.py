from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from bitglitter.config.config import engine, session, SqlBaseClass


class StreamFrame(SqlBaseClass):
    __tablename__ = 'stream_frames'
    __abstract__ = False

    #note- sha256 not included as its only verification prior to addition

    stream_id = Column(Integer, ForeignKey('stream_reads.id'))
    stream = relationship('StreamRead', back_populates='frames')
    payload_bits = Column(Integer) #  Length of payload bits within this frame, tracked to ensure padding removed
    frame_number = Column(Integer)

    is_scanned = Column(Boolean, default=False)


class StreamFile(SqlBaseClass):
    __tablename__ = 'stream_files'
    __abstract__ = False

    stream_id = Column(Integer, ForeignKey('stream_reads.id'))
    stream = relationship('StreamRead')
    payload_bit_start_position = Column(Integer)
    payload_bit_end_position = Column(Integer)
    parent_directory_id = Column(Integer, ForeignKey('stream_directories.id'))
    parent_directory = relationship('StreamDirectory', back_populates='files')

    name = Column(String)
    raw_file_size = Column(Integer)
    raw_file_hash = Column(String)
    processed_file_size = Column(Integer)
    processed_file_hash = Column(String) # only if compression or crypto


class StreamDirectory(SqlBaseClass):
    __tablename__ = 'stream_directories'
    __abstract__ = False


    stream_id = Column(Integer, ForeignKey('stream_reads.id'))
    stream = relationship('StreamRead', back_populates = 'directories')
    parent_directory_id = Column(Integer, ForeignKey('stream_directories.id'))
    parent_directory = relationship('StreamDirectory')
    name = Column(String)
    files = relationship('StreamFile', back_populates='parent_directory', cascade='all, delete', passive_deletes=True)

    # def delete(self):
    #     super() todo- both for recursive


class StreamDataProgress(SqlBaseClass):
    """Aside from tracking progress of frames, we also need to account for what index slices of the overall payload we
    have saved/processed.  This is because files can be extracted from incomplete streams; this is the mechanism to
    track and calculate that, by seeing if file start:end falls within the current coverage.
    """

    __tablename__ = 'stream_data_progress'
    __abstract__ = False

    @classmethod
    def create(cls, stream_sha256, stream_id, bit_start_position, bit_end_position, **kwargs):
        """Before an object is created, checking to see if an adjacent payload frame has already been read.  Rather than
        making a new object, the old instance will 'pool' the new edges together.
        """
        previous_progress = session.query(StreamDataProgress).filter(StreamDataProgress.stream_id == stream_id)\
            .filter(StreamDataProgress.bit_end_position == bit_start_position - 1).first()
        if previous_progress:
            previous_progress.bit_end_position = bit_end_position
            previous_progress.save()

        next_progress = session.query(StreamDataProgress).filter(StreamDataProgress.stream_id == stream_id)\
            .filter(StreamDataProgress.bit_start_position == bit_end_position + 1).first()
        if next_progress:
            if previous_progress:
                previous_progress.bit_end_position = next_progress.bit_end_position
                previous_progress.save()
                next_progress.delete()
            else:
                next_progress.bit_start_position = bit_start_position
                next_progress.save()

        if previous_progress or next_progress:
            return

        # Repopulating kwargs to send them off to super() for creation
        kwargs['stream_id'] = stream_id
        kwargs['bit_start_position'] = bit_start_position
        kwargs['bit_end_position'] = bit_end_position
        super().create(**kwargs)



    stream_id = Column(Integer, ForeignKey('stream_reads.id'))
    stream = relationship('StreamRead', back_populates='progress')
    bit_start_position = Column(Integer)
    bit_end_position = Column(Integer)


SqlBaseClass.metadata.create_all(engine)