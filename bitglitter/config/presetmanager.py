import pickle

from bitglitter.config.basemanager import BaseManager


class PresetManager(BaseManager):

    def __init__(self):
        super().__init__()
        self._SAVE_FILE_NAME = 'presetmanager'

        self.base_preset = Preset('base')
        self.preset_dict = {}

        self._save()

    def validate_preset(self, preset):
        # some validation

        if self.preset_dict[preset.nickname]:
            raise ValueError(f'\'{preset.nickname}\' already exists as a preset nickname.  Please choose a new name or'
                             f'delete the existing preset.')
        self.preset_dict[preset.nickname] = preset
        self._save()


class Preset:
    """Custom write parameters contained in a nice organized object.  If a valid preset is called in an argument, it
    override any and all other arguments provided."""

    def __init__(self,
                 nickname,

                 output_mode='video',
                 compression_enabled=True,
                 file_mask_enabled=True,  # todo revisit
                 scrypt_n=14,
                 scrypt_r=8,
                 scrypt_p=1,

                 header_palette_id='6',
                 stream_palette_id='6',
                 pixel_width=24,
                 block_height=45,
                 block_width=80,
                 frames_per_second=30,

                 logging_level='info',
                 logging_stdout_output=True,
                 logging_txt_output=False,
                 ):
        self.nickname = nickname

        self.output_mode = output_mode
        self.compression_enabled = compression_enabled
        self.file_mask_enabled = file_mask_enabled
        self.scrypt_n = scrypt_n
        self.scrypt_r = scrypt_r
        self.scrypt_p = scrypt_p

        self.header_palette_id = header_palette_id
        self.stream_palette_id = stream_palette_id
        self.pixel_width = pixel_width
        self.block_height = block_height
        self.block_width = block_width
        self.frames_per_second = frames_per_second

        self.logging_level = logging_level
        self.logging_stdout_output = logging_stdout_output
        self.logging_txt_output = logging_txt_output


try:
    with open('presetmanager.bin', 'rb') as unpickler:
        preset_manager = pickle.load(unpickler)

except:
    preset_manager = PresetManager()
