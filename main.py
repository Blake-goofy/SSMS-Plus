# Entry point for ssmsplus
from tray import TrayApp
from settings_ui import SettingsWindow
from state import state, settings
from watcher import create_watcher
from file_manager import FileManager
import threading
from watcher import on_new_sql
import os
import sys

def start_watcher_in_thread(temp_dir):
    # Stop existing watcher if it exists
    if state.current_watcher_observer:
        state.current_watcher_observer.stop()
        state.current_watcher_observer = None
    
    # Start new watcher
    state.current_watcher_observer = create_watcher(temp_dir, on_new_sql)
    return state.current_watcher_observer

def on_settings():
    # If a settings window is already open, bring it to focus
    if state.current_settings_window and state.current_settings_window.root.winfo_exists():
        try:
            state.current_settings_window.root.lift()
            state.current_settings_window.root.focus_force()
            state.current_settings_window.root.attributes('-topmost', True)
            state.current_settings_window.root.after_idle(state.current_settings_window.root.attributes, '-topmost', False)
            return
        except:
            # Window no longer exists, create a new one
            state.current_settings_window = None
    
    temp_dir = state.temp_dir
    save_dir = state.save_dir
    
    # Check if this is being called because directories don't exist
    dirs_missing = not temp_dir or not save_dir or not os.path.isdir(temp_dir) or not os.path.isdir(save_dir)
    initial_error = "Both directories must exist." if dirs_missing else None

    def on_save(new_temp, new_save):
        old_temp = state.temp_dir
        settings.set_temp_dir(new_temp)
        settings.set_save_dir(new_save)
        
        # Update state with new directories
        state.temp_dir = new_temp
        state.save_dir = new_save
        
        # Only restart watcher if temp directory changed
        if old_temp != new_temp:
            start_watcher_in_thread(new_temp)
        
        # Update tray icon and name if they changed
        if hasattr(state, 'current_tray_app') and state.current_tray_app:
            state.current_tray_app.update_icon_and_name()

    def show_settings_window():
        state.current_settings_window = SettingsWindow(temp_dir, save_dir, on_save, initial_error)
        state.current_settings_window.show()
        state.current_settings_window = None  # Clear reference when window closes

    threading.Thread(target=show_settings_window).start()

def on_exit():
    # Stop watcher if it's running 
    if state.current_watcher_observer:
        state.current_watcher_observer.stop()
        state.current_watcher_observer = None

if __name__ == '__main__':
    # Initialize session and cleanup old temp files
    if state.save_dir and os.path.isdir(state.save_dir):
        FileManager.mark_session_start()
        FileManager.cleanup_old_temp_files()
    
    # Clear tab color tracking for new session
    state.clear_tab_color_tracking()
    
    # if temp_dir or save_dir isn't a real directory, open the settings window
    if not state.temp_dir or not state.save_dir or not os.path.isdir(state.temp_dir) or not os.path.isdir(state.save_dir):
        on_settings()
    else:
        start_watcher_in_thread(state.temp_dir)
    tray = TrayApp(on_exit=on_exit, on_settings=on_settings)
    state.current_tray_app = tray  # Store reference for updates
    tray.run()