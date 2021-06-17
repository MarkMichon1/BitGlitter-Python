import logging
from multiprocessing import cpu_count, Pool

from bitglitter.config.palettemanager import palette_manager
from bitglitter.palettes.utilities import BitsToColor
from bitglitter.utilities.filemanipulation import create_default_output_folder
from bitglitter.write.render.headers import metadata_header_process, palette_initialization_header_process, \
    stream_setup_header_process
from bitglitter.write.render.framestategenerator import frame_state_generator
from bitglitter.write.render.renderutilities import draw_frame, total_frames_estimator
from bitglitter.write.render.videorender import render_video


class RenderHandler:

    def __init__(self,

                 # Basic Setup
                 stream_name, stream_description, working_dir, default_output_path, crypto_key, scrypt_n, scrypt_r,
                 scrypt_p,

                 # Stream Rendering
                 block_height, block_width, pixel_width, stream_palette_id, max_cpu_cores,

                 # Header
                 stream_sha, size_in_bytes, compression_enabled, encryption_enabled, file_mask_enabled,
                 datetime_started, bg_version, manifest, protocol_version,

                 # Render Output
                 frames_per_second, output_mode, output_path, output_name

                 ):

        self.blocks_wrote = 0
        self.frames_wrote = 0

        # Pre render

        logging.info('Beginning pre-render processes...')
        create_default_output_folder(default_output_path)
        initializer_palette = palette_manager.return_selected_palette('1')
        stream_palette = palette_manager.return_selected_palette(stream_palette_id)

        initializer_palette_dict = BitsToColor(initializer_palette, 'initializer_palette')
        stream_palette_dict = BitsToColor(stream_palette, 'stream_palette')

        metadata_header_bytes, metadata_header_hash_bytes = metadata_header_process(file_mask_enabled, crypto_key,
                                                                                    scrypt_n,
                                                                                    scrypt_r, scrypt_p, bg_version,
                                                                                    stream_name, datetime_started,
                                                                                    stream_description, manifest)
        palette_header_bytes = b''
        palette_header_hash_bytes = b''
        if stream_palette.palette_type == 'custom':
            palette_header_bytes, palette_header_hash_bytes = palette_initialization_header_process(stream_palette)

        self.frames_wrote = total_frames_estimator(block_height, block_width, len(metadata_header_bytes),
                                                   len(palette_header_bytes), size_in_bytes, stream_palette,
                                                   output_mode)

        stream_header = stream_setup_header_process(size_in_bytes, self.frames_wrote, compression_enabled,
                                                    encryption_enabled, file_mask_enabled, metadata_header_bytes,
                                                    metadata_header_hash_bytes, palette_header_bytes,
                                                    palette_header_hash_bytes)
        logging.info('Pre-render complete.')

        # Render

        if max_cpu_cores == 0 or max_cpu_cores >= cpu_count():
            pool_size = cpu_count()
        else:
            pool_size = max_cpu_cores

        block_position = 0

        with Pool(processes=pool_size) as worker_pool:
            logging.info(f'Beginning rendering on {pool_size} CPU cores...')
            count = 1
            for frame_encode in worker_pool.imap(draw_frame, frame_state_generator(block_height, block_width,
                                                                                    pixel_width, protocol_version,
                                                                                    initializer_palette, stream_palette,
                                                                                    output_mode, output_path,
                                                                                    output_name, working_dir,
                                                                                    self.frames_wrote, stream_header,
                                                                                    metadata_header_bytes,
                                                                                    palette_header_bytes, stream_sha,
                                                                                    initializer_palette_dict,
                                                                                    stream_palette_dict,
                                                                                    default_output_path), chunksize=1):
                if frame_encode['frame_number'] == self.frames_wrote:
                    block_position = frame_encode['block_position']
                logging.info(f'Processing frame {count} of {self.frames_wrote}... '
                             f'({round(((count / self.frames_wrote) * 100), 2):.2f} %)')

                count += 1
        logging.info('Rendering frames complete.')

        # Video Render

        if output_mode == 'video':
            render_video(output_path, default_output_path, output_name, working_dir, self.frames_wrote,
                         frames_per_second, stream_sha)

        # Wrap-up

        self.blocks_wrote = (block_width * block_height) * self.frames_wrote + block_position
