from bitglitter.config.presets import preset_manager


def add_new_preset(nickname, output_mode='video', compression_enabled=True, scrypt_n=14, scrypt_r=8, scrypt_p=1,
                   max_cpu_cores=0, stream_palette_id='6', pixel_width=24, block_height=45, block_width=80,
                   frames_per_second=30):

    preset_manager.add_preset(nickname, output_mode, compression_enabled, scrypt_n, scrypt_r, scrypt_p, max_cpu_cores,
                              stream_palette_id, pixel_width, block_height, block_width, frames_per_second)


def return_all_preset_data():
    preset_manager.return_all_preset_data()


def return_preset_data(nickname):
    preset_manager.return_preset_data(nickname)


def remove_preset(nickname):
    preset_manager.remove_preset(nickname)


def remove_all_presets():
    preset_manager.remove_all_presets()
