"""Filesystem watcher module."""

import os
import re
import time
import configparser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pygetwindow as gw
from ssms_window import SsmsWindow
from state import state

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

def create_watcher(temp_dir, on_new_sql):
    """Create and start a watcher observer that can be stopped later"""
    event_handler = SSMSTempSQLHandler(on_new_sql)
    observer = Observer()
    observer.schedule(event_handler, path=temp_dir, recursive=False)
    observer.start()
    print(f"[Watcher] Started watching {temp_dir} for SSMS temp .sql files.")
    return observer

def parse_server_db_from_title(title):
    # Looks for the first "SOME_SERVER.SOME_DB (" pattern
    m = re.search(r'([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+) \(', title)
    if m:
        return m.group(1), m.group(2)
    return None, None

def get_server_db(timeout=1.5, poll_interval=0.1):
    """Get server/db info specifically from SQLQuery windows"""
    end = time.time() + timeout
    while time.time() < end:
        # Get ALL SSMS windows, not just the active one
        all_windows = gw.getAllWindows()
        ssms_windows = [w for w in all_windows if w.title and "Microsoft SQL Server Management Studio" in w.title]
        
        # Look specifically for SQLQuery windows
        sqlquery_windows = [w for w in ssms_windows if "SQLQuery" in w.title and " - " in w.title]
        
        if sqlquery_windows:
            # Use the first SQLQuery window found
            title = sqlquery_windows[0].title.strip()
            print(f"[watcher.get_server_db] Using SQLQuery window title: {title}")
            server, db = parse_server_db_from_title(title)
            if server and db:
                print(f"[watcher.get_server_db] Extracted server='{server}', db='{db}'")
                return server, db
            else:
                print(f"[watcher.get_server_db] Could not parse server/db from: {title}")
        
        time.sleep(poll_interval)
    
    print("[watcher.get_server_db] Timeout - no SQLQuery windows found")
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

def get_active_ssms_title():
    w = gw.getActiveWindow()
    if w and 'SQL Server Management Studio' in w.title:
        return w.title
    return None

def on_new_sql(temp_file):
    print(f"[watcher.on_new_sql] New temp file detected: {temp_file}")
    server, db = get_server_db()
    if not server or not db:
        print(f"[watcher.on_new_sql] Could not detect server/db from SQLQuery windows, skipping: {temp_file}")
        return
    print(f"[watcher.on_new_sql] Processing file for {server}.{db}")
    save_dir = state.save_dir
    SsmsWindow.save_temp_file(temp_file, save_dir, server, db)