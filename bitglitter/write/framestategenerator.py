import logging
import math
from pathlib import Path

from bitstring import BitStream, ConstBitStream

from bitglitter.write.headers import initializer_header_process, frame_header_process


def frame_state_generator(block_height, block_width, pixel_width, protocol_version, initializer_palette, header_palette,
                          stream_palette, output_mode, stream_output_path, output_name, working_directory, total_frames,
                          date_created, stream_header, text_header_processed, stream_sha, initializer_palette_dict,
                          header_palette_dict, stream_palette_dict):
    """This function iterates over the pre-processed data, and assembles and renders the frames.  There are plenty of
    comments in this function that describe what each part is doing, to follow along.
    """

    # Determining output for images.
    if output_mode == 'image':
        if stream_output_path:
            image_output_path = Path(stream_output_path)

        else:
            image_output_path = Path(working_directory.parent / 'Stream Output')

    if output_mode == 'video':
        image_output_path = working_directory

    # Constants
    TOTAL_BLOCKS = block_height * block_width
    INITIALIZER_OVERHEAD = block_height + block_width + 323
    INITIALIZER_BIT_OVERHEAD = 324
    FRAME_HEADER_BIT_OVERHEAD = 608

    payload = ConstBitStream(filename=working_directory / 'processed.bin')
    frame_number = 1
    primary_frame_palette_dict, primary_read_length = header_palette_dict, header_palette.bit_length
    active_palette = header_palette
    stream_palette_used = False
    last_frame = False

    # Final preparations for stream header parts.
    stream_header_bitstream = BitStream(stream_header)
    stream_header_combined = BitStream(stream_header_bitstream)
    stream_header_combined.append(text_header_processed)

    # This is the primary loop where all rendering takes place.  It'll continue until it traverses the entire file.
    while payload.bitpos != payload.length:

        logging.debug(f'Generating frame data for {frame_number} of {total_frames} ...')

        stream_header_chunk = BitStream()
        payload_holder = BitStream()
        attachment_bits_append = BitStream()
        remainder_blocks_into_bits = BitStream()
        bits_to_pad = BitStream()

        max_allowable_payload_bits = len(payload) - payload.bitpos
        bits_consumed = FRAME_HEADER_BIT_OVERHEAD
        blocks_left = TOTAL_BLOCKS
        initializer_enabled = False
        blocks_used = 0
        initializer_palette_blocks_used = 0
        stream_header_blocks_used = 0

        if stream_palette_used == True:
            primary_frame_palette_dict, primary_read_length = stream_palette_dict, stream_palette.bit_length
            active_palette = stream_palette

        # Adding an initializer header if necessity.  initializer_enabled is a boolean that signals whether the
        # initializer is on or not.
        initializer_holder = BitStream()
        if frame_number == 1 or output_mode == 'image':
            initializer_holder = initializer_header_process(block_height, block_width, protocol_version, active_palette)
            initializer_palette_blocks_used += INITIALIZER_BIT_OVERHEAD
            blocks_left -= INITIALIZER_OVERHEAD
            initializer_enabled = True

        bits_left_this_frame = (blocks_left * active_palette.bit_length) - FRAME_HEADER_BIT_OVERHEAD

        # Here, we're calculating how many bits we can fit into the stream based on the palettes used.
        # Normal frame_payload frames.
        if stream_palette_used:

            # Standard frame_payload frame in the middle of the stream.
            if bits_left_this_frame <= max_allowable_payload_bits:
                payload_holder = payload.read(bits_left_this_frame)

            # Payload Frame terminates on this frame.
            else:
                logging.debug('Payload termination frame')
                payload_holder = payload.read(max_allowable_payload_bits)
                last_frame = True

        # Frames that need stream_header_combined added to them.
        else:

            # This frame has more bits left for the streamHeader than capacity.
            if len(stream_header_combined) - stream_header_combined.bitpos > bits_left_this_frame:
                stream_header_chunk = stream_header_combined.read(bits_left_this_frame)
                stream_header_blocks_used = math.ceil(len(stream_header_chunk + FRAME_HEADER_BIT_OVERHEAD)
                                                      / active_palette.bitLength)

            # stream_header_combined terminates on this frame
            else:

                logging.debug("Streamheader terminates this frame.")

                stream_header_chunk = stream_header_combined.read(len(stream_header_combined)
                                                                  - stream_header_combined.bitpos)
                bits_left_this_frame -= len(stream_header_combined)
                bits_consumed += len(stream_header_chunk)

                stream_palette_used = True
                stream_header_blocks_used = math.ceil(bits_consumed / active_palette.bit_length)

                # There may be extra bits available at the end of the blocks used for the header_palette.  If that's
                # the case, they will be calculated here.
                final_block_partial_fill = bits_consumed % active_palette.bit_length

                if final_block_partial_fill > 0:
                    attachment_bits = active_palette.bit_length - final_block_partial_fill
                    attachment_bits_append = payload.read(attachment_bits)

                    bits_consumed += attachment_bits
                    max_allowable_payload_bits -= attachment_bits

                remaining_blocks_left = blocks_left - stream_header_blocks_used

                # If there are remaining stream_palette blocks available for this frame, we go here.
                if remaining_blocks_left > 0:
                    bits_left_this_frame = remaining_blocks_left * active_palette.bit_length

                    if max_allowable_payload_bits > bits_left_this_frame:  # Payload continues on in next frame(s)
                        remainder_blocks_into_bits = payload.read(bits_left_this_frame)

                    else:  # Full frame_payload can terminate on streamHeader termination frame.
                        remainder_blocks_into_bits = payload.read(max_allowable_payload_bits)
                        last_frame = True

        frame_hashable_bits = stream_header_chunk + attachment_bits_append + remainder_blocks_into_bits + payload_holder
        combined_frame_length = frame_hashable_bits.len + FRAME_HEADER_BIT_OVERHEAD
        blocks_used = (int(initializer_enabled) * INITIALIZER_BIT_OVERHEAD) + math.ceil(combined_frame_length
                                                                                        / active_palette.bit_length)

        # On the last frame, there may be excess capacity in the final block.  This pads the payload as needed so it
        # cleanly fits into the block.
        if last_frame:

            remainder_bits = active_palette.bit_length - (combined_frame_length % active_palette.bit_length)
            if remainder_bits == active_palette.bit_length:
                remainder_bits = 0

            bits_to_pad = BitStream(bin=f"{'0' * remainder_bits}")
            frame_hashable_bits.append(bits_to_pad)

        frame_header_holder = frame_header_process(stream_sha, frame_hashable_bits, frame_number, blocks_used)
        combining_bits = initializer_holder + frame_header_holder + stream_header_chunk + attachment_bits_append \
                         + remainder_blocks_into_bits + payload_holder + bits_to_pad
        frame_payload = ConstBitStream(combining_bits)

        yield {
            'block_height': block_height, 'block_width': block_width, 'pixel_width': pixel_width, 'frame_payload':
            frame_payload, 'date_created': date_created, 'initializer_palette_blocks_used':
            initializer_palette_blocks_used, 'primary_frame_palette_dict': primary_frame_palette_dict,
            'primary_read_length': primary_read_length, 'initializer_palette_dict': initializer_palette_dict,
            'initializer_palette': initializer_palette, 'output_mode': output_mode, 'output_name': output_name,
            'initializer_enabled': initializer_enabled, 'frame_number': frame_number, 'total_frames': total_frames,
            'image_output_path': image_output_path,
        }

        frame_number += 1
