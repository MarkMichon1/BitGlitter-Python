from bitglitter.config.config import session
from bitglitter.config.configmodels import Config, Constants, Statistics
from bitglitter.config.defaultdbdata import load_default_db_data
from bitglitter.config.palettemodels import Palette
from bitglitter.config.presetmodels import Preset
from bitglitter.config.readmodels.streamread import StreamRead


def remove_session():
    """Resets persistent data to factory default settings."""
    model_list = [Config, Constants, Palette, Preset, Statistics, StreamRead]
    for model in model_list:
        session.query(model).delete()
    session.commit()
    load_default_db_data()


def return_settings():
    config = session.query(Config).first()
    return {'decoded_files_output_path': config.decoded_files_output_path, 'read_bad_frame_strikes':
            config.read_bad_frame_strikes, 'disable_bad_frame_strikes': config.disable_bad_frame_strikes, 'write_path':
            config.write_path, 'log_txt_path': config.log_txt_path, 'log_output': config.log_output,
            'maximum_cpu_cores': config.maximum_cpu_cores, 'save_statistics': config.save_statistics,
            'output_stream_title': config.output_stream_title, 'MAX_SUPPORTED_CPU_CORES':
            config.MAX_SUPPORTED_CPU_CORES, 'logging_level': config.logging_level}


def update_settings(decoded_files_output_path, read_bad_frame_strikes, disable_bad_frame_strikes, write_path,
                    log_txt_path, log_output, logging_level, maximum_cpu_cores, save_statistics, output_stream_title):
    config = session.query(Config).first()
    config.decoded_files_output_path = decoded_files_output_path
    config.read_bad_frame_strikes = read_bad_frame_strikes
    config.disable_bad_frame_strikes = disable_bad_frame_strikes
    config.write_path = write_path
    config.log_txt_path = log_txt_path
    config.log_output = log_output
    config.logging_level = logging_level
    config.maximum_cpu_cores = maximum_cpu_cores
    config.save_statistics = save_statistics
    config.output_stream_title = output_stream_title
    config.save()


def output_stats():
    """Returns a dictionary object containing read and write statistics."""
    stats = session.query(Statistics).first()
    return stats.return_stats()


def clear_stats():
    """Resets all write and read values back to zero."""
    stats = session.query(Statistics).first()
    stats.clear_stats()


def _write_update(blocks, frames, data):
    """Internal function to update stats after rendering completes, along with read update below."""
    stats = session.query(Statistics).first()
    stats.write_update(blocks, frames, data)


def _read_update(blocks, frames, data):
    stats = session.query(Statistics).first()
    stats.read_update(blocks, frames, data)
