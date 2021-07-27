from bitglitter.config.config import session
from bitglitter.config.presetmodels import Preset
from bitglitter.validation.validatewrite import write_preset_validate


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
    return session.query(Preset).all()


def return_preset(nickname):
    return session.query(Preset).filter(Preset.nickname == nickname).first()


def remove_preset(nickname):
    preset = session.query(Preset).filter(Preset.nickname == nickname).first()
    preset.delete()


def remove_all_presets():
    session.query(Preset).delete()
