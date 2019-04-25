# This gets changed every new version.  It is included in the ASCII part of the stream header for diagnostic and
# debugging purposes.
BG_VERSION = "1.0"

VALID_VIDEO_FORMATS = ['.avi', '.flv', '.mov', '.mp4', '.wmv']
VALID_IMAGE_FORMATS = ['.bmp', '.jpg', '.png']

WRITE_PATH = 'Temp'
READ_PATH = 'Partial Saves'

SCRYPT_N_DEFAULT = 14
SCRYPT_R_DEFAULT = 8
SCRYPT_P_DEFAULT = 1

# Read specific
BAD_FRAME_STRIKES = 10

# Write specific
HEADER_PALETTE_ID ='4'
STREAM_PALETTE_ID ='4'
PIXEL_WIDTH = 20
BLOCK_HEIGHT = 54
BLOCK_WIDTH = 96