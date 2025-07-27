import tkinter as tk
import threading
from tkinter import filedialog
from watcher import start_watching
from watcher import on_new_sql
from settings import Settings
from state import State
import os

settings = Settings()
state = State(settings=settings)

DARK_BG = "#222831"
DARK_FG = "#eeeeee"
ENTRY_BG = "#393e46"
BTN_BG = "#08638D"
BTN_FG = "#eeeeee"
BTN_HOVER = "#00959e"

class SettingsWindow:
    def __init__(self, current_temp, current_save, on_save):
        self.root = tk.Tk()
        self.root.title("SSMS Plus Settings")
        self.root.configure(bg=DARK_BG)
        self.root.resizable(False, False)
        self.on_save = on_save

        self.temp_dir_var = tk.StringVar(value=current_temp)
        self.save_dir_var = tk.StringVar(value=current_save)

        # Info/Error label at the top
        self.info_var = tk.StringVar(value="Save settings below")
        self.info_label = tk.Label(self.root, textvariable=self.info_var, bg=DARK_BG, fg="#FFD700", font=("Arial", 10, "bold"))
        self.info_label.grid(row=0, column=0, columnspan=3, sticky="we", padx=10, pady=(10, 0))

        def on_hover(e):
            e.widget.configure(bg=BTN_HOVER)

        def on_leave(e, src = "Default"):
            if(src == "Cancel"):
                e.widget.configure(bg=ENTRY_BG)
            else:
                e.widget.configure(bg=BTN_BG)

        # Temp Directory
        tk.Label(self.root, text="Temp Directory:", bg=DARK_BG, fg=DARK_FG).grid(row=1, column=0, sticky="w", padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.temp_dir_var, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=40).grid(row=1, column=1, padx=10, pady=10)
        btn_browse_temp = tk.Button(self.root, text="Browse", command=self.browse_temp, bg=BTN_BG, fg=BTN_FG, relief='flat')
        btn_browse_temp.grid(row=1, column=2, padx=5, pady=10)
        btn_browse_temp.bind("<Enter>", on_hover)
        btn_browse_temp.bind("<Leave>", on_leave)

        # Save Directory
        tk.Label(self.root, text="Save Directory:", bg=DARK_BG, fg=DARK_FG).grid(row=2, column=0, sticky="w", padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.save_dir_var, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=40).grid(row=2, column=1, padx=10, pady=10)
        btn_browse_save = tk.Button(self.root, text="Browse", command=self.browse_save, bg=BTN_BG, fg=BTN_FG, relief='flat')
        btn_browse_save.grid(row=2, column=2, padx=5, pady=10)
        btn_browse_save.bind("<Enter>", on_hover)
        btn_browse_save.bind("<Leave>", on_leave)


        # Buttons
        btn_frame = tk.Frame(self.root, bg=DARK_BG)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=15)
        btn_save = tk.Button(btn_frame, text="Save", command=self.save, bg=BTN_BG, fg=BTN_FG, relief='flat', width=10)
        btn_save.pack(side="left", padx=10)
        btn_save.bind("<Enter>", on_hover)
        btn_save.bind("<Leave>", on_leave)
        btn_cancel = tk.Button(btn_frame, text="Cancel", command=self.root.destroy, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=10)
        btn_cancel.pack(side="left", padx=10)
        btn_cancel.bind("<Enter>", on_hover)
        btn_cancel.bind("<Leave>", lambda e: on_leave(e, "Cancel"))

        # Focus and center
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_reqheight()) // 2
        self.root.geometry(f"+{x}+{y}")

    def browse_temp(self):
        directory = filedialog.askdirectory(initialdir=self.temp_dir_var.get() or ".")
        if directory:
            # Convert forward slashes to backslashes for Windows
            normalized_directory = directory.replace('/', '\\')
            self.temp_dir_var.set(normalized_directory)

    def browse_save(self):
        directory = filedialog.askdirectory(initialdir=self.save_dir_var.get() or ".")
        if directory:
            # Convert forward slashes to backslashes for Windows
            normalized_directory = directory.replace('/', '\\')
            self.save_dir_var.set(normalized_directory)

    def flash_info_label(self, final_fg):
        # Flash the info label to white, then to the final color
        def do_flash():
            self.info_label.config(fg="#FFFFFF")
            self.root.after(300, lambda: self.info_label.config(fg=final_fg))
        self.root.after(0, do_flash)

    def save(self):
        temp = self.temp_dir_var.get().strip()
        save = self.save_dir_var.get().strip()
        if not temp or not save or not os.path.isdir(temp) or not os.path.isdir(save):
            self.info_var.set("Both directories are required.")
            self.flash_info_label("#FF5555")  # Red for error
            return
        self.on_save(temp, save)
        self.info_var.set("Settings saved successfully.")
        self.flash_info_label("#00FF99")  # Green for success  

        def start_watcher_in_thread(temp_dir):
            watcher_thread = threading.Thread(target=start_watching, args=(temp_dir, on_new_sql), daemon=True)
            watcher_thread.start()
            return watcher_thread
        
        start_watcher_in_thread(temp)

    def show(self):
        self.root.mainloop()
