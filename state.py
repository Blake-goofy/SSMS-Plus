"""Runtime (non-persistent) state management."""

from settings import Settings
from pathlib import Path
import os

settings = Settings()

class State:
    def __init__(self, settings):
        self.save_dir = settings.get_save_dir()

    temp_dir = Path(os.getenv("TEMP"))
    regex_path = None
    color_path = None
    first_run = True