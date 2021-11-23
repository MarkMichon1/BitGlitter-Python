from bitstring import BitStream
from sqlalchemy import BLOB, Boolean, Column, ForeignKey, Integer, String

import logging
import math
import os
from pathlib import Path

from bitglitter.config.config import session, SQLBaseClass
from bitglitter.utilities.compression import decompress_file
from bitglitter.utilities.cryptography import decrypt_file, get_hash_from_file
from bitglitter.utilities.filemanipulation import refresh_directory


class StreamFrame(SQLBaseClass):
    __tablename__ = 'stream_frames'
    __abstract__ = False

    # note- sha256 not included as its only verification prior to addition
    stream_id = Column(Integer, ForeignKey('stream_reads.id', ondelete='CASCADE'))
    payload_bits = Column(Integer)  # Length of stream payload bits within this frame, tracked to ensure padding removed
    payload = Column(BLOB)
    frame_number = Column(Integer)
    is_complete = Column(Boolean, default=False)
    added_to_progress = Column(Boolean, default=False)

    def get_bit_index(self, payload_start_frame, payload_first_frame_bits, payload_bits_per_standard_frame,
                      total_frames, payload_size_in_bytes):
        """Returns the start and ending index positions of the greater stream payload, used when calculating progress
        to tell what specific data is inside of a given frame.
        """

        if self.frame_number == payload_start_frame:
            return 0, payload_first_frame_bits - 1
        elif self.frame_number == total_frames:
            padding = self.payload_bits - ((payload_size_in_bytes * 8) - (payload_bits_per_standard_frame *
                                          (total_frames - (payload_start_frame + 1))) - payload_first_frame_bits)
            bit_start = (payload_size_in_bytes * 8) - (self.payload_bits + 1)
            return bit_start, bit_start + (self.payload_bits - padding)
        else:
            bit_start = (payload_bits_per_standard_frame * (self.frame_number - payload_start_frame + 1)) + \
                        payload_first_frame_bits
            return bit_start, bit_start + self.payload_bits

    def progress_calculated(self):
        """Was used with StreamDataProgress to calculate progress, and doesn't have to be used again."""
        self.added_to_progress = True
        self.save()

    def return_partial_frame_payload(self, local_start_position, local_end_position=None):
        bits = BitStream(self.payload).read(self.payload_bits)
        bits.pos = local_start_position
        if local_end_position:
            return bits.read(local_end_position - local_start_position + 1)
        else:
            return bits.read(bits.len - local_start_position)

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

    stream_id = Column(Integer, ForeignKey('stream_reads.id', ondelete='CASCADE'))
    sequence = Column(Integer)
    start_bit_position = Column(Integer)
    end_bit_position = Column(Integer)
    is_processed = Column(Boolean, default=False)  # Successfully unpackaged into raw file
    is_eligible = Column(Boolean, default=False)  # Eligible to be processed
    save_path = Column(String)

    raw_file_size_bytes = Column(Integer)
    raw_file_hash = Column(String)
    processed_file_size_bytes = Column(Integer)
    processed_file_hash = Column(String)

    def __str__(self):
        return f'File {self.name} in {self.stream}'

    def _get_frame_indexes(self, payload_start_frame, payload_first_frame_bits, payload_bits_per_standard_frame):
        """Get start and end frames for a given file, as well as each frame's local index positions"""

        calculated_size = self.processed_file_size_bytes if self.processed_file_size_bytes else self.raw_file_size_bytes
        calculated_size *= 8

        # Finding first frame position
        if self.start_bit_position < payload_first_frame_bits:  # Starts on first payload frame
            first_file_frame = payload_start_frame
            first_file_frame_start_position = self.start_bit_position
            total_frame_bits = payload_first_frame_bits
            logging.info('AAA')
        else:  # File starts on frame beyond the first frame containing a payload
            logging.info('BBB')
            bits_until_frame = self.start_bit_position - payload_first_frame_bits
            first_file_frame = payload_start_frame + math.ceil(bits_until_frame / payload_bits_per_standard_frame)
            frame_start_index = payload_first_frame_bits + ((first_file_frame - payload_start_frame - 1)
                                                            * payload_bits_per_standard_frame)
            first_file_frame_start_position = self.start_bit_position - frame_start_index
            total_frame_bits = payload_bits_per_standard_frame

        # Finding last frame position
        if total_frame_bits - first_file_frame_start_position >= calculated_size:  # File terminates on same frame
            logging.info('CCC')
            last_file_frame = first_file_frame
            last_file_frame_finish_position = first_file_frame_start_position + calculated_size
        else:  # File terminates on subsequent frames
            logging.info('DDD')
            bits_left = calculated_size - (total_frame_bits - first_file_frame_start_position)
            frame_difference = math.ceil(bits_left / payload_bits_per_standard_frame)
            last_file_frame = first_file_frame + frame_difference
            bits_left = bits_left - (payload_bits_per_standard_frame * (frame_difference - 1))
            last_file_frame_finish_position = bits_left - 1

        return {'first_frame': first_file_frame, 'first_frame_index': first_file_frame_start_position, 'last_frame':
            last_file_frame, 'last_frame_index': last_file_frame_finish_position}

    def return_state(self, advanced):
        save_path = Path(self.save_path)
        basic_state = {'name': save_path.name, 'raw_file_size_bytes': self.raw_file_size_bytes, 'raw_file_hash':
                       self.raw_file_hash, 'save_path': self.save_path}
        advanced_state = {'stream_id': self.stream_id, 'sequence': self.sequence, 'start_bit_position':
                          self.start_bit_position, 'end_bit_position': self.end_bit_position, 'is_processed':
                          self.is_processed, 'is_eligible': self.is_eligible, 'processed_file_size_bytes':
                          self.processed_file_size_bytes, 'processed_file_hash': self.processed_file_hash}

        return basic_state | advanced_state if advanced else basic_state

    def _extract_frame_generator(self, first_frame, first_frame_index, last_frame, last_frame_index):

        first_returned_frame = StreamFrame.query.filter(StreamFrame.stream_id == self.stream_id) \
            .filter(StreamFrame.frame_number == first_frame).first()

        # 1 frame
        if first_frame == last_frame:
            yield first_returned_frame.return_partial_frame_payload(first_frame_index, last_frame_index)

        # 2+ frames
        elif last_frame > first_frame:
            # First frame
            yield first_returned_frame.return_partial_frame_payload(first_frame_index)

            # Middle frames
            mid_frame_minimum = first_frame + 1
            mid_frame_maximum = last_frame - 1
            last_consecutive_frame_number = first_returned_frame.frame_number
            # Getting groups of 100 frames
            if last_frame - first_frame > 1:
                for query_group in range(math.ceil((mid_frame_maximum - mid_frame_minimum + 1) / 100)):
                    query_minimum = mid_frame_minimum + (query_group * 100)
                    query_maximum = query_minimum + 99 if query_minimum + 99 <= mid_frame_maximum else mid_frame_maximum
                    frames = StreamFrame.query.filter(StreamFrame.stream_id == self.stream_id) \
                        .filter(StreamFrame.frame_number >= query_minimum) \
                        .filter(StreamFrame.frame_number <= query_maximum) \
                        .order_by(StreamFrame.frame_number.asc())

                    for frame in frames:
                        assert frame.frame_number - 1 == last_consecutive_frame_number
                        last_consecutive_frame_number += 1

                        yield frame.return_full_frame_payload()

            # Last frame
            last_returned_frame = StreamFrame.query.filter(StreamFrame.stream_id == self.stream_id) \
                .filter(StreamFrame.frame_number == last_frame).first()
            yield last_returned_frame.return_partial_frame_payload(0, last_frame_index)

    def extract(self, payload_start_frame, payload_first_frame_bits, payload_bits_per_standard_frame,
                encryption_enabled, compression_enabled, decryption_key, scrypt_n, scrypt_r, scrypt_p,
                temp_save_directory):
        raw_path = Path(self.save_path)
        logging.info(f'Extracting {raw_path.name} ...')
        returned_results = self.return_state(advanced=False)
        refresh_directory(temp_save_directory)  # Temp until a better logic system figured out for file names/temp files

        if os.path.exists(self.save_path):
            calculated_hash = get_hash_from_file(self.save_path)
            if self.raw_file_hash == calculated_hash:
                logging.info(f'File already exists at location with correct SHA-256.  Marking as complete...')
                returned_results['results'] = 'Success- already exists'
                self.is_processed = True
                self.save()
                return returned_results
            else:
                logging.info(f'File with this name already exists at this location: {self.save_path}.  '
                             f'Cannot extract until removed.  Skipping...')
                returned_results['results'] = 'Failure- file exists in path'
                return returned_results

        # Which frame(s) the file resides in as well as their local start and finish bit indexes
        positions = self._get_frame_indexes(payload_start_frame, payload_first_frame_bits,
                                            payload_bits_per_standard_frame)
        logging.debug(positions)
        first_frame = positions['first_frame']
        first_frame_index = positions['first_frame_index']
        last_frame = positions['last_frame']
        last_frame_index = positions['last_frame_index']

        # File assembly
        os.makedirs(raw_path.parent, exist_ok=True)
        assemble_path = raw_path if not self.processed_file_size_bytes else temp_save_directory / 'processing.bin'
        with open(assemble_path, 'wb') as file_writer:
            buffer = BitStream()
            for frame_data in self._extract_frame_generator(first_frame, first_frame_index, last_frame,
                                                            last_frame_index):
                buffer += frame_data
                max_allowable_read = (buffer.len // 8) * 8
                to_write = buffer.read(max_allowable_read).tobytes()
                file_writer.write(to_write)
                buffer = buffer.read(buffer.len - max_allowable_read)

        # Post-assembly integrity check if compression and/or encryption enabled on stream
        if self.processed_file_size_bytes:
            calculated_hash = get_hash_from_file(assemble_path)
            if calculated_hash != self.processed_file_hash or \
                    assemble_path.stat().st_size != self.processed_file_size_bytes:
                logging.warning('Assembly mismatch, aborting...')
                returned_results['results'] = 'Internal assembly error'
                return returned_results

        if encryption_enabled:
            if compression_enabled:  # Decrypt + decompress
                decrypt_path = assemble_path.parent / 'decrypted.bin'
                try:
                    decrypt_file(assemble_path, decrypt_path, decryption_key, scrypt_n, scrypt_r, scrypt_p)
                    decompress_file(decrypt_path, self.save_path)
                    calculated_hash = get_hash_from_file(self.save_path)
                    if calculated_hash != self.raw_file_hash:
                        logging.warning('Post-decryption/decompression SHA-256 failure, aborting...')
                        returned_results['results'] = 'Internal assembly error'
                        return returned_results
                except ValueError:
                    logging.warning('Incorrect decryption values, aborting unpackaging of this stream...')
                    returned_results['results'] = 'Cannot decrypt'
                    return returned_results

            else:  # Decryption only
                try:
                    decrypt_file(assemble_path, self.save_path, decryption_key, scrypt_n, scrypt_r, scrypt_p)
                except ValueError:
                    logging.warning('Incorrect decryption values, aborting unpackaging of this stream...')
                    returned_results['results'] = 'Cannot decrypt'
                    return returned_results

        elif compression_enabled:  # Just decompression
            decompress_file(assemble_path, self.save_path)
            calculated_hash = get_hash_from_file(self.save_path)
            if calculated_hash != self.raw_file_hash:
                logging.warning('Post-decompression SHA-256 failure, aborting...')
                returned_results['results'] = 'Internal assembly error'
                os.remove(self.save_path)
                return returned_results

        else:  # No compression, encryption
            calculated_hash = get_hash_from_file(self.save_path)
            if calculated_hash != self.raw_file_hash:
                logging.warning('Assembly raw file mismatch, aborting...')
                returned_results['results'] = 'Internal assembly error'
                os.remove(self.save_path)
                return returned_results

        self.is_processed = True
        self.save()
        returned_results['results'] = 'Success'
        logging.debug('Extraction successful')
        return returned_results


class StreamDataProgress(SQLBaseClass):
    """Aside from tracking progress of frames, we also need to account for what index slices of the overall payload we
    have saved/processed.  This is because files can be extracted from incomplete streams; this is the mechanism to
    track and calculate that, by seeing if file start:end falls within the current coverage.
    """

    __tablename__ = 'stream_data_progress'
    __abstract__ = False

    stream_id = Column(Integer, ForeignKey('stream_reads.id', ondelete='CASCADE'))
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
