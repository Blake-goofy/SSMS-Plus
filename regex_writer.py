"""Regex/color config updater for SSMS."""
from pathlib import Path
from state import state, settings

@staticmethod
def write_server_db_to_regex_file(server, db):
    import time
    
    # Track this server/database combination in persistent settings
    settings.add_server_db(server, db)
    
    # Get ALL regex patterns for all tracked combinations
    all_patterns = settings.get_all_regex_patterns()
    
    if not all_patterns:
        return
    
    if state.first_run:
        # Wait 2 seconds for SSMS to create config files, then process them once
        state.first_run = False
        time.sleep(2)
    
    temp_dir = Path(state.temp_dir)
    config_files = list(temp_dir.rglob("ColorByRegexConfig.txt"))
    
    if not config_files:
        return
    
    # {len(config_files)} ColorByRegexConfig.txt files")
    processed_files = 0
    
    for regex_file_path in config_files:
        try:
            # Read existing content
            with open(regex_file_path, 'r', encoding="utf-8") as f:
                existing_lines = f.readlines()
            
            # Filter out ALL old server patterns first
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
            
            # Write back filtered content plus ALL new patterns
            with open(regex_file_path, 'w', encoding="utf-8") as f:
                f.writelines(filtered_lines)
                for pattern in all_patterns:
                    f.write(f"{pattern}\n")
            
            processed_files += 1
            
        except Exception as e:
            pass

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
        return
    
    temp_dir = Path(state.temp_dir)
    config_files = list(temp_dir.rglob("ColorByRegexConfig.txt"))
    
    if not config_files:
        return

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
    
    # Update each regex file - start fresh and add only our patterns
    files_updated = 0
    for regex_file_path in config_files:
        try:
            # Start with a completely fresh file - write only our patterns
            with open(regex_file_path, 'w', encoding="utf-8") as f:
                for pattern in sorted(pattern_list):  # Sort for consistent ordering
                    f.write(f"{pattern}\n")
            
            files_updated += 1
                
        except Exception as e:
            pass