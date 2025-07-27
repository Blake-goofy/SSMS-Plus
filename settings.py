"""Settings loader/saver (INI interface)."""
import configparser
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "settings.ini")

class Settings:
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.load()

    def load(self):
        # Create config file if missing
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as f:
                f.write("[Folders]\n")
        self.config.read(self.config_path)

    def get_setting(self, section, option, fallback=None):
        """Get a setting value from the config file"""
        return self.config.get(section, option, fallback=fallback)

    def set_setting(self, section, option, value):
        """Set a setting value in the config file"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)

    def save(self):
        with open(self.config_path, "w") as f:
            self.config.write(f)

    def set_temp_dir(self, value):
        self.set_setting("Folders", "TempDir", value)
        self.save()

    def get_save_dir(self):
        return self.get_setting("Folders", "SaveDir", fallback="")

    def get_temp_dir(self):
        return self.get_setting("Folders", "TempDir", fallback="")

    def set_save_dir(self, value):
        self.set_setting("Folders", "SaveDir", value)
        self.save()

    # Server/Database tracking methods
    def add_server_db(self, server, db):
        """Add a server/database combination to persistent storage"""
        # Always add to server+db combinations
        server_db_combinations = self.get_server_db_combinations()
        combination = f"{server.upper()}.{db.upper()}"
        if combination not in server_db_combinations:
            server_db_combinations.append(combination)
            self.set_setting("ServerDB", "ServerDbCombinations", ",".join(server_db_combinations))
            
        # Also add to server-only combinations (just the server name)
        server_combinations = self.get_server_combinations()
        server_name = server.upper()
        if server_name not in server_combinations:
            server_combinations.append(server_name)
            self.set_setting("ServerDB", "ServerCombinations", ",".join(server_combinations))
            
        self.save()
    
    def get_server_db_combinations(self):
        """Get all tracked server+database combinations"""
        combinations_str = self.get_setting("ServerDB", "ServerDbCombinations", fallback="")
        if combinations_str:
            return combinations_str.split(",")
        return []
    
    def get_server_combinations(self):
        """Get all tracked server-only combinations"""
        combinations_str = self.get_setting("ServerDB", "ServerCombinations", fallback="")
        if combinations_str:
            return combinations_str.split(",")
        return []
    
    def get_tracked_combinations(self):
        """Get combinations based on current grouping mode"""
        mode = self.get_grouping_mode()
        if mode == 'server':
            return self.get_server_combinations()
        else:  # 'server_db'
            return self.get_server_db_combinations()
    
    def get_grouping_mode(self):
        """Get the current grouping mode"""
        return self.get_setting("ServerDB", "GroupingMode", fallback="server_db")
    
    def set_grouping_mode(self, mode):
        """Set the grouping mode ('server' or 'server_db')"""
        self.set_setting("ServerDB", "GroupingMode", mode)
        self.save()
    
    def get_regex_pattern(self, server, db):
        """Generate regex pattern based on current grouping mode - returns single pattern for current combination"""
        mode = self.get_grouping_mode()
        if mode == 'server':
            # Group by server only - ignore the database parameter
            return f"\\\\{server}\\\\.*(?=\\\\|$)"
        else:  # 'server_db'
            # Group by server and database
            return f"\\\\{server}\\\\{db}(?=\\\\|$)"
    
    def get_all_regex_patterns(self):
        """Generate all regex patterns for all tracked combinations"""
        mode = self.get_grouping_mode()
        patterns = []
        
        if mode == 'server':
            # Group by server only - get all tracked servers
            servers = self.get_server_combinations()
            for server in servers:
                patterns.append(f"\\\\{server}\\\\.*(?=\\\\|$)")
        else:  # 'server_db'
            # Group by server and database - get all tracked server.db combinations
            combinations = self.get_server_db_combinations()
            for combo in combinations:
                if '.' in combo:
                    combo_server, combo_db = combo.split('.', 1)
                    patterns.append(f"\\\\{combo_server}\\\\{combo_db}(?=\\\\|$)")
        
        return patterns