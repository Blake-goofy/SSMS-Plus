"""Regex/color config updater for SSMS."""
from pathlib import Path
from state import State
from settings import Settings

settings = Settings()
state = State(settings=settings)

@staticmethod
def write_server_db_to_regex_file(server, db):
    import time
    
    # Track this server/database combination in persistent settings
    settings.add_server_db(server, db)
    
    # Get the regex pattern based on current grouping mode from settings
    regex_pattern = settings.get_regex_pattern(server, db)
    
    if State.first_run:
        # Wait 2 seconds for SSMS to create config files, then process them once
        State.first_run = False
        print("Waiting 2 seconds for SSMS to create config files...")
        time.sleep(2)
    
    temp_dir = Path(state.temp_dir)
    config_files = list(temp_dir.rglob("ColorByRegexConfig.txt"))
    
    if not config_files:
        print("No ColorByRegexConfig.txt files found.")
        return
    
    print(f"Found {len(config_files)} ColorByRegexConfig.txt files")
    processed_files = 0
    
    for regex_file_path in config_files:
        try:
            # Read existing content
            with open(regex_file_path, 'r', encoding="utf-8") as f:
                existing_lines = f.readlines()
            
            # Check if this file already has the pattern
            pattern_exists = any(regex_pattern.strip() in line.strip() for line in existing_lines)
            
            if pattern_exists:
                print(f"Regex for server: {server}, db: {db} already exists in {regex_file_path}")
            else:
                # Filter out old server patterns first, then add the new one
                filtered_lines = []
                old_patterns_removed = 0
                
                for line in existing_lines:
                    line_stripped = line.strip()
                    # Check if this line looks like one of our server patterns
                    is_server_pattern = (
                        line_stripped.startswith('\\\\') and 
                        (line_stripped.endswith('(?=\\|$)') or line_stripped.endswith('(?=\\\\|$)'))
                    )
                    
                    if not is_server_pattern:
                        filtered_lines.append(line)
                    else:
                        old_patterns_removed += 1
                
                # Write back filtered content plus new pattern
                with open(regex_file_path, 'w', encoding="utf-8") as f:
                    f.writelines(filtered_lines)
                    f.write(f"{regex_pattern}\n")
                
                if old_patterns_removed > 0:
                    print(f"Updated {regex_file_path}: removed {old_patterns_removed} old patterns, added 1 new pattern (mode: {settings.get_grouping_mode()})")
                else:
                    print(f"Added regex for server: {server}, db: {db} to {regex_file_path} (mode: {settings.get_grouping_mode()})")
            
            processed_files += 1
            
        except Exception as e:
            print(f"Error processing {regex_file_path}: {e}")
    
    print(f"Processing complete: {processed_files} files processed")

@staticmethod
def regenerate_all_regex_patterns():
    """Regenerate all regex patterns based on current grouping mode and tracked combinations"""
    
    # Reload settings to get the latest values
    settings.load()
    
    # Get mode and check if we have any tracked combinations
    mode = settings.get_grouping_mode()
    if mode == 'server':
        tracked_combinations = settings.get_server_combinations()
        combination_type = "server"
    else:  # 'server_db'
        tracked_combinations = settings.get_server_db_combinations()
        combination_type = "server+database"
        
    if not tracked_combinations:
        print(f"No {combination_type} combinations tracked yet.")
        return
    
    print(f"Regenerating regex patterns for {len(tracked_combinations)} {combination_type} combinations in mode: {mode}")
    
    temp_dir = Path(state.temp_dir)
    config_files = list(temp_dir.rglob("ColorByRegexConfig.txt"))
    
    if not config_files:
        print("No ColorByRegexConfig.txt files found.")
        return

    print(f"Found {len(config_files)} ColorByRegexConfig.txt files")

    # Generate new patterns based on current mode
    pattern_list = []
    
    if mode == 'server':
        # In server mode, get unique server names and create one pattern per server
        server_combinations = settings.get_server_combinations()
        for server in server_combinations:
            pattern = f"\\\\{server}\\\\.*(?=\\\\|$)"
            if pattern not in pattern_list:
                pattern_list.append(pattern)
    else:  # 'server_db'
        # In server_db mode, get server.db combinations and create one pattern per combination
        server_db_combinations = settings.get_server_db_combinations()
        for combination in server_db_combinations:
            server, db = combination.split('.', 1)  # Split on first dot only
            pattern = f"\\\\{server}\\\\{db}(?=\\\\|$)"
            if pattern not in pattern_list:
                pattern_list.append(pattern)
    
    print(f"Generated {len(pattern_list)} unique patterns for current mode")
    
    # Update each regex file - start fresh and add only our patterns
    files_updated = 0
    for regex_file_path in config_files:
        try:
            # Start with a completely fresh file - write only our patterns
            with open(regex_file_path, 'w', encoding="utf-8") as f:
                for pattern in sorted(pattern_list):  # Sort for consistent ordering
                    f.write(f"{pattern}\n")
            
            print(f"Updated {regex_file_path}: wrote {len(pattern_list)} fresh patterns (mode: {mode})")
            files_updated += 1
                
        except Exception as e:
            print(f"Error processing {regex_file_path}: {e}")
    
    print(f"Regeneration complete: {files_updated} files updated with new grouping mode")