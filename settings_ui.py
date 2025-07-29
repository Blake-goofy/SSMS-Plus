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
        
        # Set custom icon for the window
        self.set_window_icon()

        self.temp_dir_var = tk.StringVar(value=current_temp or "")
        self.save_dir_var = tk.StringVar(value=current_save or "")
        self.grouping_mode_var = tk.StringVar(value=settings.get_grouping_mode())
        self.tray_icon_var = tk.StringVar(value=settings.get_tray_icon())
        self.tray_name_var = tk.StringVar(value=settings.get_tray_name())

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
        btn_help = tk.Button(self.root, text="Help", command=self.open_help, bg=ENTRY_BG, fg=DARK_FG, 
                            relief='flat', width=8, bd=0, highlightthickness=0)
        btn_help.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="e")
        btn_help.bind("<Enter>", on_hover)
        btn_help.bind("<Leave>", lambda e: on_leave(e, "Close"))

        # Temp Directory
        tk.Label(self.root, text="Temp Directory:", bg=DARK_BG, fg=DARK_FG).grid(row=1, column=0, sticky="w", padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.temp_dir_var, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=40, 
                bd=0, highlightthickness=0).grid(row=1, column=1, padx=10, pady=10)
        
        btn_auto_temp = tk.Button(self.root, text="Auto", command=self.auto_temp, bg=BTN_BG, fg=BTN_FG, 
                                 relief='flat', width=8, bd=0, highlightthickness=0)
        btn_auto_temp.grid(row=1, column=2, padx=5, pady=10)
        btn_auto_temp.bind("<Enter>", on_hover)
        btn_auto_temp.bind("<Leave>", on_leave)

        # Save Directory
        tk.Label(self.root, text="Save Directory:", bg=DARK_BG, fg=DARK_FG).grid(row=2, column=0, sticky="w", padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.save_dir_var, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=40,
                bd=0, highlightthickness=0).grid(row=2, column=1, padx=10, pady=10)
        btn_browse_save = tk.Button(self.root, text="Browse", command=self.browse_save, bg=BTN_BG, fg=BTN_FG, 
                                   relief='flat', width=8, bd=0, highlightthickness=0)
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
                      activebackground=DARK_BG, activeforeground=DARK_FG).pack(side="left", padx=(0, 20))
        
        tk.Radiobutton(grouping_frame, text="Server + db", 
                      variable=self.grouping_mode_var, value="server_db",
                      bg=DARK_BG, fg=DARK_FG, selectcolor=ENTRY_BG,
                      activebackground=DARK_BG, activeforeground=DARK_FG).pack(side="left")

        # Tray Icon Color
        tk.Label(self.root, text="Tray Icon:", bg=DARK_BG, fg=DARK_FG).grid(row=4, column=0, sticky="w", padx=10, pady=10)
        
        icon_frame = tk.Frame(self.root, bg=DARK_BG)
        icon_frame.grid(row=4, column=1, columnspan=2, sticky="w", padx=10, pady=10)
        
        tk.Radiobutton(icon_frame, text="Yellow", 
                      variable=self.tray_icon_var, value="yellow",
                      bg=DARK_BG, fg=DARK_FG, selectcolor=ENTRY_BG,
                      activebackground=DARK_BG, activeforeground=DARK_FG).pack(side="left", padx=(0, 20))
        
        tk.Radiobutton(icon_frame, text="Red", 
                      variable=self.tray_icon_var, value="red",
                      bg=DARK_BG, fg=DARK_FG, selectcolor=ENTRY_BG,
                      activebackground=DARK_BG, activeforeground=DARK_FG).pack(side="left")

        # Tray App Name
        tk.Label(self.root, text="Tray App Name:", bg=DARK_BG, fg=DARK_FG).grid(row=5, column=0, sticky="w", padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.tray_name_var, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=40,
                bd=0, highlightthickness=0).grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky="w")

        # Tab Coloring Mode
        tk.Label(self.root, text="Tab Coloring:", bg=DARK_BG, fg=DARK_FG).grid(row=6, column=0, sticky="w", padx=10, pady=10)
        
        tab_coloring_frame = tk.Frame(self.root, bg=DARK_BG)
        tab_coloring_frame.grid(row=6, column=1, columnspan=2, sticky="w", padx=10, pady=10)
        
        self.tab_server_enabled_var = tk.BooleanVar(value=settings.get_tab_coloring_server_enabled())
        self.tab_db_enabled_var = tk.BooleanVar(value=settings.get_tab_coloring_db_enabled())
        
        tk.Checkbutton(tab_coloring_frame, text="Server only", 
                      variable=self.tab_server_enabled_var,
                      bg=DARK_BG, fg=DARK_FG, selectcolor=ENTRY_BG,
                      activebackground=DARK_BG, activeforeground=DARK_FG).pack(side="left", padx=(0, 20))
        
        tk.Checkbutton(tab_coloring_frame, text="Server + DB", 
                      variable=self.tab_db_enabled_var,
                      bg=DARK_BG, fg=DARK_FG, selectcolor=ENTRY_BG,
                      activebackground=DARK_BG, activeforeground=DARK_FG).pack(side="left", padx=(0, 20))
        
        btn_manage_colors = tk.Button(tab_coloring_frame, text="Manage Colors", command=self.open_color_manager, 
                                     bg=BTN_BG, fg=BTN_FG, relief='flat', width=12, bd=0, highlightthickness=0)
        btn_manage_colors.pack(side="left", padx=(10, 0))
        btn_manage_colors.bind("<Enter>", on_hover)
        btn_manage_colors.bind("<Leave>", on_leave)

        # Buttons
        btn_frame = tk.Frame(self.root, bg=DARK_BG)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=15)
        
        btn_save = tk.Button(btn_frame, text="Save", command=self.save, bg=BTN_BG, fg=BTN_FG, 
                             relief='flat', width=10, bd=0, highlightthickness=0)
        btn_save.pack(side="left", padx=10)
        btn_save.bind("<Enter>", on_hover)
        btn_save.bind("<Leave>", on_leave)
        
        btn_cancel = tk.Button(btn_frame, text="Close", command=self.cancel, bg=ENTRY_BG, fg=DARK_FG, 
                              relief='flat', width=10, bd=0, highlightthickness=0)
        btn_cancel.pack(side="left", padx=10)
        btn_cancel.bind("<Enter>", on_hover)
        btn_cancel.bind("<Leave>", lambda e: on_leave(e, "Close"))

        # Focus and center
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_reqheight()) // 2
        self.root.geometry(f"+{x}+{y}")

    def set_window_icon(self):
        """Set the window icon based on current tray icon setting"""
        try:
            # Get current tray icon color from settings
            icon_color = settings.get_tray_icon()
            icon_path = f"ssmsplus_{icon_color}.ico"
            
            # Check if the icon file exists, fallback to yellow if not
            if not os.path.exists(icon_path):
                icon_path = "ssmsplus_yellow.ico"
            
            # Set the window icon
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            # If there's any error loading the icon, silently continue
            pass

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
        tray_icon = self.tray_icon_var.get()
        tray_name = self.tray_name_var.get().strip()
        
        if not temp or not save or not os.path.isdir(temp) or not os.path.isdir(save):
            self.info_var.set("Both directories must exist.")
            self.flash_info_label("#FF5555")  # Red for error
            return
        
        if not tray_name:
            self.info_var.set("Tray app name cannot be empty.")
            self.flash_info_label("#FF5555")  # Red for error
            return
            
        # Check if grouping mode changed
        old_mode = settings.get_grouping_mode()
        mode_changed = old_mode != grouping_mode
        
        # Save all settings
        settings.set_grouping_mode(grouping_mode)
        settings.set_tray_icon(tray_icon)
        settings.set_tray_name(tray_name)
        
        # Save tab coloring settings
        settings.set_tab_coloring_server_enabled(self.tab_server_enabled_var.get())
        settings.set_tab_coloring_db_enabled(self.tab_db_enabled_var.get())
        
        # Update window icon if tray icon changed
        self.set_window_icon()
        
        # If mode changed, regenerate regex patterns
        if mode_changed:
            regenerate_all_regex_patterns()
        
        self.on_save(temp, save)
        self.info_var.set("Settings saved successfully.")
        self.flash_info_label("#00FF99")  # Green for success

    def open_color_manager(self):
        """Open the tab color management window"""
        ColorManagerWindow()

    def show(self):
        self.root.mainloop()


