import logging
import os

import bitglitter.filepackager.fileio as fileio

# filepackager and fileio modules were both written by Tanmay Mishra. https://github.com/tmishra3/


class Folder:


    def __init__(self, name = None, file_path = None):

        self.contains = []
        self.current_path = []
        self.unique_folder_names = {}
        self.unique_file_names = {}

        if file_path == None:

            self.name = name
            self.file_path = file_path

        if file_path != None:

            try:
                self.name = os.path.basename(file_path)
                self.file_path = file_path
                self.index(self.file_path)
            except:
                self.name = name
                self.file_path = None


    def copy_attributes(self, source_folder):

        self.current_path = source_folder.current_path
        self.file_path = source_folder.file_path
        self.contains = source_folder.contains
        self.name = source_folder.name
        self.unique_folder_names = source_folder.unique_folder_names
        self.unique_file_names = source_folder.unique_file_names


    def __repr__(self):

        return '[' + self.name + ']'


    def __sub__(self, other = ''):

        if type(other) is str:

            if len(self.current_path) == 0:

                for items in self.contains:

                    if items.name == other:

                        self.contains.remove(items)
                        break

            if len(self.current_path) > 0:

                self.contains[self.current_path[0]] = self.action_path(other,
                                                                       self.contains[self.current_path[0]],
                                                                      self.current_path[1:],
                                                                       action = 'Subtract')

        return self


    def __add__(self, other): #Must take in File or Folder.

        if type(other) is File or type(other) is Folder:

            if len(self.current_path) == 0:

                other = self.return_fixed_name(other)
                self.contains.append(other)

            if len(self.current_path) > 0:

                self.contains[self.current_path[0]] = self.action_path(other,
                                                                       self.contains[self.current_path[0]],
                                                                      self.current_path[1:],
                                                                       action = 'Add')

        return self


    def move_into(self, folder_name):

        this_folder = Folder()
        this_folder.copy_attributes(self)

        for index in range(0, len(self.current_path)):
            this_folder = this_folder.contains[self.current_path[index]]

        index = 0

        for items in this_folder.contains:

            if items.name == folder_name and type(items) is Folder:

                self.current_path.append(index)
                break

            index += 1


    def move_up(self):
        if len(self.current_path) > 0:
            self.current_path = self.current_path[:-1]


    def return_fixed_name(self, child_other):

        try:
            if type(child_other) is Folder:
                self.unique_folder_names[child_other.name] = self.unique_folder_names[child_other.name]
            if type(child_other) is File:
                self.unique_file_names[child_other.name] = self.unique_file_names[child_other.name]
        except:
            if type(child_other) is Folder:
                self.unique_folder_names[child_other.name] = 1
            if type(child_other) is File:
                self.unique_file_names[child_other.name] = 1
        else:
            if type(child_other) is Folder:
                self.unique_folder_names[child_other.name] += 1
            if type(child_other) is File:
                self.unique_file_names[child_other.name] += 1
        finally:
            if type(child_other) is Folder:
                name_freq = self.unique_folder_names[child_other.name]
            if type(child_other) is File:
                name_freq = self.unique_file_names[child_other.name]

        if name_freq > 1:
            if type(child_other) is Folder:
                child_other.name = child_other.name + '(' + str(name_freq) + ')'
            if type(child_other) is File:
                name = fileio.separate_file_name(child_other.name)
                child_other.name = name[0] + '(' + str(name_freq) + ')' + name[1]

        return child_other


    def action_path(self, value, folder, current_path=[], action='Add'):

        if len(current_path) == 0:

            if action == 'Add':

                if type(value) is Folder:
                    value = folder.return_fixed_name(value)
                    folder.contains.append(value)

                if type(value) is File and os.path.isfile(os.path.join(value.filePath, value.name)):
                    value = folder.return_fixed_name(value)
                    folder.contains.append(value)

            if action == 'Subtract' and type(value) is str:
                for items in folder.contains:
                    if items.name == value:
                        folder.contains.remove(items)
                        break

            return folder

        if len(current_path) > 0:

            folder.contains[current_path[0]] = self.action_path(value,
                                                                folder.contains[current_path[0]],
                                                                current_path[1:])
            return folder


    def print_folder(self, print_sub = True):

        this_folder = Folder()
        this_folder.copy_attributes(self)

        for index in range(0, len(self.current_path)):

            this_folder = this_folder.contains[self.current_path[index]]

        self.print_recursive(this_folder, '', print_sub)


    def print_recursive(self, this_folder, space ='', print_sub = True):
        '''Recursively prints folder and it's children.'''

        print(space + "[" + this_folder.name + "]:")

        for items in this_folder.contains:
            if type(items) is Folder:
                if print_sub == True:
                    items.print_recursive(items, space + '    ', print_sub)
                else:
                    print('    ' + "[" + items.name + "]:")
                    print('    ' + "..." + str(len(items.contains)) + " file(s)/folder(s)..." )

            elif type(items) is File:
                print('    ' + space + "(" + items.name + ")")


    def index(self, my_path):

        default_dir = os.getcwd()
        os.chdir(my_path)
        current = os.listdir()
        self.file_path = my_path

        for something in current:

            if os.path.isdir(os.path.join(my_path, something)):

                logging.debug("Directory Found: " + something)
                new_folder = Folder(name=str(something))
                new_folder.index(my_path + '/' + something + '/')
                self.contains.append(new_folder)

            if os.path.isfile(os.path.join(my_path, something)):

                logging.debug("File Found: " + something)
                new_file = File(my_path + '/' + something)
                new_file.file_path = my_path
                self.contains.append(new_file)

        os.chdir(default_dir)

        return self.contains


