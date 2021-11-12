import logging
from multiprocessing import cpu_count, Pool

from bitglitter.config.palettefunctions import _return_palette
from bitglitter.utilities.filemanipulation import create_default_output_folder
from bitglitter.write.render.headerencode import metadata_header_encode, custom_palette_header_encode, \
    stream_header_encode
from bitglitter.write.render.framestategenerator import frame_state_generator
from bitglitter.write.render.renderutilities import draw_frame, total_frames_estimator


class RenderHandler:

    def __init__(self,

                 # Basic Setup
                 stream_name, stream_description, working_dir, default_output_path, crypto_key, scrypt_n, scrypt_r,
                 scrypt_p,

                 # Stream Rendering
                 block_height, block_width, pixel_width, stream_palette_id, max_cpu_cores,

                 # Header
                 stream_sha256, size_in_bytes, compression_enabled, encryption_enabled, file_mask_enabled,
                 datetime_started, bg_version, manifest, protocol_version,

                 # Render Output
                 output_mode, output_path, stream_name_file_output,

                 # Statistics
                 save_statistics

                 ):

        self.blocks_wrote = 0
        self.total_frames = 0

        # Pre render
        logging.info('Beginning pre-render processes...')
        create_default_output_folder(default_output_path)
        initializer_palette = _return_palette(palette_id='1')
        initializer_palette_b = _return_palette('11')
        stream_palette = _return_palette(palette_id=stream_palette_id)

        initializer_palette_dict = initializer_palette.return_encoder()
        initializer_palette_dict_b = initializer_palette_b.return_encoder()
        stream_palette_dict = stream_palette.return_encoder()

        metadata_header_bytes, metadata_header_hash_bytes = metadata_header_encode(file_mask_enabled, crypto_key,
                                                                                   scrypt_n, scrypt_r, scrypt_p,
                                                                                   bg_version, stream_name,
                                                                                   datetime_started,
                                                                                   stream_description, manifest)
        palette_header_bytes = b''
        palette_header_hash_bytes = b''
        if stream_palette.is_custom:
            palette_header_bytes, palette_header_hash_bytes = custom_palette_header_encode(stream_palette)

        self.total_frames = total_frames_estimator(block_height, block_width, len(metadata_header_bytes),
                                                   len(palette_header_bytes), size_in_bytes, stream_palette,
                                                   output_mode)

        stream_header = stream_header_encode(size_in_bytes, self.total_frames, compression_enabled,
                                             encryption_enabled, file_mask_enabled, len(metadata_header_bytes),
                                             metadata_header_hash_bytes, len(palette_header_bytes),
                                             palette_header_hash_bytes)
        logging.info('Pre-render complete.')

        #  Render
        if max_cpu_cores == 0 or max_cpu_cores >= cpu_count():
            pool_size = cpu_count()
        else:
            pool_size = max_cpu_cores

        self.total_operations = self.total_frames * (1 + int(output_mode != 'image'))

        payload_bits_rendered = 0
        with Pool(processes=pool_size) as worker_pool:
            logging.info(f'Beginning rendering on {pool_size} CPU core(s)...')

            for frame_encode in worker_pool.imap(draw_frame,
                                                 frame_state_generator(block_height, block_width, pixel_width,
                                                 protocol_version, initializer_palette, stream_palette, output_mode,
                                                 output_path, stream_name_file_output, working_dir, self.total_frames,
                                                 stream_header, metadata_header_bytes, palette_header_bytes,
                                                 stream_sha256, initializer_palette_dict, initializer_palette_dict_b,
                                                 stream_palette_dict, default_output_path, stream_name,
                                                 save_statistics), chunksize=1):
                payload_bits_rendered += 1

        #assert size_in_bytes == payload_bits_rendered * 8

        logging.info('Rendering frames complete.')
