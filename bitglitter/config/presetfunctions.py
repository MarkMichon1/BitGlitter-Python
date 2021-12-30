from bitglitter.config.config import session
from bitglitter.config.presetmodels import Preset
from bitglitter.validation.validatewrite import write_preset_validate


def _convert_preset_to_dict(preset):
    return {'nickname': preset.nickname, 'datetime_created': preset.datetime_created, 'output_mode': preset.output_mode,
            'compression_enabled': preset.compression_enabled, 'scrypt_n': preset.scrypt_n, 'scrypt_r': preset.scrypt_r,
            'scrypt_p': preset.scrypt_p, 'cpu_cores': preset.cpu_cores, 'stream_palette_id': preset.stream_palette_id,
            'pixel_width': preset.pixel_width, 'block_height': preset.block_height, 'block_width': preset.block_width,
            'frames_per_second': preset.frames_per_second}


def add_new_preset(nickname, output_mode='video', compression_enabled=True, scrypt_n=14, scrypt_r=8, scrypt_p=1,
                   max_cpu_cores=0, stream_palette_id='6', pixel_width=24, block_height=45, block_width=80,
                   frames_per_second=30):
    write_preset_validate(nickname, output_mode, compression_enabled, scrypt_n, scrypt_r, scrypt_p, max_cpu_cores,
                          stream_palette_id, pixel_width, block_height, block_width, frames_per_second)
    if session.query(Preset).filter(Preset.nickname == nickname).first():
        raise ValueError(f'\'{nickname}\' already exists as a preset nickname.  Please choose a new name or'
                         f'delete the existing preset.')
    new_preset = Preset.create(nickname=nickname, output_mode=output_mode, compression_enabled=compression_enabled,
                               scrypt_n=scrypt_n, scrypt_r=scrypt_r, scrypt_p=scrypt_p, max_cpu_cores=max_cpu_cores,
                               stream_palette_id=stream_palette_id, pixel_width=pixel_width, block_height=block_height,
                               block_width=block_width, frames_per_second=frames_per_second)
    return new_preset


def return_all_preset_data():
    returned_list = []
    presets = session.query(Preset).all()
    for preset in presets:
        returned_list.append(_convert_preset_to_dict(preset))
    return presets


def return_preset(nickname):
    preset = session.query(Preset).filter(Preset.nickname == nickname).first()
    if preset:
        return _convert_preset_to_dict(preset)
    else:
        return {}


def remove_preset(nickname):
    preset = session.query(Preset).filter(Preset.nickname == nickname).first()
    preset.delete()


def remove_all_presets():
    session.query(Preset).delete()
