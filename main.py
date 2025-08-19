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
import shutil
from dotenv import load_dotenv, set_key, find_dotenv
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Import our toolkit modules
from add_popular_trackers import add_popular_trackers
from remove_orphaned_torrents import get_orphaned_torrents_data, delete_selected_files
from generate_report import generate_html_report

# Environment variables will be loaded after .env file check


class TorrentToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TorrentToolkit - qBittorrent Management")
        self.root.geometry("1100x800")
        self.root.resizable(True, True)
        self.root.configure(bg="#2b2b2b")

        # Set minimum size
        self.root.minsize(900, 700)

        # Try to set a nice window icon (optional, will fail gracefully if not found)
        try:
            # You can add an icon file to your project and uncomment this
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass

        # Configure modern dark theme
        self.setup_modern_style()

        self.create_modern_widgets()
        self.center_window()

    def setup_modern_style(self):
        """Configure modern dark theme styling"""
        style = ttk.Style()

        # Configure the theme
        style.theme_use("clam")

        # Define color palette
        self.colors = {
            "primary": "#0d7377",
            "primary_light": "#14a085",
            "secondary": "#323232",
            "background": "#2b2b2b",
            "surface": "#3c3c3c",
            "surface_light": "#4a4a4a",
            "text": "#ffffff",
            "text_secondary": "#b0b0b0",
            "accent": "#fa7268",
            "success": "#4caf50",
            "warning": "#ff9800",
            "error": "#f44336",
        }

        # Configure styles
        style.configure("Modern.TFrame", background=self.colors["background"])

        style.configure(
            "Card.TFrame",
            background=self.colors["surface"],
            relief="flat",
            borderwidth=1,
        )

        style.configure(
            "Title.TLabel",
            background=self.colors["background"],
            foreground=self.colors["text"],
            font=("Segoe UI", 28, "bold"),
        )

        style.configure(
            "Subtitle.TLabel",
            background=self.colors["background"],
            foreground=self.colors["text_secondary"],
            font=("Segoe UI", 13),
        )

        style.configure(
            "Heading.TLabel",
            background=self.colors["surface"],
            foreground=self.colors["text"],
            font=("Segoe UI", 14, "bold"),
        )

        style.configure(
            "Status.TLabel",
            background=self.colors["surface"],
            foreground=self.colors["text_secondary"],
            font=("Segoe UI", 11),
        )

        style.configure(
            "Footer.TLabel",
            background=self.colors["background"],
            foreground=self.colors["text_secondary"],
            font=("Segoe UI", 10),
        )

        # Modern button styles
        style.configure(
            "Primary.TButton",
            background=self.colors["primary"],
            foreground="white",
            font=("Segoe UI", 12, "bold"),
            borderwidth=0,
            focuscolor="none",
            padding=(25, 15),
        )

        style.map(
            "Primary.TButton",
            background=[
                ("active", self.colors["primary_light"]),
                ("pressed", "#0a5d61"),
            ],
        )

        style.configure(
            "Secondary.TButton",
            background=self.colors["surface_light"],
            foreground=self.colors["text"],
            font=("Segoe UI", 11),
            borderwidth=0,
            focuscolor="none",
            padding=(20, 12),
        )

        style.map(
            "Secondary.TButton",
            background=[("active", "#5a5a5a"), ("pressed", "#404040")],
        )

        style.configure(
            "Success.TButton",
            background=self.colors["success"],
            foreground="white",
            font=("Segoe UI", 12, "bold"),
            borderwidth=0,
            focuscolor="none",
            padding=(20, 12),
        )

        style.configure(
            "Warning.TButton",
            background=self.colors["warning"],
            foreground="white",
            font=("Segoe UI", 12, "bold"),
            borderwidth=0,
            focuscolor="none",
            padding=(20, 12),
        )

        # Progress bar
        style.configure(
            "Modern.Horizontal.TProgressbar",
            background=self.colors["primary"],
            troughcolor=self.colors["surface_light"],
            borderwidth=0,
            lightcolor=self.colors["primary"],
            darkcolor=self.colors["primary"],
        )

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_modern_widgets(self):
        """Create modern GUI widgets with card-based layout"""
        # Main container
        main_container = ttk.Frame(self.root, style="Modern.TFrame", padding="30")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1)

        # Header section
        self.create_header(main_container)

        # Status card
        self.create_status_card(main_container)

        # Main content area
        self.create_main_content(main_container)

        # Update initial status
        self.update_config_status()

    def create_header(self, parent):
        """Create modern header with title and subtitle"""
        header_frame = ttk.Frame(parent, style="Modern.TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 30))
        header_frame.columnconfigure(0, weight=1)

        # Title with icon
        title_frame = ttk.Frame(header_frame, style="Modern.TFrame")
        title_frame.grid(row=0, column=0)

        title_label = ttk.Label(
            title_frame, text="⚡ TorrentToolkit", style="Title.TLabel"
        )
        title_label.grid(row=0, column=0)

        subtitle_label = ttk.Label(
            header_frame, text="qBittorrent Toolkit", style="Subtitle.TLabel"
        )
        subtitle_label.grid(row=1, column=0, pady=(5, 0))

    def create_status_card(self, parent):
        """Create status card with configuration info"""
        status_card = ttk.Frame(parent, style="Card.TFrame", padding="25")
        status_card.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 25))
        status_card.columnconfigure(1, weight=1)

        # Status header
        status_header = ttk.Label(
            status_card, text="🔧 Configuration Status", style="Heading.TLabel"
        )
        status_header.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))

        # Status content frame
        status_content = ttk.Frame(status_card, style="Card.TFrame")
        status_content.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        status_content.columnconfigure(1, weight=1)

        self.config_status_label = ttk.Label(
            status_content, text="", style="Status.TLabel"
        )
        self.config_status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Quick config button
        self.quick_config_btn = ttk.Button(
            status_content,
            text="⚙️ Configure",
            command=self.edit_env_config,
            style="Secondary.TButton",
        )
        self.quick_config_btn.grid(row=0, column=1, sticky=tk.E, padx=(20, 0))

    def create_main_content(self, parent):
        """Create main content area with action cards"""
        content_frame = ttk.Frame(parent, style="Modern.TFrame")
        content_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Left column - Main actions
        left_column = ttk.Frame(content_frame, style="Modern.TFrame")
        left_column.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        left_column.columnconfigure(0, weight=1)

        # Right column - Secondary actions
        right_column = ttk.Frame(content_frame, style="Modern.TFrame")
        right_column.grid(
            row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(15, 0)
        )
        right_column.columnconfigure(0, weight=1)

        # Create action cards
        self.create_action_cards(left_column, right_column)

        # Progress and status at bottom
        self.create_progress_section(parent)

    def create_action_cards(self, left_col, right_col):
        """Create modern action cards"""
        # Main actions (left column)
        main_actions_card = ttk.Frame(left_col, style="Card.TFrame", padding="25")
        main_actions_card.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 20))
        main_actions_card.columnconfigure(0, weight=1)

        # Card header
        ttk.Label(
            main_actions_card, text="🚀 Main Actions", style="Heading.TLabel"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 20))

        # Add Popular Trackers button
        self.add_trackers_btn = ttk.Button(
            main_actions_card,
            text="🔗 Add Popular Trackers",
            command=self.run_add_trackers,
            style="Primary.TButton",
        )
        self.add_trackers_btn.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Description
        ttk.Label(
            main_actions_card,
            text="Enhance your torrents with the best tracker lists",
            style="Status.TLabel",
        ).grid(row=2, column=0, sticky=tk.W, pady=(0, 25))

        # Remove Orphaned button
        self.remove_orphaned_btn = ttk.Button(
            main_actions_card,
            text="🧹 Clean Orphaned Files",
            command=self.run_remove_orphaned,
            style="Warning.TButton",
        )
        self.remove_orphaned_btn.grid(
            row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15)
        )

        # Description
        ttk.Label(
            main_actions_card,
            text="Remove files no longer tracked by qBittorrent",
            style="Status.TLabel",
        ).grid(row=4, column=0, sticky=tk.W)

        # Secondary actions (right column)
        secondary_actions_card = ttk.Frame(right_col, style="Card.TFrame", padding="25")
        secondary_actions_card.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 20)
        )
        secondary_actions_card.columnconfigure(0, weight=1)

        # Card header
        ttk.Label(
            secondary_actions_card, text="📊 Reports & Tools", style="Heading.TLabel"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 20))

        # Generate Report button
        self.generate_report_btn = ttk.Button(
            secondary_actions_card,
            text="� Generate Report",
            command=self.run_generate_report,
            style="Success.TButton",
        )
        self.generate_report_btn.grid(
            row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15)
        )

        # Description
        ttk.Label(
            secondary_actions_card,
            text="Create detailed HTML analytics report",
            style="Status.TLabel",
        ).grid(row=2, column=0, sticky=tk.W, pady=(0, 25))

        # Storage Chart button
        self.storage_chart_btn = ttk.Button(
            secondary_actions_card,
            text="📊 Storage Chart",
            command=self.show_storage_chart,
            style="Success.TButton",
        )
        self.storage_chart_btn.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # Description
        ttk.Label(
            secondary_actions_card,
            text="View storage usage by category",
            style="Status.TLabel",
        ).grid(row=4, column=0, sticky=tk.W)

    def create_progress_section(self, parent):
        """Create progress bar and status section with GitHub link"""
        progress_frame = ttk.Frame(parent, style="Modern.TFrame")
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(25, 0))
        progress_frame.columnconfigure(0, weight=1)

        # Progress bar
        self.progress = ttk.Progressbar(
            progress_frame, mode="indeterminate", style="Modern.Horizontal.TProgressbar"
        )
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Status label
        self.status_label = ttk.Label(
            progress_frame, text="Ready", style="Footer.TLabel"
        )
        self.status_label.grid(row=1, column=0, pady=(0, 15))

        # GitHub link at bottom
        github_frame = ttk.Frame(progress_frame, style="Modern.TFrame")
        github_frame.grid(row=2, column=0, pady=(10, 0))

        github_link = ttk.Label(
            github_frame,
            text="🐙 View on GitHub",
            style="Footer.TLabel",
            cursor="hand2",
        )
        github_link.grid(row=0, column=0)
        github_link.bind("<Button-1>", lambda e: self.open_github())

    def update_config_status(self):
        """Update the configuration status display with modern styling"""
        qb_url = os.getenv("QB_URL")
        qb_user = os.getenv("QB_USER", "admin")
        qb_pass = os.getenv("QB_PASS")
        completed_folder = os.getenv("COMPLETED_FOLDER")

        # Create status indicators with emojis and colors
        url_status = "🟢" if qb_url and qb_url != "http://localhost:8080" else "🟡"
        pass_status = "🟢" if qb_pass else "🔴"
        folder_status = "🟢" if completed_folder else "🔴"

        status_lines = [
            f"{url_status} qBittorrent URL: {qb_url or 'Not configured'}",
            f"👤 Username: {qb_user or 'Not set'}",
            f"{pass_status} Password: {'Configured' if qb_pass else 'Not set'}",
            f"{folder_status} Download Folder: {completed_folder or 'Not set'}",
        ]

        status_text = "\n".join(status_lines)
        self.config_status_label.config(text=status_text)

        # Enable/disable buttons based on config with modern state management
        config_valid = bool(qb_url and qb_url != "http://localhost:8080")

        # Update button states
        if hasattr(self, "add_trackers_btn"):
            self.add_trackers_btn.config(
                state=tk.NORMAL if config_valid else tk.DISABLED
            )
        if hasattr(self, "remove_orphaned_btn"):
            self.remove_orphaned_btn.config(
                state=tk.NORMAL if (config_valid and completed_folder) else tk.DISABLED
            )
        if hasattr(self, "generate_report_btn"):
            self.generate_report_btn.config(
                state=tk.NORMAL if config_valid else tk.DISABLED
            )
        if hasattr(self, "storage_chart_btn"):
            self.storage_chart_btn.config(
                state=tk.NORMAL if config_valid else tk.DISABLED
            )

    def edit_env_config(self):
        """Open a modern dialog to edit environment variables"""
        config_window = tk.Toplevel(self.root)
        config_window.title("TorrentToolkit Configuration")
        config_window.geometry("500x450")
        config_window.resizable(False, False)
        config_window.configure(bg=self.colors["background"])

        # Center the config window
        config_window.transient(self.root)
        config_window.grab_set()

        # Center the window on screen
        config_window.update_idletasks()
        width = config_window.winfo_width()
        height = config_window.winfo_height()
        x = (config_window.winfo_screenwidth() // 2) - (width // 2)
        y = (config_window.winfo_screenheight() // 2) - (height // 2)
        config_window.geometry(f"{width}x{height}+{x}+{y}")

        # Main frame with modern styling
        main_frame = ttk.Frame(config_window, style="Modern.TFrame", padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        config_window.columnconfigure(0, weight=1)
        config_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Modern header
        header_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        header_frame.grid(
            row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 25)
        )
        header_frame.columnconfigure(0, weight=1)

        ttk.Label(
            header_frame, text="⚙️ Configuration Settings", style="Title.TLabel"
        ).grid(row=0, column=0, pady=(0, 5))

        ttk.Label(
            header_frame,
            text="Configure your qBittorrent connection and preferences",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0)

        # Variables with modern styling
        vars_data = [
            (
                "QB_URL",
                "🌐 qBittorrent URL",
                os.getenv("QB_URL", "http://localhost:8080"),
            ),
            ("QB_USER", "👤 Username", os.getenv("QB_USER", "admin")),
            ("QB_PASS", "🔐 Password", os.getenv("QB_PASS", "")),
            (
                "COMPLETED_FOLDER",
                "📁 Downloads Folder",
                os.getenv("COMPLETED_FOLDER", ""),
            ),
        ]

        self.config_vars = {}

        # Create input fields with modern styling
        for i, (var_name, label, default_value) in enumerate(vars_data):
            row = i + 1

            # Label
            label_widget = ttk.Label(main_frame, text=label, style="Heading.TLabel")
            label_widget.grid(
                row=row, column=0, sticky=tk.W, pady=(15, 5), padx=(0, 20)
            )

            # Entry field
            if var_name == "QB_PASS":
                entry = ttk.Entry(main_frame, show="*", width=35, font=("Segoe UI", 12))
            else:
                entry = ttk.Entry(main_frame, width=35, font=("Segoe UI", 12))

            entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=(15, 5))
            entry.insert(0, default_value)
            self.config_vars[var_name] = entry

            # Browse button for folder selection
            if var_name == "COMPLETED_FOLDER":
                browse_btn = ttk.Button(
                    main_frame,
                    text="📂",
                    command=lambda: self.browse_folder(entry),
                    style="Secondary.TButton",
                    width=3,
                )
                browse_btn.grid(row=row, column=2, padx=(10, 0), pady=(15, 5))

        # Modern buttons frame
        buttons_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        buttons_frame.grid(row=len(vars_data) + 2, column=0, columnspan=3, pady=(30, 0))

        save_btn = ttk.Button(
            buttons_frame,
            text="💾 Save Configuration",
            command=lambda: self.save_config(config_window),
            style="Primary.TButton",
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 15))

        cancel_btn = ttk.Button(
            buttons_frame,
            text="❌ Cancel",
            command=config_window.destroy,
            style="Secondary.TButton",
        )
        cancel_btn.pack(side=tk.LEFT)

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

            # Reload environment variables to ensure they're up to date
            load_dotenv(override=True)

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
        """Run remove orphaned torrents tool with GUI"""
        try:
            # Get orphaned torrents data
            self.set_status("Scanning for orphaned torrents...")
            self.show_progress(True)

            # Run in thread to prevent GUI freezing
            def get_data():
                return get_orphaned_torrents_data()

            # Use threading to get data
            import threading

            result = {}

            def worker():
                result["data"] = get_data()

            thread = threading.Thread(target=worker)
            thread.start()
            thread.join()

            data = result["data"]
            self.show_progress(False)

            if "error" in data:
                messagebox.showerror("Error", data["error"])
                self.set_status("Ready")
                return

            if not data["orphans"]:
                messagebox.showinfo("No Orphans", "No orphaned files found!")
                self.set_status("Ready")
                return

            # Show selection dialog
            self.show_orphan_selection_dialog(data)

        except Exception as e:
            self.show_progress(False)
            messagebox.showerror("Error", f"Failed to scan for orphaned torrents: {e}")
            self.set_status("Ready")

    def show_orphan_selection_dialog(self, data):
        """Show modern dialog for selecting which orphaned torrents to delete"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Clean Orphaned Files - TorrentToolkit")
        dialog.geometry("900x600")
        dialog.resizable(True, True)
        dialog.configure(bg=self.colors["background"])
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog on screen
        dialog.update_idletasks()
        width = 900
        height = 600
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        # Main frame with modern styling
        main_frame = ttk.Frame(dialog, style="Modern.TFrame", padding="25")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Modern header
        header_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)

        ttk.Label(
            header_frame, text="🧹 Clean Orphaned Files", style="Title.TLabel"
        ).grid(row=0, column=0, pady=(0, 5))

        ttk.Label(
            header_frame,
            text="Select files to remove from your system",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0)

        # Info card
        info_card = ttk.Frame(main_frame, style="Card.TFrame", padding="15")
        info_card.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        info_card.columnconfigure(1, weight=1)

        ttk.Label(info_card, text="ℹ️", style="Title.TLabel").grid(
            row=0, column=0, padx=(0, 15)
        )

        info_text = (
            "Files shown below are no longer tracked by qBittorrent. "
            "ISO files are unchecked by default for safety. "
            "Double-click items to toggle selection."
        )

        ttk.Label(
            info_card, text=info_text, style="Status.TLabel", wraplength=700
        ).grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Create treeview for file selection
        tree_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Treeview with checkboxes
        tree = ttk.Treeview(
            tree_frame, columns=("Category", "Size"), show="tree headings"
        )
        tree.heading("#0", text="File Name")
        tree.heading("Category", text="Category")
        tree.heading("Size", text="Size")
        tree.column("#0", width=400)
        tree.column("Category", width=100)
        tree.column("Size", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Store checkbox states
        checkbox_states = {}

        # Add ISO files (unchecked by default)
        if data["iso_orphans"]:
            iso_parent = tree.insert(
                "",
                "end",
                text="📀 ISO Files (excluded by default)",
                values=("", ""),
                tags=("category",),
            )
            tree.set(iso_parent, "Category", "ISOs")
            for orphan, category in data["iso_orphans"]:
                file_path = os.path.join(data["completed_folder"], category, orphan)
                size = self.get_file_size(file_path)
                item_id = tree.insert(
                    iso_parent,
                    "end",
                    text=f"☐ {orphan}",
                    values=(category, size),
                    tags=("unchecked",),
                )
                checkbox_states[item_id] = False

        # Add deletable files (checked by default)
        if data["deletable_orphans"]:
            deletable_parent = tree.insert(
                "",
                "end",
                text="🗑️ Files for Deletion",
                values=("", ""),
                tags=("category",),
            )
            for orphan, category in data["deletable_orphans"]:
                file_path = os.path.join(
                    data["completed_folder"],
                    category if category != "root" else "",
                    orphan,
                )
                size = self.get_file_size(file_path)
                item_id = tree.insert(
                    deletable_parent,
                    "end",
                    text=f"☑ {orphan}",
                    values=(category, size),
                    tags=("checked",),
                )
                checkbox_states[item_id] = True

        # Expand all
        for item in tree.get_children():
            tree.item(item, open=True)

        # Configure tags
        tree.tag_configure("category", background="#e8f4fd")
        tree.tag_configure("checked", foreground="#2d5a2d")
        tree.tag_configure("unchecked", foreground="#666666")

        # Checkbox toggle function
        def toggle_checkbox(event):
            item = tree.selection()[0] if tree.selection() else None
            if item and item in checkbox_states:
                # Toggle state
                checkbox_states[item] = not checkbox_states[item]
                current_text = tree.item(item, "text")

                if checkbox_states[item]:
                    # Check the box
                    new_text = current_text.replace("☐", "☑")
                    tree.item(item, text=new_text, tags=("checked",))
                else:
                    # Uncheck the box
                    new_text = current_text.replace("☑", "☐")
                    tree.item(item, text=new_text, tags=("unchecked",))

        tree.bind("<Double-1>", toggle_checkbox)
        tree.bind("<Return>", toggle_checkbox)
        tree.bind("<space>", toggle_checkbox)

        # Define selection functions
        def select_all():
            for item_id in checkbox_states:
                if not checkbox_states[item_id]:
                    checkbox_states[item_id] = True
                    current_text = tree.item(item_id, "text")
                    new_text = current_text.replace("☐", "☑")
                    tree.item(item_id, text=new_text, tags=("checked",))

        def deselect_all():
            for item_id in checkbox_states:
                if checkbox_states[item_id]:
                    checkbox_states[item_id] = False
                    current_text = tree.item(item_id, "text")
                    new_text = current_text.replace("☑", "☐")
                    tree.item(item_id, text=new_text, tags=("unchecked",))

        # Modern buttons frame
        button_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        button_frame.grid(row=3, column=0, pady=(20, 0), sticky=(tk.W, tk.E))
        button_frame.columnconfigure(2, weight=1)

        # Select/Deselect all buttons with modern styling
        ttk.Button(
            button_frame,
            text="✅ Select All",
            command=select_all,
            style="Secondary.TButton",
        ).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="❌ Deselect All",
            command=deselect_all,
            style="Secondary.TButton",
        ).grid(row=0, column=1, padx=(0, 20))

        # Action buttons on the right
        action_frame = ttk.Frame(button_frame, style="Modern.TFrame")
        action_frame.grid(row=0, column=3, sticky=tk.E)

        def delete_selected():
            # Get selected files
            selected_files = []
            for item_id, is_checked in checkbox_states.items():
                if is_checked:
                    # Get file info from tree
                    text = tree.item(item_id, "text")
                    filename = text.replace("☑ ", "").replace("☐ ", "")
                    category = tree.item(item_id, "values")[0]
                    selected_files.append((filename, category))

            if not selected_files:
                messagebox.showwarning(
                    "No Selection", "Please select at least one file to delete."
                )
                return

            # Confirm deletion
            result = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to permanently delete {len(selected_files)} selected files?\n\n"
                f"This action cannot be undone!",
                icon="warning",
            )

            if result:
                dialog.destroy()
                self.perform_deletion(selected_files, data["completed_folder"])

        def cancel():
            dialog.destroy()
            self.set_status("Ready")

        # Modern action buttons
        ttk.Button(
            action_frame,
            text="🗑️ Delete Selected",
            command=delete_selected,
            style="Warning.TButton",
        ).pack(side=tk.LEFT, padx=(0, 15))

        ttk.Button(
            action_frame, text="✖️ Cancel", command=cancel, style="Secondary.TButton"
        ).pack(side=tk.LEFT)

        # Modern summary section
        summary_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        summary_frame.grid(row=4, column=0, pady=(20, 0))

        summary_text = f"📁 Found {len(data['orphans'])} orphaned files"
        if data["iso_orphans"]:
            summary_text += f" • {len(data['iso_orphans'])} ISOs excluded by default"

        ttk.Label(summary_frame, text=summary_text, style="Footer.TLabel").grid(
            row=0, column=0
        )

    def open_github(self):
        """Open the GitHub repository in the default browser"""
        webbrowser.open("https://github.com/Owen-3456/TorrentToolkit")

    def get_file_size(self, file_path):
        """Get human-readable file size"""
        try:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
                # For directories, get total size
                if os.path.isdir(file_path):
                    total_size = 0
                    for dirpath, dirnames, filenames in os.walk(file_path):
                        for filename in filenames:
                            filepath = os.path.join(dirpath, filename)
                            try:
                                total_size += os.path.getsize(filepath)
                            except:
                                continue
                    size = total_size

                # Convert to human readable
                for unit in ["B", "KB", "MB", "GB", "TB"]:
                    if size < 1024.0:
                        return f"{size:.1f} {unit}"
                    size /= 1024.0
                return f"{size:.1f} PB"
            return "Unknown"
        except:
            return "Unknown"

    def perform_deletion(self, selected_files, completed_folder):
        """Perform the actual deletion of selected files"""
        self.set_status("Deleting selected files...")
        self.show_progress(True)

        def delete_worker():
            return delete_selected_files(selected_files, completed_folder)

        # Run deletion in thread
        result = {}

        def worker():
            result["data"] = delete_worker()

        thread = threading.Thread(target=worker)
        thread.start()
        thread.join()

        self.show_progress(False)
        deletion_result = result["data"]

        # Show results
        message = f"Deletion completed!\n\n"
        message += (
            f"✅ Successfully deleted: {deletion_result['deleted_count']} files\n"
        )

        if deletion_result["error_count"] > 0:
            message += f"❌ Errors: {deletion_result['error_count']} files\n\n"
            if deletion_result["error_messages"]:
                message += "Error details:\n" + "\n".join(
                    deletion_result["error_messages"][:5]
                )
                if len(deletion_result["error_messages"]) > 5:
                    message += f"\n... and {len(deletion_result['error_messages']) - 5} more errors"

        if deletion_result["error_count"] == 0:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showwarning("Completed with Errors", message)

        self.set_status("Ready")

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

    def get_torrent_data(self):
        """Get torrent data from qBittorrent for analysis"""
        qb_url = os.getenv("QB_URL")
        qb_user = os.getenv("QB_USER", "admin")
        qb_pass = os.getenv("QB_PASS", "admin")

        if not qb_url:
            return None

        try:
            # Login to qBittorrent Web API
            session = requests.Session()
            login_response = session.post(
                f"{qb_url}/api/v2/auth/login",
                data={"username": qb_user, "password": qb_pass},
            )

            if login_response.status_code != 200:
                return None

            # Get list of torrents from qBittorrent
            torrents_response = session.get(f"{qb_url}/api/v2/torrents/info")
            if torrents_response.status_code != 200:
                return None

            return torrents_response.json()

        except Exception as e:
            print(f"Error getting torrent data: {e}")
            return None

    def calculate_storage_by_category(self, torrents):
        """Calculate storage usage by category"""
        storage_by_category = {}

        for torrent in torrents:
            category = torrent.get("category", "Uncategorized")
            if not category:
                category = "Uncategorized"

            size = torrent.get("size", 0)

            if category in storage_by_category:
                storage_by_category[category] += size
            else:
                storage_by_category[category] = size

        return storage_by_category

    def format_bytes(self, bytes_value):
        """Convert bytes to human readable format"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

    def show_storage_chart(self):
        """Show storage usage chart by category"""
        # Get torrent data
        self.set_status("Fetching torrent data...")
        self.show_progress(True)

        def get_data_and_show_chart():
            torrents = self.get_torrent_data()
            self.show_progress(False)

            if not torrents:
                self.set_status("Ready")
                messagebox.showerror(
                    "Error",
                    "Failed to fetch torrent data. Please check your configuration.",
                )
                return

            storage_by_category = self.calculate_storage_by_category(torrents)

            if not storage_by_category:
                self.set_status("Ready")
                messagebox.showinfo("No Data", "No torrents found.")
                return

            self.display_storage_chart_window(storage_by_category)
            self.set_status("Ready")

        # Run in thread to prevent GUI freezing
        threading.Thread(target=get_data_and_show_chart, daemon=True).start()

    def display_storage_chart_window(self, storage_data):
        """Display the storage chart in a new window"""
        chart_window = tk.Toplevel(self.root)
        chart_window.title("Storage Usage by Category - TorrentToolkit")
        chart_window.geometry("800x600")
        chart_window.configure(bg=self.colors["background"])
        chart_window.transient(self.root)
        chart_window.grab_set()

        # Center the window
        chart_window.update_idletasks()
        width = 800
        height = 600
        x = (chart_window.winfo_screenwidth() // 2) - (width // 2)
        y = (chart_window.winfo_screenheight() // 2) - (height // 2)
        chart_window.geometry(f"{width}x{height}+{x}+{y}")

        # Main frame
        main_frame = ttk.Frame(chart_window, style="Modern.TFrame", padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        chart_window.columnconfigure(0, weight=1)
        chart_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)

        ttk.Label(
            header_frame, text="📊 Storage Usage by Category", style="Title.TLabel"
        ).grid(row=0, column=0, pady=(0, 5))

        total_size = sum(storage_data.values())
        ttk.Label(
            header_frame,
            text=f"Total Storage: {self.format_bytes(total_size)} across {len(storage_data)} categories",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0)

        # Chart frame
        chart_frame = ttk.Frame(main_frame, style="Card.TFrame", padding="15")
        chart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)

        # Create matplotlib figure with dark theme
        plt.style.use("dark_background")
        fig = Figure(figsize=(10, 6), facecolor=self.colors["surface"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors["surface"])

        # Prepare data for chart
        categories = list(storage_data.keys())
        sizes = list(storage_data.values())

        # Convert sizes to GB for better readability
        sizes_gb = [size / (1024**3) for size in sizes]

        # Create colors for bars
        colors = plt.cm.Set3(range(len(categories)))

        # Create bar chart
        bars = ax.bar(categories, sizes_gb, color=colors)

        # Customize chart
        ax.set_xlabel("Category", color=self.colors["text"], fontsize=12)
        ax.set_ylabel("Storage (GB)", color=self.colors["text"], fontsize=12)
        ax.set_title(
            "Storage Usage by Category",
            color=self.colors["text"],
            fontsize=14,
            fontweight="bold",
        )

        # Rotate x-axis labels if there are many categories
        if len(categories) > 5:
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # Add value labels on bars
        for bar, size_gb, size_bytes in zip(bars, sizes_gb, sizes):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + max(sizes_gb) * 0.01,
                f"{self.format_bytes(size_bytes)}",
                ha="center",
                va="bottom",
                color=self.colors["text"],
                fontsize=9,
            )

        # Customize grid and ticks
        ax.grid(True, alpha=0.3, color=self.colors["text_secondary"])
        ax.tick_params(colors=self.colors["text"])

        # Adjust layout
        fig.tight_layout()

        # Embed chart in tkinter
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Button frame
        button_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        button_frame.grid(row=2, column=0, pady=(20, 0))

        ttk.Button(
            button_frame,
            text="Close",
            command=chart_window.destroy,
            style="Secondary.TButton",
        ).pack()


def check_and_create_env_file():
    """Check if .env file exists, create from .env.example if not, and prompt user to edit"""
    env_path = ".env"
    env_example_path = ".env.example"

    # Check if .env file exists
    if not os.path.exists(env_path):
        # Check if .env.example exists
        if os.path.exists(env_example_path):
            try:
                # Copy .env.example to .env
                shutil.copy2(env_example_path, env_path)

                # Show message to user
                result = messagebox.askquestion(
                    "Environment File Created",
                    "A new .env configuration file has been created from .env.example.\n\n"
                    "You need to configure your .env file before using the toolkit.\n\n"
                    "Would you like to edit the configuration now?",
                    icon="info",
                )

                return result == "yes"

            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to create .env file from .env.example:\n{e}\n\n"
                    "Please create the .env file manually.",
                )
                return False
        else:
            messagebox.showerror(
                "Missing Files",
                "Neither .env nor .env.example file found.\n\n"
                "Please ensure .env.example exists or create a .env file manually.",
            )
            return False

    # .env file exists, check if it's properly configured
    load_dotenv()
    qb_url = os.getenv("QB_URL")

    if not qb_url or qb_url == "http://localhost:8080":
        result = messagebox.askquestion(
            "Configuration Check",
            "Your .env file may need configuration updates.\n\n"
            "Would you like to review your settings?",
            icon="question",
        )
        return result == "yes"

    return False


def main():
    """Main entry point for the GUI"""
    # Check and handle .env file before creating GUI
    should_edit_config = check_and_create_env_file()

    # Now load environment variables
    load_dotenv()

    root = tk.Tk()
    app = TorrentToolkitGUI(root)

    # If we need to edit config, show the dialog after GUI is ready
    if should_edit_config:
        root.after(100, app.edit_env_config)  # Small delay to ensure GUI is ready

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
