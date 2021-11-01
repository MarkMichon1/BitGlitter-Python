#  This model has its own module because of its large size

import logging

from sqlalchemy import BLOB, Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

import json
from pathlib import Path
import time

from bitglitter.config.config import engine, SQLBaseClass


class StreamRead(SQLBaseClass):
    """This serves as the central data container and API for interacting with saved read data."""

    __tablename__ = 'stream_reads'
    __abstract__ = False

    # Core
    time_started = Column(Integer, default=time.time)
    bg_version = Column(String)
    protocol_version = Column(Integer)
    stream_sha256 = Column(String, unique=True, nullable=False)
    stream_is_video = Column(Boolean, nullable=False)
    stream_palette_id = Column(String)
    custom_palette_used = Column(Boolean)
    custom_palette_loaded = Column(Boolean)
    total_frames = Column(Integer)
    compression_enabled = Column(Boolean)
    encryption_enabled = Column(Boolean)
    file_masking_enabled = Column(Boolean)
    stream_name = Column(String)
    stream_description = Column(String)
    time_created = Column(Integer)
    size_in_bytes = Column(Integer)
    output_directory = Column(String)  # output-dir/stream-name/
    temp_directory = Column(String)  # temp-dir/stream-sha256/
    manifest_string = Column(String)


    # Read State
    remaining_pre_payload_bits = Column(Integer)
    carry_over_header_bytes = Column(BLOB)
    carry_over_padding_bits = Column(Integer) #todo
    payload_start_frame = Column(Integer)
    payload_first_frame_bits = Column(Integer)
    payload_bits_per_standard_frame = Column(Integer)
    palette_header_size_bytes = Column(Integer)
    palette_header_hash = Column(String)
    metadata_header_size_bytes = Column(Integer)
    metadata_header_hash = Column(String)
    stream_header_complete = Column(Boolean, default=False)
    palette_header_complete = Column(Boolean, default=False)
    metadata_header_complete = Column(Boolean, default=False)
    completed_frames = Column(Integer, default=0)
    highest_consecutive_frame_one_read = Column(Integer, default=0)  # Important for initial metadata grab

    # Operation State
    active_this_session = Column(Boolean, default=False)

    # Unpackage State
    auto_delete_finished_stream = Column(Boolean)
    unpackage_files = Column(Boolean)

    # Geometry
    pixel_width = Column(Integer)
    block_height = Column(Integer)
    block_width = Column(Integer)

    # Crypto
    scrypt_n = Column(Integer)
    scrypt_r = Column(Integer)
    scrypt_p = Column(Integer)
    encryption_key = Column(String)

    # Relationships
    frames = relationship('StreamFrame', back_populates='stream', cascade='all, delete', passive_deletes=True)
    files = relationship('StreamFile', back_populates='stream', cascade='all, delete', passive_deletes=True)
    progress = relationship('StreamDataProgress', back_populates='stream', cascade='all, delete', passive_deletes=True)

    def __str__(self):
        return f'{self.stream_name} - {self.stream_sha256}'

    def session_activity(self, bool_set: bool): #todo implement
        self.active_this_session = bool_set
        self.save()

    def geometry_load(self, block_height, block_width, pixel_width):
        self.block_height = block_height
        self.block_width = block_width
        self.pixel_width = pixel_width
        self.save()

    def stream_palette_id_load(self, stream_palette_id):
        self.stream_palette_id = stream_palette_id
        self.save()

    def stream_header_load(self, size_in_bytes, total_frames, compression_enabled, encryption_enabled,
                           file_masking_enabled, metadata_header_length, metadata_header_hash,
                           custom_palette_header_length, custom_palette_header_hash):
        logging.debug('Steam header load')
        self.size_in_bytes = size_in_bytes
        self.total_frames = total_frames
        self.compression_enabled = compression_enabled
        self.encryption_enabled = encryption_enabled
        self.file_masking_enabled = file_masking_enabled
        self.metadata_header_size_bytes = metadata_header_length
        self.metadata_header_hash = metadata_header_hash
        self.palette_header_size_bytes = custom_palette_header_length
        if not custom_palette_header_length:
            self.palette_header_complete = True
        self.palette_header_hash = custom_palette_header_hash
        self.stream_header_complete = True
        self.save()

    def metadata_header_load(self, bg_version, stream_name, stream_description, time_created, manifest_string):
        logging.debug('Metadata header load')
        self.bg_version = bg_version #
        self.stream_name = stream_name #
        self.stream_description = stream_description
        self.time_created = time_created
        self.manifest_string = manifest_string
        self.metadata_header_complete = True

        # Set output directory
        new_output_directory = Path(self.output_directory)
        new_output_directory = new_output_directory / stream_name
        self.output_directory = str(new_output_directory)
        self.save()

        # Manifest process
        manifest_dict = json.loads(manifest_string)
        manifest_unpack(manifest_dict, self.id, new_output_directory)

    def metadata_checkpoint_return(self):
        """If stop_at_metadata_load is enabled at read() and this hasn't ran previously, this returns a dictionary of
        all stream header and metadata attributes, as well as stream header data if its a learned palette.
        """

        #todo- return palette data if not grabbed yet
        #todo- return metadata as dict
        returned_dict = {'stream_name': self.stream_name, 'stream_sha256': self.stream_sha256, 'bg_version':
                         self.bg_version, 'stream_description': self.stream_description, 'time_created':
                         self.time_created, 'manifest': None, 'size_in_bytes': self.size_in_bytes, 'total_frames':
                         self.total_frames, 'compression_enabled': self.compression_enabled, 'encryption_enabled':
                         self.encryption_enabled, 'file_masking_enabled': self.file_masking_enabled, 'protocol_version':
                         self.protocol_version, 'block_width': self.block_width, 'block_height': self.block_height,
                         'manifest_decrypt_success': None} # <- todo



        return returned_dict


    def accept_frame(self, payload_bits, frame_number):
        logging.debug(f'Frame {frame_number} accepted')

    def attempt_unpackage(self):
        """Attempts to extract files from the partial or complete decoded data.  Returns a dictionary object giving a
        summary of the results.
        """

        # blob calculate
        # file assess ^
        return {}

    # User control
    def _delete_data_folder(self):
        pass

    def _delete_stream(self):
        self.delete()


