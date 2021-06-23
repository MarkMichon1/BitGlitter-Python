from bitglitter.config.config import engine, session, SqlBaseClass, Statistics
from bitglitter.config.defaultdata import load_default_data
from bitglitter.config.del_pending_palettes import palette_manager
from bitglitter.config.presets import preset_manager
from bitglitter.config.read import read_manager
from bitglitter.config.settingsmanager import settings_manager




def remove_session():
    """Resets persistent data to factory default settings."""

    SqlBaseClass.metadata.drop_all(engine)
    load_default_data()


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
