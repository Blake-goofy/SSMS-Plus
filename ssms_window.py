"""SSMS window parsing/interacting functions."""
import pyautogui
import pyperclip
import ctypes
import pygetwindow
import os
import time
from file_manager import FileManager
from regex_writer import write_to_regex_file
from state import settings, state

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
    def set_tab_color(color_index):
        """Set the tab color in SSMS using keyboard shortcuts"""
        print(f"[ssms_window.set_tab_color] Setting tab color to index {color_index}")
        
        try:
            pyautogui.hotkey('alt', 'w')
            pyautogui.press('s')
            pyautogui.press('up')  # Go to top of color list
            pyautogui.press('right')  # Move to color grid
            for i in range(color_index):
                pyautogui.press('down')
            pyautogui.press('enter')
            print(f"[ssms_window.set_tab_color] Tab color set successfully")
        except Exception as e:
            print(f"[ssms_window.set_tab_color] Error setting tab color: {e}")
    
    @staticmethod
    def apply_tab_color(server, db):
        """Apply tab color based on settings for the given server/db combination"""
        try:
            # Check if tab coloring is enabled
            if not settings.get_tab_coloring_enabled():
                print(f"[ssms_window.apply_tab_color] Tab coloring is disabled, skipping")
                return
            
            # Check if we've already applied color for this combination this session
            if state.is_tab_color_applied(server, db):
                print(f"[ssms_window.apply_tab_color] Tab color already applied for {server}.{db}, skipping")
                return
            
            # Get the color index for this combination
            color_index = settings.get_tab_color_for_combination(server, db)
            print(f"[ssms_window.apply_tab_color] Applying color index {color_index} for {server}.{db}")
            
            # Apply the color
            SsmsWindow.set_tab_color(color_index)
            
            # Mark this combination as having had its color applied
            state.mark_tab_color_applied(server, db)
            
        except Exception as e:
            print(f"[ssms_window.apply_tab_color] Error applying tab color: {e}")
    
    
    @staticmethod
    def save_temp_file(temp_file, save_dir, server, db):
        """Save function that waits for loading to complete before saving"""
        
        # Wait for loading to complete and file to be saved properly
        if not SsmsWindow.wait_for_query():
            print("[ssms_window.smart_naming] Save didn't complete properly, using default naming")
            return SsmsWindow.save_to_db_dir(temp_file, save_dir, server, db)
        
        # Generate consistent filename (no workflow detection needed)
        basename = os.path.basename(temp_file).replace('..sql', '.sql')
        if '_' in basename:
            unique_part = basename.split('_')[-1].replace('.sql', '')
        else:
            unique_part = basename.replace('.sql', '')
        
        # Use consistent naming pattern for all files
        custom_filename = f"{server}_{db}_{unique_part}.sql"
        print(f"[ssms_window.smart_naming] File saved successfully, target name: {custom_filename}")
        
        # Create the target path and save
        target_path = os.path.join(save_dir, server, db, 'temp', custom_filename)
        target_path = target_path.replace('/', '\\')
        
        FileManager.create_save_dir(os.path.dirname(target_path))
        SsmsWindow.automate_save_as(target_path)
        write_to_regex_file(server, db)
        # Apply tab coloring if enabled
        SsmsWindow.apply_tab_color(server, db)
        
        return target_path
    
    @staticmethod
    def save_to_db_dir(temp_file, save_dir, server, db):

        basename = os.path.basename(temp_file).replace('..sql', '.sql')
        target_path = os.path.join(save_dir, server, db, 'temp', server+'_'+db+'_'+basename)
        # Ensure Windows backslashes in target path
        target_path = target_path.replace('/', '\\')
        FileManager.create_save_dir(os.path.dirname(target_path))
        SsmsWindow.automate_save_as(target_path)
        write_to_regex_file(server, db)
        # Apply tab coloring if enabled
        SsmsWindow.apply_tab_color(server, db)
        return target_path

    @staticmethod
    def automate_save_as(target_path):
        """Automate the Save As dialog process"""
        
        # Save the current clipboard content
        original_clipboard = None
        try:
            original_clipboard = pyperclip.paste()
        except Exception:
            pass  # If clipboard is empty or inaccessible, continue
        
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
            # Restore clipboard before returning
            if original_clipboard is not None:
                try:
                    pyperclip.copy(original_clipboard)
                except Exception:
                    pass
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
            # Restore clipboard before returning
            if original_clipboard is not None:
                try:
                    pyperclip.copy(original_clipboard)
                except Exception:
                    pass
            return
                    
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        
        # Wait a moment for the save dialog to close, then restore clipboard
        time.sleep(0.5)
        if original_clipboard is not None:
            try:
                pyperclip.copy(original_clipboard)
            except Exception:
                pass