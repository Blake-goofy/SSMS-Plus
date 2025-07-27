"""Regex/color config updater for SSMS."""
import os
import json
import re
import configparser
from pathlib import Path

@staticmethod
def write_server_db_to_regex_file(server, db):
    import time
    
    # Retry logic for finding regex files
    max_retries = 5
    retry_delay = 0.5
    all_regex_files = []
    
    for attempt in range(max_retries):
        temp_dir = Path(os.getenv("TEMP"))
        config_files = list(temp_dir.rglob("ColorByRegexConfig.txt"))
        
        if config_files:
            print(f"Found {len(config_files)} ColorByRegexConfig.txt files (attempt {attempt + 1}/{max_retries})")
            all_regex_files = config_files
            break
        else:
            print(f"No ColorByRegexConfig.txt found (attempt {attempt + 1}/{max_retries})")
            
        if attempt < max_retries - 1:  # Don't wait after the last attempt
            print(f"Waiting {retry_delay} seconds before retry...")
            time.sleep(retry_delay)
    
    if not all_regex_files:
        print("Could not find any regex files after all retries.")
        return

    # Check if the server/db combination already exists in any file
    regex_pattern = f"\\\\{server}\\\\{db}(?=\\\\|$)"
    files_updated = 0
    files_already_had_entry = 0
    
    for regex_file_path in all_regex_files:
        try:
            # Check if this file already has the pattern
            with open(regex_file_path, 'r', encoding="utf-8") as f:
                existing_content = f.read()
                
            if regex_pattern in existing_content:
                print(f"Regex for server: {server}, db: {db} already exists in {regex_file_path}")
                files_already_had_entry += 1
            else:
                # Append the new regex to this file
                with open(regex_file_path, 'a', encoding="utf-8") as f:
                    f.write(f"{regex_pattern}\n")
                print(f"Added regex for server: {server}, db: {db} to {regex_file_path}")
                files_updated += 1
                
        except Exception as e:
            print(f"Error processing {regex_file_path}: {e}")
    
    print(f"Summary: {files_updated} files updated, {files_already_had_entry} files already had the entry")

@staticmethod
def apply_colors_from_ini():
    """
    Load color mappings from color_mappings.ini and apply them to the SSMS color JSON files.
    Maps regex entries to JSON group IDs by order (first regex -> first group, etc.)
    """
    import time
    
    # Find all SSMS temp directories with both regex and color files
    temp_dir = Path(os.getenv("TEMP"))
    config_files = list(temp_dir.rglob("ColorByRegexConfig.txt"))
    
    if not config_files:
        print("No ColorByRegexConfig.txt files found.")
        return
        
    ini_path = Path(__file__).parent / "config/color_mappings.ini"
    if not ini_path.exists():
        print(f"INI file not found: {ini_path}")
        return
        
    # Load color mappings from INI
    config = configparser.ConfigParser()
    config.read(ini_path)
    color_map = {}  # (server, db) -> color_index
    for section in config.sections():
        for db, color_index in config.items(section):
            color_map[(section.upper(), db.upper())] = int(color_index)
    
    print(f"Loaded {len(color_map)} color mappings from INI file")
    
    total_updated = 0
    for regex_file_path in config_files:
        try:
            # Find corresponding color JSON file in same directory
            parent_dir = regex_file_path.parent
            color_jsons = list(parent_dir.glob("customized-groupid-color-*.json"))
            
            if not color_jsons:
                print(f"No color JSON file found in {parent_dir}")
                continue
                
            # Use the most recent color JSON file
            color_json_path = max(color_jsons, key=lambda p: p.stat().st_mtime)
            
            # Parse regex file to get ordered list of (server, db)
            regex_line_re = re.compile(r"\\\\([^\\]+)\\\\([^\\(]+)(?=\\\\|\\$)")
            regex_entries = []
            
            with open(regex_file_path, 'r', encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('//') or not line:
                        continue  # Skip comments and empty lines
                    match = regex_line_re.search(line)
                    if match:
                        server, db = match.group(1).upper(), match.group(2).upper()
                        regex_entries.append((server, db))
            
            if not regex_entries:
                print(f"No server/database regex entries found in {regex_file_path}")
                continue
                
            # Load color JSON
            with open(color_json_path, 'r', encoding="utf-8") as f:
                color_json = json.load(f)
                
            color_map_json = color_json.get("ColorMap", {})
            group_ids = list(color_map_json.keys())
            
            # Map regex entries to group IDs by order
            updated = False
            for i, (server, db) in enumerate(regex_entries):
                if i >= len(group_ids):
                    print(f"Warning: More regex entries than JSON groups in {color_json_path}")
                    break
                    
                group_id = group_ids[i]
                color_index = color_map.get((server, db))
                
                if color_index is not None:
                    current_color = color_map_json[group_id]["ColorIndex"]
                    if current_color != color_index:
                        color_map_json[group_id]["ColorIndex"] = color_index
                        updated = True
                        print(f"  Updated {server}.{db}: color {current_color} -> {color_index}")
                    else:
                        print(f"  {server}.{db}: color already set to {color_index}")
                else:
                    print(f"  {server}.{db}: no color mapping found in INI")
            
            # Save JSON if updated
            if updated:
                with open(color_json_path, 'w', encoding="utf-8") as f:
                    json.dump(color_json, f, indent=2)
                print(f"Updated colors in {color_json_path}")
                total_updated += 1
            else:
                print(f"No color changes needed for {color_json_path}")
                
        except Exception as e:
            print(f"Error processing {regex_file_path}: {e}")
    
    print(f"Color update complete: {total_updated} JSON files updated")