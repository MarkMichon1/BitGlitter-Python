# This gets changed every new version.  It is included in the ASCII part of the stream header for diagnostic and
# debugging purposes.

# Dev note- this gets updated at version change.  This is included in ASCII stream header for debugging purposes.
BG_VERSION = "1.0" #todo move

# Default folder paths
DEFAULT_WRITE_PATH = 'Temp'
DEFAULT_READ_PATH = 'Partial Saves'

# Crypto
DEFAULT_SCRYPT_N = 14
DEFAULT_SCRYPT_R = 8
DEFAULT_SCRYPT_P = 1

# Read specific
DEFAULT_BAD_FRAME_STRIKES = 10
VALID_VIDEO_FORMATS = ['.avi', '.flv', '.mov', '.mp4', '.wmv'] #todo move
VALID_IMAGE_FORMATS = ['.bmp', '.jpg', '.png'] #todo move

# Write specific
DEFAULT_HEADER_PALETTE_ID = '6'
DEFAULT_STREAM_PALETTE_ID = '6'
DEFAULT_PIXEL_WIDTH = 24
DEFAULT_BLOCK_HEIGHT = 45
DEFAULT_BLOCK_WIDTH = 80
DEFAULT_FPS = 30

#todo- move to config