class File:

    def __init__(self, file_path = None):

        if file_path == None:

            self.name = None
            self.file_path = file_path
            self.real_name = None

        if file_path != None:

            try:
                self.real_name = os.path.basename(file_path)
                self.name = self.real_name
                self.file_path = '\\'.join(file_path.split('\\')[0:-1])
            except:
                self.name = None
                self.file_path = None
                self.real_name = None

    def __repr__(self):

        return '(' + self.name + ')'


def package(my_folder, file_name, mask):

    root = Folder(my_folder.name)
    root += my_folder
    dig(root, file_name + '\\package.dat', no_payload=False)
    logging.debug('Package created.')
    if not mask:
        dig(root, file_name + '\\file_list.txt', no_payload=True)
        logging.debug("file_list created.")
    else:
        logging.debug('fileMask enabled, skipping...')
    logging.debug("Internal filepackager process complete.")


def dig(my_folder, file_name, no_payload):

    open(file_name, 'a+').close()
    default_dir = os.getcwd()
    data_file = b''
    current = my_folder.contains

    for something in current:

        if type(something) is Folder:
            logging.debug("Directory Found: " + something.name)
            logging.debug("Writing Directory: " + something.name)

            with open(file_name, 'ab') as write_file:
                if no_payload == False:
                    write_file.write(b"<" + something.name.encode() + b">")

            dig(something, file_name, no_payload)

            with open(file_name, 'ab') as write_file:
                if no_payload == False:
                    write_file.write(b"</" + something.name.encode() + b">")

            logging.debug("Closing Directory: " + something.name)

        if type(something) is File:

            if something.file_path != None:

                logging.debug("File Found: " + something.name)

                try:

                    if no_payload == False:
                        data_file += b":" + something.name.encode() + b"|"
                        data_file += b"{" + str(os.path.getsize(os.path.join(something.file_path,
                                                                             something.real_name))).encode() + b"}"
                    else:
                        data_file += b"|" + something.name.encode() + b"|"
                        data_file += str(os.path.getsize(os.path.join(something.file_path, something.real_name))) \
                            .encode()
                    if no_payload == False:
                        data_file += open(something.file_path + '/' + something.real_name, 'rb').read()
                except:
                    data_file = b":|{0}"
                    logging.debug("\nERROR: Unable to package file, " + something.name + ", skipping.\n")


            if something.file_path == None:

                logging.debug("Virtual File Found: " + something.name)

                data_file += b":" + something.name.encode() + b"|"
                data_file += b"{0}"
                data_file += b''

            with open(file_name, 'ab') as open_file:

                logging.debug("Writing File: " + something.name)
                open_file.write(data_file)

            data_file = b''

    os.chdir(default_dir)


def unpackage(file_name, save_path, stream_SHA):

    output_path = save_path
    if save_path == None:
        output_path = os.getcwd()
    original_working_directory = os.getcwd()
    root_folder_created = False

    with open(file_name, 'rb') as open_file:

        read_byte = b''
        temp = b''
        current_file = b''

        while True:

            read_byte = open_file.read(1)

            if read_byte == b'':
                break

            if read_byte == b'<': #working with folder.

                while True:

                    read_byte = open_file.read(1)

                    if read_byte != b'>':

                        temp += read_byte
                    else:

                        if temp[0:1] != b'/':
                            logging.debug("Folder " + temp.decode('utf-8') + ' detected.')

                            if root_folder_created == True:
                                os.mkdir(os.path.join(output_path,temp.decode('utf-8')))
                                output_path += '/' + temp.decode('utf-8')
                                logging.debug("Making Folder: " + temp.decode('utf-8') + " and moving into it.")

                            else:
                                try:
                                    os.mkdir(os.path.join(output_path, stream_SHA))
                                except:
                                    pass
                                output_path += '/' + stream_SHA
                                logging.debug("Making Folder: " + stream_SHA + " and moving into it.")
                                root_folder_created = True

                            os.chdir(output_path)
                            temp = b''
                            break

                        if temp[0:1] == b'/':
                            logging.debug("Folder termination detected. Moving one directory up.")
                            os.chdir('..')
                            output_path = os.getcwd()
                            temp = b''
                            break

            if read_byte == b':':

                while True:

                    read_byte = open_file.read(1)

                    if read_byte != b'|':
                        temp += read_byte
                    else:
                        if not os.path.isdir(os.path.join(output_path, temp.decode('utf-8'))):
                            logging.debug("File " + temp.decode('utf-8') + ' detected.')
                            open(os.path.join(output_path, temp.decode('utf-8')), 'wb').close()
                            current_file = temp.decode('utf-8')
                            temp = b''
                        break
            if read_byte == b'{':

                while True:

                    read_byte = open_file.read(1)

                    if read_byte != b'}':

                        temp += read_byte
                    else:

                        logging.debug("Creating file " + current_file + "...")
                        with open(os.path.join(output_path, current_file), 'wb') as write_file:
                            write_file.write(open_file.read(int(temp)))
                        logging.debug("Data printed to " + current_file)
                        temp = b''
                        break

    os.chdir(original_working_directory)