# v These need to be at bottom to resolve import/DB relationship issues.  It works but perhaps a better way exists.
import bitglitter.config.readmodels.readmodels
from bitglitter.read.decode.manifest import manifest_unpack

SQLBaseClass.metadata.create_all(engine)

#todo: MULTIPLE CLASSES: merge with above model and integrate applicable stuff into readfunctions


#
#         self.active_this_session = True
#         self.is_assembled = False # Did the frames successfully merge into a single binary?
#         self.post_processor_decrypted = False # Was the stream successfully decrypted?
#         self.frame_reference_table = None
#         self.frames_prior_to_binary_preamble = []
#         self.stream_palette_read = False
#         self.assemble_hold = assemble_hold

#

#
#     #todo: add frame block byte file to signify processing on given frame

#   #todo attempt assembly- try to decrypt manifest, if success, begin unpackaging
#   #todo def return_status- dict object of stream status

#     def review_active_sessions(self):
#         '''This method will go over all stream_sha's that were read in this read session, and will check to see if
#         check if frames_ingested == total_frames AND the frame reference table is displaying all frames are present.  This
#         only runs if there is at least one active session.
#         '''
#
#         if self.active_session_hashes:
#             logging.info('Reviewing active sessions and attempting assembly...')
#             for partial_save in self.active_session_hashes:
#
#                 # Not ready to be assembled this session.
#                 if self.save_dict[partial_save]._attempt_assembly() == False \
#                         and self.save_dict[partial_save].assemble_hold == False:
#                     self.save_dict[partial_save]._close_session()
#
#                 # Assembled, temporary files pending deletion.
#                 else:
#                     logging.info(f'{partial_save} fully read!  Deleting temporary files...')
#                     self.remove_partial_save(partial_save)
#
#             self.active_session_hashes = []
#



#                     logging.info("Password incorrect, cannot continue.")
#                     os.remove(self.pass_through)
#
#             else:
#
#                 logging.warning(f'Decryption key missing from input argument, cannot continue.')
#
#         else:
#
#             logging.info('Encryption was not enabled on this stream.  Skipping step...')
#             self.is_satisfied = True
#
#
# class Decompressor:
#     '''If compression was enabled on this stream, this object will decompress it.'''
#
#     def __init__(self, working_folder, pass_through, compression_enabled):
#
#         self.pass_through = pass_through
#
#         if compression_enabled:
#             new_path = working_folder + "\\decompressed.dat"
#             logging.info('Decompressing file...')
#             decompress_file(self.pass_through, new_path)
#             self.pass_through = new_path
#             logging.info('Successfully decompressed.')
#
#         else:
#             logging.info('Compression was not enabled on this stream.  Skipping step...')
#
