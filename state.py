"""Runtime (non-persistent) state management."""

from settings import Settings

class State:
    def __init__(self, settings):
        self.settings = settings  # Store reference to settings
        self.save_dir = settings.get_save_dir()
        self.temp_dir = settings.get_temp_dir()
        self.regex_path = None
        self.color_path = None
        self.first_run = True
        
        # Application state
        self.current_settings_window = None
        self.current_watcher_observer = None
        
        # Session tracking
        self.session_start_time = None

# Create shared instances
settings = Settings()
state = State(settings=settings)