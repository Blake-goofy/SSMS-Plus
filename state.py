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
        
        # Tab color tracking - set of combinations that have had colors applied this session
        self.tab_colors_applied = set()
    
    def mark_tab_color_applied(self, server, db=None):
        """Mark that tab color has been applied for this server/db combination"""
        if db is None:
            key = server.lower()
        else:
            key = f"{server.lower()}.{db.lower()}"
        self.tab_colors_applied.add(key)
        print(f"[state] Marked tab color as applied for: {key}")
    
    def is_tab_color_applied(self, server, db=None):
        """Check if tab color has already been applied for this server/db combination"""
        if db is None:
            key = server.lower()
        else:
            key = f"{server.lower()}.{db.lower()}"
        return key in self.tab_colors_applied
    
    def clear_tab_color_tracking(self):
        """Clear all tab color tracking (useful for new sessions)"""
        self.tab_colors_applied.clear()
        print("[state] Cleared tab color tracking")
    
    def forget_tab_color_applied(self, server, db=None):
        """Remove a specific server/db combination from the applied colors tracking"""
        if db is None:
            key = server.lower()
        else:
            key = f"{server.lower()}.{db.lower()}"
        if key in self.tab_colors_applied:
            self.tab_colors_applied.remove(key)
            print(f"[state] Forgot tab color application for: {key}")
        else:
            print(f"[state] Tab color for {key} was not in applied set")

# Create shared instances
settings = Settings()
state = State(settings=settings)