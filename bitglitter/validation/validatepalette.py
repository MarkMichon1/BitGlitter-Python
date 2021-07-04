def palette_geometry_verify(stream_palette_bit_length, block_width, block_height, output_type, fps=0):
    """This function calculates the necessary overhead for both images and videos for subsequent frames after 1.  It
    returns a number between 0-100%, for what percentage the overhead occupies.  The lower the value, the higher the
    frame efficiency.
    """

    total_blocks = block_width * block_height

    INITIALIZER_OVERHEAD = block_height + block_width + 579
    FRAME_HEADER_BITS = 352
    occupied_blocks = 0

    if output_type == 'image':
        total_blocks -= INITIALIZER_OVERHEAD
        occupied_blocks += INITIALIZER_OVERHEAD
    bits_available_per_frame = (total_blocks * stream_palette_bit_length) - FRAME_HEADER_BITS
    occupied_blocks += int(FRAME_HEADER_BITS / stream_palette_bit_length)

    payload_frame_percentage = round((((total_blocks - occupied_blocks) / total_blocks) * 100), 2)

    output_per_sec = 0
    if output_type == 'video':
        output_per_sec = bits_available_per_frame * fps

    return payload_frame_percentage, bits_available_per_frame, output_per_sec


def custom_palette_values_validate(name_string, description_string, ):
    pass