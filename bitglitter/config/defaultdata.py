from bitglitter.config.config import Config, Constants, Statistics, session
from bitglitter.palettes.palettes import Palette, PaletteColor

def load_default_data():
    """Populates config.db with required models as well as some default palettes"""
    if session.query(Config).first():
        return

    constants_model = Constants()
    constants_model.save()
    statistics_model = Statistics()
    statistics_model.save()
    config_model = Config()
    config_model.save()

    # Palette create
    default_palette_data = [
        {
            'palette_id': '1',
            'name': '1 Bit Default',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
            'it has the highest reliability.',
            'color_set': ((0, 0, 0), (255, 255, 255)),
            'is_24_bit': True
        },
        {
            'palette_id': '11',
            'name': '1 Bit Default Alternate',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': ((255, 0, 255), (0, 255, 255)),
            'is_24_bit': True
        },
        {
            'palette_id': '2',
            'name': '2 Bit Default',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)),
            'is_24_bit': True
        },
        {
            'palette_id': '22',
            'name': '2 Bit Default Alternate',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': ((0, 0, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255)),
            'is_24_bit': False
        },
        {
            'palette_id': '3',
            'name': '3 Bit Default',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255),
                          (255, 255, 255)),
            'is_24_bit': False
        },
        {
            'palette_id': '4',
            'name': '4 Bit Default',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': ((0, 0, 0), (128, 128, 128), (192, 192, 192), (128, 0, 0), (255, 0, 0), (128, 128, 0), (255,
                          255, 0), (0, 255, 0), (0, 128, 128), (0, 128, 0), (0, 0, 128), (0, 0, 255), (0, 255, 255),
                          (128, 0, 128), (255, 0, 255), (255, 255, 255)),
            'is_24_bit': False
        },
        {
            'palette_id': '6',
            'name': '6 Bit Default',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': ((0, 0, 0), (0, 0, 85), (0, 0, 170), (0, 0, 255), (0, 85, 0), (0, 85, 85), (0, 85, 170),
                          (0, 85, 255), (0, 170, 0), (0, 170, 85), (0, 170, 170), (0, 170, 255), (0, 255, 0),
                          (0, 255, 85), (0, 255, 170), (0, 255, 255), (85, 0, 0), (85, 0, 85), (85, 0, 170),
                          (85, 0, 255), (85, 85, 0), (85, 85, 85), (85, 85, 170), (85, 85, 255), (85, 170, 0),
                          (85, 170, 85), (85, 170, 170), (85, 170, 255), (85, 255, 0), (85, 255, 85), (85, 255, 170),
                          (85, 255, 255), (170, 0, 0), (170, 0, 85), (170, 0, 170), (170, 0, 255), (170, 85, 0),
                          (170, 85, 85), (170, 85, 170), (170, 85, 255), (170, 170, 0), (170, 170, 85), (170, 170, 170),
                          (170, 170, 255), (170, 255, 0), (170, 255, 85), (170, 255, 170), (170, 255, 255), (255, 0, 0),
                          (255, 0, 85), (255, 0, 170), (255, 0, 255), (255, 85, 0), (255, 85, 85), (255, 85, 170),
                          (255, 85, 255), (255, 170, 0), (255, 170, 85), (255, 170, 170), (255, 170, 255),
                          (255, 255, 0), (255, 255, 85), (255, 255, 170), (255, 255, 255)),
            'is_24_bit': True
        },
        {
            'palette_id': '24',
            'name': '24 Bit Default',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': None,
            'is_24_bit': True
        }, #stellar wind
    ]

    for palette in default_palette_data:
        new_palette = Palette(palette_id=palette['palette_id'], is_valid=True, is_24_bit=palette['is_24_bit'],
                              is_default=True, name=palette['name'], description=palette['description'])
        new_palette.save()
        #new_palette.load_colors(palette['color_set'])

#load_default_data() #here for now for testing.