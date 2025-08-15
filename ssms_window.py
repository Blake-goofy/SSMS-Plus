"""SSMS window parsing/interacting functions."""
import pyautogui
import ctypes
import pygetwindow
import os
import time
from file_manager import FileManager
from regex_writer import write_to_regex_file
from state import settings, state

class SsmsWindow:
    
    @staticmethod
    def is_caps_lock_on():
        """Check if Caps Lock is currently enabled"""
        # GetKeyState for VK_CAPITAL (0x14) returns 1 if Caps Lock is on, 0 if off
        VK_CAPITAL = 0x14
        return ctypes.windll.user32.GetKeyState(VK_CAPITAL) & 1 == 1
    
    @staticmethod
    def write_text_handling_caps_lock(text):
        """Write text properly regardless of caps lock state"""
        caps_lock_is_on = SsmsWindow.is_caps_lock_on()
        
        if caps_lock_is_on:
            # If caps lock is on, we need to invert the case of letters
            # since caps lock will invert them again
            inverted_text = ""
            for char in text:
                if char.isupper():
                    inverted_text += char.lower()
                elif char.islower():
                    inverted_text += char.upper()
                else:
                    inverted_text += char
            print(f"[ssms_window.write_text_handling_caps_lock] Caps Lock ON - inverting text: '{text}' -> '{inverted_text}'")
            pyautogui.write(inverted_text, interval=0)
        else:
            print(f"[ssms_window.write_text_handling_caps_lock] Caps Lock OFF - writing text normally: '{text}'")
            pyautogui.write(text, interval=0)
    
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
                    time.sleep(0.1)
                    continue
                
                # Look for SQLQuery windows and check if they show the saved file pattern
                sqlquery_windows = [w for w in ssms_windows if "SQLQuery" in w.title and " - " in w.title]
                
                if sqlquery_windows:
                    for window in sqlquery_windows:
                        title = window.title.strip()
                        print(f"[ssms_window.wait_for_query] Checking window: {title}")
                        
                        # Check if title shows the duplicated pattern indicating file is saved
                        # Pattern: "SQLQueryX.sql - SERVER.DB (user)* - SQLQueryX.sql - SERVER.DB (user)* - Microsoft SQL Server Management Studio"
                        if title.count(" - ") >= 4:  # Should have multiple " - " separators
                            parts = title.split(" - ")
                            if len(parts) >= 5:
                                # Check if the first and third parts are the same (SQLQueryX.sql)
                                first_part = parts[0].strip()
                                third_part = parts[2].strip() if len(parts) > 2 else ""
                                
                                if first_part == third_part and first_part.startswith("SQLQuery") and first_part.endswith(".sql"):
                                    print(f"[ssms_window.wait_for_query] Ready! Saved file pattern detected: {title}")
                                    return True
                        
                        # Also check for the temp file pattern (old behavior as fallback)
                        # Pattern: "SQLQueryX.sql - TEMPFILE.sql - SERVER.DB (user)* - Microsoft SQL Server Management Studio"
                        if "_" in title and ".sql" in title:
                            temp_pattern_parts = title.split(" - ")
                            if len(temp_pattern_parts) >= 4:
                                second_part = temp_pattern_parts[1].strip()
                                if second_part.endswith(".sql") and "_" in second_part:
                                    print(f"[ssms_window.wait_for_query] Temp file pattern still showing: {title}")
                                    # Continue waiting for the saved pattern
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"[ssms_window.wait_for_query] Error checking windows: {e}")
                time.sleep(0.1)
        
        print("[ssms_window.wait_for_query] Timeout waiting for saved file pattern")
        return False
    
    @staticmethod
    def set_tab_color(color_index, server=None, db=None):
        """Set the tab color in SSMS using keyboard shortcuts"""
        print(f"[ssms_window.set_tab_color] Setting tab color to index {color_index}")
        
        try:
            # Speed up pyautogui by reducing delays
            original_pause = pyautogui.PAUSE
            pyautogui.PAUSE = 0.01  # Reduce from default 0.1 to 0.01
            
            pyautogui.hotkey('alt', 'w')
            pyautogui.press('s')
            pyautogui.press('up')  # Go to top of color list
            pyautogui.press('right')  # Move to color grid
            
            # Optimize navigation: if color_index > 8, use up arrows instead of down
            if color_index <= 8:
                # For indices 0-8, just press down
                for i in range(color_index):
                    pyautogui.press('down')
                print(f"[ssms_window.set_tab_color] Navigated down {color_index} times")
            else:
                # For indices 9-16, press up from the bottom (17 total colors: 0-16)
                # Going up from 0 wraps to 16, so up_presses = 17 - color_index
                up_presses = 17 - color_index
                for i in range(up_presses):
                    pyautogui.press('up')
                print(f"[ssms_window.set_tab_color] Navigated up {up_presses} times to reach index {color_index}")
                        
            pyautogui.press('enter')
            print(f"[ssms_window.set_tab_color] Tab color set successfully")
            
            # Restore original pause setting
            pyautogui.PAUSE = original_pause
            
        except Exception as e:
            # Make sure to restore pause setting even if there's an error
            pyautogui.PAUSE = original_pause
            print(f"[ssms_window.set_tab_color] Error setting tab color: {e}")
    
    @staticmethod
    def apply_tab_color(server, db):
        """Apply tab color based on settings for the given server/db combination"""
        try:
            # Check if tab coloring is enabled
            if not settings.get_tab_coloring_enabled():
                print(f"[ssms_window.apply_tab_color] Tab coloring is disabled, skipping")
                return
            
            # Check if the ColorByRegexConfig.txt file exists (this also clears state if missing)
            if not SsmsWindow.is_combination_in_actual_regex_files(server, db):
                print(f"[ssms_window.apply_tab_color] Regex file missing or combination not found, skipping color application")
                return
            
            # Check if we've already applied color for this combination this session
            if state.is_tab_color_applied(server, db):
                print(f"[ssms_window.apply_tab_color] Tab color already applied for {server}.{db}, skipping")
                return
            
            # Get the color index for this combination
            color_index = settings.get_tab_color_for_combination(server, db)
            print(f"[ssms_window.apply_tab_color] Applying color index {color_index} for {server}.{db}")
            
            # Apply the color
            SsmsWindow.set_tab_color(color_index, server, db)
            
            # Mark this combination as having had its color applied
            state.mark_tab_color_applied(server, db)
            
        except Exception as e:
            print(f"[ssms_window.apply_tab_color] Error applying tab color: {e}")
    
    @staticmethod
    def is_combination_in_actual_regex_files(server, db):
        """Check if the ColorByRegexConfig.txt file exists and clear state if no color JSON files exist"""
        try:
            # Get the temp directory and search for the actual SSMS GUID folder
            temp_dir_str = settings.get_temp_dir()
            
            if not temp_dir_str:
                print(f"[ssms_window.is_combination_in_actual_regex_files] No temp directory configured")
                return False
            
            from pathlib import Path
            temp_dir = Path(temp_dir_str)
            
            # Look for ColorByRegexConfig.txt files recursively (they're in GUID subfolders)
            config_files = list(temp_dir.rglob("ColorByRegexConfig.txt"))
            
            if not config_files:
                print(f"[ssms_window.is_combination_in_actual_regex_files] No ColorByRegexConfig.txt files found in {temp_dir}")
                # Clear all applied color state since no config files exist
                print(f"[ssms_window.is_combination_in_actual_regex_files] Clearing all tab color state due to missing config files")
                state.clear_tab_color_tracking()
                return False
            
            # Find the most recent config file (in case there are multiple GUID folders)
            def folder_time(path):
                folder = path.parent
                stat = folder.stat()
                return max(stat.st_mtime, stat.st_ctime)
            
            latest_config = max(config_files, key=folder_time)
            latest_folder = latest_config.parent
            
            print(f"[ssms_window.is_combination_in_actual_regex_files] Found ColorByRegexConfig.txt in: {latest_folder}")
            
            # Check for color JSON files - if none exist, clear state but still allow color application
            try:
                color_json_files = list(latest_folder.glob("customized-groupid-color-*.json"))
                
                if color_json_files:
                    print(f"[ssms_window.is_combination_in_actual_regex_files] Found {len(color_json_files)} existing color JSON files: {[f.name for f in color_json_files]}")
                else:
                    print(f"[ssms_window.is_combination_in_actual_regex_files] No color JSON files found yet - clearing state to allow fresh color application")
                    # Clear state since no color files exist yet, but allow the function to proceed
                    state.clear_tab_color_tracking()
                
                # Return True as long as ColorByRegexConfig.txt exists - color JSONs will be created when colors are applied
                return True
                    
            except Exception as e:
                print(f"[ssms_window.is_combination_in_actual_regex_files] Error listing directory {latest_folder}: {e}")
                # Still return True if we can find the config file, even if we can't list the directory
                return True
                
        except Exception as e:
            print(f"[ssms_window.is_combination_in_actual_regex_files] Error checking color files: {e}")
            return False
        
    
    @staticmethod
    def save_temp_file(temp_file, save_dir, server, db):
        """Save function that waits for loading to complete before saving"""
        
        # Extract temp name for unique naming
        basename = os.path.basename(temp_file).replace('..sql', '.sql')
        
        # Convert server and db to uppercase for filename, leave basename as-is
        custom_filename = f"{server.upper()}_{db.upper()}_{basename}"
        print(f"[ssms_window.save_temp_file] Using filename: {custom_filename}")
        
        # Create the target path and save (use original case for directory structure)
        target_path = os.path.join(save_dir, server, db, 'temp', custom_filename)
        target_path = target_path.replace('/', '\\')
        print(f"[ssms_window.save_temp_file] Target path: {target_path}")
        
        # Try to wait for loading to complete before proceeding
        print(f"[ssms_window.save_temp_file] Waiting for any loading screens to complete...")
        SsmsWindow.wait_for_query()
        
        # Check if the ColorByRegexConfig.txt file exists before proceeding
        # This will also clear tab color state if the file is missing
        SsmsWindow.is_combination_in_actual_regex_files(server, db)
        
        FileManager.create_save_dir(os.path.dirname(target_path))
        SsmsWindow.automate_save_as(target_path)
        write_to_regex_file(server, db)
        # Apply tab coloring if enabled
        SsmsWindow.apply_tab_color(server, db)

        return target_path

    @staticmethod
    def automate_save_as(target_path):
        """Automate the Save As dialog process using caps lock-aware typing"""
        
        # Speed up pyautogui by reducing delays
        original_pause = pyautogui.PAUSE
        pyautogui.PAUSE = 0.001  # Reduce from default 0.1 to 0.001

        try:
            print(f"[ssms_window.automate_save_as] Will type filename with caps lock detection: {target_path}")
            
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
            
            def perform_save_attempt():
                """Perform a single save attempt using caps lock-aware typing"""
                if not wait_until_keys_released():
                    return False
                
                print(f"[ssms_window.perform_save_attempt] Performing save attempt with caps lock handling: {target_path}")
                
                # must use keyDown/press/keyUp to avoid issues with modifier keys
                pyautogui.keyDown('ctrl')
                pyautogui.press('s')
                pyautogui.keyUp('ctrl')
                
                # Check for Save As dialog with loading window detection
                end = time.time() + 0.5
                while time.time() < end:
                    # Check if Save As dialog appeared
                    w = pygetwindow.getActiveWindow()
                    if w and w.title.strip().startswith("Save File As"):
                        print("[ssms_window.perform_save_attempt] Save As dialog appeared")
                        
                        # Use caps lock-aware typing
                        print(f"[ssms_window.perform_save_attempt] Typing filename with caps lock detection: {target_path}")
                        
                        SsmsWindow.write_text_handling_caps_lock(target_path)
                        
                        pyautogui.press('enter')
                        return True
                    
                    # Check if loading window appeared (indicating save was intercepted)
                    try:
                        all_windows = pygetwindow.getAllWindows()
                        loading_windows = [w for w in all_windows if w.title and w.title.strip() == "Microsoft SQL Server Management Studio"]
                        
                        if loading_windows:
                            print("[ssms_window.perform_save_attempt] Loading window detected, waiting for it to disappear...")
                            
                            # Wait for loading window to go away
                            loading_end = time.time() + 10  # Give it 10 seconds to load
                            while time.time() < loading_end:
                                all_windows = pygetwindow.getAllWindows()
                                loading_windows = [w for w in all_windows if w.title and w.title.strip() == "Microsoft SQL Server Management Studio"]
                                if not loading_windows:
                                    print("[ssms_window.perform_save_attempt] Loading window gone, retrying save...")
                                    break
                                time.sleep(0.1)
                            
                            # Retry the save after loading is done
                            print("[ssms_window.perform_save_attempt] Retrying save after loading screen...")
                            
                            pyautogui.keyDown('ctrl')
                            pyautogui.press('s')
                            pyautogui.keyUp('ctrl')
                            # Continue the loop to check for Save As dialog again
                            
                    except Exception as e:
                        print(f"[ssms_window.perform_save_attempt] Error checking for loading window: {e}")
                    
                    time.sleep(0.01)
                
                print("[ssms_window.perform_save_attempt] Save As dialog did not appear within timeout")
                return False
            
            # First save attempt
            print(f"[ssms_window.automate_save_as] First save attempt for: {target_path}")
            if perform_save_attempt():
                print(f"[ssms_window.automate_save_as] Save successful on first attempt")
            else:
                print(f"[ssms_window.automate_save_as] First attempt failed, retrying...")
                # Second attempt - don't check result, just proceed
                perform_save_attempt()
                print(f"[ssms_window.automate_save_as] Second attempt completed")
                    
        finally:
            # Always restore original pause setting
            pyautogui.PAUSE = original_pause