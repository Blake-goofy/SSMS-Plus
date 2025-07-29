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

    # Appearance settings
    def get_tray_icon(self):
        """Get the tray icon color (yellow or red)"""
        return self.get_setting("Appearance", "TrayIcon", fallback="yellow")
    
    def set_tray_icon(self, icon_color):
        """Set the tray icon color (yellow or red)"""
        self.set_setting("Appearance", "TrayIcon", icon_color)
        self.save()
    
    def get_tray_name(self):
        """Get the tray app name"""
        return self.get_setting("Appearance", "TrayName", fallback="SSMS Plus")
    
    def set_tray_name(self, name):
        """Set the tray app name"""
        self.set_setting("Appearance", "TrayName", name)
        self.save()

    # Tab coloring settings
    def get_tab_coloring_enabled(self):
        """Get whether tab coloring is enabled"""
        return self.get_setting("TabColoring", "Enabled", fallback="true").lower() == "true"
    
    def set_tab_coloring_enabled(self, enabled):
        """Set whether tab coloring is enabled"""
        self.set_setting("TabColoring", "Enabled", "true" if enabled else "false")
        self.save()
    
    def get_tab_color_for_combination(self, server, db=None):
        """Get the tab color index for a server/db combination
        
        Args:
            server (str): Server name
            db (str, optional): Database name. If None, uses server-only mode
            
        Returns:
            int: Color index (0-16), defaults to 0 (random)
        """
        mode = self.get_grouping_mode()
        
        if mode == 'server':
            # Server-only mode - ignore database
            key = server
        else:
            # Server+DB mode
            key = f"{server}.{db}" if db else server
        
        color_str = self.get_setting("TabColoring", key, fallback="0")
        try:
            color_index = int(color_str)
            # Validate range (0-16)
            if 0 <= color_index <= 16:
                return color_index
            else:
                return 0  # Default to random if invalid
        except ValueError:
            return 0  # Default to random if not a valid integer
    
    def set_tab_color_for_combination(self, server, db=None, color_index=0):
        """Set the tab color index for a server/db combination
        
        Args:
            server (str): Server name
            db (str, optional): Database name. If None, uses server-only mode
            color_index (int): Color index (0-16)
        """
        mode = self.get_grouping_mode()
        
        if mode == 'server':
            # Server-only mode - ignore database
            key = server
        else:
            # Server+DB mode
            key = f"{server}.{db}" if db else server
        
        # Validate color index
        if not (0 <= color_index <= 16):
            color_index = 0
        
        self.set_setting("TabColoring", key, str(color_index))
        self.save()

    # Server/DB settings
    def get_server_db_combinations(self):
        """Get the list of server.database combinations"""
        combinations_str = self.get_setting("ServerDB", "ServerDBCombinations", fallback="")
        return [combo.strip() for combo in combinations_str.split(",") if combo.strip()]

    def set_server_db_combinations(self, combinations):
        """Set the list of server.database combinations"""
        combinations_str = ",".join(combinations)
        self.set_setting("ServerDB", "ServerDBCombinations", combinations_str)
        self.save()

    def get_server_combinations(self):
        """Get the list of server combinations"""
        combinations_str = self.get_setting("ServerDB", "ServerCombinations", fallback="")
        return [combo.strip() for combo in combinations_str.split(",") if combo.strip()]

    def set_server_combinations(self, combinations):
        """Set the list of server combinations"""
        combinations_str = ",".join(combinations)
        self.set_setting("ServerDB", "ServerCombinations", combinations_str)
        self.save()

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
