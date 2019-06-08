import ast
import logging
import zlib


def decode_stream_header_ascii_compressed(bitstream, custom_color_enabled, encryption_enabled):
    '''This function encodes the raw bit string taken from the frame(s) back into ASCII, and returns the split
    components inside of it.
    '''

    logging.debug('Reading stream header...')
    custom_color_name = None
    custom_color_description = None
    custom_color_date_created = None
    custom_color_palette = None
    post_compression_sha = None

    to_bytes = bitstream.tobytes()
    logging.debug(f'ASCII header byte size inputted to read function: {int(len(bitstream) / 8)} B')
    uncompressed_string = zlib.decompress(to_bytes).decode()
    string_broken_into_parts = uncompressed_string.split('\\\\')[1:-1]
    bg_version = string_broken_into_parts[0]
    stream_name = string_broken_into_parts[1]
    stream_description = string_broken_into_parts[2]
    file_list = string_broken_into_parts[3]

    index_bump = 0
    if custom_color_enabled == True:
        custom_color_name = string_broken_into_parts[4]
        custom_color_description = string_broken_into_parts[5]
        custom_color_date_created = string_broken_into_parts[6]
        custom_color_palette = ast.literal_eval(string_broken_into_parts[7])
        index_bump += 4

    if encryption_enabled == True:
        post_compression_sha = string_broken_into_parts[4 + index_bump]

    logging.debug('Stream header ASCII part successfully read.')

    return bg_version,stream_name,stream_description,file_list,custom_color_name,custom_color_description,\
           custom_color_date_created,custom_color_palette, post_compression_sha


def decode_stream_header_binary_preamble(bitStream):
    '''This function takes the raw bit string taken from the frame(s) and extracts stream data from it.'''

    size_in_bytes = bitStream.read('uint : 64')
    total_frames = bitStream.read('uint : 32')
    compression_enabled = bitStream.read('bool')
    encryption_enabled = bitStream.read('bool')
    file_masking_enabled = bitStream.read('bool')
    is_custom_palette = bitStream.read('bool')
    date_created = bitStream.read('uint : 34')

    if is_custom_palette == False:
        stream_palette_id = str(bitStream.read('uint : 256'))

    else:
        stream_palette_id = str(bitStream.read('hex : 256'))

    ascii_header_compressed_in_bytes = bitStream.read('uint : 32')

    return size_in_bytes, total_frames, compression_enabled, encryption_enabled, file_masking_enabled, \
           is_custom_palette,  date_created, stream_palette_id, ascii_header_compressed_in_bytes

def format_file_list(file_string):
    '''This takes in the file manifest inside of the stream header, and prints it in a nice formatted way.'''

    broken_apart = file_string.split('|')[1:]
    formatted_string = ''

    for position in range(int(len(broken_apart) / 2)):
        formatted_string +=(f"\n    {broken_apart[2 * position]} - {broken_apart[2 * position + 1]} B")

    return formatted_string