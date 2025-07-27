"""Handles file moving, renaming, and opening in SSMS."""

import os
import configparser
import json
import re
from state import State
from pathlib import Path

class FileManager:
    def __init__(self):
        pass

    @staticmethod
    def create_save_dir(path):
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created save directory: {path}")
        else:
            print(f"Save directory already exists: {path}")

    @staticmethod
    def delete_temp_files():
        """Delete all but the latest 3 files from each temp folder in the save directory structure"""
        if not hasattr(State, 'save_dir') or not State.save_dir:
            print("No save directory configured.")
            return
            
        save_dir = Path(State.save_dir)
        if not save_dir.exists():
            print(f"Save directory does not exist: {save_dir}")
            return
            
        try:
            # Find all 'temp' folders in the save directory structure
            temp_folders = list(save_dir.rglob("temp"))
            
            if not temp_folders:
                print("No temp folders found in save directory structure.")
                return
                
            print(f"Found {len(temp_folders)} temp folders to clean up...")
            
            total_deleted = 0
            for temp_folder in temp_folders:
                if not temp_folder.is_dir():
                    continue
                    
                try:
                    # Get all files in this temp folder
                    all_files = [f for f in temp_folder.iterdir() if f.is_file()]
                    
                    if len(all_files) <= 3:
                        print(f"{temp_folder}: Only {len(all_files)} files, keeping all.")
                        continue
                        
                    # Sort by modification time (newest first)
                    all_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                    
                    # Keep the latest 3, delete the rest
                    files_to_delete = all_files[3:]
                    
                    print(f"{temp_folder}: Keeping latest 3 files, deleting {len(files_to_delete)} old files...")
                    
                    for file_path in files_to_delete:
                        try:
                            file_path.unlink()
                            print(f"  Deleted: {file_path.name}")
                            total_deleted += 1
                        except Exception as e:
                            print(f"  Error deleting {file_path}: {e}")
                            
                except Exception as e:
                    print(f"Error processing temp folder {temp_folder}: {e}")
                    
            print(f"Cleanup complete: {total_deleted} total files deleted from temp folders.")
                    
        except Exception as e:
            print(f"Error processing save directory {save_dir}: {e}")

    @staticmethod
    def get_ssms_temp():
        temp_dir = State.temp_dir
        config_files = list(temp_dir.rglob("ColorByRegexConfig.txt"))

        if not config_files:
            print("No ColorByRegexConfig.txt found.")
            return

        # Find the parent folder with the most recent modification or creation time
        def folder_time(path):
            folder = path.parent
            stat = folder.stat()
            return max(stat.st_mtime, stat.st_ctime)

        latest_config = max(config_files, key=folder_time)
        latest_folder = latest_config.parent

        State.regex_path = str(latest_config)
        print(f"Found config path: {State.regex_path}")

        # Find the color json file in the same folder
        color_jsons = list(latest_folder.glob("customized-groupid-color-*.json"))
        if color_jsons:
            # Pick the most recent one if multiple
            latest_json = max(color_jsons, key=lambda p: max(p.stat().st_mtime, p.stat().st_ctime))
            State.color_path = str(latest_json)
            print(f"Found color path: {State.color_path}")
        else:
            print("No customized-groupid-color-*.json found in latest folder.")