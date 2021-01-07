from pathlib import Path
import pickle

from bitglitter.config.basemanager import BaseManager


class SettingsManager(BaseManager):
    """Holds both some constants as well as user settings which will be more expanded during GUI development."""

    def __init__(self):
        super().__init__()
        self._SAVE_FILE_NAME = 'settingsmanager'

        # Constants
        self.BG_VERSION = '2.0'  # Change this during version updates!  Used for internal/debug stuff.
        self.PROTOCOL_VERSION = 1  # This will be moved when we have more protocols.
        self.WRITE_WORKING_DIR = Path(__file__).resolve().parent.parent / 'Temp'
        self.DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parent.parent / 'Render Output'
        self.DEFAULT_PARTIAL_SAVE_PATH = Path(__file__).resolve().parent.parent / 'Partial Stream Data'
        self.VALID_VIDEO_FORMATS = ['.avi', '.flv', '.mov', '.mp4', '.wmv']
        self.VALID_IMAGE_FORMATS = ['.bmp', '.jpg', '.png']

        # Configurable
        self.default_bad_frame_strikes = 10
        self.write_path = self.DEFAULT_OUTPUT_PATH  # Desktop
        self.log_txt_path = Path(__file__).resolve().parent.parent / 'Logs'
        self.maximum_cpu_cores = 0  # unused for library, will be used in Desktop version.
        self.save_statistics = True  # Desktop

        self._save()

    def ffmpeg_verify(self):
        pass  # Desktop

    def reset_defaults(self):
        pass  # todo for desktop


try:
    current_directory = Path(__file__).resolve().parent
    pickle_path = current_directory / 'settingsmanager.bin'
    with open(pickle_path, 'rb') as unpickler:
        settings_manager = pickle.load(unpickler)

except FileNotFoundError:
    settings_manager = SettingsManager()
