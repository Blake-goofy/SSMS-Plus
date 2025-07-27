import tkinter as tk
import threading
from tkinter import filedialog
from pathlib import Path
import webbrowser
from regex_writer import regenerate_all_regex_patterns
from state import settings
import os

DARK_BG = "#222831"
DARK_FG = "#eeeeee"
ENTRY_BG = "#393e46"
BTN_BG = "#08638D"
BTN_FG = "#eeeeee"
BTN_HOVER = "#00959e"

class SettingsWindow:
    def __init__(self, current_temp, current_save, on_save, initial_error=None):
        self.root = tk.Tk()
        self.root.title("SSMS Plus Settings")
        self.root.configure(bg=DARK_BG)
        self.root.resizable(False, False)
        self.on_save = on_save
        self.dirs_required = initial_error is not None  # Track if directories are required for app to run

        self.temp_dir_var = tk.StringVar(value=current_temp or "")
        self.save_dir_var = tk.StringVar(value=current_save or "")
        self.grouping_mode_var = tk.StringVar(value=settings.get_grouping_mode())

        # Info/Error label at the top
        if initial_error:
            self.info_var = tk.StringVar(value=initial_error)
            self.info_label = tk.Label(self.root, textvariable=self.info_var, bg=DARK_BG, fg="#FF5555", font=("Arial", 10, "bold"))
        else:
            self.info_var = tk.StringVar(value="Save settings below")
            self.info_label = tk.Label(self.root, textvariable=self.info_var, bg=DARK_BG, fg="#FFD700", font=("Arial", 10, "bold"))
        self.info_label.grid(row=0, column=0, columnspan=2, sticky="we", padx=10, pady=(10, 0))
        
        def on_hover(e):
            e.widget.configure(bg=BTN_HOVER)

        def on_leave(e, src = "Default"):
            if(src == "Close"):
                e.widget.configure(bg=ENTRY_BG)
            else:
                e.widget.configure(bg=BTN_BG)

        # Help button in top right corner
        btn_help = tk.Button(self.root, text="Help", command=self.open_help, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=8)
        btn_help.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="e")
        btn_help.bind("<Enter>", on_hover)
        btn_help.bind("<Leave>", lambda e: on_leave(e, "Close"))

        # Temp Directory
        tk.Label(self.root, text="Temp Directory:", bg=DARK_BG, fg=DARK_FG).grid(row=1, column=0, sticky="w", padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.temp_dir_var, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=40).grid(row=1, column=1, padx=10, pady=10)
        
        btn_auto_temp = tk.Button(self.root, text="Auto", command=self.auto_temp, bg=BTN_BG, fg=BTN_FG, relief='flat', width=8)
        btn_auto_temp.grid(row=1, column=2, padx=5, pady=10)
        btn_auto_temp.bind("<Enter>", on_hover)
        btn_auto_temp.bind("<Leave>", on_leave)

        # Save Directory
        tk.Label(self.root, text="Save Directory:", bg=DARK_BG, fg=DARK_FG).grid(row=2, column=0, sticky="w", padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.save_dir_var, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=40).grid(row=2, column=1, padx=10, pady=10)
        btn_browse_save = tk.Button(self.root, text="Browse", command=self.browse_save, bg=BTN_BG, fg=BTN_FG, relief='flat', width=8)
        btn_browse_save.grid(row=2, column=2, padx=5, pady=10)
        btn_browse_save.bind("<Enter>", on_hover)
        btn_browse_save.bind("<Leave>", on_leave)

        # Grouping Mode
        tk.Label(self.root, text="Tab Grouping:", bg=DARK_BG, fg=DARK_FG).grid(row=3, column=0, sticky="w", padx=10, pady=10)
        
        grouping_frame = tk.Frame(self.root, bg=DARK_BG)
        grouping_frame.grid(row=3, column=1, columnspan=2, sticky="w", padx=10, pady=10)
        
        tk.Radiobutton(grouping_frame, text="Server only", 
                      variable=self.grouping_mode_var, value="server",
                      bg=DARK_BG, fg=DARK_FG, selectcolor=ENTRY_BG,
                      activebackground=DARK_BG, activeforeground=DARK_FG).pack(anchor="w")
        
        tk.Radiobutton(grouping_frame, text="Server + db", 
                      variable=self.grouping_mode_var, value="server_db",
                      bg=DARK_BG, fg=DARK_FG, selectcolor=ENTRY_BG,
                      activebackground=DARK_BG, activeforeground=DARK_FG).pack(anchor="w")


        # Buttons
        btn_frame = tk.Frame(self.root, bg=DARK_BG)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=15)
        
        btn_save = tk.Button(btn_frame, text="Save", command=self.save, bg=BTN_BG, fg=BTN_FG, relief='flat', width=10)
        btn_save.pack(side="left", padx=10)
        btn_save.bind("<Enter>", on_hover)
        btn_save.bind("<Leave>", on_leave)
        
        btn_cancel = tk.Button(btn_frame, text="Close", command=self.cancel, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=10)
        btn_cancel.pack(side="left", padx=10)
        btn_cancel.bind("<Enter>", on_hover)
        btn_cancel.bind("<Leave>", lambda e: on_leave(e, "Close"))

        # Focus and center
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_reqheight()) // 2
        self.root.geometry(f"+{x}+{y}")

    def auto_temp(self):
        """Auto-fill temp directory with current user's temp folder"""
        temp_dir = str(Path(os.getenv("TEMP")))
        self.temp_dir_var.set(temp_dir)

    def open_help(self):
        """Open the GitHub README in the default browser"""
        webbrowser.open("https://github.com/Blake-goofy/ssmsplus#readme")

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

    def cancel(self):
        # If directories are required for the app to function, check them before allowing cancel
        if self.dirs_required:
            temp = self.temp_dir_var.get().strip()
            save = self.save_dir_var.get().strip()
            
            if not temp or not save or not os.path.isdir(temp) or not os.path.isdir(save):
                self.info_var.set("Both directories must exist to continue.")
                self.flash_info_label("#FF5555")  # Red for error
                return
        
        self.root.destroy()

    def save(self):
        temp = self.temp_dir_var.get().strip()
        save = self.save_dir_var.get().strip()
        grouping_mode = self.grouping_mode_var.get()
        
        if not temp or not save or not os.path.isdir(temp) or not os.path.isdir(save):
            self.info_var.set("Both directories must exist.")
            self.flash_info_label("#FF5555")  # Red for error
            return
            
        # Check if grouping mode changed
        old_mode = settings.get_grouping_mode()
        mode_changed = old_mode != grouping_mode
        
        # Save the grouping mode to settings
        settings.set_grouping_mode(grouping_mode)
        
        # If mode changed, regenerate regex patterns
        if mode_changed:
            regenerate_all_regex_patterns()
        
        self.on_save(temp, save)
        self.info_var.set("Settings saved successfully.")
        self.flash_info_label("#00FF99")  # Green for success

    def show(self):
        self.root.mainloop()
