![BitGlitter Logo](https://i.imgur.com/3GJ4bDx.png)

For a complete guide on BitGlitter please go here: TBD

# The basics

![BitGlitter Sample Frame](https://i.imgur.com/RO0YsuI.png)
#todo- video gif here ###################


BitGlitter is an easy to use script that allows you to embed data inside of ordinary pictures or video.  Store and host
any files wherever images or videos can be hosted.

### From physical barcodes to digital data transfer

Whether it's barcodes at the store or QR codes you can scan with your phone- they both work on the same principle.  Data
is encoded into the black and white.  You each think of each color as an abstraction for a binary value, so then when
those colors are read in sequence, you can pull meaningful data from the image.  I wondered how this concept could be
improved upon.  BitGlitter was born.

Conventional barcodes are severely limited in application, in terms of their data density.  Much capability is gained 
when you maximize the original concept.  BitGlitter is in a class of it's own in several ways:

+ **Color Palettes:**  By removing the constraint of only using black and white, the amount of data you can hold in a
given "block" on the frame skyrockets.  Your regular two color setup holds one bit per block.  Four colors holds two 
bits (2x), sixty four colors holds six bits (6x), and lossless ~16.7M color palette holds 24 bits (24x improvement over 
black & white).
+ **Multi-Frame Videos:** BitGlitter automatically breaks up larger files into multiple frames.  These frames have
unique ID's in their headers
+ **Variable block size:** Each of the blocks in the frame can be set to any size, including one pixel.  Larger block sizes give
your stream protection in lossy environments, while smaller blocks allow for greater densities mean.

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

Put simply, you can now make videos that can hold large volumes of data inside of them.  There may be some pretty
interesting applications that can come out of this.

# Features

### Data

+ **Compression Added:** This is done automatically, so don't worry about putting your files in a rar or zip prior to
sending.
+ **Encryption Added:** Optional AES-256 encryption to protect your files.  Passwords are hashed with scrypt, parameters
can be customized for your needs.
+ **File Masking:**  Optional ability to mask what files are included in the stream.  Only those who successfully grab 
the stream (and decrypt it if applicable) will know of its contents.

### Video

You can choose between either outputting all of your frames as a series of images (.png), or as a single .mp4.

+ **Customizable resolution:** You have complete control of the size of the outputted frames, whether they are 480p or
8K.
+ **Customizable Framerate:** Currently supports 30 and 60 FPS, custom values are coming soon.

![Custom Color Showcase](https://i.imgur.com/4uQTxwT.png)

+ **Custom Color Palettes:** The included default palettes are just a starting point.  Make any color palette that you
want to match the aesthetic where it's being used.  Anyone reading the stream will have the palette automatically saved
to their machine, so then they can use it as well!

### Reading

+ **Colorsnap Error Correction:** BitGlitter protect your file against corruption and artifacts on the image or video.
After loading the correct palette, whenever it detects an incorrect color, it will "snap" it to the nearest color in the
palette.  This gives your file resistance against format changes, codecs, or file size reduction.

+ **File Integrity Check Mechanisms:** When the stream is created, a hash (SHA-256) is taken of the entire stream, as
well as each frame.  The data must match what is expected to be accepted.  Damaged or corrupt files will not be blindly
passed on to you.

### Design

+ **Easy to understand:** Whether you're learning about Python and want to understand how it works, or you're looking to
contribute, docstrings and notes are throughout the library.

+ **Built in future-proofing:** As of now, BitGlitter has a single protocol (Protocol 1), which is a specific set of
  procedures around how data is handled, and the components of a frame, as well as their layout.  Each protocol has its
  own unique ID to identify it with.  This ID is added in the  header during the write process, and is picked up at 
  read.  As new protocols get created, older versions of BitGlitter that don't have these included will notify the user
  to update their version in order for it to be read.  All older protocol versions are saved in future library
  iterations, so no matter how old the protocol version is used on the stream, it will always be able to be read.

+ **Fully modular design:** Do you have a specialized use case?  Adapting this library to your own needs is quite easy.
  I've built BitGlitter to be easy to modify and expand upon.  Rather than worrying about the lower-level functionality,
  achieve your goal with the modular components I've created.

### Applications
To be determined.  This will be updated as time progresses.


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


Link to wiki.

# How it works


Reading- explain colorsnap
(pythagorean theorem?  check it)

Discuss the implications of it.

I put together a google doc sheet.  new programmers, etc #todo no

```TBD!```

# How to use

This is all you need to know to get up and running.  There is additional functionality as well, 
[and here is the link.](https://github.com/MarkMichon1/BitGlitter/wiki/Using-BitGlitter)

###Use BitGlitter in 60 seconds
`tba`

###Base Usage
`write()` is the function that inputs files and turns them into a BitGlitter stream.  There are quite a few arguments
to customize the stream, but there is only one required argument.  Everything else has defaults.

Not surprisingly, that required argument defines what files or folders you wish to embed in the stream.  Argument 
`fileList` takes a tuple of strings, there is no limit to how many you can add.  Remember when using tuples,
with a single item it requires a comma after it, for instance `fileList=('C:\\Users\\Mark\\Desktop\\file.pdf',)`.
File or folder paths that don't exist are automatically ignored.

`streamName=''` is what you can use to optionally title your stream, which will be printed out on the screen of whoever
reads the file, along with other stream data.

`streamDescription=''` serves as a text field to optionally put a description for the stream.

`streamOutputPath=False` is where you can optionally define the path of where the created media is outputted.  By
default, media is saved where the python file is ran.  The folder path must already exist if used.

`outputMode='video'` is where you define how you wish the stream to output, whether as an .mp4 video, or a series of
.png images.  The only two valid arguments are `'image'` and `'video'`.

`compressionEnabled=True` enables or disables compression of your data, prior to rendering into frames.  This is enabled
by default.

`fileMaskEnabled=False` is where you can omit the listing of files/folders from the stream header.  This effectively
hides the contents of the stream, unless it is fully read.  By default, this is disabled.  What this means is when
someone reads your stream, in the first several frames it will automatically display the contents of the stream (files
as well as their size) on the screen.

`encryptionKey=''` optionally encrypts your data with AES-256.  By default, this is disabled.  The stream will not be
able to be read unless the reader successfully inputs this.

There is a little bit more advanced security functionality which is beyond what most will need, check out the Wiki pages
to learn more.

`headerPaletteID='4'` sets the palette used in the 'setup' frames in the beginning.  It is strongly recommended you use
a default palette here if you don't know what you're doing, because this is where important information regarding the
stream is read, and by using a custom palette, it will be impossible for anyone to read it who hasn't already 'learned'
the palette.

`streamPaletteID='4'` sets the palette used for the payload.  By default, the 4 bit default color set is used.  I'll 
explain all about palettes below.

`pixelWidth=20` sets how many pixels wide each block is when rendered.  By default it's 20 pixels.  This is a very
important value regarding readability.  Having them overly large will make reading them easier, but will result in less
efficient frames and require substantially longer streams.  Making them very small will greatly increase their
efficiency, but at the same time a lot more susceptible to read failures if the files are shrunk, or otherwise
distorted.

`blockHeight=54` sets how many blocks tall the frame will be, by default this is set to 54 (which along with 
`blockWidth`, creates a perfect 1080p sized frame).

`blockWidth=96` sets how many blocks wide the frame will be, by default this is set to 96.

`framesPerSecond=30` sets how many frames per second the video will play at, assuming argument `outputMode = "video"`.
Currently, 30fps and 60fps are accepted.

There is a few more arguments to control what level gets logged or printed out on the screen, check out the Wiki pages
to learn more about them.


---

`read()` is what you use to input BitGlitter streams (whether images or video), and will output the files.

###Color Palettes

BitGlitter provides a nice selection of default palettes to choose from:

![BitGlitter Default Palettes](https://i.imgur.com/dSYmq7V.png)

add here

###TBD
```TBD```

# Installation

In addition to downloading the code from Github, you can also grab it directly from PyPI:

`pip install bitglitter`

#todo- ffmpeg exe figure out

## Required Third Party Libraries

+ `bitstring` - Bit manipulation.
+ `cryptography` - Cryptographic functions.
+ `ffmpeg-python` - Video rendering and output.
+ `opencv-python` - Video loading and frame manipulation.
+ `filepackager` - File manipulation for writing and 
reading.
+ `Pillow` - Frame creation and output, as well as loading images and reading pixel values.


# Contributing
Whether you're a seasoned programmer or brand new, there's plenty of things you can do to help this project succeed.
Join our discord server, and check out all of the information I posted in the "Information" category.  Thank you for
your interest!

https://discord.gg/t9uv2pZ

Also, be sure to check out the 
[contributing master page](https://github.com/MarkMichon1/BitGlitter/wiki/Contributing-Master-Page).  It contains a lot
of information.

Being my first project into Python and programming in general, this project took countless hours to bring it from 
a sentence-long idea to what you see now.  Numerous commercial offers to obtain this project have been turned down - 
BitGlitter is a free, open-source project, and will forever stay that way.  Seeing the reception so far makes it all
worthwhile to me.  And I'm only getting started.  However, taking this project to the next level requires resources to
grow, and this is something I cannot do on my own.  If you see the potential in this idea and can afford a donation, 
you're ensuring this prototype grows in capability and impact.  Thank you for reading.  - Mark

Bitcoin address: 12TrCXqqFU67b2JFt7sZkw5iWAYEnpRZ5e

Paypal address: [https://www.paypal.me/markmichon7](https://www.paypal.me/markmichon7)

![Splitter](https://i.imgur.com/qIygifj.png)

# MIT License
© 2019 - ∞ Mark Michon

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
 persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
