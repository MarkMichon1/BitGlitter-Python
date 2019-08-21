[![Downloads](https://pepy.tech/badge/bitglitter)](https://pepy.tech/project/bitglitter)

**[Discord Server](https://discord.gg/t9uv2pZ)**

![BitGlitter Logo](https://i.imgur.com/3GJ4bDx.png)

# The basics

![BitGlitter Sample GIF](https://i.imgur.com/n7E7lnd.gif)

**[Click here](https://www.youtube.com/watch?v=HrY4deFrOoA) for a demo video of a real stream.**

BitGlitter is an easy to use library that allows you to embed data inside of ordinary pictures or video.  Store and host
files wherever images or videos can be hosted.

### From physical barcodes to digital data transfer

Whether it's barcodes at the store or QR codes you can scan with your phone- they both work on the same principle.  Data
is encoded into the black and white.  You can think of each color as an abstraction for a binary value, so then when
those colors are read in sequence, you can pull meaningful data from the image.  I wondered how this concept could be
improved upon, and I wanted a cool first project as an introduction to programming.  BitGlitter was born.

Conventional barcodes are severely limited in application, in terms of their data density.  When you maximize the 
concept and configure it for digital-digital transmission, a lot of capability is gained.  
BitGlitter is in a class of it's own in several ways:

![BitGlitter Default Palettes](https://i.imgur.com/dSYmq7V.png)

+ **Multiple Color Palettes:**  By removing the constraint of only using black and white, the amount of data you can 
hold in a given "block" (each square) on the frame skyrockets.  The regular two color setup holds one bit per block.  
Four colors holds two  bits (2x), sixty four colors holds six bits (6x), and lossless ~16.7M color palette holds 24 bits 
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

+ **Supports streams up to ~1 EB in size, or ~4.3B frames:**  In other words, there is no practical limit to the
 stream's size.
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

![Custom Color Showcase](https://i.imgur.com/4uQTxwT.png)

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

+ **No metadata saved in the file:**  Compress the stream, change formats, upload it somewhere.  All data is encoded in
the blocks, so you don't have to worry (as much) about rendering the stream unreadable.

+ **Easy to understand:** Whether you're learning about Python and want to understand how it works, or you're looking to
contribute, docstrings and notes are throughout the library.

+ **Built in future-proofing:** As of now, BitGlitter has a single protocol (Protocol 1), which is a specific set of
  procedures around how data is handled, and the components of a frame, as well as their layout.  Each protocol has its
  own unique ID to identify it with.  This ID is added in the  header during the write process, and is picked up at 
  `read()`.  As new protocols get created, older versions of BitGlitter that don't have these included will notify the user
  to update their version in order for it to be read.  All older protocol versions are saved in future library
  iterations, so no matter how old the protocol version is used on the stream, it will always be able to be read.

+ **Fully modular design:** Do you have a specialized use case?  Adapting this library to your own needs is quite easy.
  I've built BitGlitter to be easy to modify and expand upon.  Rather than worrying about the lower-level functionality,
  achieve your goal with the modular components I've created.

### CLI

**Temporary warning-** Due to issues uploading to PyPI, these features are only available on Github for now.  The PyPI version of BitGlitter still performs everything else fine.  This will be removed when the problem is fixed.

Write from command line:

+ `python3 -m bitglitter write`

      `-file` - The absolute path to the file
      `-mode` - Either 'image' or 'video'. Default: video
      `-o` - Output path

 Read from commnad line:

+ `python3 -m bitglitter read`
    
      `-file` - The absolute path to the file
      `-o` - Output path

### Applications
To be determined.  This will be updated as time progresses!

# How to use

All of the functions to run this library are explained below.  I'm also working on several Wikipedia pages, explaining
BitGlitter in greater detail (how it works, etc) with some included illustrations.  These are not yet complete, 
[but here is the link to the project's Wiki if you'd like to see it!](https://github.com/MarkMichon1/BitGlitter/wiki/Using-BitGlitter)

### Installation

In addition to downloading the code from Github, you can also grab it directly from PyPI:

`pip install bitglitter`

**IMPORTANT:** The only part you will need to grab manually is a copy of ffmpeg.exe .  Place it in the same folder the 
code will be running, and you'll be set.  This will be done automatically in the near future.  Get the package here on
the left side of the screen:

[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

ffmpeg.exe is all that is needed.

**Required Third Party Libraries**

+ `bitstring` - Bit manipulation.
+ `cryptography` - Cryptographic functions.
+ `ffmpeg-python` - Video rendering and output.
+ `opencv-python` - Video loading and frame manipulation.
+ `Pillow` - Frame creation and output, as well as loading images and reading pixel values.

Thanks to Tanmay Mishra for giving me a pre-release version of his upcoming library `filepackager`.  It has been heavily
modified and stripped down to suit this library.  The code is included with BitGlitter; there is no need to download it.

**BitGlitter in 60 seconds**

Even though it comes shipped with a lot of functionality, all you need to use it is `write()` (creates the streams) and 
`read()` (which reads them and extracts the data encoded in it).  The only required argument for both is the file you
wish to input in string format.

### write(), converting files into BitGlitter streams

We'll go a bit more in depth now.

`write()` is the function that inputs files and turns them into a BitGlitter stream.  There are quite a few arguments
to customize the stream, but there is only one required argument.  Everything else has defaults.

Not surprisingly, that required argument defines what files or folders you wish to embed in the stream.  If and only if
you're sending a single file or folder path, argument `fileList` takes a string of the path.  BitGlitter also supports
sending multiple files and folder together, of which there is no limit!  This would require using a tuple or list item
filled with strings of the file or folder paths.  File or folder paths that don't exist are automatically ignored.

`stream_name=''` is what you can use to optionally title your stream, which will be printed out on the screen of whoever
reads the file, along with other stream data.

`stream_description=''` serves as a text field to optionally put a description for the stream.

`output_path=False` is where you can optionally define the path of where the created media is outputted.  By
default, media is saved where the python file is ran.  The folder path must already exist if used.

`output_mode='video'` is where you define how you wish the stream to output, whether as an .mp4 video, or a series of
.png images.  The only two valid arguments are `'image'` and `'video'`.

`compression_enabled=True` enables or disables compression of your data, prior to rendering into frames.  This is enabled
by default.

`file_mask_enabled=False` is where you can omit the listing of files/folders from the stream header.  This effectively
hides the contents of the stream, unless it is fully read.  By default, this is disabled.  What this means is when
someone reads your stream, in the first several frames it will automatically display the contents of the stream (files
as well as their size) on the screen.

`encryption_key=''` optionally encrypts your data with AES-256.  By default, this is disabled.  The stream will not be
able to be read unless the reader successfully inputs this.

Arguments `scrypt_N=14`, `scrypt_R=8` and `scrypt_P=1` allow you to customize the parameters of the `scrypt` key derivation 
function.  If you're a casual user, you'll never need to touch these (and shouldn't).  Only change these settings if
 you're comfortable with cryptography and you know what you're doing!  It's worth noting `scrypt_N` uses it's argument as
 2^n.  Finally, if you're changing these numbers, they MUST be manually inputted during `read()` otherwise decryption
 will fail!  Custom values are deliberately not transmitted in the stream for security reasons.  Your end users of the
 stream must know these custom parameters.

`header_palette_id='6'` sets the palette used in the 'setup' frames in the beginning.  It is strongly recommended you use
a default palette here if you don't know what you're doing, because this is where important information regarding the
stream is read, and by using a custom palette, it will be impossible for anyone to read it who hasn't already 'learned'
the palette.

`stream_palette_id='6'` sets the palette used for the payload.  By default, the 4 bit default color set is used.  I'll 
explain all about palettes below.

`pixel_width=24` sets how many pixels wide each block is when rendered.  By default it's 20 pixels.  This is a very
important value regarding readability.  Having them overly large will make reading them easier, but will result in less
efficient frames and require substantially longer streams.  Making them very small will greatly increase their
efficiency, but at the same time a lot more susceptible to read failures if the files are shrunk, or otherwise
distorted.

`block_height=45` sets how many blocks tall the frame will be, by default this is set to 45 (which along with 
`block_width`, creates a perfect 1080p sized frame).

`block_width=80` sets how many blocks wide the frame will be.  By default this is set to 96.

`frames_per_second=30` sets how many frames per second the video will play at, assuming argument `output_mode = "video"`.
Currently, 30fps and 60fps are accepted.

Finally we have several arguments to control logging.

`logging_level='info'` determines what level logging messages get outputted.  It accepts three arguments- `info` is
default and only shows core status data during `read()` and `write()`.  `'debug'`  shows INFO level messages as well as
lower level messages from the various processes.  Boolean `False` disables logging altogether.

`logging_screen_output=True` sets whether logging messages are displayed on the screen or not.  Only accepts type `bool`. 
Enabled by default.

`logging_save_output=False` determines whether logging messages are saved as text files or not.  Only accepts type `bool`.
Disabled by default.  If set to `True`, a log folder will be created, and text files will be automatically saved there.

These default values have an 81KB/s transmission rate.  This is only a starting point that should be pretty resistant to
corruption.

### read(), converting streams back into data

`read()` is what you use to input BitGlitter streams (whether images or video), and will output the files.

Like with `write()`, the only argument required is the BitGlitter-encoded file, whether that's an image or a video.
`file_to_input` is the only required argument.  We'll go over the other ones.

`output_path=None` Is where you can set where this stream will be saved once all frames have been successfully loaded.
  It's 'set and forget', so if you are loading images this argument only has to be used once, and the folder path will
  stick with that stream.  This argument requires a strong of a folder path that already exists.

`bad_frame_strikes=10` This sets how many corrupted frames the reader is to detect before it aborts out of a video.  This
allows you to break out of a stream relatively quickly if the video is substantially corrupted, without needing to
 iterate over each frame.  If this is set to 0, it will disable strikes altogether, and attempt to read each frame 
 regardless of the level of corruption.

`block_height_override=False` and `block_width_override=False` allow you to manually input the stream's block height and 
block width.  Normally you'll never need to use this, as these values are automatically obtained as the frame is locked
onto.  But for a badly corrupted or compressed frame, this may not be the case.  By using the override, the reader will
attempt to lock onto the screen given these parameters.  Both must be filled in order for the override to work.

`encryption_key=None` is where you add the encryption key to decrypt the stream.  Like argument `output_path`, you only
need this argument once, and it will bind to that save.

Arguments `scrypt_n=14`, `scrypt_r=8` and `scrypt_p=1`

`logging_level = 'info'`, `logging_screen_output = True`, `logging_save_output = False` - Please see the full explanation at
`write().`

### Color Palettes

If you wish to make your own custom color palettes, BitGlitter gives you the ability to do that with these functions.

`add_custom_palette(palette_name, palette_description, color_set, optional_nickname = "")`  This function adds custom palettes
to use.  

Argument `palette_name` takes a string and is the name of the palette that gets displayed and transmitted. 

Argument`palette_description` takes a string as well, and is the description of the palette, if you wish to add it.  

Argument `color_set` takes a tuple of RGB tuples, these will be the actual colors used in the BitGlitter stream.  Here's 
a simple example of what it would look like using two colors: `color_set=((0, 255, 0), (0, 0, 255))`.  There are a few
requirements to these tuples:
+ No two identical values can be added.  For instance, the color black with the same RGB values twice.  Each color used
must be unique!  The more 'different' the colors are, the better.
+ You must have a minimum of two colors.
+ It must be 2^n colors used, so 2, 4, 8, 16, etc.

Argument `optional_nickname=""` allows you to use an easy to input nickname for your custom palette.  This nickname is 
  how you select this palette to specifically run on your stream.  Internally, custom palettes have a 64 character ID 
  code which you can use (more on this below).  This allows you to give it a string of your choosing to designate it as 
  well.  This field is optional.  If you do decide to use it though, both the internal ID AND the nickname will work.

`edit_nickname_to_custom_palette(id_or_nick, new_name)` This function allows you to edit the nickname of your custom palette 
to something else.  Both arguments require strings.  You can use it's nickname you assigned it, or it's internal ID.

`print_full_palette_list(path)` This function outputs a text file to the folder path outlining the palettes available, both
default palettes and custom.  It shows information such as their name, description, date created, color set, nickname,
and more.  The required argument is a string of a folder path, which must already exist.  Here's an example of how to
format it: `C:\Users\Mark\Desktop`

`clear_all_custom_palettes()` This removes all custom palettes from your config.  Please note that the default palettes 
will not be removed.

`remove_custom_palette(id_or_nick)` This function removes the custom palette from your config.  It takes a string argument
of either it's internal ID, or a nickname you've previously given it.

`remove_custom_palette_nickname(id_or_nick)` This function strips any nickname associated with a custom palette.  It takes a
string argument of either the internal ID or a previous nickname.

`clear_custom_palette_nicknames()`  This removes all nicknames from all custom palettes.

### Partial Save Control

Once the first frame of a stream is read, a PartialSave object is created.  This is essentially what manages the binary
strings, and holds various information on it's state.  These functions help better interface with them.

`update_partial_save(stream_sha, reattempt_assembly = True, password_update = None, scrypt_n =  None, scrypt_r = None, 
scrypt_p = None, change_output_path = None)` This function allows you to update various parameters of the save.  Requires
a string input for `streamSHA` which is the ID number of the string.  

Argument `reattempt_assembly` makes the assembler
attempt to reassemble the frames, as well as output the embedded files and folders.  This would be used in the case of
an incorrect password or scrypt parameters, and you'd like to try again.

Argument `password_update` takes a string argument, and will add (or replace) the encryption key tied to this stream.

Arguments `scrypt_n, scrypt_r and scrypt_p` change the scrypt parameters used to derive the key used for decryption.  If
the scrypt parameters were left at default during `write()` of the stream, these can be left as is.  Otherwise, the 
custom values will need to be inputted whether here or in the optional arguments of `read()`.

`begin_assembly(stream_sha)` This function exists to initiate assembly of a package at a later time, rather than doing so 
immediately for whatever reason.

`print_full_save_list(path, debug_data=False)` This function outputs a text file to the folder path outlining all (if any)
partial saves you have on your system.  You can check their status, as well as the state of the PartialSave object 
itself.  Argument `debugData` is `False` by default, but enabling it to `True` outputs various debug information 
pertaining to the object as well, which wouldn't serve much utility seeing for someone such as a casual end user.

`remove_partial_save(stream_sha)`  Using a string argument for the stream's ID (or stream SHA, as commonly used), this will
remove the object from your config, as well as remove all temporary data associated with it.

`remove_all_partial_saves()` All saves are removed from the config object, clearing all temporary data.

### General Configuration

`outputStats(path)` This function gives you a neat bird's eye view of your BitGlitter usage.  During all `read()` and 
`write()` cycles, the total amount of data transferred, as well as total frames transferred and individual blocks 
scanned gets added to a running total.  Argument `path` requires a string argument of a folder path that already exists.
A small text file will be written to this location.

`clear_stats()` All statistics will be reset to zero.

`clear_session()` This wipes all inputted data.  Custom colors, statistics, and partial save objects will all be erased,
as well as any temporary data for the partially read streams.  This is in essence a hard reset.

# Contributing

Whether you're a seasoned programmer or brand new, there's plenty of things you can do to help this project succeed.
Join our discord server, and check out all of the information I posted in the "Information" category.  Thank you for
your interest!

**Discord Link**

**https://discord.gg/t9uv2pZ**

Also, be sure to check out the 
[contributing master page](https://github.com/MarkMichon1/BitGlitter/wiki/Contributing-Master-Page).  It contains a lot
of information.

![Splitter](https://i.imgur.com/qIygifj.png)

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

In closing, know the environment the video will be used in to ensure success in reading it.

# MIT License
© 2019 - ∞ Mark Michon

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
