import math


def palette_verify(header_type, bit_length, block_width, block_height, output_type, fps=0):
    """This function calculates the necessary overhead for both images and videos for subsequent frames after 1.  It
    returns a number between 0-100%, for what percentage the overhead occupies.  The lower the value, the higher the
    frame efficiency.
    """

    total_blocks = block_width * block_height

    block_overhead = block_height + block_width + 323
    frame_header_in_bits = 608

    blocks_needed = 0

    if header_type == 'header_palette' or output_type == 'image':
        blocks_needed += block_overhead

    bits_available = (total_blocks - blocks_needed) * bit_length
    bits_available -= frame_header_in_bits
    occupied_blocks = blocks_needed + math.ceil(frame_header_in_bits / bit_length)

    if occupied_blocks > total_blocks:
        raise ValueError(f"{header_type} has {occupied_blocks - total_blocks} too few blocks with this configuration."
                         f"\nPlease fix this by using a palette with a larger bitlength or use more blocks per frame.")

    output_per_sec = None
    if output_type == 'video' and header_type == 'stream_palette':
        output_per_sec = bits_available * fps

    return (round(100 - (occupied_blocks / total_blocks * 100), 2)), bits_available, output_per_sec
