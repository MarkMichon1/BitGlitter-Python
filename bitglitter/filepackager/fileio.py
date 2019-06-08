import os

#Written by Tanmay Mishra.  See filepackager module for more information.

def copy_file(source, destination, byte_start=None, byte_end=None):

    try:
        write_file = open(str(destination), 'wb')

        with open(str(source), 'rb') as open_file:
            write_file.write(open_file.read()[byte_start:byte_end])

        write_file.close()
        return True

    except:
        return False

def file_to_bytes(file_name, byte_start=None, byte_end=None):

    try:
        with open(file_name, 'rb') as open_file:
            my_bytes = open_file.read()[byte_start:byte_end]
        return my_bytes

    except:
        return b''


def bytes_to_file(file_name, my_bytes):
    try:

        with open(file_name, 'wb') as write_file:
            write_file.write(my_bytes)
        return True
    except:
        return False

def bytes_or_files_to_bytes(items=[]):

    bytes_return = b''

    for item in items:
        if type(item) is bytes:
            bytes_return += item
        if type(item) is str and does_file_exist(item):
            bytes_from_file = file_to_bytes(item)
            bytes_return += bytes_from_file

    return bytes_return

def bytes_or_files_to_file(file_name, items=[]):

    try:
        my_bytes = bytes_or_files_to_bytes(items)
        return bytes_to_file(file_name, my_bytes)
    except:
        delete_file(file_name)
        return False

def does_file_exist(file_name):

    return os.path.isfile(file_name)

def get_file_size(file_name):
    try:
        return os.path.getsize(str(file_name))
    except:
        return None

def delete_file(file_name):

    try:
        os.remove(str(file_name))
        return True
    except:
        return False

def separate_file_name(file_name =""):

    index_ext = 0
    len_file = len(file_name)

    for i in range(0,len_file):
        if file_name[(len_file - i):len_file - i + 1] == '.':
            index_ext = len_file-i
            break

    if file_name[index_ext:] == file_name:
        return [file_name[index_ext:], file_name[0:index_ext]]
    else:
        return [file_name[0:index_ext], file_name[index_ext:]]