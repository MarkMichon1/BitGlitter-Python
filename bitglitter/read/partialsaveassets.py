import logging
import zlib

def readStreamHeaderASCIICompressed(bitstream, customColorEnabled, encryptionEnabled):
    logging.debug('Reading stream header...')
    customColorName = None
    customColorDescription = None
    customColorDateCreated = None
    customColorPalette = None
    postCompressionSHA = None

    toBytes = bitstream.tobytes()
    logging.debug(f'ASCII header byte size inputted to read function: {int(len(bitstream) / 8)} B')
    uncompressedString = zlib.decompress(toBytes).decode()
    stringBrokenIntoParts = uncompressedString.split('\\\\')[1:-1]
    bgVersion = stringBrokenIntoParts[0]
    streamName = stringBrokenIntoParts[1]
    streamDescription = stringBrokenIntoParts[2]
    fileList = stringBrokenIntoParts[3]

    indexBump = 0
    if customColorEnabled == True:
        customColorName = stringBrokenIntoParts[4]
        customColorDescription = stringBrokenIntoParts[5]
        customColorDateCreated = stringBrokenIntoParts[6]
        customColorPalette = stringBrokenIntoParts[7]
        indexBump += 4

    if encryptionEnabled == True:
        postCompressionSHA = stringBrokenIntoParts[4 + indexBump]

    logging.debug('Stream header ASCII part successfully read.')
    return bgVersion,streamName,streamDescription,fileList,customColorName,customColorDescription,\
           customColorDateCreated,customColorPalette, postCompressionSHA


def readStreamHeaderBinaryPreamble(bitStream):
    sizeInBytes = bitStream.read('uint : 64')
    totalFrames = bitStream.read('uint : 32')
    compressionEnabled = bitStream.read('bool')
    encryptionEnabled = bitStream.read('bool')
    fileMaskingEnabled = bitStream.read('bool')
    isCustomPalette = bitStream.read('bool')
    dateCreated = bitStream.read('uint : 34')

    if isCustomPalette == False:
        streamPaletteID = bitStream.read('uint : 256')
    else:
        streamPaletteID = bitStream.read('hex : 256')

    asciiHeaderCompressedInBytes = bitStream.read('uint : 32')

    return sizeInBytes, totalFrames, compressionEnabled, encryptionEnabled, fileMaskingEnabled, isCustomPalette, \
        dateCreated, streamPaletteID, asciiHeaderCompressedInBytes

def formatFileList(fileString):
    '''This takes in the file manifest inside of the stream header, and prints it in a nice formatted way.'''

    brokenApart = fileString.split('|')[1:]
    formattedString = ''
    for position in range(int(len(brokenApart) / 2)):
        formattedString +=(f"\n    {brokenApart[2 * position]} - {brokenApart[2 * position + 1]} B")
    return formattedString