"""System tray/taskbar widget code."""

import threading
import os
import sys
import pystray
from PIL import Image
from state import settings, state

class TrayApp:
    def __init__(self, on_exit=None, on_settings=None):
        self.icon = None
        self.on_exit = on_exit
        self.on_settings = on_settings
        self.running = True

    def run(self):
        # Get icon color from settings (default to yellow)
        icon_color = settings.get_tray_icon()
        icon_filename = f'ssmsplus_{icon_color}.ico'
        icon_path = os.path.join(os.path.dirname(sys.argv[0]), icon_filename)
        
        try:
            image = Image.open(icon_path)
        except Exception as e:
            # Try fallback to yellow if specified color doesn't exist
            if icon_color != 'yellow':
                fallback_path = os.path.join(os.path.dirname(sys.argv[0]), 'ssmsplus_yellow.ico')
                try:
                    image = Image.open(fallback_path)
                except:
                    # Final fallback to blank image
                    image = Image.new('RGB', (64, 64), color='white')
            else:
                # Final fallback to blank image
                image = Image.new('RGB', (64, 64), color='white')

        # Get tray name from settings
        tray_name = settings.get_tray_name()

        # Create menu - add a separator and make the first item the default
        menu = pystray.Menu(
            pystray.MenuItem('Open Settings', self.show_settings, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Reset Tab Colors', self.reset_tab_colors),
            pystray.MenuItem('Exit', self.exit_app)
        )
        
        self.icon = pystray.Icon("SSMS Plus", image, tray_name, menu)
        self.icon.run()

    def show_settings(self):
        if self.on_settings:
            self.on_settings()

    def reset_tab_colors(self):
        """Reset tab color tracking so colors will be applied again"""
        state.clear_tab_color_tracking()
        print("[tray] Tab color tracking reset - colors will be applied to new files")

    def exit_app(self):
        self.running = False
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()
    
    def update_icon_and_name(self):
        """Update the tray icon and name from current settings"""
        if self.icon:
            # Get current settings
            icon_color = settings.get_tray_icon()
            tray_name = settings.get_tray_name()
            
            # Load new icon
            icon_filename = f'ssmsplus_{icon_color}.ico'
            icon_path = os.path.join(os.path.dirname(sys.argv[0]), icon_filename)
            
            try:
                new_image = Image.open(icon_path)
                # Update the icon image and title
                self.icon.icon = new_image
                self.icon.title = tray_name
            except Exception as e:
                pass  # Keep current icon if loading fails

def start_tray_app():
    tray = TrayApp()
    thread = threading.Thread(target=tray.run, daemon=True)
    thread.start()
    return tray