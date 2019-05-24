import logging
import os

import bitglitter.filepackager.fileio as fileio

# filepackager and fileio modules were both written by Tanmay Mishra. https://github.com/tmishra3/


class Folder:


    def __init__(self, name = None, filePath = None):

        self.contains = []
        self.currentPath = []
        self.uniqueFolderNames = {}
        self.uniqueFileNames = {}

        if filePath == None:

            self.name = name
            self.filePath = filePath

        if filePath != None:

            try:
                self.name = os.path.basename(filePath)
                self.filePath = filePath
                self.index(self.filePath)
            except:
                self.name = name
                self.filePath = None


    def copyAttributes(self, sourceFolder):

        self.currentPath = sourceFolder.currentPath
        self.filePath = sourceFolder.filePath
        self.contains = sourceFolder.contains
        self.name = sourceFolder.name
        self.uniqueFolderNames = sourceFolder.uniqueFolderNames
        self.uniqueFileNames = sourceFolder.uniqueFileNames


    def __repr__(self):

        return '[' + self.name + ']'


    def __sub__(self, other = ''):

        if type(other) is str:

            if len(self.currentPath) == 0:

                for items in self.contains:

                    if items.name == other:

                        self.contains.remove(items)
                        break

            if len(self.currentPath) > 0:

                self.contains[self.currentPath[0]] = self.actionPath(other,
                                                                     self.contains[self.currentPath[0]],
                                                                     self.currentPath[1:],
                                                                     action = 'Subtract')

        return self


    def __add__(self, other): #Must take in File or Folder.

        if type(other) is File or type(other) is Folder:

            if len(self.currentPath) == 0:

                other = self.returnFixedName(other)
                self.contains.append(other)

            if len(self.currentPath) > 0:

                self.contains[self.currentPath[0]] = self.actionPath(other,
                                                                     self.contains[self.currentPath[0]],
                                                                     self.currentPath[1:],
                                                                     action = 'Add')

        return self


    def moveInto(self, folderName):

        thisFolder = Folder()
        thisFolder.copyAttributes(self)

        for index in range(0,len(self.currentPath)):
            thisFolder = thisFolder.contains[self.currentPath[index]]

        index = 0

        for items in thisFolder.contains:

            if items.name == folderName and type(items) is Folder:

                self.currentPath.append(index)
                break

            index += 1


    def moveUp(self):
        if len(self.currentPath) > 0:
            self.currentPath = self.currentPath[:-1]


    def returnFixedName(self, childOther):

        try:
            if type(childOther) is Folder:
                self.uniqueFolderNames[childOther.name] = self.uniqueFolderNames[childOther.name]
            if type(childOther) is File:
                self.uniqueFileNames[childOther.name] = self.uniqueFileNames[childOther.name]
        except:
            if type(childOther) is Folder:
                self.uniqueFolderNames[childOther.name] = 1
            if type(childOther) is File:
                self.uniqueFileNames[childOther.name] = 1
        else:
            if type(childOther) is Folder:
                self.uniqueFolderNames[childOther.name] += 1
            if type(childOther) is File:
                self.uniqueFileNames[childOther.name] += 1
        finally:
            if type(childOther) is Folder:
                nameFreq = self.uniqueFolderNames[childOther.name]
            if type(childOther) is File:
                nameFreq = self.uniqueFileNames[childOther.name]

        if nameFreq > 1:
            if type(childOther) is Folder:
                childOther.name = childOther.name + '(' + str(nameFreq) + ')'
            if type(childOther) is File:
                name = fileio.separateFileName(childOther.name)
                childOther.name = name[0] + '(' + str(nameFreq) + ')' + name[1]

        return childOther


    def actionPath(self, value, folder, currentPath=[], action='Add'):

        if len(currentPath) == 0:

            if action == 'Add':

                if type(value) is Folder:
                    value = folder.returnFixedName(value)
                    folder.contains.append(value)

                if type(value) is File and os.path.isfile(os.path.join(value.filePath, value.name)):
                    value = folder.returnFixedName(value)
                    folder.contains.append(value)

            if action == 'Subtract' and type(value) is str:
                for items in folder.contains:
                    if items.name == value:
                        folder.contains.remove(items)
                        break

            return folder

        if len(currentPath) > 0:

            folder.contains[currentPath[0]] = self.actionPath(value,
                                                              folder.contains[currentPath[0]],
                                                              currentPath[1:])
            return folder


    def printFolder(self, printSub = True):

        thisFolder = Folder()
        thisFolder.copyAttributes(self)

        for index in range(0,len(self.currentPath)):

            thisFolder = thisFolder.contains[self.currentPath[index]]

        self.printRecursive(thisFolder,'',printSub)


    def printRecursive(self, thisFolder, space = '', printSub = True): #Recursively prints folder and its
        #children.

        print(space + "[" + thisFolder.name + "]:")

        for items in thisFolder.contains:
            if type(items) is Folder:
                if printSub == True:
                    items.printRecursive(items, space + '    ', printSub)
                else:
                    print('    ' + "[" + items.name + "]:")
                    print('    ' + "..." + str(len(items.contains)) + " file(s)/folder(s)..." )

            elif type(items) is File:
                print('    ' + space + "(" + items.name + ")")


    def index(self, myPath):

        default_dir = os.getcwd()
        os.chdir(myPath)
        current = os.listdir()
        self.filePath = myPath

        for something in current:

            if os.path.isdir(os.path.join(myPath, something)):

                logging.debug("Directory Found: " + something)
                newFolder = Folder(name=str(something))
                newFolder.index(myPath + '/' + something + '/')
                self.contains.append(newFolder)

            if os.path.isfile(os.path.join(myPath, something)):

                logging.debug("File Found: " + something)
                newFile = File(myPath + '/' + something)
                newFile.filePath = myPath
                self.contains.append(newFile)

        os.chdir(default_dir)

        return self.contains


