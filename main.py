# Entry point for ssmsplus
from tray import TrayApp
from settings import Settings
from settings_ui import SettingsWindow
from state import State
from watcher import start_watching
import threading
from watcher import on_new_sql
from file_manager import FileManager

settings = Settings()
state = State(settings=settings)

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
    start_watcher_in_thread(state.temp_dir)
    FileManager.save_colors()
    tray = TrayApp(on_exit=on_exit, on_settings=on_settings, on_save_colors=on_save_colors)
    tray.run()