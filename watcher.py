"""Filesystem watcher module."""

import os
import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
