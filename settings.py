"""Settings loader/saver (INI interface)."""
import configparser
import os
import sys

if getattr(sys, 'frozen', False):
    # Running as exe
    CONFIG_PATH = os.path.join(os.path.dirname(sys.executable), "settings.ini")
else:
    # Running as script
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
    def get_tab_coloring_server_enabled(self):
        """Get whether server-based tab coloring is enabled"""
        return self.get_setting("TabColoringServer", "enabled", fallback="false").lower() == "true"
    
    def set_tab_coloring_server_enabled(self, enabled):
        """Set whether server-based tab coloring is enabled"""
        self.set_setting("TabColoringServer", "enabled", "true" if enabled else "false")
        self.save()
    
    def get_tab_coloring_db_enabled(self):
        """Get whether database-based tab coloring is enabled"""
        return self.get_setting("TabColoringDB", "enabled", fallback="false").lower() == "true"
    
    def set_tab_coloring_db_enabled(self, enabled):
        """Set whether database-based tab coloring is enabled"""
        self.set_setting("TabColoringDB", "enabled", "true" if enabled else "false")
        self.save()
    
    def get_tab_color_for_combination(self, server, db=None):
        """Get the tab color index for a server/db combination
        
        Priority: Database-specific > Server-specific > Default (0)
        
        Args:
            server (str): Server name
            db (str, optional): Database name
            
        Returns:
            int: Color index (0-16), defaults to 0 (random)
        """
        server_lower = server.lower()
        
        # First, check database-specific coloring if enabled and db is provided
        if db and self.get_tab_coloring_db_enabled():
            db_key = f"{server_lower}.{db.lower()}"
            color_str = self.get_setting("TabColoringDB", db_key, fallback=None)
            if color_str is not None:
                try:
                    color_index = int(color_str)
                    if 0 <= color_index <= 16:
                        return color_index
                except ValueError:
                    pass
        
        # Second, check server-specific coloring if enabled
        if self.get_tab_coloring_server_enabled():
            color_str = self.get_setting("TabColoringServer", server_lower, fallback=None)
            if color_str is not None:
                try:
                    color_index = int(color_str)
                    if 0 <= color_index <= 16:
                        return color_index
                except ValueError:
                    pass
        
        # Default to 0 (random) if no specific color found
        return 0
    
    def set_tab_color_for_server(self, server, color_index=0):
        """Set the tab color index for a server
        
        Args:
            server (str): Server name
            color_index (int): Color index (0-16)
        """
        # Validate color index
        if not (0 <= color_index <= 16):
            color_index = 0
        
        server_key = server.lower()
        self.set_setting("TabColoringServer", server_key, str(color_index))
        self.save()
    
    def set_tab_color_for_database(self, server, db, color_index=0):
        """Set the tab color index for a server+database combination
        
        Args:
            server (str): Server name
            db (str): Database name
            color_index (int): Color index (0-16)
        """
        # Validate color index
        if not (0 <= color_index <= 16):
            color_index = 0
        
        db_key = f"{server.lower()}.{db.lower()}"
        self.set_setting("TabColoringDB", db_key, str(color_index))
        self.save()
    
    def set_tab_color_for_combination(self, server, db=None, color_index=0):
        """Legacy method - set color based on current grouping mode for backward compatibility"""
        mode = self.get_grouping_mode()
        
        if mode == 'server' or db is None:
            self.set_tab_color_for_server(server, color_index)
        else:
            self.set_tab_color_for_database(server, db, color_index)
    
    def get_tab_coloring_enabled(self):
        """Legacy method - returns True if either server or database coloring is enabled"""
        return self.get_tab_coloring_server_enabled() or self.get_tab_coloring_db_enabled()
    
    def set_tab_coloring_enabled(self, enabled):
        """Legacy method - enables/disables both server and database coloring"""
        self.set_tab_coloring_server_enabled(enabled)
        self.set_tab_coloring_db_enabled(enabled)

    def get_configured_db_combinations(self):
        """Get the list of server.database combinations that have colors configured"""
        if not self.config.has_section("TabColoringDB"):
            return []
        
        combinations = []
        for key in self.config["TabColoringDB"]:
            if key != "enabled" and "." in key:
                # Convert back to display format (uppercase)
                parts = key.split(".", 1)
                if len(parts) == 2:
                    server, db = parts
                    combinations.append(f"{server.upper()}.{db.upper()}")
        
        return sorted(combinations)

    def get_configured_server_combinations(self):
        """Get the list of servers that have colors configured"""
        if not self.config.has_section("TabColoringServer"):
            return []
        
        servers = []
        for key in self.config["TabColoringServer"]:
            if key != "enabled":
                # Convert back to display format (uppercase)
                servers.append(key.upper())
        
        return sorted(servers)

    def add_server_db(self, server, db):
        """Add a server/database combination to TabColoring sections with default colors"""
        # Add to database coloring section if enabled
        if self.get_tab_coloring_db_enabled():
            db_key = f"{server.lower()}.{db.lower()}"
            if not self.config.has_section("TabColoringDB"):
                self.config.add_section("TabColoringDB")
            
            # Only add if not already present
            if not self.config.has_option("TabColoringDB", db_key):
                self.set_setting("TabColoringDB", db_key, "0")  # Default color
                print(f"[settings] Added new database combination: {server}.{db} with default color")
        
        # Add to server coloring section if enabled  
        if self.get_tab_coloring_server_enabled():
            server_key = server.lower()
            if not self.config.has_section("TabColoringServer"):
                self.config.add_section("TabColoringServer")
            
            # Only add if not already present
            if not self.config.has_option("TabColoringServer", server_key):
                self.set_setting("TabColoringServer", server_key, "0")  # Default color
                print(f"[settings] Added new server: {server} with default color")
        
        self.save()

    def get_tracked_combinations(self):
        """Get combinations based on current grouping mode from TabColoring sections"""
        mode = self.get_grouping_mode()
        if mode == 'server':
            return self.get_configured_server_combinations()
        else:  # 'server_db'
            return self.get_configured_db_combinations()
    
    def get_grouping_mode(self):
        """Get the current grouping mode"""
        return self.get_setting("Appearance", "GroupingMode", fallback="server_db")
    
    def set_grouping_mode(self, mode):
        """Set the grouping mode ('server' or 'server_db')"""
        self.set_setting("Appearance", "GroupingMode", mode)
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
            # Group by server only - get all configured servers from TabColoring
            servers = self.get_configured_server_combinations()
            for server in servers:
                patterns.append(f"\\\\{server}\\\\.*(?=\\\\|$)")
        else:  # 'server_db'
            # Group by server and database - get all configured server.db combinations from TabColoring
            combinations = self.get_configured_db_combinations()
            for combo in combinations:
                if '.' in combo:
                    combo_server, combo_db = combo.split('.', 1)
                    patterns.append(f"\\\\{combo_server}\\\\{combo_db}(?=\\\\|$)")
        
        return patterns
