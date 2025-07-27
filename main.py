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
import sys
import tempfile
import atexit

settings = Settings()
state = State(settings=settings)

# Single instance check
LOCK_FILE = os.path.join(tempfile.gettempdir(), "ssmsplus.lock")

def is_already_running():
    """Check if another instance is already running"""
    if os.path.exists(LOCK_FILE):
        try:
            # Try to read the PID from the lock file
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if the process is still running (Windows)
            import subprocess
            result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                  capture_output=True, text=True, shell=True)
            if str(pid) in result.stdout:
                return True
            else:
                # Process no longer exists, remove stale lock file
                os.remove(LOCK_FILE)
                return False
        except (ValueError, FileNotFoundError, subprocess.SubprocessError):
            # If we can't check properly, assume not running and remove lock
            try:
                os.remove(LOCK_FILE)
            except:
                pass
            return False
    return False

def create_lock_file():
    """Create a lock file with current process ID"""
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

def cleanup_lock_file():
    """Remove the lock file on exit"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except:
        pass

def start_watcher_in_thread(temp_dir):
    watcher_thread = threading.Thread(target=start_watching, args=(temp_dir, on_new_sql), daemon=True)
    watcher_thread.start()
    return watcher_thread

def on_settings():
    temp_dir = state.temp_dir
    save_dir = state.save_dir

    def on_save(new_temp, new_save):
        settings.set("Folders", "TempDir", new_temp)
        settings.set("Folders", "SaveDir", new_save)
        settings.save()
        print("Settings updated:", new_temp, new_save)

    threading.Thread(target=lambda: SettingsWindow(temp_dir, save_dir, on_save).show()).start()

def on_exit():
    print("Exiting app.")

def on_save_colors():
    FileManager.save_colors()

if __name__ == '__main__':
    # Check if another instance is already running
    if is_already_running():
        print("SSMS Plus is already running! Only one instance can run at a time.")
        print("If you believe this is an error, delete the lock file at:", LOCK_FILE)
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Create lock file and register cleanup
    create_lock_file()
    atexit.register(cleanup_lock_file)
    
    # if temp_dir or save_dir isn't a real directory, open the settings window
    if not state.temp_dir or not state.save_dir or not os.path.isdir(state.temp_dir) or not os.path.isdir(state.save_dir):
        on_settings()
    else:
        start_watcher_in_thread(state.temp_dir)
        #FileManager.save_colors()
    tray = TrayApp(on_exit=on_exit, on_settings=on_settings, on_save_colors=on_save_colors)
    tray.run()