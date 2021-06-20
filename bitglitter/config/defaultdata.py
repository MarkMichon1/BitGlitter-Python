from bitglitter.config.config import session
from bitglitter.palettes.palettes import Palette, PaletteColor

def load_default_data():
    """Populates config.db with required models as well as some default palettes"""
    pending_commit_objects = []

    # Palette create
    default_palette_data = [
        {
            'palette_id': '1',
            'name': '1 Bit Default',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
            'it has the highest reliability.',
            'color_set': ((0, 0, 0), (255, 255, 255)),
        },
        {
            'palette_id': '11',
            'name': '1 Bit Default Alternate',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': ((255, 0, 255), (0, 255, 255)),
        },
        {
            'palette_id': '2',
            'name': '2 Bit Default',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)),
        },
        {
            'palette_id': '22',
            'name': '2 Bit Default Alternate',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': ((0, 0, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255)),
        },
        {
            'palette_id': '3',
            'name': '3 Bit Default',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255),
                          (255, 255, 255)),
        },
        {
            'palette_id': '4',
            'name': '4 Bit Default',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': ((0, 0, 0), (128, 128, 128), (192, 192, 192), (128, 0, 0), (255, 0, 0), (128, 128, 0), (255,
                          255, 0), (0, 255, 0), (0, 128, 128), (0, 128, 0), (0, 0, 128), (0, 0, 255), (0, 255, 255),
                          (128, 0, 128), (255, 0, 255), (255, 255, 255)),
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
        },
        {
            'palette_id': '24',
            'name': '24 Bit Default',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           'it has the highest reliability.',
            'color_set': None,
        },
    ]

    for palette in default_palette_data:
        new_palette = Palette(palette_id=palette['palette_id'], palette_type='default', name=palette['palette_id'], description=palette['palette_id'], color_set=palette['palette_id'],
                      color_distance=2.532, number_of_colors=7, bit_length=3)
        pending_commit_objects.append(new_palette)

    session.add_all(pending_commit_objects)
    session.commit()


load_default_data()