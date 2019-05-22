# This gets changed every new version.  It is included in the ASCII part of the stream header for diagnostic and
# debugging purposes.

# Dev note- this gets updated at version change.  This is included in ASCII stream header for debugging purposes.
BG_VERSION = "1.0"

# Default folder paths
WRITE_PATH = 'Temp'
READ_PATH = 'Partial Saves'

# Crypto
SCRYPT_N_DEFAULT = 14
SCRYPT_R_DEFAULT = 8
SCRYPT_P_DEFAULT = 1

# Read specific
BAD_FRAME_STRIKES = 10
VALID_VIDEO_FORMATS = ['.avi', '.flv', '.mov', '.mp4', '.wmv']
VALID_IMAGE_FORMATS = ['.bmp', '.jpg', '.png']

# Write specific
HEADER_PALETTE_ID ='6'
STREAM_PALETTE_ID ='6'
PIXEL_WIDTH = 24
BLOCK_HEIGHT = 45
BLOCK_WIDTH = 80
FRAMES_PER_SECOND = 30