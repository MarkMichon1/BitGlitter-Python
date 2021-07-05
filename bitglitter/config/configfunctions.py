from bitglitter.config.config import session
from bitglitter.config.configmodels import Config, Constants, Statistics
from bitglitter.config.defaultdbdata import load_default_db_data
from bitglitter.config.palettemodels import Palette, PaletteColor
from bitglitter.config.presetmodels import Preset
from bitglitter.config.readmodels import StreamRead


def remove_session():
    """Resets persistent data to factory default settings."""
    model_list = [Config, Constants, Palette, PaletteColor, Preset, Statistics, StreamRead]
    for model in model_list:
        session.query(model).delete()
    session.commit()
    load_default_db_data()


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
