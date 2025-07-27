"""SSMS window parsing/interacting functions."""
import pyautogui
import pyperclip
import ctypes
import pygetwindow
import os
import time
from file_manager import FileManager
from regex_writer import write_server_db_to_regex_file


class SsmsWindow:
    
    def save_temp_file_to_db_dir(temp_file, save_dir, server, db):

        def automate_save_as(target_path):

            VK_CTRL = 0x11
            VK_N = 0x4E

            def wait_until_keys_released(vk_list=[VK_CTRL, VK_N], timeout=1):

                def any_keys_pressed(vk_list):
                    # Returns True if any of the keys in vk_list are currently pressed
                    return any(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000 for vk in vk_list)
                
                print("Waiting for all hotkeys to be released...")
                end = time.time() + timeout
                while time.time() < end:
                    if not any_keys_pressed(vk_list):
                        print("All hotkeys released.")
                        return True
                    time.sleep(0.05)
                print("Timeout: Keys still pressed.")
                return False
            
            if not wait_until_keys_released():
                print("Aborting save: Hotkeys still pressed.")
                return
            
            pyperclip.copy(target_path)
            # must use keyDown/press/keyUp to avoid issues with modifier keys
            pyautogui.keyDown('ctrl')
            pyautogui.press('s')
            pyautogui.keyUp('ctrl')

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

            
            if not wait_for_save_as_dialog():
                print("Aborting save: Save File As dialog didn't focus.")
                return
                        
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('enter')

        basename = os.path.basename(temp_file).replace('..sql', '.sql')
        target_path = os.path.join(save_dir, server, db, 'temp', server+'_'+db+'_'+basename)
        # Ensure Windows backslashes in target path
        target_path = target_path.replace('/', '\\')
        print(f"Saving to: {target_path}")
        FileManager.create_save_dir(os.path.dirname(target_path))
        automate_save_as(target_path)
        write_server_db_to_regex_file(server, db)
        FileManager.delete_temp_files()
        return target_path