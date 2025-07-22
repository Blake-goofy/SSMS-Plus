"""System tray/taskbar widget code."""

import threading
import os
import sys
import pystray
from PIL import Image

class TrayApp:
    def __init__(self, on_exit=None, on_settings=None, on_save_colors=None):
        self.icon = None
        self.on_exit = on_exit
        self.on_settings = on_settings
        self.on_save_colors = on_save_colors
        self.running = True

    def run(self):
        icon_path = os.path.join(os.path.dirname(sys.argv[0]), 'ssms.ico')
        try:
            image = Image.open(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
            # fallback to blank image
            image = Image.new('RGB', (64, 64), color='white')

        menu = pystray.Menu(
            pystray.MenuItem('Settings', self.show_settings),
            pystray.MenuItem('Save Colors', self.save_colors),
            pystray.MenuItem('Exit', self.exit_app)
        )
        self.icon = pystray.Icon("SSMS Plus", image, "SSMS Plus", menu)
        self.icon.run()

    def show_settings(self):
        if self.on_settings:
            self.on_settings()
        else:
            print("Settings selected.")

    def save_colors(self):
        if self.on_save_colors:
            self.on_save_colors()
        else:
            print("Save Colors selected.")

    def exit_app(self):
        self.running = False
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()

def start_tray_app():
    tray = TrayApp()
    thread = threading.Thread(target=tray.run, daemon=True)
    thread.start()
    return tray

if __name__ == "__main__":
    # Example: start in standalone mode
    start_tray_app()
    # Keep main thread alive
    while True:
        try:
            if not threading.main_thread().is_alive():
                break
        except KeyboardInterrupt:
            break