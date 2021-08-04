from bitglitter.config.config import session
from bitglitter.config.configmodels import Config, Constants, CurrentJobState, Statistics
from bitglitter.config.palettemodels import Palette


def load_default_db_data():
    """Populates config.db with required models as well as some default palettes"""
    if session.query(Config).first():
        return

    Constants.create()
    Statistics.create()
    Config.create()
    CurrentJobState.create()

    # Palette create
    default_palette_data = [
        {
            'palette_id': '1',
            'nickname': '1',
            'name': '1 Bit Default',
            'description': 'Two colors, black and white.  While it has the lowest density of one bit of data per pixel,'
                           ' it has the highest reliability.  This palette is used in all initial headers, displaying'
                           ' core stream metadata.',
            'color_set': ((0, 0, 0), (255, 255, 255)),
            'is_24_bit': False,
            'is_custom': False
        },
        {
            'palette_id': '11',
            'nickname': '11',
            'name': '1 Bit Default Alternate',
            'description': 'Alternate version.  Uses cyan/magenta instead of white/black.  This palette is used in the'
                           ' vertical and horizontal calibration blocks seen in all image frames, and the first frame'
                           ' of videos.',
            'color_set': ((255, 0, 255), (0, 255, 255)),
            'is_24_bit': False,
            'is_custom': False
        },
        {
            'palette_id': '2',
            'nickname': '2',
            'name': '2 Bit Default',
            'description': 'Four colors- black, red, green, blue.',
            'color_set': ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)),
            'is_24_bit': False,
            'is_custom': False
        },
        {
            'palette_id': '22',
            'nickname': '22',
            'name': '2 Bit Default Alternate',
            'description': 'Alternate version.  Four colors- black, magenta, cyan, yellow.',
            'color_set': ((0, 0, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255)),
            'is_24_bit': False,
            'is_custom': False
        },
        {
            'palette_id': '3',
            'nickname': '3',
            'name': '3 Bit Default',
            'description': 'Eight colors.',
            'color_set': ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255),
                          (255, 255, 255)),
            'is_24_bit': False,
            'is_custom': False
        },
        {
            'palette_id': '4',
            'nickname': '4',
            'name': '4 Bit Default',
            'description': 'Sixteen colors.',
            'color_set': ((0, 0, 0), (128, 128, 128), (192, 192, 192), (128, 0, 0), (255, 0, 0), (128, 128, 0), (255,
                                                                                                                 255,
                                                                                                                 0),
                          (0, 255, 0), (0, 128, 128), (0, 128, 0), (0, 0, 128), (0, 0, 255), (0, 255, 255),
                          (128, 0, 128), (255, 0, 255), (255, 255, 255)),
            'is_24_bit': False,
            'is_custom': False
        },
        {
            'palette_id': '6',
            'nickname': '6',
            'name': '6 Bit Default',
            'description': 'Sixty-four colors.  This is the default palette used for BitGlitter because it has good '
                           'performance while still quite resistant to typical compression/distortion.',
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
            'is_24_bit': False,
            'is_custom': False
        },
        {
            'palette_id': '24',
            'nickname': '24',
            'name': '24 Bit Default',
            'description': '~16.7 million colors, the best performing palette possible by a factor of three (with a '
                           'very big if).  This only works in lossless environments, any sort of distortion to the'
                           'rendered file WILL corrupt the data!  There is zero margin for error.\n\nOnly currently'
                           'works in rendering images as its a semi-experimental palette.',
            'color_set': None,
            'is_24_bit': True,
            'is_custom': False
        },
    ]
    custom_palette_data = [
        {
            'palette_id': '',
            'nickname': 'paperback2',
            'name': 'Paperback-2',
            'description': 'Two colors.  Credit goes to Doph of lospec.com.',
            'color_set': ('b8c2b9', '382b26'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'pixelink',
            'name': 'Pixel Ink',
            'description': 'Two colors.  Credit goes to Polyducks of lospec.com.',
            'color_set': ('3e232c', 'edf6d6'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'knockia',
            'name': 'Knockia3310',
            'description': 'Two colors.  Credit goes to Imogia Games of lospec.com.',
            'color_set': ('212c28', '72a488'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'note2c',
            'name': 'Note-2C',
            'description': 'Two colors.  Credit goes to Rytzi of lospec.com.',
            'color_set': ('222a3d', 'edf2e2'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'funkyjam',
            'name': 'Y\'s Funky Jam',
            'description': 'Two colors.  Credit goes to Yelta of lospec.com.',
            'color_set': ('920244', 'fec28c'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'kirokaze',
            'name': 'Kirokaze Gameboy Palette',
            'description': 'Four colors.  Credit goes to Kirokaze of lospec.com.',
            'color_set': ('332c50', '46878f', '94e344', 'e2f3e4'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'icecream',
            'name': 'Ice Cream GB',
            'description': 'Four colors.  Credit goes to Kerrie Lake of lospec.com.',
            'color_set': ('7c3f58', 'eb6b6f', 'f9a875', 'fff6d3'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': '2bitgrayscale',
            'name': '2-Bit Grayscale',
            'description': 'Four colors.  Credit goes to lospec.com.',
            'color_set': ('000000', '676767', 'b6b6b6', 'ffffff'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'mist',
            'name': 'Mist GB',
            'description': 'Four colors.  Credit goes to Kerrie Lake of lospec.com.',
            'color_set': ('2d1b00', '1e606e', '5ab9a8', 'c4f0c2'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'rustic',
            'name': 'Rustic GB',
            'description': 'Four colors.  Credit goes to Kerrie Lake of lospec.com.',
            'color_set': ('2c2137', '764462', 'edb4a1', 'a96868'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'spacehaze',
            'name': 'SpaceHaze',
            'description': 'Four colors.  Credit goes to WildLeoKnight of lospec.com.',
            'color_set': ('f8e3c4', 'cc3495', '6b1fb1', '0b0630'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'slso8',
            'name': 'SLSO8',
            'description': 'Eight colors.  Credit goes to Luis Miguel Maldonado of lospec.com.',
            'color_set': ('0d2b45', '203c56', '544e68', '8d697a', 'd08159', 'ffaa5e', 'ffd4a3', 'ffecd6'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'dreamscape8',
            'name': 'Dreamscape8',
            'description': 'Eight colors.  Credit goes to Kerrie Lake of lospec.com.',
            'color_set': ('c9cca1', 'caa05a', 'ae6a47', '8b4049', '543344', '515262', '63787d', '8ea091'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'pollen8',
            'name': 'Pollen8',
            'description': 'Eight colors.  Credit goes to Conker of lospec.com.',
            'color_set': ('73464c', 'ab5675', 'ee6a7c', 'ffa7a5', 'ffe07e', 'ffe7d6', '72dcbb', '34acba'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'ammo8',
            'name': 'Ammo-8',
            'description': 'Eight colors.  Credit goes to rsvp asap of lospec.com.',
            'color_set': ('040c06', '112318', '1e3a29', '305d42', '4d8061', '89a257', 'bedc7f', 'eeffcc'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'funkyfuture8',
            'name': 'FunkyFuture 8',
            'description': 'Eight colors.  Credit goes to Shamaboy of lospec.com.',
            'color_set': ('2b0f54', 'ab1f65', 'ff4f69', 'fff7f8', 'ff8142', 'ffda45', '3368dc', '49e7ec'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'justparchment8',
            'name': 'JustParchment 8',
            'description': 'Eight colors.  Credit goes to JustJimmy of lospec.com.',
            'color_set': ('292418', '524839', '73654a', '8b7d62', 'a48d6a', 'bda583', 'cdba94', 'e6ceac'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'rustgold',
            'name': 'Rust Gold 8',
            'description': 'Eight colors.  Credit goes to Trigo Mathmancer of lospec.com.',
            'color_set': ('f6cd26', 'ac6b26', '563226', '331c17', 'bb7f57', '725956', '393939', '202020'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'oddfeeling',
            'name': 'Odd Feeling',
            'description': 'Eight colors.  Credit goes to XENO of lospec.com.',
            'color_set': ('900c3f', 'e84a5f', 'ff847c', 'fc9d9d', 'feceab', 'ccafaf', '99b898', 'ffffff'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'retrocal',
            'name': 'RetroCal-8',
            'description': 'Eight colors.  Credit goes to polyphorge of lospec.com.',
            'color_set': ('6eb8a8', '2a584f', '74a33f', 'fcffc0', 'c6505a', '2f142f', '774448', 'ee9c5d'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'citrink',
            'name': 'Citrink',
            'description': 'Eight colors.  Credit goes to Inkpendude of lospec.com.',
            'color_set': ('ffffff', 'fcf660', 'b2d942', '52c33f', '166e7a', '254d70', '252446', '201533'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'waverator',
            'name': 'Waverator',
            'description': 'Eight colors.  Credit goes to Mig Moog of lospec.com.',
            'color_set': ('0c0d14', '181c28', '23313d', '33505d', '4e7f7d', '53a788', '70d38b', 'cbffd8'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'winterwonderland',
            'name': 'Winter Wonderland',
            'description': 'Eight colors.  Credit goes to Jimison3 of lospec.com.',
            'color_set': ('20284e', '2c4a78', '3875a1', '8bcadd', 'ffffff', 'd6e1e9', 'a7bcc9', '738d9d'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'sobeachy',
            'name': 'SoBeachy8',
            'description': 'Eight colors.  Credit goes to Snowy Owl of lospec.com.',
            'color_set': ('e55388', 'e57d88', 'e59f88', 'e5d988', 'e3d5cc', 'bad5cc', '6dd5cc', '5ac5cc'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'sweetie',
            'name': 'Sweetie 16',
            'description': 'Sixteen colors.  Credit goes to GrafxKid of lospec.com.',
            'color_set': ('1a1c2c', '5d275d', 'b13e53', 'ef7d57', 'ffcd75', 'a7f070', '38b764', '257179', '29366f',
                          '3b5dc9', '41a6f6', '73eff7', 'f4f4f4', '94b0c2', '566c86', '333c57'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'steamlords',
            'name': 'Steam Lords',
            'description': 'Sixteen colors.  Credit goes to Slynyrd of lospec.com.',
            'color_set': ('213b25', '3a604a', '4f7754', 'a19f7c', '77744f', '775c4f', '603b3a', '3b2137', '170e19',
                          '2f213b', '433a60', '4f5277', '65738c', '7c94a1', 'a0b9ba', 'c0d1cc'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'islandjoy',
            'name': 'Island Joy 16',
            'description': 'Sixteen colors.  Credit goes to Kerrie Lake of lospec.com.',
            'color_set': ('ffffff', '6df7c1', '11adc1', '606c81', '393457', '1e8875', '5bb361', 'a1e55a', 'f7e476',
                          'f99252', 'cb4d68', '6a3771', 'c92464', 'f48cb6', 'f7b69e', '9b9c82'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'lostcentury',
            'name': 'Lost Century',
            'description': 'Sixteen colors.  Credit goes to CalmRadish of lospec.com.',
            'color_set': ('d1b187', 'c77b58', 'ae5d40', '79444a', '4b3d44', 'ba9158', '927441', '4d4539', '77743b',
                          'b3a555', 'd2c9a5', '8caba1', '4b726e', '574852', '847875', 'ab9b8e'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'vanillamilkshake',
            'name': 'Vanilla Milkshake',
            'description': 'Sixteen colors.  Credit goes to Space Sandwich of lospec.com.',
            'color_set': ('28282e', '6c5671', 'd9c8bf', 'f98284', 'b0a9e4', 'accce4', 'b3e3da', 'feaae4', '87a889',
                          'b0eb93', 'ffe6c6', 'dea38b', 'e9f59d', 'ffc384', 'fff7a0', 'fff7e4'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'galaxyflame',
            'name': 'Galaxy Flame',
            'description': 'Sixteen colors.  Credit goes to Rhoq of lospec.com.',
            'color_set': ('699fad', '3a708e', '2b454f', '111215', '151d1a', '1d3230', '314e3f', '4f5d42', '9a9f87',
                          'ede6cb', 'f5d893', 'e8b26f', 'b6834c', '704d2b', '40231e', '151015'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'endesga32',
            'name': 'Endesga 32',
            'description': 'Thirty-two colors.  Credit goes to ENDESGA of lospec.com.',
            'color_set': ('be4a2f', 'd77643', 'ead4aa', 'e4a672', 'b86f50', '733e39', '3e2731', 'a22633', 'e43b44',
                          'f77622', 'feae34', 'fee761', '63c74d', '3e8948', '265c42', '193c3e', '124e89', '0099db',
                          '2ce8f5', 'ffffff', 'c0cbdc', '8b9bb4', '5a6988', '3a4466', '262b44', '181425', 'ff0044',
                          '68386c', 'b55088', 'f6757a', 'e8b796', 'c28569'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'mulfok32',
            'name': 'MulfoK32',
            'description': 'Thirty-two colors.  Credit goes to MulfoK of lospec.com.',
            'color_set': ('5ba675', '6bc96c', 'abdd64', 'fcef8d', 'ffb879', 'ea6262', 'cc425e', 'a32858', '751756',
                          '390947', '611851', '873555', 'a6555f', 'c97373', 'f2ae99', 'ffc3f2', 'ee8fcb', 'd46eb3',
                          '873e84', '1f102a', '4a3052', '7b5480', 'a6859f', 'd9bdc8', 'ffffff', 'aee2ff', '8db7ff',
                          '6d80fa', '8465ec', '834dc4', '7d2da0', '4e187c'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'warm32',
            'name': 'Warm32',
            'description': 'Thirty-two colors.  Credit goes to David of lospec.com.',
            'color_set': ('0d0e1e', '2f3144', '626a73', '94a5aa', 'd3dfe1', '291820', '694749', 'a56e66', 'cb9670',
                          'ecd8b7', '28092d', '692b58', '804061', 'a1516a', 'e19393', '1e1d38', '514569', '84788b',
                          'bea8bf', '232d4f', '3a4b6d', '65799a', '99b4dd', '41648b', '6fa9c3', 'b9e2e5', 'd3ead8',
                          '0a2325', '204039', '3e6248', '778f73', 'b4c3a8'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'res64',
            'name': 'Resurrect64',
            'description': 'Sixty-four colors.  Credit goes to Kerrie Lake of lospec.com.',
            'color_set': ('2e222f', '3e3546', '625565', '966c6c', 'ab947a', '694f62', '7f708a', '9babb2', 'c7dcd0',
                          'ffffff', '6e2727', 'b33831', 'ea4f36', 'f57d4a', 'ae2334', 'e83b3b', 'fb6b1d', 'f79617',
                          'f9c22b', '7a3045', '9e4539', 'cd683d', 'e6904e', 'fbb954', '4c3e24', '676633', 'a2a947',
                          'd5e04b', 'fbff86', '165a4c', '239063', '1ebc73', '91db69', 'cddf6c', '313638', '374e4a',
                          '547e64', '92a984', 'b2ba90', '0b5e65', '0b8a8f', '0eaf9b', '30e1b9', '8ff8e2', '323353',
                          '484a77', '4d65b4', '4d9be6', '8fd3ff', '45293f', '6b3e75', '905ea9', 'a884f3', 'eaaded',
                          '753c54', 'a24b6f', 'cf657f', 'ed8099', '831c5d', 'c32454', 'f04f78', 'f68181', 'fca790',
                          'fdcbb0'),

            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'nanner',
            'name': 'Nanner Pancakes',
            'description': 'Thirty-two colors.  Credit goes to Nanner of lospec.com.',
            'color_set': ('a0ddd3', '6fb0b7', '577f9d', '4a5786', '3e3b66', '392945', '2d1e2f', '452e3f', '5d4550',
                          '7b6268', '9c807e', 'c3a79c', 'dbc9b4', 'fcecd1', 'aad795', '64b082', '488885', '3f5b74',
                          'ebc8a7', 'd3a084', 'b87e6c', '8f5252', '6a3948', 'c57f79', 'ab597d', '7c3d64', '4e2b45',
                          '7a3b4f', 'a94b54', 'd8725e', 'f09f71', 'f7cf91'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'stardust32',
            'name': 'Stardust32',
            'description': 'Thirty-two colors.  Credit goes to Isa of lospec.com.',
            'color_set': ('000833', '200261', '330a80', '851694', 'd42a6e', 'ff5b4f', 'ffb366', 'fff673', 'aff04f',
                          '48d43b', '1aab87', '2e51c7', '2320ab', '3f87d9', '54b8e3', '78f0e2', 'b8ffd9', 'ffffe1',
                          'ffa8bf', 'e681ac', 'bd448e', 'ffdac9', 'eba698', 'cc6e6e', 'a14869', '80335e', '521d45',
                          '2b1744', '54508a', '6f75a6', '91a2c2', 'cadbe8'),
            'is_24_bit': False,
            'is_custom': True
        },
        {
            'palette_id': '',
            'nickname': 'pastel64',
            'name': 'Pastel-64',
            'description': 'Sixty-four colors.  Credit goes to helixei of lospec.com.',
            'color_set': ('998276', 'c4c484', 'abd883', 'a2f2bd', 'a2ebf2', 'b88488', 'd1b182', 'd4eb91', 'ccfcc4',
                          '907699', 'c484a4', 'ea8c79', 'f2e5a2', '9a84b8', 'd182ca', 'eb91a8', 'ffddc4', '768d99',
                          '8484c4', 'c479ea', 'f2a2d7', '84b8b4', '82a2d1', 'a791eb', 'fbc8f5', '7c957a', '84c4a4',
                          '79d7ea', 'a2aff2', 'a2b884', '82d189', '91ebd4', 'c9e5fa', 'b8a784', 'b9ca89', '91eb91',
                          'c9fce9', '957686', 'c49484', 'eade7a', 'c3f2a2', 'b884af', 'd1828f', 'ebbd91', 'f7f9c4',
                          '797699', 'b484c4', 'ea79bb', 'f2a9a2', '8495b8', '9d82d1', 'ea91eb', 'ffc8d4', '76958d',
                          '84b4c4', '7982ea', 'd1a2f2', '84b88d', '82d1c4', '91beeb', 'd2c6fa', '969976', '94c484',
                          '79eaa8'),
            'is_24_bit': False,
            'is_custom': True
        }
    ]

    palettes_types_pending = default_palette_data + custom_palette_data

    for palette in palettes_types_pending:
        Palette.create(palette_id=palette['palette_id'], is_valid=True, is_24_bit=palette['is_24_bit'],
                       is_custom=palette['is_custom'], name=palette['name'], description=palette['description'],
                       nickname=palette['nickname'], is_included_with_repo=True,
                       time_created=946706400, color_set=palette['color_set'])