class File:

    def __init__(self, filePath = None):

        if filePath == None:

            self.name = None
            self.filePath = filePath
            self.realName = None

        if filePath != None:

            try:
                self.realName = os.path.basename(filePath)
                self.name = self.realName
                self.filePath = '\\'.join(filePath.split('\\')[0:-1])
            except:
                self.name = None
                self.filePath = None
                self.realName = None

    def __repr__(self):

        return '(' + self.name + ')'


def package(myFolder, fileName, mask):

    root = Folder(myFolder.name)
    root += myFolder
    dig(root, fileName + '\\package.dat', noPayload=False)
    logging.debug('Package created.')
    if not mask:
        dig(root, fileName + '\\fileList.txt', noPayload=True)
        logging.debug("fileList created.")
    else:
        logging.debug('fileMask enabled, skipping...')
    logging.debug("Internal filepackager process complete.")


def dig(myFolder, fileName, noPayload):

    open(fileName, 'a+').close()
    default_dir = os.getcwd()
    dataFile = b''
    current = myFolder.contains

    for something in current:

        if type(something) is Folder:
            logging.debug("Directory Found: " + something.name)
            logging.debug("Writing Directory: " + something.name)

            with open(fileName,'ab') as write_file:
                if noPayload == False:
                    write_file.write(b"<" + something.name.encode() + b">")

            dig(something, fileName, noPayload)

            with open(fileName,'ab') as write_file:
                if noPayload == False:
                    write_file.write(b"</" + something.name.encode() + b">")

            logging.debug("Closing Directory: " + something.name)

        if type(something) is File:

            if something.filePath != None:

                logging.debug("File Found: " + something.name)

                try:

                    if noPayload == False:
                        dataFile += b":" + something.name.encode() + b"|"
                        dataFile += b"{" + str(os.path.getsize(os.path.join(something.filePath, something.realName)))\
                            .encode() + b"}"
                    else:
                        dataFile += b"|" + something.name.encode() + b"|"
                        dataFile += str(os.path.getsize(os.path.join(something.filePath, something.realName))) \
                            .encode()
                    if noPayload == False:
                        dataFile += open(something.filePath + '/' + something.realName, 'rb').read()
                except:
                    dataFile = b":|{0}"
                    logging.debug("\nERROR: Unable to package file, " + something.name + ", skipping.\n")


            if something.filePath == None:

                logging.debug("Virtual File Found: " + something.name)

                dataFile += b":" + something.name.encode() + b"|"
                dataFile += b"{0}"
                dataFile += b''

            with open(fileName,'ab') as open_file:

                logging.debug("Writing File: " + something.name)
                open_file.write(dataFile)

            dataFile = b''

    os.chdir(default_dir)


def unpackage(fileName, savePath, streamSHA):

    outputPath = savePath
    if savePath == None:
        outputPath = os.getcwd()
    originalWorkingDirectory = os.getcwd()
    rootFolderCreated = False

    with open(fileName,'rb') as open_file:

        readByte = b''
        temp = b''
        currentFile = b''

        while True:

            readByte = open_file.read(1)

            if readByte == b'':
                break

            if readByte == b'<': #working with folder.

                while True:

                    readByte = open_file.read(1)

                    if readByte != b'>':

                        temp += readByte
                    else:

                        if temp[0:1] != b'/':
                            logging.debug("Folder " + temp.decode('utf-8') + ' detected.')

                            if rootFolderCreated == True:
                                os.mkdir(os.path.join(outputPath,temp.decode('utf-8')))
                                outputPath += '/' + temp.decode('utf-8')
                                logging.debug("Making Folder: " + temp.decode('utf-8') + " and moving into it.")

                            else:
                                try:
                                    os.mkdir(os.path.join(outputPath, streamSHA))
                                except:
                                    pass
                                outputPath += '/' + streamSHA
                                logging.debug("Making Folder: " + streamSHA + " and moving into it.")
                                rootFolderCreated = True

                            os.chdir(outputPath)
                            temp = b''
                            break

                        if temp[0:1] == b'/':
                            logging.debug("Folder termination detected. Moving one directory up.")
                            os.chdir('..')
                            outputPath = os.getcwd()
                            temp = b''
                            break

            if readByte == b':':

                while True:

                    readByte = open_file.read(1)

                    if readByte != b'|':
                        temp += readByte
                    else:
                        if not os.path.isdir(os.path.join(outputPath, temp.decode('utf-8'))):
                            logging.debug("File " + temp.decode('utf-8') + ' detected.')
                            open(os.path.join(outputPath, temp.decode('utf-8')), 'wb').close()
                            currentFile = temp.decode('utf-8')
                            temp = b''
                        break
            if readByte == b'{':

                while True:

                    readByte = open_file.read(1)

                    if readByte != b'}':

                        temp += readByte
                    else:

                        logging.debug("Creating file " + currentFile + "...")
                        with open(os.path.join(outputPath, currentFile), 'wb') as write_file:
                            write_file.write(open_file.read(int(temp)))
                        logging.debug("Data printed to " + currentFile)
                        temp = b''
                        break

    os.chdir(originalWorkingDirectory)