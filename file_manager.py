"""Handles file moving, renaming, and opening in SSMS."""

import os
import shutil
import configparser
import json
import re
from state import State
from pathlib import Path

class FileManager:
    def __init__(self):
        pass

    def delete_temp_dirs(self, *dirs):
        for dir_path in dirs:
            if os.path.exists(dir_path):
                try:
                    shutil.rmtree(dir_path)
                    print(f"Deleted: {dir_path}")
                except Exception as e:
                    print(f"Error deleting {dir_path}: {e}")
            else:
                print(f"Directory not found: {dir_path}")

    @staticmethod
    def get_ssms_temp():
        temp_dir = Path(os.getenv("TEMP"))
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

    @staticmethod
    def save_colors():
        """
        Loads color mappings from color_mappings.ini and applies them to the temp regex and color json files.
        """
        FileManager.get_ssms_temp()

        ini_path = Path(__file__).parent / "config/color_mappings.ini"
        regex_path = getattr(State, "regex_path", None)
        color_json_path = getattr(State, "color_path", None)

        if not ini_path.exists():
            print(f"INI file not found: {ini_path}")
            return
        if not regex_path or not Path(regex_path).exists():
            print(f"Regex file not found: {regex_path}")
            return
        if not color_json_path or not Path(color_json_path).exists():
            print(f"Color JSON file not found: {color_json_path}")
            return

        # 1. Parse INI for color mappings
        config = configparser.ConfigParser()
        config.read(ini_path)
        color_map = {}  # (server, db) -> color_index
        for section in config.sections():
            for db, color_index in config.items(section):
                color_map[(section.upper(), db.upper())] = int(color_index)

        # 2. Parse regex file to get list of (server, db)
        regex_line_re = re.compile(r"\\\\([^\\]+)\\\\([^\\(]+)\(\?\=\\\\\|\$\)")
        regex_entries = []
        with open(regex_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                match = regex_line_re.fullmatch(line)
                if match:
                    server, db = match.group(1).upper(), match.group(2).upper()
                    regex_entries.append((server, db))

        # 3. Load color JSON and get GroupIds in order
        with open(color_json_path, encoding="utf-8") as f:
            color_json = json.load(f)
        color_map_json = color_json.get("ColorMap", {})
        group_ids = list(color_map_json.keys())

        # 4. Associate regex_entries with group_ids by order
        updated = False
        for i, (server, db) in enumerate(regex_entries):
            if i >= len(group_ids):
                break
            group_id = group_ids[i]
            color_index = color_map.get((server, db))
            if color_index is not None:
                if color_map_json[group_id]["ColorIndex"] != color_index:
                    color_map_json[group_id]["ColorIndex"] = color_index
                    updated = True

        # 5. Save JSON if updated
        if updated:
            with open(color_json_path, "w", encoding="utf-8") as f:
                json.dump(color_json, f, indent=2)
            print(f"Updated color indices in {color_json_path}")
        else:
            print("No color indices updated.")