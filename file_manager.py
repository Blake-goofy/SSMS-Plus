"""Handles file moving, renaming, and opening in SSMS."""

import os
import time
from pathlib import Path
from state import state

class FileManager:
    def __init__(self):
        pass

    @staticmethod
    def create_save_dir(path):
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def mark_session_start():
        """Create a session marker file to track when this session started"""
        try:
            temp_dir = Path(state.temp_dir)
            session_marker = temp_dir / ".ssmsplus_session"
            
            # Create session marker with current timestamp
            with open(session_marker, 'w') as f:
                f.write(str(time.time()))
            
            state.session_start_time = time.time()
            print(f"[FileManager] Session started at {time.ctime(state.session_start_time)}")
            
        except Exception as e:
            print(f"[FileManager] Error creating session marker: {e}")
            state.session_start_time = time.time()  # Fallback to current time

    @staticmethod
    def cleanup_old_temp_files():
        """Delete temp files from previous sessions at startup"""
        if not hasattr(state, 'session_start_time'):
            print("[FileManager] No session start time available, skipping cleanup")
            return
            
        save_dir = Path(state.save_dir)
        if not save_dir.exists():
            print(f"[FileManager] Save directory does not exist: {save_dir}")
            return
            
        try:
            # Find all 'temp' folders in the save directory structure
            temp_folders = list(save_dir.rglob("temp"))
            
            if not temp_folders:
                print("[FileManager] No temp folders found in save directory structure.")
                return
                
            print(f"[FileManager] Found {len(temp_folders)} temp folders to check for old files...")
            
            total_deleted = 0
            for temp_folder in temp_folders:
                if not temp_folder.is_dir():
                    continue
                    
                try:
                    # Get all files in this temp folder
                    all_files = [f for f in temp_folder.iterdir() if f.is_file()]
                    
                    if not all_files:
                        continue
                        
                    # Find files older than this session
                    old_files = []
                    for file_path in all_files:
                        file_mtime = file_path.stat().st_mtime
                        if file_mtime < state.session_start_time:
                            old_files.append(file_path)
                    
                    if not old_files:
                        print(f"[FileManager] {temp_folder}: No old files to delete")
                        continue
                        
                    print(f"[FileManager] {temp_folder}: Deleting {len(old_files)} old files from previous sessions...")
                    
                    for file_path in old_files:
                        try:
                            file_path.unlink()
                            print(f"[FileManager]   Deleted: {file_path.name}")
                            total_deleted += 1
                        except Exception as e:
                            print(f"[FileManager]   Error deleting {file_path}: {e}")
                            
                except Exception as e:
                    print(f"[FileManager] Error processing temp folder {temp_folder}: {e}")
                    
            print(f"[FileManager] Cleanup complete: {total_deleted} old temp files deleted.")
                    
        except Exception as e:
            print(f"[FileManager] Error during temp file cleanup: {e}")

    @staticmethod
    def get_ssms_temp():
        temp_dir = state.temp_dir
        config_files = list(temp_dir.rglob("ColorByRegexConfig.txt"))

        if not config_files:
            return

        # Find the parent folder with the most recent modification or creation time
        def folder_time(path):
            folder = path.parent
            stat = folder.stat()
            return max(stat.st_mtime, stat.st_ctime)

        latest_config = max(config_files, key=folder_time)
        latest_folder = latest_config.parent

        state.regex_path = str(latest_config)

        # Find the color json file in the same folder
        color_jsons = list(latest_folder.glob("customized-groupid-color-*.json"))
        if color_jsons:
            # Pick the most recent one if multiple
            latest_json = max(color_jsons, key=lambda p: max(p.stat().st_mtime, p.stat().st_ctime))
            state.color_path = str(latest_json)