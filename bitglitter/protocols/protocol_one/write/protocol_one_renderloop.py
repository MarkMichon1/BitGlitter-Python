import logging
import math
import time

from bitstring import BitStream, ConstBitStream
from PIL import Image, ImageDraw

from bitglitter.protocols.protocol_one.write.protocol_one_renderassets import render_calibrator, generate_initializer, \
    generate_frame_header, generate_stream_header_binary_preamble, loop_generator


def render_loop(block_height, block_width, pixel_width, protocol_version, initializer_palette, header_palette,
                stream_palette, output_mode, stream_output_path, output_name, active_path, pass_through, size_in_bytes,
                total_frames, compression_enabled, encryption_enabled, file_mask_enabled, date_created,
                ascii_compressed, stream_sha, initializer_palette_dict, header_palette_dict, stream_palette_dict):
    '''This function iterates over the preProcessed data, and assembles and renders the frames.  There are plenty of
    # comments in this function that describe what each part is doing, to follow along.
    '''

    logging.debug('Entering render_loop...')

    # Determining output for images.
    if output_mode == 'image':
        if stream_output_path:
            image_output_path = stream_output_path + '\\'

        else:
            image_output_path = ""

    if output_mode == 'video':
        image_output_path = active_path + '\\'

    # Constants
    TOTAL_BLOCKS = block_height * block_width
    INITIALIZER_OVERHEAD = block_height + block_width + 323
    INITIALIZER_DATA_BITS = 324
    FRAME_HEADER_OVERHEAD = 608

    active_payload = ConstBitStream(filename=pass_through)
    frame_number = 1
    primary_frame_palette_dict, primary_read_length = header_palette_dict, header_palette.bit_length
    active_palette = header_palette
    stream_palette_used = False
    last_frame = False

    # Final preparations for stream header parts.
    stream_header_binary_preamble = generate_stream_header_binary_preamble(size_in_bytes, total_frames,
                                                            compression_enabled, encryption_enabled, file_mask_enabled,
                                                            stream_palette.palette_type == "custom", date_created,
                                                            stream_palette.id, len(ascii_compressed))
    stream_header_combined = BitStream(stream_header_binary_preamble)
    stream_header_combined.append(ascii_compressed)

    # This is the primary loop where all rendering takes place.  It'll continue until it traverses the entire file.
    while active_payload.bitpos != active_payload.length:

        logging.info(f'Rendering frame {frame_number} of {total_frames} ...')

        # Setting up frame to draw on.
        image = Image.new('RGB', (pixel_width * block_width, pixel_width * block_height), 'white')
        draw = ImageDraw.Draw(image)

        stream_header_chunk = BitStream()
        payload_holder = BitStream()
        attachment_bits_append = BitStream()
        remainder_blocks_into_bits = BitStream()
        bits_to_pad = BitStream()

        max_allowable_payload_bits = len(active_payload) - active_payload.bitpos
        bits_consumed = FRAME_HEADER_OVERHEAD
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
            image = render_calibrator(image, block_height, block_width, pixel_width)
            initializer_holder = generate_initializer(block_height, block_width, protocol_version, active_palette)
            initializer_palette_blocks_used += INITIALIZER_DATA_BITS
            blocks_left -= INITIALIZER_OVERHEAD
            initializer_enabled = True

        bits_left_this_frame = (blocks_left * active_palette.bit_length) - FRAME_HEADER_OVERHEAD

        # Here, we're calculating how many bits we can fit into the stream based on the palettes used.
        # Normal frame_payload frames.
        if stream_palette_used == True:

            # Standard frame_payload frame in the middle of the stream.
            if bits_left_this_frame <= max_allowable_payload_bits:
                payload_holder = active_payload.read(bits_left_this_frame)

            # Payload Frame terminates on this frame.
            else:
                logging.debug('Payload termination frame')
                payload_holder = active_payload.read(max_allowable_payload_bits)
                last_frame = True


        # Frames that need stream_header_combined added to them.
        else:

            # This frame has more bits left for the streamHeader than capacity.
            if len(stream_header_combined) - stream_header_combined.bitpos > bits_left_this_frame:
                stream_header_chunk = stream_header_combined.read(bits_left_this_frame)
                stream_header_blocks_used = math.ceil(len(stream_header_chunk + FRAME_HEADER_OVERHEAD)
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
                    attachment_bits = active_palette.bit_length - (final_block_partial_fill)
                    attachment_bits_append = active_payload.read(attachment_bits)

                    bits_consumed += attachment_bits
                    max_allowable_payload_bits -= attachment_bits

                remaining_blocks_left = blocks_left - stream_header_blocks_used

                # If there are remaining stream_palette blocks available for this frame, we go here.
                if remaining_blocks_left > 0:
                    bits_left_this_frame = remaining_blocks_left * active_palette.bit_length

                    if max_allowable_payload_bits > bits_left_this_frame: # Payload continues on in next frame(s)
                        remainder_blocks_into_bits = active_payload.read(bits_left_this_frame)

                    else: # Full frame_payload can terminate on streamHeader termination frame.
                        remainder_blocks_into_bits = active_payload.read(max_allowable_payload_bits)
                        last_frame = True

        frame_hashable_bits = stream_header_chunk + attachment_bits_append + remainder_blocks_into_bits + payload_holder
        combined_frame_length = frame_hashable_bits.len + FRAME_HEADER_OVERHEAD
        blocks_used = (int(initializer_enabled) * INITIALIZER_DATA_BITS) + math.ceil(combined_frame_length
                                                                                   / active_palette.bit_length)

        #On the last frame, there may be excess capacity in the final block.  This pads the payload as needed so it
        #cleanly fits into the block.
        if last_frame == True:

            remainder_bits = active_palette.bit_length - (combined_frame_length % active_palette.bit_length)
            if remainder_bits == active_palette.bit_length:
                remainder_bits = 0

            bits_to_pad = BitStream(bin=f"{'0' * remainder_bits}")
            frame_hashable_bits.append(bits_to_pad)

        frame_header_holder = generate_frame_header(stream_sha, frame_hashable_bits, frame_number, blocks_used)
        combining_bits = initializer_holder + frame_header_holder + stream_header_chunk + attachment_bits_append \
                        + remainder_blocks_into_bits + payload_holder + bits_to_pad

        all_bits_to_write = ConstBitStream(combining_bits)
        next_coordinates = loop_generator(block_height, block_width, pixel_width, initializer_enabled)
        block_position = 0

        # Drawing blocks to screen.
        while len(all_bits_to_write) != all_bits_to_write.bitpos:

            # Primary palette selection (ie, header_palette or stream_palette depending on where we are in the stream)
            if block_position >= initializer_palette_blocks_used:
                active_palette_dict, read_length = primary_frame_palette_dict, primary_read_length

            # Initializer palette selection
            elif block_position < initializer_palette_blocks_used:
                active_palette_dict, read_length = (initializer_palette_dict, initializer_palette.bit_length)

            # Here to signal something has broken.
            else:
                raise Exception('Something has gone wrong in matching block position to palette.  This state'
                                '\nis reached only if something is broken.')

            # This is loading the next bit(s) to be written in the frame, and then converting it to an RGB value.
            next_bits = all_bits_to_write.read(f'bits : {read_length}')
            color_value = active_palette_dict.get_color(ConstBitStream(next_bits))

            # With the color loaded, we'll get the coordinates of the next block (each corner), and draw it in.
            active_coordinates = next(next_coordinates)
            draw.rectangle((active_coordinates[0], active_coordinates[1], active_coordinates[2], active_coordinates[3]),
                           fill=f'rgb{str(color_value)}')

            block_position += 1

        # Frames get saved as .png files.
        frame_number_to_string = str(frame_number)

        if output_mode == 'video':
            file_name = frame_number_to_string.zfill(math.ceil(math.log(total_frames + 1, 10)))

        else:
            if output_name:
                file_name = output_name + ' - ' + str(frame_number)
            else:
                file_name = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(date_created)) + ' - ' + str(frame_number)

        image.save(f'{image_output_path}{str(file_name)}.png')
        frame_number += 1

    logging.debug('Render complete, running cleanup()...')
    return block_position, image_output_path, str(frame_number)