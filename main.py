# Entry point for ssmsplus
from tray import TrayApp
from settings import Settings
from settings_ui import SettingsWindow

settings = Settings()

def on_settings():
    temp_dir = settings.get("Folders", "TempDir", fallback="C:/Temp")
    save_dir = settings.get("Folders", "DestRoot", fallback="C:/Save")

    def on_save(new_temp, new_save):
        settings.set("Folders", "TempDir", new_temp)
        settings.set("Folders", "DestRoot", new_save)
        settings.save()
        print("Settings updated:", new_temp, new_save)

    # You may run in a new thread if called from the tray
    import threading
    threading.Thread(target=lambda: SettingsWindow(temp_dir, save_dir, on_save).show()).start()

def on_exit():
    print("Exiting app.")

def on_save_colors():
    print("Save Colors selected.")

if __name__ == '__main__':
    tray = TrayApp(on_exit=on_exit, on_settings=on_settings, on_save_colors=on_save_colors)
    tray.run()