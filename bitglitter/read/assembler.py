import logging
import shutil

from bitglitter.config.constants import READ_PATH
from bitglitter.read.partialsave import PartialSave


class Assembler:
    '''This object holds PartialSave objects, which holds the state of the file being read until it is fully assembled
    and complete, which then purges the record.
    '''

    def __init__(self):
        self.working_folder = READ_PATH
        self.save_dict = {}
        self.active_session_hashes = []


    def check_if_frame_needed(self, stream_sha, frame_number):

        if stream_sha not in self.save_dict:
            return True
        else:
            if self.save_dict[stream_sha].is_frame_needed(frame_number) == False:
                logging.info(f'Frame # {frame_number} / {self.save_dict[stream_sha].total_frames} for stream SHA '
                             f'{stream_sha} is already saved!  Skipping...')
            else:
                return True
        return False


    def create_partial_save(self, stream_sha, scrypt_n, scrypt_r, scrypt_p, output_path, encryption_key, assemble_hold):
        self.save_dict[stream_sha] = PartialSave(stream_sha, self.working_folder, scrypt_n, scrypt_r, scrypt_p, output_path,
                                                 encryption_key, assemble_hold)


    def save_frame_into_partial_save(self, stream_sha, payload, frame_number):
        logging.info(f'Frame # {frame_number} / {self.save_dict[stream_sha].total_frames} for stream SHA {stream_sha} '
                     f'saved!')
        self.save_dict[stream_sha].load_frame_data(payload, frame_number)


    def accept_frame(self, stream_sha, payload, frame_number, scrypt_n, scrypt_r, scrypt_p, output_path, encryption_key,
                     assemble_hold):
        '''This method accepts a validated frame.'''

        if stream_sha not in self.save_dict:
            self.create_partial_save(stream_sha, scrypt_n, scrypt_r, scrypt_p, output_path, encryption_key, assemble_hold)

        if stream_sha not in self.active_session_hashes:
            self.active_session_hashes.append(stream_sha)

        self.save_frame_into_partial_save(stream_sha, payload, frame_number)


    def review_active_sessions(self):
        '''This method will go over all stream_sha's that were read in this read session, and will check to see if
        check if frames_ingested == total_frames AND the frame reference table is displaying all frames are present.  This
        only runs if there is at least one active session.
        '''

        if self.active_session_hashes:
            logging.info('Reviewing active sessions and attempting assembly...')
            for partial_save in self.active_session_hashes:

                # Not ready to be assembled this session.
                if self.save_dict[partial_save]._attempt_assembly() == False \
                        and self.save_dict[partial_save].assemble_hold == False:
                    self.save_dict[partial_save]._close_session()

                # Assembled, temporary files pending deletion.
                else:
                    logging.info(f'{partial_save} fully read!  Deleting temporary files...')
                    self.remove_partial_save(partial_save)

            self.active_session_hashes = []


    def remove_partial_save(self, stream_sha):
        '''Removes PartialSave from dictionary.  Is used either through direct user argument, or by read() once a stream
        is successfully converted back into a file.
        '''

        del self.save_dict[stream_sha]
        shutil.rmtree(self.working_folder + f'\\{stream_sha}')
        logging.debug(f'Temporary files successfully removed.')


    def clear_partial_saves(self):
        '''This removes all save data.  Called by user function remove_all_partial_saves() in savedfilefunctions.'''

        try:
            shutil.rmtree(self.working_folder)
        except:
            pass

        self.save_dict = {}