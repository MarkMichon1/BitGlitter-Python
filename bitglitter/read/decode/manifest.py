from bitglitter.config.readmodels.readmodels import StreamFile


def manifest_unpack(manifest_dict, stream_id, save_directory, bit_index=0, file_sequence=1):
    """Takes a manifest dictionary and unpacks it into file models, and calculates their byte index within the greater
    payload.
    """

    def file_process(file_dict, file_sequence, bit_index, save_directory, stream_id):

        if 'ps' in file_dict:
            payload_bit_size = file_dict['ps'] * 8
        else:
            payload_bit_size = file_dict['rs'] * 8

        start_bit_position = bit_index
        end_bit_position = bit_index + payload_bit_size - 1

        save_path = save_directory / file_dict['fn']

        StreamFile.create(stream_id=stream_id, sequence=file_sequence, start_bit_position=start_bit_position,
                          end_bit_position=end_bit_position, save_path=str(save_path),
                          raw_file_size_bytes=file_dict['rs'], raw_file_hash=file_dict['rh'],
                          processed_file_size_bytes=file_dict['ps'] if 'ps' in file_dict else None,
                          processed_file_hash=file_dict['ph'] if 'ph' in file_dict else None)

    file_sequence = file_sequence
    bit_index = bit_index

    if 'fn' not in manifest_dict:  # Root is directory
        if 'f' in manifest_dict:
            for file in manifest_dict['f']:
                file_process(file, file_sequence, bit_index, save_directory, stream_id)
                file_sequence += 1
                if 'ps' in file:
                    bit_index += file['ps'] * 8
                else:
                    bit_index += file['rs'] * 8
        if 's' in manifest_dict:
            for subdirectory_dict in manifest_dict['s']:
                bit_index, file_sequence = manifest_unpack(subdirectory_dict, stream_id,
                                                           save_directory=save_directory / subdirectory_dict['n'],
                                                           bit_index=bit_index, file_sequence=file_sequence)

    else:  # Root is single file
        file_process(manifest_dict, file_sequence, bit_index, save_directory, stream_id)

    return bit_index, file_sequence
