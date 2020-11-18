import pickle

from bitglitter.config.basemanager import BaseManager


class SettingsManager(BaseManager):
    """Holds both some constants as well as user settings which will be more expanded during GUI development."""

    def __init__(self):
        super().__init__()
        self._SAVE_FILE_NAME = 'settingsmanager'

        self.BG_VERSION = '1.1'  # Change this during version updates!  Used for internal/debug stuff.
        self.DEFAULT_TEMP_WRITE_PATH = 'Temp'
        self.DEFAULT_PARTIAL_SAVE_PATH = 'Partial Stream Saves'
        self.VALID_VIDEO_FORMATS = ['.avi', '.flv', '.mov', '.mp4', '.wmv']
        self.VALID_IMAGE_FORMATS = ['.bmp', '.jpg', '.png']

        self.default_bad_frame_strikes = 10
        self.write_path = None  # todo: implement and add as utility external function
        self.log_txt_path = None  # todo... implement

        self._save()

    def ffmpeg_verify(self):
        pass  # todo


try:
    with open('settingsmanager.bin', 'rb') as unpickler:
        settings_manager = pickle.load(unpickler)

except:
    settings_manager = SettingsManager()
