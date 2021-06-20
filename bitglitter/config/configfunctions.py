from bitglitter.config.palettes import palette_manager
from bitglitter.config.presets import preset_manager
from bitglitter.config.read import read_manager
from bitglitter.config.settingsmanager import settings_manager
from bitglitter.config.statistics import stats_manager


def remove_session():
    """Triggers all managers to reset their state."""

    palette_manager.remove_all_custom_palettes()
    preset_manager.remove_all_presets()
    read_manager.delete_all_streams()
    settings_manager.reset_defaults()
    stats_manager.clear_stats()
