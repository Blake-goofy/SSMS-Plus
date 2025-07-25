"""Settings loader/saver (INI interface)."""
import configparser
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "settings.ini")

class Settings:
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.load()

    def load(self):
        # Create config file if missing
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as f:
                f.write(r"[Folders]\nTempDir = C:\Temp\nSaveDir = C:\Save\n")
        self.config.read(self.config_path)

    def get(self, section, option, fallback=None):
        return self.config.get(section, option, fallback=fallback)

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)

    def save(self):
        with open(self.config_path, "w") as f:
            self.config.write(f)
            
    def get_temp_dir(self):
        return self.get("Folders", "TempDir", fallback=r"C:\Temp")

    def set_temp_dir(self, value):
        self.set("Folders", "TempDir", value)
        self.save()

    def get_save_dir(self):
        return self.get("Folders", "SaveDir", fallback=r"C:\Save")