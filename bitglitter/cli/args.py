import argparse

from bitglitter.cli.analyzer import CliArgumentParser

parser = argparse.ArgumentParser(description=""""Embed data payloads inside of ordinary
                                             images or video with high-performance 2-D barcodes.""")


subparsers = parser.add_subparsers(dest="subparser_name")


write_parser = subparsers.add_parser(
     'write',
     help="""This is the primary function in creating BitGlitter 
     streams from files.  Please see Wiki page for more information.""",
)

write_parser.add_argument(
     '-file',
     type=str,
     help='The file in which data will be written.'
)

write_parser.add_argument(
     '-streamname',
     type=str,
     help='Stream name.'
)

write_parser.add_argument(
     '-mode',
     type=str,
     help='File output mode: "image" or "video".'
)
write_parser.add_argument(
     '-o',
     type=str,
     help='File output path.'
)


# To implement here
read_parser = subparsers.add_parser(
     'read',
     help="""This is the high level function that decodes BitGlitter encoded images and video back into
               the files/folders contained within them.  This along with write() are the two primary
               functions of this library."""
)

read_parser.add_argument(
     '-file',
     type=str,
     help='File to be decoded.'
)

read_parser.add_argument(
     '-o',
     type=str,
     help='File to be decoded.'
)


cli_argument = vars(parser.parse_known_args()[0]).get('subparser_name')
if cli_argument == 'read':
     read_parser.set_defaults(func=CliArgumentParser.read(vars(read_parser.parse_known_args()[0])))
elif cli_argument == 'write':
     write_parser.set_defaults(func=CliArgumentParser.write(vars(write_parser.parse_known_args()[0])))

# TODO:
# parser.add_argument('--clearSession',
#                     help='Tries to remove the session pickle if it exists, clearing all statistics and custom colors.')
# parser.add_argument('--clearStats',
#                     help='Resets statistics back to zero in all fields.')
# parser.add_argument('--outputStats',
#                     help='Writes a text file to a folder path outlining usage statistics.')

# parser.add_argument('--beginAssembly',
#                     help='This function exists to initiate assembly of a package at a later time, rather than doing so' 
#                         '\nimmediately for whatever reason.')
# parser.add_argument('--printFullSaveList',
#                     help='This function will output a text file displaying the current status of all of the partial'
#                          '\nsaves in BitGlitter.  Path specifies the folder path it will be outputted to.  Argument'
#                          '\ndebugData will show various debug information pertaining to the partial save, that the'
#                          '\nnormal user has no need to see.')
# parser.add_argument('--removePartialSave',
#                     help='Taking the stream SHA as an argument, this function will remove the partial save object, as'
#                          '\nwell as remove any temporary data BitGlitter may have had with it.')
# parser.add_argument('--updatePartialSave',
#                     help="This function will update the PartialSave object with the parameters provided, once they've" 
#                         '\nbeen verified.')
# parser.add_argument('--removeAllPartialSaves',
#                     help='This removes all partial save objects saved, as well as any temporary data.')

# parser.add_argument('--addCustomPalette',
#                     help='This function allows you to save a custom palette to be used for future writes.  Arguments'
#                          '\nneeded are name, description, color set, which is a tuple of tuples, and optionally a'
#                          '\nnickname.  All other object are attributes are added in this process.  Before anything gets'
#                          '\nadded, we need to ensure the arguments are valid.')
# parser.add_argument('--editNicknameToCustomPalette')
# parser.add_argument('--clearAllCustomPalettes')
# parser.add_argument('--clearCustomPaletteNicknames')
# parser.add_argument('--printFullPaletteList')
# parser.add_argument('--removeCustomPalette')
# parser.add_argument('--removeCustomPaletteNickname')


