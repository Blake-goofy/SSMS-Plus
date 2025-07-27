"""Runtime (non-persistent) state management."""

from settings import Settings

settings = Settings()

class State:
    def __init__(self, settings):
        self.save_dir = settings.get_save_dir()
        self.temp_dir = settings.get_temp_dir()

    regex_path = None
    color_path = None
    first_run = True