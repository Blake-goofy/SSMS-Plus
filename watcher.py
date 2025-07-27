"""Filesystem watcher module."""

import os
import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pygetwindow as gw
import os
import configparser
import re
import time
from ssms_window import SsmsWindow
from settings import Settings
from state import State

settings = Settings()
state = State(settings=settings)

# Pattern: 8 chars + "..sql" (e.g., qhrai0ji..sql)
SSMS_TEMP_PATTERN = re.compile(r"^[a-z0-9]{8}\.\.sql$", re.IGNORECASE)

class SSMSTempSQLHandler(FileSystemEventHandler):
    def __init__(self, on_new_sql):
        super().__init__()
        self.on_new_sql = on_new_sql

    def on_created(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            if SSMS_TEMP_PATTERN.match(filename):
                print(f"[Watcher] New SSMS temp SQL file: {event.src_path}")
                self.on_new_sql(event.src_path)

def start_watching(temp_dir, on_new_sql):
    event_handler = SSMSTempSQLHandler(on_new_sql)
    observer = Observer()
    observer.schedule(event_handler, path=temp_dir, recursive=False)
    observer.start()
    print(f"[Watcher] Watching {temp_dir} for SSMS temp .sql files.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def parse_server_db_from_title(title):
    # Looks for the first "SOME_SERVER.SOME_DB (" pattern
    m = re.search(r'([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+) \(', title)
    if m:
        return m.group(1), m.group(2)
    return None, None

def get_server_db(timeout=1.5, poll_interval=0.1):
    end = time.time() + timeout
    while time.time() < end:
        title = get_active_ssms_title()
        if title:
            server, db = parse_server_db_from_title(title)
            if server and db:
                return server, db
        time.sleep(poll_interval)
    return None, None

def update_color_mappings_ini(config_path, server, db):
    config = configparser.ConfigParser()
    config.read(config_path)
    if not config.has_section(server):
        config.add_section(server)
    if not config.has_option(server, db):
        config.set(server, db, "-1")
        with open(config_path, "w") as f:
            config.write(f)
        print(f"Added {server}/{db} to color_mappings.ini with -1")

def get_active_ssms_title():
    w = gw.getActiveWindow()
    if w and 'SQL Server Management Studio' in w.title:
        return w.title
    return None

def on_new_sql(temp_file):
    server, db = get_server_db()
    if not server or not db:
        print("Could not detect server/db in SSMS window title after waiting. Skipping file:", temp_file)
        return
    save_dir = state.save_dir
    SsmsWindow.save_temp_file_to_db_dir(temp_file, save_dir, server, db)