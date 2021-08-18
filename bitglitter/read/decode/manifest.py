from bitglitter.config.readmodels.readmodels import StreamFile

def manifest_unpack(manifest_dict, byte_index=0, depth=0, file_sequence=0, save_directory=None):
    """Takes a manifest dictionary and unpacks it into file models, and calculates their byte index within the greater
    payload.
    """

    def file_thing(file_dict, depth, file_sequence, byte_index, save_directory):

        if 'ps' in file_dict:
            payload_size = file_dict['ps']
        else:
            payload_size = file_dict['rs']

        start_byte = byte_index
        end_byte = byte_index + payload_size - 1

        # add file data TODO

        if 'ps' in file_dict:
            pass

    file_sequence = file_sequence
    depth = depth
    byte_index = byte_index

    if 'fn' not in manifest_dict:  #  Root is directory
        if 'f' in manifest_dict:
            for file in manifest_dict['f']:
                file_thing(file, depth, file_sequence, byte_index, save_directory)
                file_sequence += 1
                if 'ps' in file:
                    byte_index += file['ps']
                else:
                    byte_index += file['rs']
        if 's' in manifest_dict:
            depth += 1
            for subdirectory in manifest_dict['s']:
                byte_index, file_sequence = manifest_unpack(subdirectory, byte_index, depth, file_sequence,
                                                            save_directory=save_directory / subdirectory['n'])

    else:  # Root is single file
        file_thing(manifest_dict, depth, file_sequence, byte_index, save_directory)

    return byte_index, file_sequence