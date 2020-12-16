'''The GUI executable version of BitGlitter will use this Python library as a dependency.  Contained in this module (as
it is developed) is functionality meant for the application.  Most or all of this will simply be functions to pass
data/objects in and out of the configuration object.  User input validation will be included in these functions.  This
functionality will be exposed to any end users using this library, but this is the cleanest way I know to go about doing
this.  If you know of a better way, let us know on the official Discord server:  https://discord.gg/t9uv2pZ
'''

from bitglitter.config.palettemanager import palette_manager

def return_all_palette_objects():
    '''This function is used both in the write 'wizard' when selecting a color, and in the palette settings menu.  This
    returns both default palette and custom palette objects.
    '''

    # Thought- import may have to be in the function itself.  Otherwise future changes to the pickle object may not
    # properly load.  Test this further into development.

    default_palettes = palette_manager.DEFAULT_PALETTE_LIST
    custom_palettes = palette_manager.custom_palette_list

    return list(default_palettes.values()), list(custom_palettes.values())