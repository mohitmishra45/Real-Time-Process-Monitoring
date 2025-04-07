import tkinter as tk
from tkinter import ttk

class Footer:
    def __init__(self, root, app):
        """Initialize the footer with process controls and system alerts"""
        self.app = app
        self.theme = app.theme
        self.root = root
        
        # Create the footer frame directly on the root window
        self.frame = ttk.Frame(root, style="Card.TFrame")
        
        # Force the footer to be at the bottom with explicit pack parameters
        self.frame.pack(side="bottom", fill="x", padx=15, pady=(0, 15))
        
        # Create a container for the footer content
        self.container = ttk.Frame(self.frame, style="Card.TFrame")
        self.container.pack(fill="x", padx=10, pady=10)
        
        # Left side: Process controls
        process_frame = ttk.Frame(self.container, style="Card.TFrame")
        process_frame.pack(side="left", fill="y", padx=(0, 20))
        
        # Process controls title
        process_title = ttk.Label(process_frame, 
                                 text="PROCESS CONTROLS", 
                                 style="Title.TLabel",
                                 font=("Segoe UI", 12, "bold"))
        process_title.pack(anchor="w", pady=(0, 10))
        
        # Process control buttons
        button_frame = ttk.Frame(process_frame, style="Card.TFrame")
        button_frame.pack(fill="x")
        
        # Kill Process button
        kill_btn = ttk.Button(button_frame, 
                             text="Kill Process", 
                             command=self.app.kill_process,
                             style="Danger.TButton")
        kill_btn.pack(side="left", padx=(0, 10))
        
        # Process Details button
        details_btn = ttk.Button(button_frame, 
                                text="Process Details", 
                                command=self.app.show_process_details,
                                style="Accent.TButton")
        details_btn.pack(side="left", padx=(0, 10))
        
        # Export button - make it more prominent
        export_btn = ttk.Button(button_frame, 
                               text="Export CSV", 
                               command=self.app.export_process_list,
                               style="Success.TButton",
                               width=12)  # Make it wider for visibility
        export_btn.pack(side="left")
        
        # Add a tooltip/label to explain the export function
        export_label = ttk.Label(button_frame,
                                text="(Save processes as CSV)",
                                style="Small.TLabel",
                                font=("Segoe UI", 8))
        export_label.pack(side="left", padx=(2, 10))
        
        # Center: System alerts
        alert_frame = ttk.Frame(self.container, style="Card.TFrame")
        alert_frame.pack(side="left", fill="y", expand=True, padx=20)
        
        # Alerts title
        alert_title = ttk.Label(alert_frame, 
                               text="SYSTEM ALERTS", 
                               style="Title.TLabel",
                               font=("Segoe UI", 12, "bold"))
        alert_title.pack(anchor="w", pady=(0, 10))
        
        # Alert thresholds
        threshold_frame = ttk.Frame(alert_frame, style="Card.TFrame")
        threshold_frame.pack(fill="x", pady=(0, 10))
        
        # CPU threshold
        ttk.Label(threshold_frame, text="CPU:", style="TLabel").pack(side="left", padx=(0, 5))
        self.cpu_threshold = ttk.Entry(threshold_frame, width=5)
        self.cpu_threshold.insert(0, "80")
        self.cpu_threshold.pack(side="left", padx=(0, 10))
        
        # Memory threshold
        ttk.Label(threshold_frame, text="Memory:", style="TLabel").pack(side="left", padx=(0, 5))
        self.mem_threshold = ttk.Entry(threshold_frame, width=5)
        self.mem_threshold.insert(0, "80")
        self.mem_threshold.pack(side="left", padx=(0, 10))
        
        # Disk threshold
        ttk.Label(threshold_frame, text="Disk:", style="TLabel").pack(side="left", padx=(0, 5))
        self.disk_threshold = ttk.Entry(threshold_frame, width=5)
        self.disk_threshold.insert(0, "90")
        self.disk_threshold.pack(side="left", padx=(0, 10))
        
        # Apply button
        ttk.Button(threshold_frame, text="Apply",
                   command=self.apply_thresholds,
                   style="Accent.TButton").pack(side="left")
        
        # Right side: Refresh rate
        refresh_frame = ttk.Frame(self.container, style="Card.TFrame")
        refresh_frame.pack(side="right", fill="y", padx=(20, 0))
        
        # Refresh rate title
        refresh_title = ttk.Label(refresh_frame, 
                                 text="REFRESH RATE", 
                                 style="Title.TLabel",
                                 font=("Segoe UI", 12, "bold"))
        refresh_title.pack(anchor="w", pady=(0, 10))
        
        # Refresh rate control
        rate_frame = ttk.Frame(refresh_frame, style="Card.TFrame")
        rate_frame.pack(fill="x")
        
        ttk.Label(rate_frame, text="Update interval (seconds):", style="TLabel").pack(side="left", padx=(0, 10))
        
        self.refresh_rate = ttk.Entry(rate_frame, width=5)
        self.refresh_rate.insert(0, "1")  # Default to 1 second
        self.refresh_rate.pack(side="left")
    
    def apply_thresholds(self):
        """Apply the alert thresholds"""
        try:
            cpu_threshold = int(self.cpu_threshold.get())
            mem_threshold = int(self.mem_threshold.get())
            disk_threshold = int(self.disk_threshold.get())
            self.app.update_alert_thresholds(cpu_threshold, mem_threshold, disk_threshold)
        except ValueError:
            # Error handling is done in the app class
            pass
    
    def get_refresh_rate(self):
        """Get the current refresh rate value"""
        try:
            return int(self.refresh_rate.get())
        except ValueError:
            return 1  # Default to 1 second if invalid value 
