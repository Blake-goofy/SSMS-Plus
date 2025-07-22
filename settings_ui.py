import tkinter as tk
from tkinter import filedialog, messagebox

DARK_BG = "#222831"
DARK_FG = "#eeeeee"
ENTRY_BG = "#393e46"
BTN_BG = "#08638D"
BTN_FG = "#eeeeee"

class SettingsWindow:
    def __init__(self, current_temp, current_save, on_save):
        self.root = tk.Tk()
        self.root.title("SSMS Plus Settings")
        self.root.configure(bg=DARK_BG)
        self.root.resizable(False, False)
        self.on_save = on_save

        self.temp_dir_var = tk.StringVar(value=current_temp)
        self.save_dir_var = tk.StringVar(value=current_save)

        # Temp Directory
        tk.Label(self.root, text="Temp Directory:", bg=DARK_BG, fg=DARK_FG).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.temp_dir_var, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=40).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.browse_temp, bg=BTN_BG, fg=BTN_FG, relief='flat').grid(row=0, column=2, padx=5, pady=10)

        # Save Directory
        tk.Label(self.root, text="Save Directory:", bg=DARK_BG, fg=DARK_FG).grid(row=1, column=0, sticky="w", padx=10, pady=10)
        tk.Entry(self.root, textvariable=self.save_dir_var, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=40).grid(row=1, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse", command=self.browse_save, bg=BTN_BG, fg=BTN_FG, relief='flat').grid(row=1, column=2, padx=5, pady=10)

        # Buttons
        btn_frame = tk.Frame(self.root, bg=DARK_BG)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=15)
        tk.Button(btn_frame, text="Save", command=self.save, bg=BTN_BG, fg=BTN_FG, relief='flat', width=10).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancel", command=self.root.destroy, bg=ENTRY_BG, fg=DARK_FG, relief='flat', width=10).pack(side="left", padx=10)

        # Focus and center
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_reqheight()) // 2
        self.root.geometry(f"+{x}+{y}")

    def browse_temp(self):
        directory = filedialog.askdirectory(initialdir=self.temp_dir_var.get() or ".")
        if directory:
            self.temp_dir_var.set(directory)

    def browse_save(self):
        directory = filedialog.askdirectory(initialdir=self.save_dir_var.get() or ".")
        if directory:
            self.save_dir_var.set(directory)

    def save(self):
        temp = self.temp_dir_var.get().strip()
        save = self.save_dir_var.get().strip()
        if not temp or not save:
            messagebox.showerror("Error", "Both directories are required.")
            return
        self.on_save(temp, save)
        self.root.destroy()

    def show(self):
        self.root.mainloop()

# Example usage:
if __name__ == "__main__":
    def on_save(temp, save):
        print("Saving settings:", temp, save)
    SettingsWindow("C:/Temp", "C:/Save", on_save).show()
