import datetime
import math


class AbstractPalette:
    '''Setting a foundation for DefaultPalette and CustomPalette objects by defining some functionality.
    AbstractPalette is not meant to be instantiated, only it's children!
    '''

    def __init__(self, name, description, colorSet, colorDistance):

        self.name = name
        self.description = description
        self.colorSet = colorSet
        self.colorDistance = colorDistance

        self.id = None
        self.numberOfColors = len(self.colorSet)
        self.bitLength = int(math.log(self.numberOfColors, 2))

    def __getitem__(self, item):
        return self.colorSet[item]


class DefaultPalette(AbstractPalette):
    '''These are palettes that come default with BitGlitter.'''

    def __init__(self, name, description, colorSet, colorDistance, id):

        super().__init__(name, description, colorSet, colorDistance)
        self.id = str(id)
        self.paletteType = 'default'


    def __str__(self):
        return (f'Name: {self.name}\nIdentification Code: {str(self.id)}\nDescription: {self.description}\nBit Length: '
        f'{str(self.bitLength)}\nNumber of Colors: {str(self.numberOfColors)}\nColor Set: {str(self.colorSet)}'
        f'\nColor Distance: {str(self.colorDistance)}\n')


class CustomPalette(AbstractPalette):
    '''This is what custom color palettes become.  It blindly accepts all values; all necessary checks are performed in
    addCustomPalette() in bitglitter.palettes.palettefunctions.
    '''

    def __init__(self, name, description, colorSet, colorDistance, dateCreated, id, nickname):

        super().__init__(name, description, colorSet, colorDistance)

        self.dateCreated = int(dateCreated)
        self.id = id
        self.nickname = nickname
        self.paletteType = 'custom'


    def __str__(self):
        return (f"Name: {self.name}\nIdentification Code: {str(self.id)}\nNickname: {self.nickname}\nDescription: "
        f"{self.description}"
        f"\nDate Created: {datetime.datetime.fromtimestamp(self.dateCreated).strftime('%A, %B %d, %Y - %I:%M:%S %p')}"
        f"\nBit Length: {str(self.bitLength)}"
        f"\nNumber of Colors: {str(self.numberOfColors)}\nColor Set: {str(self.colorSet)}"
        f"\nColor Distance: {str(self.colorDistance)}\n")


class TwentyFourBitPalette:
    '''This class doesn't function exactly like the other two classes.  You'll notice it takes no arguments and there
    are no colors in colorSet.  There is only one object that can exist of this class, because of the specific values
    needed.  This object is what represents the 24 bit color set.
    '''
    def __init__(self):
        self.name = "24 bit default"
        self.description = "EXPERIMENTAL!  ~16.7 million colors.  This will only work in lossless" \
         " environments, any sort of compression will corrupt the data."
        self.colorSet = None
        self.numberOfColors = 16777216
        self.bitLength = 24
        self.id = str(self.bitLength)
        self.colorDistance = 0
        self.paletteType = 'default'


    def __str__(self):
        return (f'Name: {self.name}\nIdentification Code: {str(self.id)}\nDescription: {self.description}\nBit Length: '
                f'{str(self.bitLength)}\nNumber of Colors: {str(self.numberOfColors)}\nColor Set: Too many '
                f'to list (see directly above)\nColor Distance: {str(self.colorDistance)}\n')