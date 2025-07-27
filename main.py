# Entry point for ssmsplus
from tray import TrayApp
from settings import Settings
from settings_ui import SettingsWindow
from state import State
from watcher import start_watching
import threading
from watcher import on_new_sql
from file_manager import FileManager
import os

settings = Settings()
state = State(settings=settings)

# Global variable to track the current settings window
current_settings_window = None

def start_watcher_in_thread(temp_dir):
    watcher_thread = threading.Thread(target=start_watching, args=(temp_dir, on_new_sql), daemon=True)
    watcher_thread.start()
    return watcher_thread

def on_settings():
    global current_settings_window
    
    # If a settings window is already open, bring it to focus
    if current_settings_window and current_settings_window.root.winfo_exists():
        try:
            current_settings_window.root.lift()
            current_settings_window.root.focus_force()
            current_settings_window.root.attributes('-topmost', True)
            current_settings_window.root.after_idle(current_settings_window.root.attributes, '-topmost', False)
            return
        except:
            # Window no longer exists, create a new one
            current_settings_window = None
    
    temp_dir = state.temp_dir
    save_dir = state.save_dir
    
    # Check if this is being called because directories don't exist
    dirs_missing = not temp_dir or not save_dir or not os.path.isdir(temp_dir) or not os.path.isdir(save_dir)
    initial_error = "Both directories must exist." if dirs_missing else None

    def on_save(new_temp, new_save):
        settings.set_temp_dir(new_temp)
        settings.set_save_dir(new_save)
        print("Settings updated:", new_temp, new_save)

    def show_settings_window():
        global current_settings_window
        current_settings_window = SettingsWindow(temp_dir, save_dir, on_save, initial_error)
        current_settings_window.show()
        current_settings_window = None  # Clear reference when window closes

    threading.Thread(target=show_settings_window).start()

def on_exit():
    print("Exiting app.")

def on_save_colors():
    FileManager.save_colors()

if __name__ == '__main__':
    # if temp_dir or save_dir isn't a real directory, open the settings window
    if not state.temp_dir or not state.save_dir or not os.path.isdir(state.temp_dir) or not os.path.isdir(state.save_dir):
        on_settings()
    else:
        start_watcher_in_thread(state.temp_dir)
        #FileManager.save_colors()
    tray = TrayApp(on_exit=on_exit, on_settings=on_settings, on_save_colors=on_save_colors)
    tray.run()