class ColorManagerWindow:
    """Window for managing tab colors for servers and databases"""
    
    # Color definitions with names and hex values
    COLORS = [
        ("None", "#808080"),      # 0 - no color (default)
        ("Lavender", "#9083ef"),  # 1
        ("Gold", "#d0b132"),      # 2  
        ("Cyan", "#30b1cd"),      # 3
        ("Burgundy", "#cf6468"),  # 4
        ("Green", "#6ba12a"),     # 5
        ("Brown", "#bc8f6f"),     # 6
        ("Royal Blue", "#5bb2fa"), # 7
        ("Pumpkin", "#d67441"),   # 8
        ("Gray", "#bdbcbc"),      # 9
        ("Volt", "#cbcc38"),      # 10
        ("Teal", "#2aa0a4"),      # 11
        ("Magenta", "#d957a7"),   # 12
        ("Mint", "#6bc6a5"),      # 13
        ("Dark Brown", "#946a5b"), # 14
        ("Blue", "#6a8ec6"),      # 15
        ("Pink", "#e0a3a5")       # 16
    ]
    
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("Tab Color Manager")
        self.root.configure(bg=DARK_BG)
        self.root.resizable(False, False)
        self.root.geometry("600x500")
        
        # Set custom icon
        self.set_window_icon()
        
        # Status label at top
        self.status_var = tk.StringVar(value="Manage tab colors for servers and databases")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, bg=DARK_BG, fg="#FFD700", 
                                   font=("Arial", 10, "bold"))
        self.status_label.pack(pady=(10, 0))
        
        # Main container with scrollbar
        self.create_scrollable_frame()
        
        # Populate the color options
        self.populate_color_options()
        
        # Center the window
        self.center_window()
        
        # Make window modal
        self.root.transient()
        self.root.grab_set()
        
    def set_window_icon(self):
        """Set the window icon based on current tray icon setting"""
        try:
            icon_color = settings.get_tray_icon()
            icon_path = f"ssmsplus_{icon_color}.ico"
            if not os.path.exists(icon_path):
                icon_path = "ssmsplus_yellow.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass
    
    def create_scrollable_frame(self):
        """Create a scrollable frame for the color options"""
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.root, bg=DARK_BG, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=DARK_BG)
        
        def update_scroll_region():
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Check if scrolling is needed
            canvas_height = self.canvas.winfo_height()
            content_height = self.scrollable_frame.winfo_reqheight()
            
            if content_height <= canvas_height:
                # Content fits, disable scrolling
                self.canvas.configure(scrollregion=(0, 0, 0, 0))
            else:
                # Content doesn't fit, enable scrolling
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        self.scrollable_frame.bind("<Configure>", lambda e: update_scroll_region())
        self.canvas.bind("<Configure>", lambda e: update_scroll_region())
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        self.scrollbar.pack(side="right", fill="y", pady=10, padx=(0, 10))
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            # Only scroll if scrolling is actually needed
            canvas_height = self.canvas.winfo_height()
            content_height = self.scrollable_frame.winfo_reqheight()
            if content_height > canvas_height:
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def populate_color_options(self):
        """Populate the scrollable frame with color options"""
        row = 0
        
        # Server coloring section
        if settings.get_tab_coloring_server_enabled():
            # Section header
            header_frame = tk.Frame(self.scrollable_frame, bg=DARK_BG)
            header_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=(10, 5))
            
            tk.Label(header_frame, text="Server Colors", bg=DARK_BG, fg="white", 
                    font=("Arial", 12, "bold")).pack(anchor="w")
            
            tk.Frame(header_frame, bg="white", height=2).pack(fill="x", pady=(2, 0))
            row += 1
            
            # Get all known servers
            servers = settings.get_configured_server_combinations()
            for server in servers:
                self.create_color_row(row, server, None, is_server=True)
                row += 1
        
        # Database coloring section  
        if settings.get_tab_coloring_db_enabled():
            # Section header
            header_frame = tk.Frame(self.scrollable_frame, bg=DARK_BG)
            header_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=(20, 5))
            
            tk.Label(header_frame, text="Database Colors", bg=DARK_BG, fg="white", 
                    font=("Arial", 12, "bold")).pack(anchor="w")
            
            tk.Frame(header_frame, bg="white", height=2).pack(fill="x", pady=(2, 0))
            row += 1
            
            # Get all known server.database combinations
            combinations = settings.get_configured_db_combinations()
            for combo in combinations:
                if '.' in combo:
                    server, db = combo.split('.', 1)
                    self.create_color_row(row, server, db, is_server=False)
                    row += 1
        
        # If no sections are enabled
        if not settings.get_tab_coloring_server_enabled() and not settings.get_tab_coloring_db_enabled():
            tk.Label(self.scrollable_frame, text="Tab coloring is disabled.\nEnable it in the main settings to manage colors.", 
                    bg=DARK_BG, fg="#FF5555", font=("Arial", 11), justify="center").grid(row=0, column=0, pady=50)
        
        # Update scroll region after content is populated
        self.root.after(100, self.update_scroll_region)
    
    def update_scroll_region(self):
        """Update the scroll region and check if scrolling is needed"""
        self.canvas.update_idletasks()
        self.scrollable_frame.update_idletasks()
        
        canvas_height = self.canvas.winfo_height()
        content_height = self.scrollable_frame.winfo_reqheight()
        
        if content_height <= canvas_height:
            # Content fits, disable scrolling by setting scroll region to zero
            self.canvas.configure(scrollregion=(0, 0, 0, 0))
        else:
            # Content doesn't fit, enable scrolling
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
    def create_color_row(self, row, server, db, is_server):
        """Create a row with server/db name and color dropdown"""
        # Display name
        if is_server:
            display_name = server
            current_color = settings.get_tab_color_for_combination(server)
        else:
            display_name = f"{server}.{db}"
            current_color = settings.get_tab_color_for_combination(server, db)
        
        # Name label
        name_label = tk.Label(self.scrollable_frame, text=display_name, bg=DARK_BG, fg=DARK_FG, 
                             font=("Arial", 10), width=20, anchor="w")
        name_label.grid(row=row, column=0, sticky="w", padx=(10, 5), pady=2)
        
        # Color dropdown
        color_var = tk.StringVar()
        color_combo = tk.OptionMenu(self.scrollable_frame, color_var, *[name for _, (name, _) in enumerate(self.COLORS)])
        color_combo.configure(bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=15, 
                             highlightthickness=0, bd=0, activebackground=BTN_HOVER)
        # Style the dropdown menu
        color_combo['menu'].configure(bg=ENTRY_BG, fg=DARK_FG, relief='flat', bd=0)
        color_combo.grid(row=row, column=1, padx=5, pady=2)
        
        # Set current value
        color_var.set(self.COLORS[current_color][0])
        
        # Color swatch - smaller rounded square
        swatch_frame = tk.Frame(self.scrollable_frame, bg=self.COLORS[current_color][1], 
                               width=20, height=20, relief="flat", bd=0)
        swatch_frame.grid(row=row, column=2, padx=(5, 10), pady=2)
        swatch_frame.grid_propagate(False)
        
        # Bind color change
        def on_color_change(value, s=server, d=db, is_srv=is_server, swatch=swatch_frame):
            try:
                # Find the color index by name
                color_index = None
                for i, (name, _) in enumerate(self.COLORS):
                    if name == value:
                        color_index = i
                        break
                
                if color_index is None:
                    return
                    
                color_hex = self.COLORS[color_index][1]
                
                # Update swatch
                swatch.configure(bg=color_hex)
                
                # Save to settings
                if is_srv:
                    settings.set_tab_color_for_server(s, color_index)
                else:
                    settings.set_tab_color_for_database(s, d, color_index)
                
                # Show success message
                self.flash_status("Color saved!", "#00FF99")
                
            except Exception as e:
                self.flash_status("Error saving color!", "#FF5555")
        
        color_var.trace('w', lambda *args, val=color_var: on_color_change(val.get()))
        
    def flash_status(self, message, color):
        """Flash a status message"""
        self.status_var.set(message)
        self.status_label.configure(fg=color)
        self.root.after(2000, lambda: self.status_var.set("Manage tab colors for servers and databases"))
        self.root.after(2000, lambda: self.status_label.configure(fg="#FFD700"))
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_reqheight()) // 2
        self.root.geometry(f"+{x}+{y}")
