#!/usr/bin/env python3
"""
TorrentToolkit GUI - A simple GUI for qBittorrent management
Author: Owen-3456
Repository: https://github.com/Owen-3456/TorrentToolkit
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
from dotenv import load_dotenv, set_key, find_dotenv

# Import our toolkit modules
from add_popular_trackers import add_popular_trackers
from remove_orphaned_torrents import remove_orphaned_torrents
from generate_report import generate_html_report

# Load environment variables
load_dotenv()


class TorrentToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TorrentToolkit - qBittorrent Management")
        self.root.geometry("500x400")
        self.root.resizable(True, True)

        # Configure style
        style = ttk.Style()
        style.theme_use("clam")

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="🔧 TorrentToolkit", font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        subtitle_label = ttk.Label(
            main_frame, text="qBittorrent Management Suite", font=("Arial", 10)
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 20))

        # Configuration status
        self.status_frame = ttk.LabelFrame(
            main_frame, text="Configuration Status", padding="10"
        )
        self.status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        self.status_frame.columnconfigure(0, weight=1)

        self.config_status_label = ttk.Label(self.status_frame, text="")
        self.config_status_label.grid(row=0, column=0)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        buttons_frame.columnconfigure(0, weight=1)

        # Button style
        button_style = {"width": 25, "padding": (10, 5)}

        # Edit .env button
        self.edit_env_btn = ttk.Button(
            buttons_frame,
            text="⚙️ Edit Configuration",
            command=self.edit_env_config,
            **button_style,
        )
        self.edit_env_btn.grid(row=0, column=0, pady=5, sticky=tk.EW)

        # Add trackers button
        self.add_trackers_btn = ttk.Button(
            buttons_frame,
            text="🔗 Add Popular Trackers",
            command=self.run_add_trackers,
            **button_style,
        )
        self.add_trackers_btn.grid(row=1, column=0, pady=5, sticky=tk.EW)

        # Remove orphaned button
        self.remove_orphaned_btn = ttk.Button(
            buttons_frame,
            text="🧹 Remove Orphaned Torrents",
            command=self.run_remove_orphaned,
            **button_style,
        )
        self.remove_orphaned_btn.grid(row=2, column=0, pady=5, sticky=tk.EW)

        # Generate report button
        self.generate_report_btn = ttk.Button(
            buttons_frame,
            text="📊 Generate HTML Report",
            command=self.run_generate_report,
            **button_style,
        )
        self.generate_report_btn.grid(row=3, column=0, pady=5, sticky=tk.EW)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(20, 10))

        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", font=("Arial", 9))
        self.status_label.grid(row=5, column=0)

        # Update config status
        self.update_config_status()

    def update_config_status(self):
        """Update the configuration status display"""
        qb_url = os.getenv("QB_URL")
        qb_user = os.getenv("QB_USER", "admin")
        qb_pass = os.getenv("QB_PASS")
        completed_folder = os.getenv("COMPLETED_FOLDER")

        status_text = f"URL: {qb_url or 'Not set'}\\n"
        status_text += f"User: {qb_user or 'Not set'}\\n"
        status_text += f"Password: {'***' if qb_pass else 'Not set'}\\n"
        status_text += f"Completed Folder: {completed_folder or 'Not set'}"

        self.config_status_label.config(text=status_text)

        # Enable/disable buttons based on config
        config_valid = bool(qb_url)
        state = tk.NORMAL if config_valid else tk.DISABLED

        self.add_trackers_btn.config(state=state)
        self.remove_orphaned_btn.config(
            state=state if completed_folder else tk.DISABLED
        )
        self.generate_report_btn.config(state=state)

    def edit_env_config(self):
        """Open a dialog to edit environment variables"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Edit Configuration")
        config_window.geometry("400x300")
        config_window.resizable(False, False)

        # Center the config window
        config_window.transient(self.root)
        config_window.grab_set()

        # Main frame
        main_frame = ttk.Frame(config_window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        config_window.columnconfigure(0, weight=1)
        config_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        ttk.Label(
            main_frame, text="Configuration Settings", font=("Arial", 12, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # Variables
        vars_data = [
            (
                "QB_URL",
                "qBittorrent URL:",
                os.getenv("QB_URL", "http://localhost:8080"),
            ),
            ("QB_USER", "Username:", os.getenv("QB_USER", "admin")),
            ("QB_PASS", "Password:", os.getenv("QB_PASS", "")),
            (
                "COMPLETED_FOLDER",
                "Completed Folder:",
                os.getenv("COMPLETED_FOLDER", ""),
            ),
        ]

        self.config_vars = {}

        for i, (var_name, label, default_value) in enumerate(vars_data):
            ttk.Label(main_frame, text=label).grid(
                row=i + 1, column=0, sticky=tk.W, pady=2
            )

            if var_name == "QB_PASS":
                entry = ttk.Entry(main_frame, show="*", width=30)
            else:
                entry = ttk.Entry(main_frame, width=30)

            entry.grid(row=i + 1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
            entry.insert(0, default_value)
            self.config_vars[var_name] = entry

            # Browse button for folder selection
            if var_name == "COMPLETED_FOLDER":
                browse_btn = ttk.Button(
                    main_frame, text="Browse", command=lambda: self.browse_folder(entry)
                )
                browse_btn.grid(row=i + 1, column=2, padx=(5, 0))

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=len(vars_data) + 2, column=0, columnspan=3, pady=(20, 0))

        ttk.Button(
            buttons_frame, text="Save", command=lambda: self.save_config(config_window)
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=config_window.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def browse_folder(self, entry_widget):
        """Open folder browser dialog"""
        folder = filedialog.askdirectory()
        if folder:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder)

    def save_config(self, config_window):
        """Save configuration to .env file"""
        try:
            env_file = find_dotenv()
            if not env_file:
                env_file = os.path.join(os.getcwd(), ".env")

            for var_name, entry in self.config_vars.items():
                value = entry.get().strip()
                set_key(env_file, var_name, value)
                os.environ[var_name] = value

            self.update_config_status()
            config_window.destroy()
            messagebox.showinfo("Success", "Configuration saved successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def set_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def show_progress(self, show=True):
        """Show/hide progress bar"""
        if show:
            self.progress.start()
        else:
            self.progress.stop()

    def run_in_thread(self, func, success_msg, error_msg):
        """Run a function in a separate thread"""

        def worker():
            try:
                self.set_status("Running...")
                self.show_progress(True)

                result = func()

                self.show_progress(False)
                if result:
                    self.set_status("Completed successfully!")
                    messagebox.showinfo("Success", success_msg)
                else:
                    self.set_status("Completed with errors")
                    messagebox.showwarning(
                        "Warning",
                        "Operation completed with warnings or errors. Check console for details.",
                    )

            except Exception as e:
                self.show_progress(False)
                self.set_status("Error occurred")
                messagebox.showerror("Error", f"{error_msg}\\n\\n{str(e)}")

        threading.Thread(target=worker, daemon=True).start()

    def run_add_trackers(self):
        """Run add popular trackers tool"""
        self.run_in_thread(
            add_popular_trackers,
            "Popular trackers added successfully!",
            "Failed to add popular trackers",
        )

    def run_remove_orphaned(self):
        """Run remove orphaned torrents tool"""
        self.run_in_thread(
            remove_orphaned_torrents,
            "Orphaned torrents analysis completed! Check console for removal commands.",
            "Failed to analyze orphaned torrents",
        )

    def run_generate_report(self):
        """Run generate HTML report tool"""

        def generate_and_open():
            success, filepath = generate_html_report()
            if success and filepath:
                # Open the HTML file in the default browser
                webbrowser.open(f"file://{os.path.abspath(filepath)}")
                return True
            return False

        self.run_in_thread(
            generate_and_open,
            "HTML report generated and opened in browser!",
            "Failed to generate HTML report",
        )


def main():
    """Main entry point for the GUI"""
    root = tk.Tk()
    app = TorrentToolkitGUI(root)

    # Handle window close
    def on_closing():
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
