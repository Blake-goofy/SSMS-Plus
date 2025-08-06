import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
import webbrowser
from regex_writer import regenerate_all_regex_patterns
from state import settings, state
import os
import ctypes
import subprocess
import tempfile
import threading
import sys
from version import get_version

# Try to import requests, but gracefully handle if it's not available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

DARK_BG = "#222831"
DARK_FG = "#eeeeee"
ENTRY_BG = "#393e46"
BTN_BG = "#08638D"
BTN_FG = "#eeeeee"
BTN_HOVER = "#00959e"

class ToolTip:
    """Create a tooltip for a given widget"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.tipwindow = None

    def enter(self, event=None):
        self.showtip()

    def leave(self, event=None):
        self.hidetip()

    def showtip(self):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class SettingsWindow:
    def __init__(self, current_temp, current_save, on_save, initial_error=None):
        self.root = tk.Tk()
        self.root.title("SSMS Plus Settings")
        self.root.configure(bg=DARK_BG)
        self.root.resizable(False, False)
        self.on_save = on_save
        self.dirs_required = initial_error is not None  # Track if directories are required for app to run
        
        # Update-related variables
        self.current_version = get_version()
        self.update_available = False
        self.latest_version = None
        self.download_url = None
        self.checking_updates = False
        
        # Set custom icon for the window
        self.set_window_icon()

        self.temp_dir_var = tk.StringVar(value=current_temp or "")
        self.save_dir_var = tk.StringVar(value=current_save or "")
        self.grouping_mode_var = tk.StringVar(value=settings.get_grouping_mode())
        self.tray_icon_var = tk.StringVar(value=settings.get_tray_icon())
        self.tray_name_var = tk.StringVar(value=settings.get_tray_name())
        self.auto_tab_coloring_var = tk.BooleanVar(value=settings.get_auto_tab_coloring_enabled())

        # Create the tab system
        self.create_tab_system()
        
        # Create the settings tab content
        self.create_settings_tab()
        
        # Create the color management tab content
        self.create_color_tab()

        # Bind Enter key to save function
        self.root.bind('<Return>', lambda event: self.save())

        # Focus and center
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_reqheight()) // 2
        self.root.geometry(f"+{x}+{y}")
        
        # Check for updates on startup (in background)
        if REQUESTS_AVAILABLE:
            self.check_for_updates_async(silent=True)
    def create_tab_system(self):
        """Create the tab notebook"""
        self.notebook = ttk.Notebook(self.root)
        
        # Create frames for each tab
        self.settings_frame = tk.Frame(self.notebook, bg=DARK_BG)
        self.color_frame = tk.Frame(self.notebook, bg=DARK_BG)
        
        # Add tabs to notebook
        self.notebook.add(self.settings_frame, text="Settings")
        self.notebook.add(self.color_frame, text="Tab Colors")
        
        # Configure notebook style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=DARK_BG, borderwidth=0)
        style.configure('TNotebook.Tab', background=ENTRY_BG, foreground=DARK_FG, 
                       padding=[12, 8], focuscolor='none')
        style.map('TNotebook.Tab', 
                 background=[('selected', BTN_BG), ('active', BTN_HOVER)],
                 foreground=[('selected', BTN_FG), ('active', BTN_FG)])
        
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

    def create_settings_tab(self):
        """Create the main settings tab content"""
        # Info/Error label at the top
        if self.dirs_required:
            self.info_var = tk.StringVar(value="Both directories must exist to continue.")
            self.info_label = tk.Label(self.settings_frame, textvariable=self.info_var, bg=DARK_BG, fg="#FF5555", font=("Arial", 10, "bold"))
        else:
            self.info_var = tk.StringVar(value="Change settings below")
            self.info_label = tk.Label(self.settings_frame, textvariable=self.info_var, bg=DARK_BG, fg="#FFD700", font=("Arial", 10, "bold"))
        self.info_label.grid(row=0, column=0, columnspan=2, sticky="we", padx=10, pady=(10, 0))
        
        def on_hover(e):
            e.widget.configure(bg=BTN_HOVER)

        def on_leave(e, src = "Default"):
            if(src == "Close"):
                e.widget.configure(bg=ENTRY_BG)
            else:
                e.widget.configure(bg=BTN_BG)

        # Help button in top right corner
        btn_help = tk.Button(self.settings_frame, text="Help", command=self.open_help, bg=ENTRY_BG, fg=DARK_FG, 
                            relief='flat', width=8, bd=0, highlightthickness=0)
        btn_help.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="e")
        btn_help.bind("<Enter>", on_hover)
        btn_help.bind("<Leave>", lambda e: on_leave(e, "Close"))

        # Temp Directory
        temp_label = tk.Label(self.settings_frame, text="Temp Directory:", bg=DARK_BG, fg=DARK_FG)
        temp_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        ToolTip(temp_label, "The directory where SSMS saves .sql files when opening from Object Explorer")
        
        tk.Entry(self.settings_frame, textvariable=self.temp_dir_var, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=40, 
                bd=0, highlightthickness=0).grid(row=1, column=1, padx=10, pady=10)
        
        btn_auto_temp = tk.Button(self.settings_frame, text="Auto", command=self.auto_temp, bg=BTN_BG, fg=BTN_FG, 
                                 relief='flat', width=8, bd=0, highlightthickness=0)
        btn_auto_temp.grid(row=1, column=2, padx=5, pady=10)
        btn_auto_temp.bind("<Enter>", on_hover)
        btn_auto_temp.bind("<Leave>", on_leave)

        # Save Directory
        save_label = tk.Label(self.settings_frame, text="Save Directory:", bg=DARK_BG, fg=DARK_FG)
        save_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)
        ToolTip(save_label, "The directory where .sql files will be automatically saved after editing")
        
        tk.Entry(self.settings_frame, textvariable=self.save_dir_var, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=40,
                bd=0, highlightthickness=0).grid(row=2, column=1, padx=10, pady=10)
        btn_browse_save = tk.Button(self.settings_frame, text="Browse", command=self.browse_save, bg=BTN_BG, fg=BTN_FG, 
                                   relief='flat', width=8, bd=0, highlightthickness=0)
        btn_browse_save.grid(row=2, column=2, padx=5, pady=10)
        btn_browse_save.bind("<Enter>", on_hover)
        btn_browse_save.bind("<Leave>", on_leave)

        # Tray Icon Color
        tray_icon_label = tk.Label(self.settings_frame, text="Tray Icon:", bg=DARK_BG, fg=DARK_FG)
        tray_icon_label.grid(row=3, column=0, sticky="w", padx=10, pady=10)
        ToolTip(tray_icon_label, "Choose the color of the system tray icon")
        
        icon_frame = tk.Frame(self.settings_frame, bg=DARK_BG)
        icon_frame.grid(row=3, column=1, columnspan=2, sticky="w", padx=10, pady=10)
        
        tk.Radiobutton(icon_frame, text="Yellow", 
                      variable=self.tray_icon_var, value="yellow",
                      bg=DARK_BG, fg=DARK_FG, selectcolor=ENTRY_BG,
                      activebackground=DARK_BG, activeforeground=DARK_FG,
                      command=self.on_tray_icon_changed).pack(side="left", padx=(0, 20))
        
        tk.Radiobutton(icon_frame, text="Red", 
                      variable=self.tray_icon_var, value="red",
                      bg=DARK_BG, fg=DARK_FG, selectcolor=ENTRY_BG,
                      activebackground=DARK_BG, activeforeground=DARK_FG,
                      command=self.on_tray_icon_changed).pack(side="left")

        # Tray App Name
        tray_name_label = tk.Label(self.settings_frame, text="Tray App Name:", bg=DARK_BG, fg=DARK_FG)
        tray_name_label.grid(row=4, column=0, sticky="w", padx=10, pady=10)
        ToolTip(tray_name_label, "The name displayed in the system tray and taskbar")
        
        tk.Entry(self.settings_frame, textvariable=self.tray_name_var, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=40,
                bd=0, highlightthickness=0).grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="w")

        # Tab Grouping Mode
        grouping_label = tk.Label(self.settings_frame, text="Tab Grouping:", bg=DARK_BG, fg=DARK_FG)
        grouping_label.grid(row=5, column=0, sticky="w", padx=10, pady=10)
        ToolTip(grouping_label, "How to group tabs by color:\nServer only - Same color for all tabs from same server\nServer + DB - Different colors for each server.database combination")
        
        grouping_frame = tk.Frame(self.settings_frame, bg=DARK_BG)
        grouping_frame.grid(row=5, column=1, columnspan=2, sticky="w", padx=10, pady=10)
        
        tk.Radiobutton(grouping_frame, text="Server only", 
                      variable=self.grouping_mode_var, value="server",
                      bg=DARK_BG, fg=DARK_FG, selectcolor=ENTRY_BG,
                      activebackground=DARK_BG, activeforeground=DARK_FG,
                      command=self.on_grouping_mode_changed).pack(side="left", padx=(0, 20))
        
        tk.Radiobutton(grouping_frame, text="Server + DB", 
                      variable=self.grouping_mode_var, value="server_db",
                      bg=DARK_BG, fg=DARK_FG, selectcolor=ENTRY_BG,
                      activebackground=DARK_BG, activeforeground=DARK_FG,
                      command=self.on_grouping_mode_changed).pack(side="left")

        # Auto Tab Coloring
        auto_coloring_label = tk.Label(self.settings_frame, text="Auto Tab Coloring:", bg=DARK_BG, fg=DARK_FG)
        auto_coloring_label.grid(row=6, column=0, sticky="w", padx=10, pady=10)
        ToolTip(auto_coloring_label, "Automatically color SSMS tabs based on server/database\nUse the Tab Colors tab to assign specific colors")
        
        auto_coloring_frame = tk.Frame(self.settings_frame, bg=DARK_BG)
        auto_coloring_frame.grid(row=6, column=1, columnspan=2, sticky="w", padx=10, pady=10)
        
        tk.Checkbutton(auto_coloring_frame, text="Enable automatic tab coloring", 
                      variable=self.auto_tab_coloring_var,
                      bg=DARK_BG, fg=DARK_FG, selectcolor=ENTRY_BG,
                      activebackground=DARK_BG, activeforeground=DARK_FG,
                      command=self.on_auto_coloring_changed).pack(side="left", padx=(0, 20))

        # Buttons
        btn_frame = tk.Frame(self.settings_frame, bg=DARK_BG)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=15)
        
        btn_save = tk.Button(btn_frame, text="Save", command=self.save, bg=BTN_BG, fg=BTN_FG, 
                             relief='flat', width=10, bd=0, highlightthickness=0)
        btn_save.pack(side="left", padx=10)
        btn_save.bind("<Enter>", on_hover)
        btn_save.bind("<Leave>", on_leave)
        
        # Update button (only show if requests is available)
        if REQUESTS_AVAILABLE:
            self.btn_update = tk.Button(btn_frame, text="Check for Updates", command=self.handle_update_click, 
                                       bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=15, bd=0, highlightthickness=0)
            self.btn_update.pack(side="left", padx=10)
            self.btn_update.bind("<Enter>", on_hover)
            self.btn_update.bind("<Leave>", lambda e: on_leave(e, "Close"))
        
        btn_cancel = tk.Button(btn_frame, text="Close", command=self.cancel, bg=ENTRY_BG, fg=DARK_FG, 
                              relief='flat', width=10, bd=0, highlightthickness=0)
        btn_cancel.pack(side="left", padx=10)
        btn_cancel.bind("<Enter>", on_hover)
        btn_cancel.bind("<Leave>", lambda e: on_leave(e, "Close"))

    def create_color_tab(self):
        """Create the color management tab content"""
        # Color definitions with names and hex values
        self.COLORS = [
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
        
        # Track known combinations for auto-refresh
        self.last_known_servers = set()
        self.last_known_combinations = set()
        
        # Status label at top
        self.color_status_var = tk.StringVar(value="Manage tab colors for servers and databases")
        self.color_status_label = tk.Label(self.color_frame, textvariable=self.color_status_var, bg=DARK_BG, fg="#FFD700", 
                                          font=("Arial", 10, "bold"))
        self.color_status_label.pack(pady=(10, 0))
        
        # Create scrollable frame for color options
        self.create_color_scrollable_frame()
        
        # Populate the color options and start auto-refresh
        self.populate_color_options()
        self.start_auto_refresh()

    def create_color_scrollable_frame(self):
        """Create a scrollable frame for the color options"""
        # Container frame
        container = tk.Frame(self.color_frame, bg=DARK_BG)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        self.color_canvas = tk.Canvas(container, bg=DARK_BG, highlightthickness=0)
        self.color_scrollbar = tk.Scrollbar(container, orient="vertical", command=self.color_canvas.yview)
        self.color_scrollable_frame = tk.Frame(self.color_canvas, bg=DARK_BG)
        
        def update_color_scroll_region():
            self.color_canvas.update_idletasks()
            self.color_scrollable_frame.update_idletasks()
            
            canvas_height = self.color_canvas.winfo_height()
            content_height = self.color_scrollable_frame.winfo_reqheight()
            
            if content_height <= canvas_height:
                # Content fits, hide scrollbar and disable scrolling
                self.color_scrollbar.pack_forget()
                self.color_canvas.configure(scrollregion=(0, 0, 0, 0))
                self.color_canvas.pack(side="left", fill="both", expand=True)
            else:
                # Content doesn't fit, show scrollbar and enable scrolling
                self.color_canvas.pack(side="left", fill="both", expand=True)
                self.color_scrollbar.pack(side="right", fill="y")
                self.color_canvas.configure(scrollregion=self.color_canvas.bbox("all"))
        
        self.color_scrollable_frame.bind("<Configure>", lambda e: update_color_scroll_region())
        self.color_canvas.bind("<Configure>", lambda e: update_color_scroll_region())
        
        self.color_canvas.create_window((0, 0), window=self.color_scrollable_frame, anchor="nw")
        self.color_canvas.configure(yscrollcommand=self.color_scrollbar.set)
        
        # Initially pack canvas (scrollbar will be shown/hidden as needed)
        self.color_canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mousewheel to canvas
        def _on_color_mousewheel(event):
            # Only scroll if scrolling is actually needed
            canvas_height = self.color_canvas.winfo_height()
            content_height = self.color_scrollable_frame.winfo_reqheight()
            if content_height > canvas_height:
                self.color_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.color_canvas.bind_all("<MouseWheel>", _on_color_mousewheel)

    def refresh_color_tab(self):
        """Refresh the color tab content"""
        # Clear existing content
        for widget in self.color_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Repopulate the color options
        self.populate_color_options()

    def start_auto_refresh(self):
        """Start the automatic refresh timer"""
        self.check_for_new_combinations()
        # Check every 3 seconds for new combinations
        self.root.after(3000, self.start_auto_refresh)

    def check_for_new_combinations(self):
        """Check if new server/database combinations have been discovered"""
        try:
            grouping_mode = settings.get_grouping_mode()
            needs_refresh = False
            
            if grouping_mode == "server":
                current_servers = set(settings.get_configured_server_combinations())
                if current_servers != self.last_known_servers:
                    needs_refresh = True
                    self.last_known_servers = current_servers
                    
            elif grouping_mode == "server_db":
                current_combinations = set(settings.get_configured_db_combinations())
                if current_combinations != self.last_known_combinations:
                    needs_refresh = True
                    self.last_known_combinations = current_combinations
            
            if needs_refresh:
                self.refresh_color_tab()
                # Brief visual feedback for auto-refresh
                self.flash_color_status("New servers/databases detected!", "#00AAFF")
                
        except Exception as e:
            # Silently handle any errors during auto-refresh
            pass

    def populate_color_options(self):
        """Populate the scrollable frame with color options"""
        row = 0
        
        # Only show color options if auto coloring is enabled
        if settings.get_auto_tab_coloring_enabled():
            grouping_mode = settings.get_grouping_mode()
            
            # Server coloring section (only show in "server" mode)
            if grouping_mode == "server" and settings.get_tab_coloring_server_enabled():
                # Section header
                header_frame = tk.Frame(self.color_scrollable_frame, bg=DARK_BG)
                header_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=(10, 5))
                
                tk.Label(header_frame, text="Server Colors", bg=DARK_BG, fg="white", 
                        font=("Arial", 12, "bold")).pack(anchor="w")
                
                tk.Frame(header_frame, bg="white", height=2).pack(fill="x", pady=(2, 0))
                row += 1
                
                # Get all known servers and update tracking
                servers = settings.get_configured_server_combinations()
                self.last_known_servers = set(servers)
                for server in servers:
                    self.create_color_row(row, server, None, is_server=True)
                    row += 1
            
            # Database coloring section (only show in "server_db" mode)
            if grouping_mode == "server_db" and settings.get_tab_coloring_db_enabled():
                # Section header
                header_frame = tk.Frame(self.color_scrollable_frame, bg=DARK_BG)
                header_frame.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=(10, 5))
                
                tk.Label(header_frame, text="Server + Database Colors", bg=DARK_BG, fg="white", 
                        font=("Arial", 12, "bold")).pack(anchor="w")
                
                tk.Frame(header_frame, bg="white", height=2).pack(fill="x", pady=(2, 0))
                row += 1
                
                # Get all known server.database combinations and update tracking
                combinations = settings.get_configured_db_combinations()
                self.last_known_combinations = set(combinations)
                for combo in combinations:
                    if '.' in combo:
                        server, db = combo.split('.', 1)
                        self.create_color_row(row, server, db, is_server=False)
                        row += 1
        
        # If auto coloring is disabled
        if not settings.get_auto_tab_coloring_enabled():
            tk.Label(self.color_scrollable_frame, text="Auto tab coloring is disabled.\nEnable it in the Settings tab to manage colors.", 
                    bg=DARK_BG, fg="#FF5555", font=("Arial", 11), justify="center").grid(row=0, column=0, pady=50)
        # If auto coloring is enabled but no servers/databases exist yet
        else:
            grouping_mode = settings.get_grouping_mode()
            has_content = False
            
            if grouping_mode == "server" and settings.get_configured_server_combinations():
                has_content = True
            elif grouping_mode == "server_db" and settings.get_configured_db_combinations():
                has_content = True
            
            if not has_content:
                if grouping_mode == "server":
                    message = "No servers found yet.\nOpen a document in SSMS to see servers here."
                else:  # server_db
                    message = "No server + database combinations found yet.\nOpen a document in SSMS to see combinations here."
                
                tk.Label(self.color_scrollable_frame, text=message, 
                        bg=DARK_BG, fg="white", font=("Arial", 11), justify="center").grid(row=0, column=0, pady=50)
        
        # Update scroll region after content is populated
        self.root.after(100, self.update_color_scroll_region)
    
    def update_color_scroll_region(self):
        """Update the scroll region and check if scrolling is needed"""
        self.color_canvas.update_idletasks()
        self.color_scrollable_frame.update_idletasks()
        
        canvas_height = self.color_canvas.winfo_height()
        content_height = self.color_scrollable_frame.winfo_reqheight()
        
        if content_height <= canvas_height:
            # Content fits, hide scrollbar and disable scrolling
            self.color_scrollbar.pack_forget()
            self.color_canvas.configure(scrollregion=(0, 0, 0, 0))
            self.color_canvas.pack(side="left", fill="both", expand=True)
        else:
            # Content doesn't fit, show scrollbar and enable scrolling
            self.color_canvas.pack(side="left", fill="both", expand=True)
            self.color_scrollbar.pack(side="right", fill="y")
            self.color_canvas.configure(scrollregion=self.color_canvas.bbox("all"))
            
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
        name_label = tk.Label(self.color_scrollable_frame, text=display_name, bg=DARK_BG, fg=DARK_FG, 
                             font=("Arial", 10, "bold"), width=20, anchor="w")
        name_label.grid(row=row, column=0, sticky="w", padx=(10, 5), pady=2)
        
        # Color dropdown
        color_var = tk.StringVar()
        color_combo = tk.OptionMenu(self.color_scrollable_frame, color_var, *[name for _, (name, _) in enumerate(self.COLORS)])
        color_combo.configure(bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=15, 
                             highlightthickness=0, bd=0, activebackground="#555555")
        # Style the dropdown menu
        color_combo['menu'].configure(bg=ENTRY_BG, fg=DARK_FG, relief='flat', bd=0, 
                                    activebackground="#555555", activeborderwidth=0)
        color_combo.grid(row=row, column=1, padx=5, pady=2)
        
        # Set current value
        color_var.set(self.COLORS[current_color][0])
        
        # Color swatch - rounded square using Canvas
        swatch_canvas = tk.Canvas(self.color_scrollable_frame, width=20, height=20, bg=DARK_BG, highlightthickness=0)
        swatch_canvas.grid(row=row, column=2, padx=(5, 10), pady=2)
        
        # Create simple flat rectangle
        def create_swatch(canvas, x1, y1, x2, y2, fill):
            canvas.delete("all")  # Clear previous content
            # Simple flat rectangle with sharp corners
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")
        
        # Initial color
        create_swatch(swatch_canvas, 2, 2, 18, 18, self.COLORS[current_color][1])
        
        # Bind color change
        def on_color_change(value, s=server, d=db, is_srv=is_server, swatch=swatch_canvas):
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
                
                # Update swatch using the swatch function
                create_swatch(swatch, 2, 2, 18, 18, color_hex)
                
                # Save to settings
                if is_srv:
                    settings.set_tab_color_for_server(s, color_index)
                    # Forget this server from applied colors so it gets colored on next save
                    state.forget_tab_color_applied(s)
                else:
                    settings.set_tab_color_for_database(s, d, color_index)
                    # Forget this server/db combination from applied colors so it gets colored on next save
                    state.forget_tab_color_applied(s, d)
                
                # Show success message
                self.flash_color_status("Color saved!", "#00FF99")
                
            except Exception as e:
                self.flash_color_status("Error saving color!", "#FF5555")
        
        color_var.trace('w', lambda *args, val=color_var: on_color_change(val.get()))
        
    def flash_color_status(self, message, color):
        """Flash a status message in the color tab"""
        self.color_status_var.set(message)
        self.color_status_label.configure(fg=color)
        self.root.after(2000, lambda: self.color_status_var.set("Manage tab colors for servers and databases"))
        self.root.after(2000, lambda: self.color_status_label.configure(fg="#FFD700"))

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
                
            # Try to enable dark mode for the title bar
            self.enable_dark_title_bar()
        except Exception as e:
            # If there's any error loading the icon, silently continue
            pass

    def on_auto_coloring_changed(self):
        """Handle auto coloring checkbox changes - save immediately"""
        settings.set_auto_tab_coloring_enabled(self.auto_tab_coloring_var.get())
        self.show_saved_message()
        # Refresh the color tab content when auto coloring is toggled
        self.refresh_color_tab()
    
    def on_tray_icon_changed(self):
        """Handle tray icon changes - save immediately"""
        settings.set_tray_icon(self.tray_icon_var.get())
        self.set_window_icon()  # Update window icon immediately
        self.show_saved_message()
    
    def on_grouping_mode_changed(self):
        """Handle grouping mode changes - save immediately"""
        old_mode = settings.get_grouping_mode()
        new_mode = self.grouping_mode_var.get()
        
        if old_mode != new_mode:
            settings.set_grouping_mode(new_mode)
            # Regenerate regex patterns when mode changes
            regenerate_all_regex_patterns()
            self.show_saved_message()
            # Refresh the color tab content when grouping mode changes
            self.refresh_color_tab()
    
    def show_saved_message(self):
        """Show a brief 'saved' message"""
        self.info_var.set("Setting saved!")
        self.flash_info_label("#00FF99")  # Green for success
        # Always restore to default message and color after 1.5 seconds
        self.root.after(1500, lambda: self.info_var.set("Change settings below"))
        self.root.after(1500, lambda: self.info_label.configure(fg="#FFD700"))
    
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
                # Always restore to default message and color after 3 seconds
                self.root.after(3000, lambda: self.info_var.set("Change settings below"))
                self.root.after(3000, lambda: self.info_label.configure(fg="#FFD700"))
                return
        
        self.root.destroy()

    def save(self):
        temp = self.temp_dir_var.get().strip()
        save = self.save_dir_var.get().strip()
        tray_name = self.tray_name_var.get().strip()
        
        if not temp or not save or not os.path.isdir(temp) or not os.path.isdir(save):
            self.info_var.set("Both directories must exist.")
            self.flash_info_label("#FF5555")  # Red for error
            # Always restore to default message and color after 3 seconds
            self.root.after(3000, lambda: self.info_var.set("Change settings below"))
            self.root.after(3000, lambda: self.info_label.configure(fg="#FFD700"))
            return
        
        if not tray_name:
            self.info_var.set("Tray app name cannot be empty.")
            self.flash_info_label("#FF5555")  # Red for error
            # Always restore to default message and color after 3 seconds
            self.root.after(3000, lambda: self.info_var.set("Change settings below"))
            self.root.after(3000, lambda: self.info_label.configure(fg="#FFD700"))
            return
            
        # Save tray name setting
        settings.set_tray_name(tray_name)
        
        # Call the callback with directory settings
        self.on_save(temp, save)
        self.show_saved_message()

    def handle_update_click(self):
        """Handle the update button click"""
        if not REQUESTS_AVAILABLE or self.checking_updates:
            return  # Can't check without requests or already checking
            
        if self.update_available:
            # Update is available, start the download/install process
            self.start_update_process()
        else:
            # Check for updates
            self.check_for_updates_async(silent=False)
    
    def check_for_updates_async(self, silent=True):
        """Check for updates in a background thread"""
        if self.checking_updates:
            return
            
        if not REQUESTS_AVAILABLE:
            if not silent:
                self.root.after(0, lambda: self.show_update_error_message())
            return
            
        def check_updates():
            self.checking_updates = True
            if not silent:
                self.root.after(0, lambda: self.btn_update.configure(text="Checking..."))
                
            try:
                # Check GitHub releases API
                response = requests.get("https://api.github.com/repos/Blake-goofy/ssmsplus/releases/latest", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data.get("tag_name", "").lstrip("v")
                    
                    # Find the setup exe in assets
                    download_url = None
                    for asset in data.get("assets", []):
                        if asset["name"].endswith("Setup.exe"):
                            download_url = asset["browser_download_url"]
                            break
                    
                    if download_url and self.is_newer_version(latest_version):
                        # Update available
                        self.latest_version = latest_version
                        self.download_url = download_url
                        self.update_available = True
                        self.root.after(0, lambda: self.btn_update.configure(text="Update Available"))
                        self.root.after(0, lambda: self.btn_update.configure(bg=BTN_BG))
                        
                        if not silent:
                            self.root.after(0, lambda: self.show_update_available_message())
                    else:
                        # No update available
                        self.update_available = False
                        self.root.after(0, lambda: self.btn_update.configure(text="Check for Updates"))
                        self.root.after(0, lambda: self.btn_update.configure(bg=ENTRY_BG))
                        
                        if not silent:
                            self.root.after(0, lambda: self.show_no_update_message())
                else:
                    if not silent:
                        self.root.after(0, lambda: self.show_update_error_message())
                        
            except Exception as e:
                print(f"Error checking for updates: {e}")
                if not silent:
                    self.root.after(0, lambda: self.show_update_error_message())
            finally:
                self.checking_updates = False
                if not silent and not self.update_available:
                    self.root.after(0, lambda: self.btn_update.configure(text="Check for Updates"))
        
        # Start the check in a background thread
        threading.Thread(target=check_updates, daemon=True).start()
    
    def is_newer_version(self, latest_version):
        """Compare versions to see if latest is newer than current"""
        try:
            def version_tuple(v):
                return tuple(map(int, v.split('.')))
            return version_tuple(latest_version) > version_tuple(self.current_version)
        except:
            return False
    
    def show_update_available_message(self):
        """Show message that update is available"""
        self.info_var.set(f"Update available: v{self.latest_version}")
        self.flash_info_label("#00FF99")  # Green
        self.root.after(3000, lambda: self.info_var.set("Change settings below"))
        self.root.after(3000, lambda: self.info_label.configure(fg="#FFD700"))
    
    def show_no_update_message(self):
        """Show message that no update is available"""
        self.info_var.set("You have the latest version!")
        self.flash_info_label("#00FF99")  # Green
        self.root.after(3000, lambda: self.info_var.set("Change settings below"))
        self.root.after(3000, lambda: self.info_label.configure(fg="#FFD700"))
    
    def show_update_error_message(self):
        """Show message that update check failed"""
        self.info_var.set("Could not check for updates")
        self.flash_info_label("#FF5555")  # Red
        self.root.after(3000, lambda: self.info_var.set("Change settings below"))
        self.root.after(3000, lambda: self.info_label.configure(fg="#FFD700"))
    
    def start_update_process(self):
        """Download and install the update"""
        if not self.download_url or not REQUESTS_AVAILABLE:
            return
            
        def download_and_install():
            try:
                self.root.after(0, lambda: self.btn_update.configure(text="Downloading..."))
                self.root.after(0, lambda: self.info_var.set("Downloading update..."))
                
                # Download the installer
                response = requests.get(self.download_url, timeout=300)  # 5 minutes timeout
                if response.status_code == 200:
                    # Save to temp file
                    temp_file = tempfile.mktemp(suffix=".exe")
                    with open(temp_file, 'wb') as f:
                        f.write(response.content)
                    
                    self.root.after(0, lambda: self.info_var.set("Preparing to install update..."))
                    
                    # Show completion message
                    self.root.after(0, lambda: self.show_update_installing_message())
                    
                    # Schedule the update process to run after a delay
                    self.root.after(2000, lambda: self.execute_update(temp_file))
                    
                else:
                    self.root.after(0, lambda: self.show_update_error_message())
                    self.root.after(0, lambda: self.btn_update.configure(text="Update Available"))
                    
            except Exception as e:
                print(f"Error during update: {e}")
                self.root.after(0, lambda: self.show_update_error_message())
                self.root.after(0, lambda: self.btn_update.configure(text="Update Available"))
        
        # Start download in background thread
        threading.Thread(target=download_and_install, daemon=True).start()
    
    def execute_update(self, installer_path):
        """Execute the update installer and properly close the application"""
        try:
            # Start the installer with additional parameters for auto-restart
            subprocess.Popen([installer_path, "/SILENT", "/RESTARTEXITCODE=3010"], shell=True)
            
            # Properly shutdown the application
            # First close the settings window
            self.root.destroy()
            
            # Then trigger application exit through the main app
            # This allows proper cleanup of resources
            if hasattr(state, 'current_tray_app') and state.current_tray_app:
                # Force quit the tray app properly
                try:
                    # Stop any watchers first
                    if hasattr(state, 'current_watcher_observer') and state.current_watcher_observer:
                        state.current_watcher_observer.stop()
                        state.current_watcher_observer = None
                    
                    # Quit the tray app's main loop
                    state.current_tray_app.icon.stop()
                    
                    # Schedule immediate exit
                    import threading
                    def force_exit():
                        import time
                        time.sleep(0.5)  # Give time for cleanup
                        import os
                        os._exit(0)
                    
                    threading.Thread(target=force_exit, daemon=True).start()
                    
                except Exception as e:
                    print(f"Error during tray app shutdown: {e}")
                    # Fallback to direct exit
                    import os
                    os._exit(0)
            else:
                # Fallback to direct exit
                import os
                os._exit(0)
                
        except Exception as e:
            print(f"Error executing update: {e}")
            # If update fails, just close settings window
            self.root.destroy()
    
    def show_update_installing_message(self):
        """Show message that update is installing"""
        self.info_var.set("Closing app for update - installer will start...")
        self.flash_info_label("#00FF99")  # Green

    def enable_dark_title_bar(self):
        """Enable dark title bar on Windows 10/11"""
        try:
            # Windows API constants for dark title bar
            DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            
            # Get window handle
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            
            # Try the newer attribute first, fallback to older if needed
            value = ctypes.c_int(1)
            result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(value), ctypes.sizeof(value)
            )
            
            # If that failed, try the older attribute
            if result != 0:
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1, ctypes.byref(value), ctypes.sizeof(value)
                )
        except:
            # Silently fail if dark mode can't be enabled
            pass

    def show(self):
        self.root.mainloop()
