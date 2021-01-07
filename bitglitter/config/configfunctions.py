from bitglitter.config.palettemanager import palette_manager
from bitglitter.config.presetmanager import preset_manager
from bitglitter.config.readmanager import read_manager
from bitglitter.config.settingsmanager import settings_manager
from bitglitter.config.statisticsmanager import stats_manager


def remove_session():
    """Triggers all managers to reset their state."""

    palette_manager.remove_all_custom_palettes()
    preset_manager.remove_all_presets()
    read_manager.delete_all_streams()
    settings_manager.reset_defaults()
    stats_manager.clear_stats()
