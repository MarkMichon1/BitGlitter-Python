![BitGlitter Logo](https://i.imgur.com/pX8b4Dy.png)

# Python Library (you are here) | [Electron Desktop App](https://github.com/MarkMichon1/BitGlitter) | [Python Backend For App](https://github.com/MarkMichon1/BitGlitter-Backend)

## Store and transfer files using high-performance animated barcodes ⚡

![BitGlitter Sample GIF](https://i.imgur.com/lPFR5kA.gif) 

**[Discord Server](https://discord.gg/t9uv2pZ)** 
[![Downloads](https://pepy.tech/badge/bitglitter)](https://pepy.tech/project/bitglitter)

**[Youtube video of a real stream transferring ~75KB/s of data](https://www.youtube.com/watch?v=KI1lSVkSO-c)**

BitGlitter is an easy to use Python library that lets you embed data inside ordinary pictures or video.  Store and host
files wherever images or videos can be hosted.  The carrier for data is the 'blocks' within the frames and not
the file itself, and there are various measures to read imperfect distorted frames.  What this means for you is streams
are resistant to compression and distortion, and aren't broken by things such as format changes, metadata changes, etc.
BitGlitter gives you a unique way to make your data more portable.

### Using ordinary barcodes as a launchpad

Barcodes and QR codes are everywhere.  They embed binary data (0's and 1's) in them, symbolized as black and white.  While
they are pretty constrained in the real world, using them for digital transfer removes many of those limits.  What if you
could have multiple barcodes (frames), that if read sequentially could have the capacity of many thousands of individual
ones?  What if we added colors to the barcodes, so a given barcode could have 2x, 6x, 24x the capacity?  What if we greatly
increased the size of the frames to lets say the size of a standard 1080p video, so the frames once again increase their
capacity by a couple orders of magnitude.  Combine all of these together, and you're able to move serious amounts of 
data.  This is BitGlitter.

![BitGlitter Default Palettes](https://i.imgur.com/T6CiFOf.png)

+ **Fully configurable stream creation:** `tba`
+ **Built in file integrity:**

+ **Multiple Color Palettes:**  By removing the constraint of only using black and white, the amount of data you can 
hold in a given "block" (each square) on the frame skyrockets.  The regular two color setup holds one bit per block.  
Four colors holds two  bits (2x), sixty-four colors holds six bits (6x), and lossless ~16.7M color palette holds 24 bits 
(24x improvement over black & white).  You choose what color palette you'd like to use according to your application.  
Smaller sets are far resistant to compression and corruption, while larger sets have higher data densities.  You can
create your own custom palettes as well with whatever colors you'd like to use.  More about that below.
+ **Multi-Frame Videos:** BitGlitter automatically breaks up larger files into multiple frames, with several headers
built into them.  These include several layers of protection against corruption, as well as metadata about the frame
as well as the stream itself so the reader can intelligently decide how to handle it.  By stitching these frames
 together and turning them into a video, you can embed files and folders of arbitrary size into videos and images.  
You're only limited by your hard drive.
+ **Variable block size:** Each of the blocks in the frame can be set to any size, including one pixel.  Larger block 
sizes give your stream protection in lossy environments, while smaller blocks allow for greater densities.

Currently, BitGlitter is configured to transport files and folders on a computer.  But with minimal modification you can
use videos or images as a carrier for virtually any kind of binary data.

### What this means in practical terms

Here's some real data that gives you an idea of what is possible with this:

Number of Colors | Bits Per Block | Screen Resolution | Block Size in Pixels | Block Dimensions | Framerate | Throughput | Lossless Application
--- | --- | --- | --- | --- | --- | --- | ---
2 | 1 | 640 x 480 (480p) | 20 | 32 x 24 | 30 | 2.88 KB/s | No
4 | 2 | 1280 × 720 (720p) | 20 | 64 x 36 | 30 | 17.28 KB/s | No
8 | 3 | 1280 × 720 (720p) | 20 | 64 x 36 | 30 | 25.92 KB/s | No
16 | 4 | 1920 x 1080 (1080p) | 20 | 96 x 54 | 30 | 77.76 KB/s | No
64 | 6 | 1920 x 1080 (1080p) | 20 | 96 x 54 | 30 | 116.64 KB/s | No
64 | 6 | 1920 x 1080 (1080p) | 20 | 96 x 54 | 60 | 233.28 KB/s | No
16,777,216 | 24 | 1920 x 1080 (1080p) | 5 | 384 x 216 | 30 | 7.47 MB/s | Yes
16,777,216 | 24 | 3840 x 2160 (4k) | 5 | 768 x 432 | 60 | 59.7 MB/s | Yes

Put simply, you can now make videos that can hold large amounts of data inside of them.  There may be some pretty
interesting applications that can come out of this.

# Features

### Data

+ **Supports streams up to ~1 [EB](https://en.wikipedia.org/wiki/Exabyte) in size, or ~4.3B rendered frames:**  In other words,
  there is no practical limit to the stream's size.
+ **Compression added:** This is done automatically, so don't worry about putting your files in a rar or zip prior to
sending.
+ **Encryption added:** Optional AES-256 encryption to protect your files.  Passwords are hashed with `scrypt`, 
parameters can be customized for your needs.
+ **File masking:**  Optional ability to mask what files are included in the stream.  Only those who successfully grab 
the stream (and decrypt it if applicable) will know of its contents.

### Outputted Files

You can choose between either outputting all of your frames as a series of images (.png), or as a single .mp4.

+ **Customizable resolution:** You have complete control of the size of the outputted frames, whether they are 480p or
8K.
+ **Customizable framerate:** Currently supports 30 and 60 FPS, custom values are coming soon.

![Custom Color Showcase](https://i.imgur.com/YGfHhKE.png)

+ **Custom Color Palettes:** The included default palettes are just a starting point.  Make any color palette that you
want to match the aesthetic where it's being used.  Anyone reading the stream will have the palette automatically saved
to their machine, so then they can use it as well!  Functionality is included to output a text file outlining all of the
color palettes you have available to use, both default and custom.

### Reading

+ **Error correction against compression or corruption:** BitGlitter protects your file against corruption and artifacts 
on the image or video. After loading the correct palette, whenever it detects an incorrect color, it will "snap" it to 
the nearest color in the palette.  This gives your file resistance against format changes, codecs, or file size 
reduction.  This allows BitGlitter streams to still be read in environments that would otherwise render all existing 
steganography methods unreadable.

+ **Complete file integrity:** When the stream is created, a hash (SHA-256) is taken of the entire stream, as
well as each frame.  The data must match what is expected to be accepted.  Damaged or corrupt files will not be blindly
passed on to you.

+ **Streamlined frame bypassing:**  If a frame cannot or doesn't need to be read (ie, a duplicate already read), the 
reader determines this from an initial frame header

### Design

+ **No metadata saved in the rendered file:**  Compress the stream, change formats, upload it wherever.  All data is 
encoded in the frames itself unlike most steganography, giving your files much more protection against corruption.

+ **Easy to understand:** Whether you're learning about Python and want to understand how it works, or you're looking to
contribute, docstrings and notes are throughout the library.

+ **Built in future-proofing:** As of now, BitGlitter has a single protocol (Protocol 1), which is a specific set of
  procedures around how data is handled, and the components of a frame, as well as their layout.  Each protocol has its
  own unique ID to identify it with.  This ID is added in the  header during the write process, and is picked up at 
  `read()`.  As new protocols get created, older versions of BitGlitter that don't have these included will notify the
  user to update their version in order for it to be read.  All older protocol versions are saved in future library
  iterations, so no matter how old the protocol version is used on the stream, it will always be able to be read.

+ **Fully modular design:** Do you have a specialized use case?  Adapting this library to your own needs is quite easy.
  I've built BitGlitter to be easy to modify and expand upon.  Rather than worrying about the lower-level functionality,
  achieve your goal with the modular components I've created.


### Applications
To be determined by you, the end user!  This will be updated as the library becomes more popular.

# Using BitGlitter

All of the functions to run this library are explained below.  I'm also working on several Wikipedia pages, explaining
BitGlitter in greater detail (how it works, etc) with some included illustrations.  These are not yet complete, 
[but here is the link to the project's Wiki if you'd like to see it!](https://github.com/MarkMichon1/BitGlitter/wiki/Using-BitGlitter)

## Installation

In addition to downloading the code from Github, you can also grab it directly from PyPI:

`pip install bitglitter`

##**The 2 Core Functions of BitGlitter**

Ignoring the bells and whistles for now, all you need to use BitGlitter is `write()` and `read()` 

+ `write()` takes your files and directories, and creates the BitGlitter stream (either as a video of a collection of 
images).
+ `read()` scans your BitGlitter encoded files and outputs the files/directories embedded in it.

## write() -- converting files and directories into BitGlitter streams

We'll go a bit more in depth now.

`write()` is the function that inputs files and turns them into a BitGlitter stream.  There are quite a few arguments
to customize the stream, but there is only one required argument.  Everything else has defaults.

`input_path` defines what file or folder you wish to embed in the stream.  It must be an absolute path.

`preset_nickname` allows you to use a saved assortment of `write` arguments with a `str` nickname for easy switching 
between preferred configs.  Learn more below in the **Preset Configuration** section.

`stream_name=''` **Required** argument to name your stream, which will be printed out on the screen of whoever
reads the file, along with other stream data. TODO: 150 char max

`stream_description=''` serves as a text field to optionally put a description for the stream.

`output_directory=False` is where you can optionally define the path of where the created media is outputted.  By
default, media is saved where the python file is ran.  The folder path must already exist if used.

`output_mode='video'` is where you define how you wish the stream to output, whether as an .mp4 video, or a series of
.png images.  The only two valid arguments are `'image'` and `'video'`.

`stream_name_file_output=False` Contols if outputted files will use the stream's SHA-256 as a name, or the provided name
for the stream.  By default, it uses the SHA-256, a 64 character hex 'thumbprint' of the stream.

`max_cpu_cores=0` determines how many CPU cores you'd like to use when rendering frames.  0 is default, which is
maximum.

`compression_enabled=True` enables or disables compression of your data, prior to rendering into frames.  
This is enabled by default.

`file_mask_enabled=False` is where you can omit the listing of files/folders from the stream header.  This effectively
hides the contents of the stream, unless it is fully read.  By default, this is disabled.  What this means is when
someone reads your stream, in the first several frames it will automatically display the contents of the stream (files
as well as their size) on the screen.

`encryption_key=''` optionally encrypts your data with AES-256.  By default, this is disabled.  The stream will not be
able to be read unless the reader successfully inputs this.

Arguments `scrypt_N=14`, `scrypt_R=8` and `scrypt_P=1` allow you to customize the parameters of the `scrypt` key 
derivation function.  If you're a casual user, you'll never need to touch these (and shouldn't).  Only change these 
settings if you're comfortable with cryptography and you know what you're doing!  It's worth noting `scrypt_N` uses its
argument as 2^n.  Finally, if you're changing these numbers, they MUST be manually inputted during `read()` otherwise 
decryption will fail!  Custom values are deliberately not transmitted in the stream for security reasons.  Your end 
users of the stream must know these custom parameters.

`stream_palette_id='6'` sets the palette used for the payload after the initialization headers,  By default, the 4 bit
default color set is used.  I'll 
explain all about palettes below.

`pixel_width=24` sets how many pixels wide each block is when rendered.  By default it's 20 pixels.  This is a very
important value regarding readability.  Having them overly large will make reading them easier, but will result in less
efficient frames and require substantially longer streams.  Making them very small will greatly increase their
efficiency, but at the same time a lot more susceptible to read failures if the files are shrunk, or otherwise
distorted.

`block_height=45` sets how many blocks tall the frame will be, by default this is set to 45 (which along with 
`block_width`, creates a perfect 1080p sized frame).

`block_width=80` sets how many blocks wide the frame will be.  By default this is set to 96.

`frames_per_second=30` sets how many frames per second the video will play at, assuming argument 
`output_mode = "video"`. Currently, 30fps and 60fps are accepted.

Finally we have several arguments to control logging.

`logging_level='info'` determines what level logging messages get outputted.  It accepts three arguments- `info` is
default and only shows core status data during `read()` and `write()`.  `'debug'`  shows INFO level messages as well as
lower level messages from the various processes.  Boolean `False` disables logging altogether.

`logging_stdout_output=True` sets whether logging messages are displayed on the screen or not.  Only accepts type 
`bool`. Enabled by default.

`logging_txt_output=False` determines whether logging messages are saved as text files or not.  Only accepts type 
`bool`. Disabled by default.  If set to `True`, a log folder will be created, and text files will be automatically saved
there.

`save_session_overview=False` saves an overview of the write session as an object, storing some key information about
it such as files rendered, stream size, configuration settings, etc.  Its main use will be for the desktop app coming
soon, but you can still call it with `tba`.  Function for both an ID, and all of them.

`save_statistics=False` saves some fun statistics about your usage of the program- total number of blocks rendered,
total frames rendered, and total payload data rendered.  This updates after each successful write session.  Functions
to interact with this data are below.

These default values have an 81KB/s transmission rate.  This is a safe starting point that should be pretty resistant to
corruption.

## read() -- converting BitGlitter streams back into directories and files

`read()` is what you use to input BitGlitter streams (whether images or video), and will output the files.  While this 
is the basic function to decode streams, there are several other functions included to interact with these streams 
(inputting the password, removing one or all streams, changing its save path, etc).  Please check **Read Functions** 
below.

Like with `write()`, the only argument required is the input path (`file_path`), except in this case it accepts files
only, not directories.  Files can either be a supported video format (.avi, .flv, .mov, .mp4, .wmv) or a support image
format (.bmp, .jpg, .png).

`output_directory=False` Is where you can set where files will be written as they become available through decoding.
  It's 'set and forget', so if you are loading images this argument only has to be used once, and the folder path will
  stick with that stream.  This argument requires a string of a folder path that already exists.

`bad_frame_strikes=25` This sets how many corrupted frames the reader is to detect before it aborts out of a video.  
This allows you to break out of a stream relatively quickly if the video is substantially corrupted, without needing to
 iterate over each frame.  If this is set to 0, it will disable strikes altogether, and attempt to read each frame 
 regardless of the level of corruption.

`max_cpu_cores=0` determines the amount of CPU cores to utilize during decoding, like `write()`.  The default value of 0
sets it to maximum.

`live_payload_unpackaging=False` gives you the option to receive files in realtime as frame payloads get processed, rather than them getting processed all at once at the end of the frame processing.  The tradeoff is a small amount of overhead at the end of each frame to do the necessarily calculations/checks.  Enable this if you're reading a large stream with a large amount of files, and you'd like to start receiving them ASAP.

`block_height_override=False` and `block_width_override=False` allow you to manually input the stream's block height and 
block width.  Normally you'll never need to use this, as these values are automatically obtained as the frame is locked
onto.  But for a badly corrupted or compressed frame, this may not be the case.  By using the override, the reader will
attempt to lock onto the screen given these parameters.  Both must be filled in order for the override to work.

`stream_palette_id_override=False` is something you'd only touch if reading from
a folder of images (of BitGlitter frames)

`encryption_key=None` is where you add the encryption key to decrypt the stream.  Like argument `output_directory`, you only
need this argument once, and it will bind to that save.

`logging_level='info'`, `logging_stdout_output=True`, `logging_txt_output=False`, and `save_statistics=False` are 
arguments as well.  Scroll a little bit up to see them explained in `write()`

## Configuration Functions

### Custom Color Palette Functions

If you aren't happy with the 8 'official' palettes included with the library, you also have the freedom to create and 
use your own, to have them match with whatever aesthetic/style or performance you want.  The entire process is very simple.
There is nothing you have to do for other people to read streams using your custom palettes; the software automagically
'learns' and adds them through a special header on the stream, which then gives the ability for others to use your palette
as well.  If you want to share your palette with others without them needing to read a BitGlitter stream, we got you 
covered.  Custom palettes can also be imported and exported with [Base64](https://en.wikipedia.org/wiki/Base64) encoded 
share strings.

`add_custom_palette(palette_name, color_set, nickname='', palette_description='')` Creates a custom palette.  Once it has
been created, a string of its unique ID is returned to you (a SHA-256 of its values as well as a timestamp, making it more
or less entirely unique to that palette).

+ `palette_name` is the its name which will it will be saved as.  It has a max length of 50 characters.

+ `palette_description` is an optional field to include a brief description that will be attached with it.  It has a max
length of 100 characters.

+ `color_set` Is the actual colors that will be used in it.  It can be a list of lists, or a tuple of tuples (no 
difference) of [RGB24](https://en.wikipedia.org/wiki/RGB_color_model) values.  Heres an example to give you a better 
idea: `color_set=((0, 255, 0), (0, 0, 255))`.  There are a few constraints you must follow:
  + No two identical values can be added.  For instance, the color black with the same RGB values twice.  Each color used
must be unique!  The more 'different' the colors are in terms of their values, the better.
  + A minimum of two colors must be used.
  + You must have 2^n total colors (2, 4, 8, 16, 32, etc), with up to 256 currently supported.

+ `nickname` is an optional field that is a shorter, simple way to remember and use the palette, rather than its long
generated ID.  Both serve as a unique way to identify the palette.

`return_palette(palette_id=None, palette_nickname=None)` Returns a dictionary object of all of the palettes values.

`edit_nickname_to_custom_palette(palette_id, existing_nickname, new_nickname)` Allows you to change the nickname of the 
palette.  Please note that the nickname must be unique, and no other palettes may already be using it.

`export_palette_base64(palette_id=None, palette_nickname=None)` Export any of your custom palettes using this.  It returns
a share code which anyone can use to import your palette.

`import_palette_base64(base64_string)` Import palettes from a unique share code (see directly above).

`generate_sample_frame(directory_path, palette_id=None, palette_nickname=None, all_palettes=False, include_default=False)` 
Generates a small 'thumbprint' frame of a palette, giving you an idea of how it would appear in a normal rendering.  
`directory_path` is an existing directory in which it will be saved. `all_palettes` toggles whether you want to get a 
sample from a specific palette (using `palette_id` or `palette_nickname`) or all palettes saved.  `include_default` toggles
whether you want to include all default palettes in the generated output, or if you only want to generate custom palettes.

`return_all_palettes()` Returns a list of dictionary objects of all palettes in your database.

`return_default_palettes()` Returns a list of dictionary objects of all default palettes in your database.

`return_custom_palettes()` Returns a list of dictionary objects of all custom palettes in your database.

`remove_custom_palette(palette_id, nickname)` Deletes a custom palette.

`remove_custom_palette_nickname(palette_id, existing_nickname)` Removes the nickname from a given palette.  This doesn't
remove the palettes themselves, and they can still be accessible through their palette ID.

`remove_all_custom_palette_nicknames()` Removes all nicknames from all custom palettes.  As said directly above, this only
removes the nickname, not the actual palette.

`remove_all_custom_palettes()` Deletes all custom palettes, leaving only the default (hardwired) palettes.

### Read Functions

During the read process, persistent data is stored in a sqlite database tracking its state.  These functions give you a
look inside, as well as some greater control of the reads themselves.  BitGlitter automatically deletes temporary byte
data for frames as soon as it can (ie, files can begin to be unpackaged).  What remains of finished streams is a small,
minimal view of their internal state, as well as stream metadata.  Be aware that the `read()` argument 
`auto_delete_finished_stream=True` (default) will automatically delete these when the stream is fully decoded (ie, all frames
are accounted for).  For more information read about `auto_delete_finished_stream` above.

Final note before proceeding- many of these functions you'll see `stream_sha256`; this is a string of the stream's 
SHA-256 hash.

`unpackage(stream_sha256)` If `unpackage_files=False` was an argument in read(), this will unpackage the stream (or as
much as it can from what has been scanned).

`return_single_read(stream_sha256)` Returns a dictionary object of the full state of the read.

`return_all_read_information()` Returns a list of dictionary objects of the full state of all stream reads.

`attempt_password(stream_sha256, encryption_key, attempt_unpackaging, scrypt_n=None, scrypt_r=None, scrypt_p=None)` Will
attempt to decrypt a locked password protected stream with your encryption key.  Will return `True` or `False` indicating
its success (or failure).  Optional `scrypt_n` `scrypt_r` `scrypt_p` parameters shouldn't be changed unless you know what
you're doing.  See `write()` for more information on these.

`return_stream_manifest(stream_sha256)` Returns a raw unformatted JSON string as received by BitGlitter in a stream's
metadata header.  Nested directory structures (if applicable) and file data are described in the string.  Keys are quite
short to minimize manifest size when being transmitted.

+ For directories:  `n` directory name, `f` files in that directory (not including subdirectories), `s` subdirectories for
that given directory.

+ For files: `fn` file name, `rs` raw file size (its true size), `rh` raw file hash (its true SHA-256 hash), `ps` processed
file size (its packaged size when being transmitted), `ph` processed file hash (its packaged SHA-256 hash when being transmitted).
Files are compressed in transit (unless you explicitly disable it in `write()` settings), hence the alternate size and hash for them.

`remove_partial_save(stream_sha256)` Completely removes the stream read from the database.  Be aware that read argument
`auto_delete_finished_stream` automatically does this if enabled for the stream.

`remove_all_partial_save_data()` Removes all stream reads from the database.

`update_stream_read(stream_sha256, auto_delete_finished_stream=None, unpackage_files=None)` Is where you can configure 
other values for stream reads.


### Preset Functions

Presets allow you to define `write()` behavior (geometry, palettes, etc) and save it with a nickname, so you can 
quickly and easily use your favorite configurations with a single string, without needing to explictly state all 
parameters every time.

`add_new_preset(nickname, output_mode='video', compression_enabled=True, scrypt_n=14, scrypt_r=8, scrypt_p=1,
stream_palette_id='6', header_palette_id='6', pixel_width=24, block_height=45, block_width=80, frames_per_second=30)`
is how you add a new preset.  Please note all of its default arguments are identical to default `write` arguments.  For
more information on each of these arguments, check out the `write()` section for arguments above.

`return_preset_data(nickname)` returns a dictionary object returning the full state of the preset.

`return_all_preset_data()` returns a list of all of the presets as dictionaries.

`remove_preset(nickname)` removes the preset with the `nickname` you gave it.

`remove_all_presets()` removes all saved presets.

### Statistics Functions

`output_stats()` Returns a dictionary object displaying the following data for both reads and writes: blocks processed,
frames processed, data processed.

`clear_stats()` All statistics reset back to zero.

### General Functions

`remove_session()` Resets the entire state of the library.  Removes statistics data, all saved streams, saved presets,
and saved palettes.  All settings get reverted to default, and default/included palettes are re-added.  This can't be undone.

`return_settings()` Returns a dictionary object of all settings.

`update_settings(decoded_files_output_path=None, read_bad_frame_strikes=None, disable_bad_frame_strikes=None, 
                    write_path=None, log_txt_path=None, log_output=None, logging_level=None, maximum_cpu_cores=None,
                    save_statistics=None, output_stream_title=None)` Allows you to update any of the settings.  Use caution
when changing these, as it could potentially result in crashes for invalid values.

![Splitter](https://i.imgur.com/qIygifj.png)

### Contributing

Whether you're a seasoned programmer or brand new, there's plenty of things you can do to help this project succeed.
Join our discord server, and check out all of the information I posted in the "Information" category.  Thank you for
your interest!

**Discord Link**

**https://discord.gg/t9uv2pZ**

### Practical Limits

It's worth stating the constraints you may face while using this.  While the images and video BitGlitter exports are
lossless (no compression applied), the "real world" on the internet is much different.  For instance, multimedia 
uploaded to popular social media sites is regularly compressed in order to save space (and ultimately cut down on 
expenses).  You are protected *to an extent* with BitGlitter from this.  Write parameters are fully customizable
primarily for this reason.  

While you can have greater throughput with larger colorsets, smaller blocks, and faster framerates, there may be a
practical limit to whether it will work depending on the degree their compression reduces quality.  At the expense of
throughput, larger blocks, slower framerates, and fewer colors used will make the stream *far* more resistant to
possible corruption.  Approaching the extreme limits of these parameters (tiny block sizes, very fast framerates, very
large colorsets), in terms of reading it and converting it back into data, requires very precise measurements of
position and color value; *a codec's purpose is to blur those precise values to reduce it's bitrate, and in turn it's
file size.*  While BitGlitter will detect corruption and perform an "emergency stop," I know you don't want to deal with
that, and neither do the people you're sharing with.

In closing, know the environment the video will be used in to ensure success in reading it.  And fortunately, the
ability to finely control the stream to accomodate the environment is not just possible, but simple.  :)

### Acknowledgements
Thank you to [Tanmay Mishra](https://github.com/tmishra3) for giving me guidance during planning of the library, as well
as its initial development. A big thank you to [Jack Robison](https://github.com/jackrobison) as well for his continued
wisdom.

**The third party libraries that make BitGlitter possible:**

+ `bitstring` - Bit manipulation
+ `cryptography` - Cryptographic functions
+ `numpy` - Formatting frames as high performance array during read()
+ `opencv-python` - Video loading, frame rendering, scanning and frame manipulation.
+ `SQLAlchemy` - Managing all persistent data

# MIT License
© 2021 - ∞ Mark Michon

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
 persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
