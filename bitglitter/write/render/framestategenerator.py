import logging
from pathlib import Path

from bitstring import BitStream, ConstBitStream

from bitglitter.write.render.headerencode import initializer_header_encode, frame_header_encode


def frame_state_generator(block_height, block_width, pixel_width, protocol_version, initializer_palette,
                          stream_palette, output_mode, stream_output_path, output_name, working_directory, total_frames,
                          stream_header, metadata_header, palette_header, stream_sha256,
                          initializer_palette_dict, initializer_palette_dict_b, stream_palette_dict,
                          default_output_path):
    """This function iterates over the pre-processed data, and assembles and renders the frames.  There are plenty of
    comments in this function that describe what each part is doing, to follow along.
    """

    # Determining output for images.
    if output_mode == 'image':
        if stream_output_path:
            image_output_path = Path(stream_output_path)
        else:
            image_output_path = default_output_path

    if output_mode == 'video':
        image_output_path = working_directory

    # Constants
    TOTAL_BLOCKS = block_height * block_width
    INITIALIZER_CALIBRATOR_BLOCK_OVERHEAD = (block_height + block_width - 1) + 580  # calibrator + initializer
    INITIALIZER_BIT_OVERHEAD = 580
    FRAME_HEADER_BIT_OVERHEAD = 352

    #  Final preparations for stream header parts.
    stream_payload = ConstBitStream(filename=working_directory / 'processed.bin')

    #  These are the headers before stream palette is used, to be perfectly clear
    pre_stream_palette_headers_merged = BitStream()
    pre_stream_palette_headers_merged.append(BitStream(stream_header))
    pre_stream_palette_headers_merged.append(BitStream(metadata_header))
    pre_stream_palette_headers_merged.append(palette_header)
    pre_stream_palette_headers_merged = ConstBitStream(pre_stream_palette_headers_merged)

    frame_number = 1

    # This is the primary loop; it will yield until it traverses the entire file.
    while stream_payload.bitpos != stream_payload.length:

        logging.debug(f'GENERATOR:  Generating frame data for {frame_number} of {total_frames} ...')

        initializer_bits = BitStream()
        setup_headers_bits = BitStream()
        payload_bits = BitStream()
        padding_bits = BitStream()
        stream_sha_bytes = bytes.fromhex(stream_sha256)

        max_allowable_payload_bits = len(stream_payload) - stream_payload.bitpos
        max_allowable_pre_stream_palette_header_bits = pre_stream_palette_headers_merged.length \
                                                       - pre_stream_palette_headers_merged.bitpos
        blocks_left_this_frame = TOTAL_BLOCKS
        initializer_enabled = False
        initializer_palette_blocks_used = 0
        last_frame = False

        if frame_number == 1 or output_mode == 'image':
            initializer_bits = initializer_header_encode(block_height, block_width, protocol_version, stream_palette,
                                                         stream_sha_bytes)
            initializer_palette_blocks_used += INITIALIZER_BIT_OVERHEAD
            blocks_left_this_frame -= INITIALIZER_CALIBRATOR_BLOCK_OVERHEAD
            initializer_enabled = True

        # Pre stream palette headers to be rendered on these frames
        if pre_stream_palette_headers_merged.bitpos != pre_stream_palette_headers_merged.length:
            blocks_left_this_frame -= FRAME_HEADER_BIT_OVERHEAD
            initializer_palette_blocks_used += FRAME_HEADER_BIT_OVERHEAD

            # Pre stream palette headers don't have enough room to finish on this frame.
            if blocks_left_this_frame <= max_allowable_pre_stream_palette_header_bits:
                setup_headers_bits = pre_stream_palette_headers_merged.read(blocks_left_this_frame)
                initializer_palette_blocks_used += blocks_left_this_frame

            # Pre stream palette headers have enough room to finish on this frame.
            else:
                setup_headers_bits = pre_stream_palette_headers_merged.read(
                    max_allowable_pre_stream_palette_header_bits)
                initializer_palette_blocks_used += max_allowable_pre_stream_palette_header_bits
                blocks_left_this_frame -= max_allowable_pre_stream_palette_header_bits

                # There is room on this pre stream palette header termination frame to start writing the payload
                if blocks_left_this_frame:
                    bits_left_this_frame = blocks_left_this_frame * stream_palette.bit_length
                    payload_bits = stream_payload.read(min(bits_left_this_frame, max_allowable_payload_bits))

                    # The payload will finish on this frame.
                    if blocks_left_this_frame >= max_allowable_payload_bits:
                        last_frame = True

        # Standard frame containing only the payload, frame header, and initializer if enabled.
        else:
            bits_left_this_frame = (blocks_left_this_frame * stream_palette.bit_length) - FRAME_HEADER_BIT_OVERHEAD
            payload_bits = stream_payload.read(min(bits_left_this_frame, max_allowable_payload_bits))

            # Payload will finish on this frame.
            if bits_left_this_frame >= max_allowable_payload_bits:
                last_frame = True

        frame_hashable_bits = setup_headers_bits + payload_bits
        combined_frame_length = frame_hashable_bits.len + FRAME_HEADER_BIT_OVERHEAD

        # On the last frame, there may be excess bit capacity in the final block.  This pads the payload so it cleanly
        # fits into the final block.
        if last_frame:
            remainder_bits = stream_palette.bit_length - (combined_frame_length % stream_palette.bit_length)
            if remainder_bits == stream_palette.bit_length:
                remainder_bits = 0

            padding_bits = BitStream(bin=f"{'0' * remainder_bits}")
            frame_hashable_bits.append(padding_bits)

        frame_header_holder = frame_header_encode(frame_hashable_bits.tobytes(), frame_hashable_bits.len, frame_number)
        merged_pieces = initializer_bits + frame_header_holder + setup_headers_bits + payload_bits + padding_bits
        frame_payload = ConstBitStream(merged_pieces)

        yield {
            'block_height': block_height, 'block_width': block_width, 'pixel_width': pixel_width, 'frame_payload':
                frame_payload, 'initializer_palette_blocks_used': initializer_palette_blocks_used,
            'stream_palette_dict': stream_palette_dict, 'stream_palette_bit_length': stream_palette.bit_length,
            'initializer_palette_dict': initializer_palette_dict, 'initializer_palette_dict_b':
                initializer_palette_dict_b, 'initializer_palette': initializer_palette, 'output_mode': output_mode,
            'output_name': output_name, 'initializer_enabled': initializer_enabled, 'frame_number': frame_number,
            'total_frames': total_frames, 'image_output_path': image_output_path, 'stream_sha256': stream_sha256
        }

        frame_number += 1
