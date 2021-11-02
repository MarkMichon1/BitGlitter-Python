![BitGlitter Logo](https://i.imgur.com/pX8b4Dy.png)

Latest: `v1.0.3`

**11/1/21 Note:** This library is actively being pushed to v2.0.  It is mostly complete.  It is recommended to avoid
using the library until that point... countless bugs are fixed, as well as major additions, optimizations, and 
improvements across the board.  2.0 is a complete rebuild of the original 1.0 library.  I think you will like it. Stay
tuned... :)

### Python Library (you are here) | [Electron Desktop App](https://github.com/MarkMichon1/BitGlitter) | [Python Backend For App](https://github.com/MarkMichon1/BitGlitter-Backend)

## ⚡ Store and transfer files using high-performance animated barcodes

![BitGlitter Sample GIF](https://i.imgur.com/lPFR5kA.gif) 

**[Discord Server](https://discord.gg/t9uv2pZ)** 
[![Downloads](https://pepy.tech/badge/bitglitter)](https://pepy.tech/project/bitglitter)

**[Youtube video of a real stream transferring ~80KB/s of data](https://youtu.be/TIKEEA2mXrI)**

BitGlitter is an easy to use Python library that lets you embed data inside ordinary pictures or video.  Store and host
files wherever images or videos can be hosted.  The carrier for data is the 'blocks' within the frames and not
the file itself, and there are various measures to read imperfect distorted frames.  What this means for you is streams
are resistant to compression and distortion, and aren't broken by things such as format changes, metadata changes, etc.
BitGlitter gives you a unique way to make your data more portable.

![Frame Demo](https://i.imgur.com/Pgq4h1o.png)

Sample frame taken from video using default settings, holding 2.7 KB of data

### Using ordinary barcodes as a launchpad

Barcodes and QR codes are everywhere.  They embed binary data (0's and 1's) in them, symbolized as black and white.  While
they are pretty constrained in the real world, using them for digital transfer removes many of those limits.  What if you
could have multiple barcodes (frames), that if read sequentially could have the capacity of many thousands of individual
ones?  What if we added colors to the barcodes, so a given barcode could have 2x, 6x, 24x the capacity?  What if we greatly
increased the size of the frames to lets say the size of a standard 1080p video, so the frames once again increase their
capacity by a couple orders of magnitude.  Combine all of these together, and you're able to move serious amounts of 
data.  This is BitGlitter.

![BitGlitter Default Palettes](https://i.imgur.com/T6CiFOf.png)

+ **Designed to survive what breaks existing steganography schemes:** BitGlitter doesn't rely on reading the exact stream that
it outputs at write.  Because the data is in the video data itself and not in any metadata or byte format embedded in it,
its resistant to format changes, resolution changes, compression, corruption, and other distortion.  Not much different
from how barcodes in real life are resistant.
+ **Hardened against frame corruption:** Virtually all video/image hosting social media type sites run your multimedia 
files through compression to minimize their file size.  This can cause compression artifacts (visual distortions) to 
appear.  In lossless steganography, this will completely corrupt the data, rendering it unreadable.  Not BitGlitter.  
Taking in the palette used in the stream, it will "snap" incorrect colors to their nearest value, allowing you to read 
data from frames that have gone though a gauntlet of compression.  The default write settings have been tested on 
several major sites, and were tweaked until there was 100% readability across tens of thousands of test frames.
+ **Fully configurable stream creation:** While the default values cover most uses, you have full control of the write parameters:
  + **Color set:** 8 default palettes to choose from that provide higher performance or greater file integrity.  You can
  even make your own custom palettes (more on that below)
  + **Block size:** These are the colorful squares that hold data.  They can be as small as one pixel, or as large as
  you'd like.  Larger block sizes gives you greater data integrity, and smaller block sizes increase data capacity per
  frame.
  + **Frame dimensions:** Whether you want to output 144p compatible videos or 8K, it does it all.
  + **Frame rate:** If its an integer, yes
  + **Output mode:**  Choose from either an MP4 video output, or a series of PNG images (BitGlitter accepts and reads both),
  giving you greater flexibility on where you can host your data.
+ **Built in file integrity:** Metadata, files, and the stream and frames themselves are protected with SHA-256 hashes.
Only valid data is accepted.
+ **Built in encryption and file masking:** Encrypt your files with AES-256, and optionally the file manifest as well, 
masking its contents until the correct key is used.
+ **Built in compression:** Payloads are compressed using max zlib settings prior to rendering, to minimize stream 
size.  No need to zip or rar your files prior.
+ **Supports very large streams:** Current protocol can handle up to one [exabyte](https://en.wikipedia.org/wiki/Byte#Multiple-byte_units)
in size, or ~4.3 billion rendered frames.  Put simply, there's no practical limit to your stream's size.

![Custom Color Showcase](https://i.imgur.com/o4xa0Fq.png)

### What is possible with various configurations?

Because everything can be customized, you can have completely different outputs with vastly different performance
characteristics (data integrity vs performance).  In **bold** is the default parameters used which have been 
consistently readable on major social media sites.  This is all new territory, what is readable can likely be tweaked and increased even more.

| Number of Colors in Palette 	| Bits of Data Per Block 	| Frame Resolution        	| Block Size in Pixels 	| Frame Dimensions (w * h in blocks) 	| Frames Rate 	| Data Throughput 	| Lossless? 	|
|:---------------------------:	|------------------------	|-------------------------	|----------------------	|------------------------------------	|-------------	|-----------------	|-----------	|
| 2                           	| 1                      	| 640 x 480 (480p)        	| 20                   	| 32 x 24                            	| 30 FPS      	| 1.56 KB/s       	| No        	|
| 4                           	| 2                      	| 1280 x 720 (720p)       	| 20                   	| 64 x 36                            	| 30 FPS      	| 15.96 KB/s      	| No        	|
| 8                           	| 3                      	| 1280 x 720 (720p)       	| 20                   	| 64 x 36                            	| 30 FPS      	| 24.6 KB/s       	| No        	|
| 16                          	| 4                      	| 1920 x 1080 (1080p)     	| 24                   	| 80 x 45                            	| 30 FPS      	| 52.68 KB/s      	| No        	|
| **64**                      	| **6**                  	| **1920 x 1080 (1080p)** 	| **24**               	| **80 x 45**                        	| **30 FPS**  	| **79.68 KB/s**  	| **No**    	|
| 64                          	| 6                      	| 1920 x 1080 (1080p)     	| 24                   	| 80 x 45                            	| 60 FPS      	| 159.36 KB/s     	| No        	|
| 16,777,216                  	| 24                     	| 1920 x 1080 (1080p)     	| 5                    	| 384 x 216                          	| 30 FPS      	| 7.46 MB/s       	| Yes       	|
| 16,777,216                  	| 24                     	| 3840 x 2160 (4K)        	| 5                    	| 768 x 432                          	| 60 FPS      	| 59.71 MB/s      	| Yes       	|

### Installation

In addition to downloading the code from Github, you can also grab it directly from PyPI:

`pip install bitglitter`

###**The 2 Core Functions of BitGlitter**

Ignoring the bells and whistles for now, all you need to use BitGlitter is `write()` and `read()`.  Both use an assortment
of default arguments to remove a lot of the complexity starting out.

+ `write()` takes your files and directories, and creates the BitGlitter stream (either as a video of a collection of 
images).
+ `read()` scans your BitGlitter encoded files and outputs the files/directories embedded in it.

### write() -- converting files and directories into BitGlitter streams

We'll go a bit more in depth now.

`write()` is the function that inputs files and turns them into a BitGlitter stream.  There are quite a few arguments
to customize the stream, but there is only one required argument.  Everything else has defaults.

`input_path` is an absolute path pointing to the file or directory you'd like convert into a stream.

`preset_nickname=None` takes in a string name for a preset.  Learn more below in **Preset Functions**.

`stream_name=''` **required** argument to name your stream, which will be encoded into the metadata of the stream when
read.  150 character limit.

`stream_description=''` serves as a text field to optionally put a description for the stream.  No character limit.

`output_directory=None` is a string for the absolute path of an existing directory you'd like the stream to output to.is where you can optionally define the path of where the created media is outputted.  By default, the stream outputs in a "Render Output"
 folder within the library's directory.

`output_mode='video'` controls the type of output you will have created.  Your two choices are `'video'`,
or `'image'`.  Video outputs a single .mp4 file, whereas image output returns all of the frames.

`stream_name_file_output=False` controls if outputted files will use the stream's SHA-256 hash as a name, or the 
provided name (`stream_name`) for the stream.  By default, it uses the SHA-256, a 64 character hexadecimal 'fingerprint'
of the stream.

`max_cpu_cores=0` determines how many CPU cores you'd like to use when rendering frames.  0 is default, which is
maximum.

`compression_enabled=True` enables or disables compression of your data, prior to rendering into frames.  
This is enabled by default.

`encryption_key=''` optionally encrypts your data with AES-256.  By default, this is disabled.  The stream will not be
able to be read unless the reader successfully inputs this.

`file_mask_enabled=False` toggles whether you want the stream manifest to be encrypted or not when your stream itself is
encrypted.  What this means is simpler terms is the contents of the stream will be hidden until or unless the correct
encryption key is inputted.  If set to False, the full contents of the stream will be visible.  This only does anything
when an encryption key is used.

`scrypt_N=14`, `scrypt_R=8` and `scrypt_P=1` allow you to customize the parameters of the `scrypt` key 
derivation function.  You shouldn't touch this if you don't know what is.  Only change these settings if you're 
comfortable with cryptography, and you know what you're doing!  It's worth noting `scrypt_N` uses its argument as 2^n.
Finally, if you're changing these numbers, they MUST be manually added when using read functionality, otherwise 
decryption will fail.  Custom values are deliberately not transmitted in the stream for security reasons. Your end users
of the stream must know these parameters if they are changed, otherwise BitGlitter will use the default parameters when
decrypting.

`stream_palette_id='6'` sets the palette used in the stream, after initialization headers are ran.  Takes a string of
the palette's palette_id.

`pixel_width=24` sets how many pixels wide each 'block' is when rendered on screen.  24 pixels is default.  This is one 
of those values that have a large impact on readability.  Having them overly large will make reading it easier, but will
result in less efficient frames and require substantially longer streams.  Making them very small will greatly increase 
their efficiency, but at the same time a lot more susceptible to read failures if the files are shrunk, or otherwise
distorted.  This default value offers a nice middleground.

`block_height=45` sets how many blocks tall the frame will be, by default this is set to 45 (which along with 
`block_width`, creates a perfect 1080p sized frame).

`block_width=80` sets how many blocks wide the frame will be.  By default this is set to 80.

`frames_per_second=30` sets how many frames per second the video will play at, assuming `output_mode = "video"` is used.

Finally we have several arguments to control logging.

`logging_level='info'` determines what level logging messages get outputted.  It accepts three arguments- `info` is
default and only shows core status data during `read()` and `write()`.  `'debug'`  shows info level messages as well as
debug messages from the various processes.  Boolean `False` disables logging altogether.

`logging_stdout_output=True` sets whether logging messages are displayed on the screen or not.  Only accepts booleans.
Enabled by default.

`logging_txt_output=False` determines whether logging messages are saved as text files or not.  Only accepts type 
`bool`. Disabled by default.  If set to `True`, a log folder will be created, and text files will be automatically saved
there.

`save_statistics=False` saves some fun statistics about your usage of the program- total number of blocks rendered,
total frames rendered, and total payload data rendered.  This updates after each successful write session.  Functions
to interact with this data are below.

**These default values transmit data at about 80 KB/s.**  This is a safe starting point that should be pretty resistant to
corruption.

### read() -- converting BitGlitter streams back into directories and files

`read()` is how we input BitGlitter streams (whether images or video), and output the files and directories encoded in
them.  There are several other functions included to interact with these streams (changing the encryption key to decrypt
the stream, removing one or all streams, changing its save path, etc).  Check out **Read Functions** below to learn more.

Like with `write()`, the only argument required is the input path (`file_path`), except in this case it only accepts 
files.  Supported video formats are `.avi, .flv, .mov, .mp4, .wmv` and supported image formats are `.bmp, .jpg, .png`.
Can accept a string with a single absolute file path (image or video), or a list of strings of absolute file paths.
Lists can only contain image files, videos must be one at a time.  **Important:**  When inputting image
files, it is important to add the first few frames containing metadata FIRST, before adding the rest of the standard
payload type frames.  This metadata gives the reader important data on palettes, stream configuration, and on the payload
itself.  Some frames may be recognized as corrupted when this data is lacking.  Once metadata is received, the order of
images to input becomes irrelevant, and the library takes care of the rest.

`stop_at_metadata_load=False` This will break out of the function *if* metadata for the stream is read.  This allows you
to view the metadata and manifest (file/directory contents) of the stream itself, to verify the values for yourself.  From
there, you can choose to either re-read the file and continue getting the files, or delete it.  This is a security feature
to double check what the contents are, before you extract the files onto your computer.  Please note that this will only
run **once** per stream.  When re-ran, the stream will continue to read and decode the files (if enabled in the arguments).

`unpackage_files=True` controls whether files embedded in the stream should be extracted during read as the frame data
becomes available to do so.  This lets you extract all files that are available each time read concludes if enabled.  If
disabled, you can unpackage files using the function `unpackage(stream_sha256)`.  For more information, go to **Read Functions**

`auto_delete_finished_stream=True` deletes all stream metadata and temporary files from your system once the read is
complete, leaving you only with the decoded files pulled from the stream.  In most cases you probably wouldn't change this,
but in the event you want to view the data, you can do so here.

`output_directory=None` sets where files will be written as they become available through decoding.  Takes in a string
of an absolute path of an existing file directory.  This is "set and forget", in the sense the first time a stream is
recognized/created during read, the output path will be bound to the stream.  Subsequent read() calls for other frames 
will continue to have the outputted files going to the right place.

`bad_frame_strikes=25` Sets how many corrupted frames the reader is to detect before it aborts out of a video.  
This allows you to break out of a stream relatively quickly if the video is substantially corrupted, without needing to
 iterate over each frame.  If this is set to 0, it will disable strikes altogether and attempt to read each frame 
 regardless of the level of corruption.

`max_cpu_cores=0` determines the amount of CPU cores to use, like `write()`.  The default value of 0
sets it to maximum available.

`block_height_override=False` and `block_width_override=False` allow you to manually input the stream's block height and 
block width.  Normally you'll never need to use this, as these values are automatically obtained as the frame is locked
onto.  But for a badly corrupted or compressed frame, this may not be the case.  By using the override, the reader will
attempt to lock onto the screen given these parameters.  Both must be filled in order for the override to work.

`encryption_key=None` is where you add the encryption key to decrypt the stream.  Like argument `output_directory`, you only
need this argument once, and it will bind to that save.

`scrypt_n=14`, `scrypt_r=8`, and `scrypt_p=1` are values that control scrypt password hashing if your stream is encrypted.
These only need to be touched if the stream creator changed the default values during `write()`.  IF that is the case,
these values must be identical to the values used during write; decryption won't work even with the correct encryption
key.  Please note that you can change these values even after `read()` `with attempt_password()`.  See **Read Functions**
below for more information.

`logging_level='info'`, `logging_stdout_output=True`, `logging_txt_output=False`, and `save_statistics=False` are 
arguments as well.  These are seen in `write()` as well; read their descriptions above to see what these do.

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

`generate_sample_frame(directory_path, palette_id=None, palette_nickname=None, all_palettes=False, include_default=False,
pixel_width=20, block_height=20, block_width=20)` 
Generates a small 'thumbprint' frame of a palette, giving you an idea of how it would appear in a normal rendering.  
`directory_path` is an existing directory in which it will be saved. `all_palettes` toggles whether you want to get a 
sample from a specific palette (using `palette_id` or `palette_nickname`) or all palettes saved.  `include_default` toggles
whether you want to include all default palettes in the generated output, or if you only want to generate custom palettes.
The last 3 arguments let you control the exact size of the frames.  You can also use this function to generate artwork
or cool looking wallpapers using the palettes as well.

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

`blacklist_stream_sha256(stream_sha256)` Disallow a specific SHA-256 hash of a stream to be read on your client.  Will
also remove the Stream Read containing that hash as well, if it exists.

`return_all_blacklist_sha256()` Returns a list of all blacklisted SHA-256 hashes as strings.

`remove_blacklist_sha256(stream_sha256)` Removes a specific SHA-256 hash.  Returns `True` or `False` depending on whether
it existed.

`remove_all_blacklist_sha256()` Removes all SHA-256 hashes from the blacklist.

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

`update_settings(read_path=None, read_bad_frame_strikes=None, enable_bad_frame_strikes=None, 
                    write_path=None, log_txt_path=None, log_output=None, logging_level=None, maximum_cpu_cores=None,
                    save_statistics=None, output_stream_title=None)` Allows you to update any of the settings.  Use caution
when changing these, as it could potentially result in crashes for invalid values.

![Splitter](https://i.imgur.com/tozbtUz.png)

### Contributing

**Let me know of your ideas and suggestions!**  There are many directions this technology can go in, and with enough interest
your ideas can be future additions to this core library (as well as the desktop app).

Heres my Discord server, feel free to drop in and say hi:

**https://discord.gg/t9uv2pZ**

### Disclaimer

There are a few points worth bringing up on using this library:

+ **Output sizes can be huge.** At the end of the day, we're using far less dense storage mediums (color data in image and video 
frames) to hold and transmit good amounts of data.  The payback, however, is giving you much greater portability in how
or where you can store, host, and transmit it.  Depending on the settings, stream size can be 1.1x-100x+ the size of the
payload itself.  Start with relatively smaller files when starting out with this library to get a better feel for this.  
For now until we get a better feel for how people are using it and how things can be fine tuned, its a fair assumption that
BitGlitter is best suited for payloads less than 50-100MB.
+ **This library is completely experimental:** In its current state, BitGlitter is merely a proof of concept to see if
doing this was possible and if there is interest.  It started as one of my first projects learning Python and programming
as a whole.  I am one person doing my best to create a well-rounded product that accomplishes what it is designed to do.
Please use the issues page or let me know on Discord if there is something not working.

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
