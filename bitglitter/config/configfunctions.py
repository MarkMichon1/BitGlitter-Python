from bitglitter.config.config import Config, Constants, session, Statistics
from bitglitter.config.defaultdbdata import load_default_db_data
from bitglitter.config.palettemodels import Palette, PaletteColor




def remove_session():
    """Resets persistent data to factory default settings."""
    # todo: add future read models
    model_list = [Config, Constants, Palette, PaletteColor, Statistics]
    for model in model_list:
        session.query(model).delete()
    session.commit()
    load_default_db_data()


def output_stats():
    """Returns a dictionary object containing read and write statistics."""
    stats = session.query(Statistics).first()
    return stats.return_stats()


def _write_update(blocks, frames, data):
    """Internal function to update stats after rendering completes, along with read update below."""
    stats = session.query(Statistics).first()
    stats.write_update(blocks, frames, data)


def _read_update(blocks, frames, data):
    stats = session.query(Statistics).first()
    stats.read_update(blocks, frames, data)


def clear_stats():
    """Resets all write and read values back to zero."""
    stats = session.query(Statistics).first()
    stats.clear_stats()
