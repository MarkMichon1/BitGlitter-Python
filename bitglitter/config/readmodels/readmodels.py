from bitstring import BitStream
from sqlalchemy import BLOB, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from bitglitter.config.config import session, SQLBaseClass


class StreamFrame(SQLBaseClass):
    __tablename__ = 'stream_frames'
    __abstract__ = False

    # note- sha256 not included as its only verification prior to addition
    stream_id = Column(Integer, ForeignKey('stream_reads.id'))
    stream = relationship('StreamRead', back_populates='frames')
    payload_bits = Column(Integer)  # Length of stream payload bits within this frame, tracked to ensure padding removed
    payload = Column(BLOB)
    frame_number = Column(Integer)
    is_complete = Column(Boolean, default=False)
    added_to_progress = Column(Boolean, default=False)


    def get_bit_index(self, payload_start_frame, payload_first_frame_bits, payload_bits_per_standard_frame):
        """Returns the start and ending index positions of the greater stream payload, used when calculating progress
        to tell what specific data is inside of a given frame.
        """
        bit_start = 0
        bit_end = 0

        return bit_start, bit_end

    def progress_calculated(self):
        """Was used with StreamDataProgress to calculate progress, and doesn't have to be used again."""
        self.added_to_progress = True
        self.save()

    def return_partial_frame_payload(self):
        pass

    def return_full_frame_payload(self):
        return BitStream(self.payload).read(self.payload_bits)

    def finalize_frame(self, payload_bits=None):
        if payload_bits:
            self.payload_bits = payload_bits.len
            self.payload = payload_bits.tobytes()
        else:
            self.added_to_progress = True  # Removing empty frames from upcoming calculation
        self.is_complete = True
        self.save()

    def __str__(self):
        return f'Frame {self.frame_number}/{self.stream.total_frames} for {self.stream}'


class StreamFile(SQLBaseClass):
    __tablename__ = 'stream_files'
    __abstract__ = False

    stream_id = Column(Integer, ForeignKey('stream_reads.id'))
    stream = relationship('StreamRead')
    sequence = Column(Integer)
    start_bit_position = Column(Integer)
    end_bit_position = Column(Integer)
    is_processed = Column(Boolean, default=False)
    is_eligible = Column(Boolean, default=False) # Eligible to be processed
    save_path = Column(String)

    name = Column(String)
    raw_file_size_bytes = Column(Integer)
    raw_file_hash = Column(String)
    processed_file_size_bytes = Column(Integer)
    processed_file_hash = Column(String)

    def extract(self):
        # assess existing files (from previous sessions)
        pass

    def __str__(self):
        return f'File {self.name} in {self.stream}'


class StreamDataProgress(SQLBaseClass):
    """Aside from tracking progress of frames, we also need to account for what index slices of the overall payload we
    have saved/processed.  This is because files can be extracted from incomplete streams; this is the mechanism to
    track and calculate that, by seeing if file start:end falls within the current coverage.
    """

    __tablename__ = 'stream_data_progress'
    __abstract__ = False

    stream_id = Column(Integer, ForeignKey('stream_reads.id'))
    stream = relationship('StreamRead', back_populates='progress')
    bit_start_position = Column(Integer)
    bit_end_position = Column(Integer)

    def __str__(self):
        return f'Progress slice for {self.stream.stream_name} - bit pos [{self.bit_start_position}:' \
               f'{self.bit_end_position}]'

    @classmethod
    def create(cls, stream_id, bit_start_position, bit_end_position, **kwargs):
        """Before an object is created, checking to see if an adjacent payload frame has already been read.  Rather than
        making a new object, the old instance will 'pool' the new edges together.
        """
        identical_progress = session.query(StreamDataProgress).filter(StreamDataProgress.stream_id == stream_id) \
            .filter(StreamDataProgress.bit_end_position == bit_end_position) \
            .filter(StreamDataProgress.bit_start_position == bit_start_position).first()
        if identical_progress:
            return

        previous_progress = session.query(StreamDataProgress).filter(StreamDataProgress.stream_id == stream_id) \
            .filter(StreamDataProgress.bit_end_position == bit_start_position - 1).first()
        if previous_progress:
            previous_progress.bit_end_position = bit_end_position
            previous_progress.save()

        next_progress = session.query(StreamDataProgress).filter(StreamDataProgress.stream_id == stream_id) \
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


class StreamSHA256Blacklist(SQLBaseClass):
    """When metadata is loaded and you """
    __tablename__ = 'stream_sha256_blacklists'
    __abstract__ = False

    stream_sha256 = Column(String, unique=True)

    def __str__(self):
        return self.stream_sha256
