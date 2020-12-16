def humanize_file_size(size_in_bytes):
    if 0 < size_in_bytes < 1000:
        return f'{size_in_bytes} B'
    elif 1000 <= size_in_bytes < 1000 ** 2:
        return f'{round((size_in_bytes / 1000), 2)} KB'
    elif 1000 ** 2 <= size_in_bytes < 1000 ** 3:
        return f'{round((size_in_bytes / 1000 ** 2), 2)} MB'
    elif 1000 ** 3 <= size_in_bytes < 1000 ** 4:
        return f'{round((size_in_bytes / 1000 ** 3), 2)} GB'
    elif 1000 ** 4 <= size_in_bytes < 1000 ** 5:
        return f'{round((size_in_bytes / 1000 ** 4), 2)} TB'
    elif 1000 ** 5 <= size_in_bytes < 1000 ** 6:
        return f'{round((size_in_bytes / 1000 ** 5), 2)} PB'


def format_file_list(file_string):  # todo: redo with new manifest
    """This takes in the file manifest inside of the stream header, and prints it in a nice formatted way."""
    pass
    # broken_apart = file_string.split('|')[1:]
    # for position in range(int(len(broken_apart) / 2)):
    #     print(f"    {broken_apart[2 * position]} - {broken_apart[2 * position + 1]} B")
