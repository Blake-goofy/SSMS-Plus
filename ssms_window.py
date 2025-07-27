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
    
    @staticmethod
    def wait_for_query(timeout=10):
        """Wait for SSMS loading state to disappear and query window to be ready"""
        print("[ssms_window.wait_for_query] Waiting for loading state to disappear...")
        end = time.time() + timeout
        
        # Monitor for window title changes
        while time.time() < end:
            try:
                # Get ALL windows containing "Microsoft SQL Server Management Studio"
                all_windows = pygetwindow.getAllWindows()
                ssms_windows = [w for w in all_windows if w.title and "Microsoft SQL Server Management Studio" in w.title]
                
                # Check if any window is still in loading state
                loading_windows = [w for w in ssms_windows if w.title.strip() == "Microsoft SQL Server Management Studio"]
                
                if loading_windows:
                    print(f"[ssms_window.wait_for_query] Still loading... ({len(loading_windows)} loading windows)")
                    time.sleep(0.2)
                    continue
                
                # Look for SQLQuery windows (indicating ready state)
                sqlquery_windows = [w for w in ssms_windows if "SQLQuery" in w.title and " - " in w.title]
                
                if sqlquery_windows:
                    # Found SQLQuery window and no loading windows - we're ready
                    print(f"[ssms_window.wait_for_query] Ready! SQLQuery window detected: {sqlquery_windows[0].title.strip()}")
                    return True
                
                time.sleep(0.2)
                
            except Exception as e:
                print(f"[ssms_window.wait_for_query] Error checking windows: {e}")
                time.sleep(0.2)
        
        print("[ssms_window.wait_for_query] Timeout waiting for loading to complete")
        return False
    
    @staticmethod
    def save_temp_file_with_smart_naming(temp_file, save_dir, server, db):
        """Save function that waits for loading to complete before saving"""
        
        # Wait for loading to complete
        if not SsmsWindow.wait_for_query():
            print("[ssms_window.smart_naming] Loading didn't complete, using default naming")
            return SsmsWindow.save_temp_file_to_db_dir(temp_file, save_dir, server, db)
        
        # Generate consistent filename (no workflow detection needed)
        basename = os.path.basename(temp_file).replace('..sql', '.sql')
        if '_' in basename:
            unique_part = basename.split('_')[-1].replace('.sql', '')
        else:
            unique_part = basename.replace('.sql', '')
        
        # Use consistent naming pattern for all files
        custom_filename = f"{server}_{db}_{unique_part}.sql"
        print(f"[ssms_window.smart_naming] Saving as: {custom_filename}")
        
        # Create the target path and save
        target_path = os.path.join(save_dir, server, db, 'temp', custom_filename)
        target_path = target_path.replace('/', '\\')
        
        FileManager.create_save_dir(os.path.dirname(target_path))
        SsmsWindow.automate_save_as(target_path)
        write_server_db_to_regex_file(server, db)
        
        return target_path
    
    @staticmethod
    def save_temp_file_to_db_dir(temp_file, save_dir, server, db):

        basename = os.path.basename(temp_file).replace('..sql', '.sql')
        target_path = os.path.join(save_dir, server, db, 'temp', server+'_'+db+'_'+basename)
        # Ensure Windows backslashes in target path
        target_path = target_path.replace('/', '\\')
        FileManager.create_save_dir(os.path.dirname(target_path))
        SsmsWindow.automate_save_as(target_path)
        write_server_db_to_regex_file(server, db)
        return target_path

    @staticmethod
    def automate_save_as(target_path):
        """Automate the Save As dialog process"""
        
        VK_CTRL = 0x11
        VK_N = 0x4E

        def wait_until_keys_released(vk_list=[VK_CTRL, VK_N], timeout=1):

            def any_keys_pressed(vk_list):
                # Returns True if any of the keys in vk_list are currently pressed
                return any(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000 for vk in vk_list)
            
            end = time.time() + timeout
            while time.time() < end:
                if not any_keys_pressed(vk_list):
                    return True
                time.sleep(0.05)
            return False
        
        if not wait_until_keys_released():
            return
        
        pyperclip.copy(target_path)
        # must use keyDown/press/keyUp to avoid issues with modifier keys
        pyautogui.keyDown('ctrl')
        pyautogui.press('s')
        pyautogui.keyUp('ctrl')

        def wait_for_save_as_dialog(timeout=1):
            end = time.time() + timeout
            while time.time() < end:
                w = pygetwindow.getActiveWindow()
                if w and w.title.strip().startswith("Save File As"):
                    return True
                time.sleep(0.05)
            return False

        
        if not wait_for_save_as_dialog():
            return
                    
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')