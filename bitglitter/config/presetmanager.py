import pickle

from bitglitter.config.basemanager import BaseManager
from bitglitter.validation.validate_write import write_preset_validate


class PresetManager(BaseManager):

    def __init__(self):
        super().__init__()
        self._SAVE_FILE_NAME = 'presetmanager'

        self.base_preset = Preset('base')
        self.preset_dict = {}

        self._save()

    def add_preset(self,
                   nickname,
                   output_mode='video',
                   compression_enabled=True,
                   scrypt_n=14,
                   scrypt_r=8,
                   scrypt_p=1,
                   stream_palette_id='6',
                   header_palette_id='6',
                   pixel_width=24,
                   block_height=45,
                   block_width=80,
                   frames_per_second=30):

        write_preset_validate(output_mode, compression_enabled, scrypt_n, scrypt_r, scrypt_p, stream_palette_id,
                              header_palette_id, pixel_width, block_height, block_width, frames_per_second)
        if self.preset_dict[nickname]:
            raise ValueError(f'\'{nickname}\' already exists as a preset nickname.  Please choose a new name or'
                             f'delete the existing preset.')

        validated_preset = Preset(nickname, output_mode, compression_enabled, scrypt_n, scrypt_r, scrypt_p,
                                  stream_palette_id, header_palette_id, pixel_width, block_height, block_width,
                                  frames_per_second)
        self.preset_dict[nickname] = validated_preset
        self._save()

    def return_preset(self, nickname):
        try:
            return self.preset_dict[nickname]
        except:
            raise ValueError(f'write() preset \'{nickname}\' does not exist.')


class Preset:
    """Custom write parameters contained in a nice organized object.  If a valid preset is called in an argument, it
    override any and all other arguments provided."""

    def __init__(self,
                 nickname,

                 output_mode='video',
                 compression_enabled=True,
                 scrypt_n=14,
                 scrypt_r=8,
                 scrypt_p=1,

                 stream_palette_id='6',
                 header_palette_id='6',
                 pixel_width=24,
                 block_height=45,
                 block_width=80,
                 frames_per_second=30,
                 ):
        self.nickname = nickname

        self.output_mode = output_mode
        self.compression_enabled = compression_enabled
        self.scrypt_n = scrypt_n
        self.scrypt_r = scrypt_r
        self.scrypt_p = scrypt_p

        self.header_palette_id = header_palette_id
        self.stream_palette_id = stream_palette_id
        self.pixel_width = pixel_width
        self.block_height = block_height
        self.block_width = block_width
        self.frames_per_second = frames_per_second


try:
    with open('presetmanager.bin', 'rb') as unpickler:
        preset_manager = pickle.load(unpickler)

except:
    preset_manager = PresetManager()
