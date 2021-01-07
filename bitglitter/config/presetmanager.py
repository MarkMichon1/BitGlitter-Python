from pathlib import Path
import pickle

from bitglitter.config.basemanager import BaseManager
from bitglitter.validation.validatewrite import write_preset_validate


class PresetManager(BaseManager):

    def __init__(self):
        super().__init__()
        self._SAVE_FILE_NAME = 'presetmanager'

        self.base_preset = Preset('base')  # desktop
        self.preset_dict = {}

        self._save()

    def add_preset(self,
                   nickname,
                   output_mode='video',
                   compression_enabled=True,
                   scrypt_n=14,
                   scrypt_r=8,
                   scrypt_p=1,
                   max_cpu_cores=0,
                   stream_palette_id='6',
                   header_palette_id='6',
                   pixel_width=24,
                   block_height=45,
                   block_width=80,
                   frames_per_second=30):

        write_preset_validate(nickname, output_mode, compression_enabled, scrypt_n, scrypt_r, scrypt_p, max_cpu_cores,
                              stream_palette_id, header_palette_id, pixel_width, block_height, block_width,
                              frames_per_second)
        if self.preset_dict[nickname]:
            raise ValueError(f'\'{nickname}\' already exists as a preset nickname.  Please choose a new name or'
                             f'delete the existing preset.')

        validated_preset = Preset(nickname, output_mode, compression_enabled, scrypt_n, scrypt_r, scrypt_p,
                                  max_cpu_cores, stream_palette_id, header_palette_id, pixel_width, block_height,
                                  block_width, frames_per_second)
        self.preset_dict[nickname] = validated_preset
        self._save()

    def return_preset(self, nickname):
        try:
            return self.preset_dict[nickname]
        except KeyError:
            raise ValueError(f'write() preset \'{nickname}\' does not exist.')

    def return_preset_data(self, nickname):
        if nickname in self.preset_dict:
            return self.preset_dict[nickname].return_as_dict()
        else:
            raise ValueError(f'Preset \'{nickname}\' does not exist.')

    def return_all_preset_data(self):
        returned_list = []
        for preset in self.preset_dict.values():
            returned_list.append(preset.return_as_dict())
        return returned_list

    def remove_preset(self, nickname):
        if not self.preset_dict[nickname]:
            raise ValueError(f'\'{nickname}\' does not exist as a preset nickname')
        del self.preset_dict[nickname]
        self._save()

    def remove_all_presets(self):
        self.preset_dict = {}
        self._save()


class Preset:
    """Custom write parameters contained in a nice organized object.  If a valid preset is called in an argument, it
    override any and all other arguments provided."""

    def __init__(self,
                 nickname,

                 output_mode='video',
                 compression_enabled=True,
                 error_correction=False,
                 scrypt_n=14,
                 scrypt_r=8,
                 scrypt_p=1,
                 cpu_cores=0,

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
        self.error_correction = error_correction  # Currently has no effect.  Will be implemented in future.
        self.scrypt_n = scrypt_n
        self.scrypt_r = scrypt_r
        self.scrypt_p = scrypt_p
        self.cpu_cores = cpu_cores

        self.header_palette_id = header_palette_id
        self.stream_palette_id = stream_palette_id
        self.pixel_width = pixel_width
        self.block_height = block_height
        self.block_width = block_width
        self.frames_per_second = frames_per_second

    def return_as_dict(self):
        return {
            'nickname': self.nickname, 'compression_enabled': self.compression_enabled, 'output_mode': self.output_mode,
            'scrypt_n': self.scrypt_n, 'scrypt_r': self.scrypt_r, 'scrypt_p': self.scrypt_p, 'header_palette_id':
                self.header_palette_id, 'stream_palette_id': self.stream_palette_id, 'pixel_width': self.pixel_width,
            'block_height': self.block_height, 'block_width': self.block_width, 'frames_per_second':
                self.frames_per_second,
        }


try:
    current_directory = Path(__file__).resolve().parent
    pickle_path = current_directory / 'presetmanager.bin'
    with open(pickle_path, 'rb') as unpickler:
        preset_manager = pickle.load(unpickler)

except FileNotFoundError:
    preset_manager = PresetManager()
