import os

#Written by Tanmay Mishra.  See filepackager module for more information.

def copyFile(src, dest, byteStart=None, byteEnd=None):

    try:
        write_file = open(str(dest), 'wb')

        with open(str(src), 'rb') as open_file:
            write_file.write(open_file.read()[byteStart:byteEnd])

        write_file.close()
        return True

    except:
        return False

def fileToBytes(fileName, byteStart=None, byteEnd=None):

    try:
        with open(fileName, 'rb') as open_file:
            myBytes = open_file.read()[byteStart:byteEnd]
        return myBytes

    except:
        return b''


def bytesToFile(fileName, myBytes):
    try:

        with open(fileName, 'wb') as write_file:
            write_file.write(myBytes)
        return True
    except:
        return False

def bytesOrFilesToBytes(items=[]):

    bytesReturn = b''

    for item in items:
        if type(item) is bytes:
            bytesReturn += item
        if type(item) is str and doesFileExist(item):
            bytesFromFile = fileToBytes(item)
            bytesReturn += bytesFromFile

    return bytesReturn

def bytesOrFilesToFile(fileName, items=[]):

    try:
        myBytes = bytesOrFilesToBytes(items)
        return bytesToFile(fileName,myBytes)
    except:
        deleteFile(fileName)
        return False

def doesFileExist(fileName):

    return os.path.isfile(fileName)

def getFileSize(fileName):
    try:
        return os.path.getsize(str(fileName))
    except:
        return None

def deleteFile(fileName):

    try:
        os.remove(str(fileName))
        return True
    except:
        return False

def separateFileName(fileName = ""):

    indexExt = 0
    lenFile = len(fileName)

    for i in range(0,lenFile):
        if fileName[(lenFile-i):lenFile-i+1] == '.':
            indexExt = lenFile-i
            break

    if fileName[indexExt:] == fileName:
        return [fileName[indexExt:],fileName[0:indexExt]]
    else:
        return [fileName[0:indexExt],fileName[indexExt:]]