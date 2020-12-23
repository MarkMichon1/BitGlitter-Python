from bitstring import BitStream, ConstBitStream

import logging
from multiprocessing import cpu_count, Pool
from pathlib import Path
import time

from bitglitter.palettes.utilities import palette_grabber, ValuesToColor
from bitglitter.write.headers import stream_header_process, text_header_process
from bitglitter.write.renderworker import render_cycle
from bitglitter.write.renderutilities import total_frames_estimator
from bitglitter.write.videorender import render_video


class RenderHandler:

    def __init__(self,

                 # Basic Setup
                 stream_name, stream_description, working_dir, crypto_key, scrypt_n, scrypt_r, scrypt_p,

                 # Stream Rendering
                 block_height, block_width, pixel_width, header_palette_id, stream_palette_id, max_cpu_cores,

                 # Header
                 stream_sha, size_in_bytes, compression_enabled, encryption_enabled, file_mask_enabled,
                 datetime_started, bg_version, manifest,

                 # Render Output
                 frames_per_second, output_mode, output_path, output_name

                 ):

        self.blocks_wrote = 0
        self.frames_wrote = 0

        # Pre render

        logging.info('Beginning pre-render processes...')
        initializer_palette = palette_grabber('1')
        header_palette = palette_grabber(header_palette_id)
        stream_palette = palette_grabber(stream_palette_id)

        initializer_palette_dict = ValuesToColor(initializer_palette, 'initializer_palette')
        header_palette_dict = ValuesToColor(header_palette, 'header_palette')
        stream_palette_dict = ValuesToColor(stream_palette, 'stream_palette')

        text_header_bytes, raw_text_header_hash_bytes = text_header_process(file_mask_enabled, crypto_key, scrypt_n,
                                                                            scrypt_r, scrypt_p, bg_version,
                                                                            stream_palette, stream_name,
                                                                            stream_description, manifest)
        self.frames_wrote = total_frames_estimator(block_height, block_width, text_header_bytes,
                                                                  size_in_bytes, stream_palette, header_palette,
                                                                  output_mode)

        stream_header = stream_header_process(size_in_bytes, self.frames_wrote, compression_enabled, encryption_enabled,
                                              file_mask_enabled, stream_palette.palette_type == "custom",
                                              datetime_started, stream_palette.id, len(text_header_bytes),
                                              raw_text_header_hash_bytes)
        if output_mode == 'image':
            if output_path:
                frame_output_path = None
            else:
                frame_output_path = None
        else:
            frame_output_path = working_dir

        # Render

        # Constants
        TOTAL_BLOCKS = block_height * block_width
        INITIALIZER_OVERHEAD = block_height + block_width + 323
        INITIALIZER_BIT_OVERHEAD = 324
        FRAME_HEADER_BIT_OVERHEAD = 608

        # Final Setup
        payload = ConstBitStream(filename=Path(working_dir / 'processed.bin'))
        frame_number = 1
        primary_frame_palette_dict = header_palette_dict
        primary_read_length = header_palette.bit_length
        active_palette = header_palette
        stream_palette_used = False
        last_frame = False
        stream_header = None #refer to unchanged renderloop...
        stream_header_combined = BitStream(stream_header)
        stream_header_combined.append(text_header_bytes)

        # Multicore Setup
        if max_cpu_cores == 0 or max_cpu_cores >= cpu_count():
            pool_size = cpu_count()
        else:
            pool_size = max_cpu_cores
        worker_pool = Pool(processes=pool_size)

        logging.info(f'Beginning rendering on {None} cores...')
        frame_number = 1
        last_frame_blocks = 0



        ##########

        if output_mode == 'video':
            render_video(self.stream_output_path, output_name, datetime_started, working_dir,
                         self.frame_number_formatted, frames_per_second)

        # Wrap-up

        self.datetime_finished = time.time()
        self.blocks_wrote = (block_width * block_height) * self.frames_wrote + last_frame_blocks