# Entry point for ssmsplus
from tray import TrayApp
from settings import Settings
from settings_ui import SettingsWindow
from state import State
from watcher import start_watching
import threading
import pygetwindow as gw
import os
import configparser
import re
import time
import pyautogui
import pyperclip
import ctypes
import pygetwindow

settings = Settings()
temp_dir = settings.get_temp_dir()
state = State(settings)

VK_CTRL = 0x11
VK_N = 0x4E

def any_keys_pressed(vk_list):
    # Returns True if any of the keys in vk_list are currently pressed
    return any(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000 for vk in vk_list)

def wait_for_save_as_dialog(timeout=1):
    print("Waiting for 'Save File As' dialog to be focused...")
    end = time.time() + timeout
    while time.time() < end:
        w = pygetwindow.getActiveWindow()
        if w and w.title.strip().startswith("Save File As"):
            print("Save dialog focused.")
            return True
        time.sleep(0.05)
    print("Timeout: Save dialog not focused.")
    return False

def wait_until_keys_released(vk_list=[VK_CTRL, VK_N], timeout=1):
    print("Waiting for all hotkeys to be released...")
    end = time.time() + timeout
    while time.time() < end:
        if not any_keys_pressed(vk_list):
            print("All hotkeys released.")
            return True
        time.sleep(0.05)
    print("Timeout: Keys still pressed.")
    return False

def automate_save_as(target_path):

    if not wait_until_keys_released():
        print("Aborting save: Hotkeys still pressed.")
        return
    
    pyperclip.copy(target_path)
    pyautogui.press('alt')
    pyautogui.press('f')
    pyautogui.press('a')
    
    if not wait_for_save_as_dialog():
        print("Aborting save: Save File As dialog didn't focus.")
        return

    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')

def parse_server_db_from_title(title):
    # Looks for the first "SOME_SERVER.SOME_DB (" pattern
    m = re.search(r'([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+) \(', title)
    if m:
        return m.group(1), m.group(2)
    return None, None

def get_server_db_with_retry(timeout=1.5, poll_interval=0.1):
    end = time.time() + timeout
    while time.time() < end:
        title = get_active_ssms_title()
        if title:
            server, db = parse_server_db_from_title(title)
            if server and db:
                return server, db
        time.sleep(poll_interval)
    return None, None

def update_color_mappings_ini(config_path, server, db):
    config = configparser.ConfigParser()
    config.read(config_path)
    if not config.has_section(server):
        config.add_section(server)
    if not config.has_option(server, db):
        config.set(server, db, "-1")
        with open(config_path, "w") as f:
            config.write(f)
        print(f"Added {server}/{db} to color_mappings.ini with -1")

def save_temp_file_to_db_dir(temp_file, save_dir, server, db):
    basename = os.path.basename(temp_file).replace('..sql', '.sql')
    target_path = os.path.join(save_dir, server, db, 'temp', basename)
    automate_save_as(target_path)
    return target_path

def get_active_ssms_title():
    w = gw.getActiveWindow()
    if w and 'SQL Server Management Studio' in w.title:
        return w.title
    return None

def on_new_sql(temp_file):
    server, db = get_server_db_with_retry()
    if not server or not db:
        print("Could not detect server/db in SSMS window title after waiting. Skipping file:", temp_file)
        return
    save_dir = state.save_dir
    save_temp_file_to_db_dir(temp_file, save_dir, server, db)
    color_mappings_path = os.path.join(os.path.dirname(__file__), "config", "color_mappings.ini")
    update_color_mappings_ini(color_mappings_path, server, db)

def start_watcher_in_thread(temp_dir):
    watcher_thread = threading.Thread(target=start_watching, args=(temp_dir, on_new_sql), daemon=True)
    watcher_thread.start()
    return watcher_thread

def on_settings():
    temp_dir = settings.get("Folders", "TempDir", fallback="C:/Temp")
    save_dir = settings.get("Folders", "DestRoot", fallback="C:/Save")

    def on_save(new_temp, new_save):
        settings.set("Folders", "TempDir", new_temp)
        settings.set("Folders", "DestRoot", new_save)
        settings.save()
        print("Settings updated:", new_temp, new_save)

    threading.Thread(target=lambda: SettingsWindow(temp_dir, save_dir, on_save).show()).start()

def on_exit():
    print("Exiting app.")

def on_save_colors():
    print("Save Colors selected.")

if __name__ == '__main__':
    start_watcher_in_thread(temp_dir)
    tray = TrayApp(on_exit=on_exit, on_settings=on_settings, on_save_colors=on_save_colors)
    tray.run()