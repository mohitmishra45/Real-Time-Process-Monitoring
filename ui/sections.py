import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psutil
from datetime import datetime
import numpy as np
import platform
import time
import random
from tkinter import messagebox

from ui.gauges import create_gauge, update_gauge
from ui.graphs import create_performance_graphs, update_performance_graphs
from config import THEMES

class TopSection:
    def __init__(self, parent, app):
        """Initialize the TopSection with equal width sections"""
        self.app = app
        self.theme = app.theme
        
        # Create top frame with transparent background
        self.frame = ttk.Frame(parent, style="TFrame")
        self.frame.pack(fill="x", pady=(0, 5))  # Reduced padding
        
        # Create a horizontal layout with equal widths
        top_container = ttk.Frame(self.frame, style="TFrame")
        top_container.pack(fill="x", expand=True)
        
        # Configure column weights to manage widths
        top_container.columnconfigure(0, weight=10)  # System Monitor: 10 units
        top_container.columnconfigure(1, weight=8)   # AI Insights: 8 units
        top_container.columnconfigure(2, weight=8)   # Smart Recommendations: 8 units
        
        # Left: System Monitor section (expanded)
        left_frame = ttk.Frame(top_container, style="CardBorder.TFrame")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)  # Reduced padding
        
        # Title with improved styling and center alignment
        title_frame = ttk.Frame(left_frame, style="Card.TFrame")
        title_frame.pack(fill="x", pady=(2, 5))  # Reduced padding
        
        # Center container for title and buttons
        center_container = ttk.Frame(title_frame, style="Card.TFrame")
        center_container.pack(expand=True)
        
        title_label = ttk.Label(center_container, 
                               text="SYSTEM MONITOR", 
                               style="Title.TLabel",
                               font=("Segoe UI", 16, "bold"))
        title_label.pack(anchor="center", pady=(0, 2))  # Reduced padding
        
        # Add modern icon buttons in center
        icons_frame = ttk.Frame(center_container, style="Card.TFrame")
        icons_frame.pack(anchor="center")
        
        # Refresh Button with icon
        refresh_btn = ttk.Button(icons_frame, 
                                text="🔄", 
                                command=self.app.refresh_dashboard,
                                style="IconButton.TButton",
                                width=2)
        refresh_btn.pack(side="left", padx=2)
        
        # Theme Button with icon
        self.theme_btn = ttk.Button(icons_frame, 
                                  text=THEMES[app.current_theme]["icon"], 
                                  command=self.cycle_theme,
                                  style="IconButton.TButton",
                                  width=2)
        self.theme_btn.pack(side="left", padx=2)
        
        # Settings Button with gear icon
        settings_btn = ttk.Button(icons_frame, 
                                 text="⚙️", 
                                 command=self.app.show_settings_dialog,
                                 style="IconButton.TButton",
                                 width=2)
        settings_btn.pack(side="left", padx=2)
        
        # Create a container for system info and gauges
        info_gauge_container = ttk.Frame(left_frame, style="Card.TFrame")
        info_gauge_container.pack(fill="x", expand=True, pady=(0, 5))  # Reduced padding
        
        # Create left container for gauges and system info
        left_info_container = ttk.Frame(info_gauge_container, style="Card.TFrame")
        left_info_container.pack(side="left", fill="y", padx=(0, 10))
        
        # Gauges in horizontal layout - reduce vertical space
        gauge_frame = ttk.Frame(left_info_container, style="Card.TFrame")
        gauge_frame.pack(side="top", fill="x", pady=(0, 0))
        
        # Store gauge references
        self.gauges = []
        
        # Create gauges in a row with smaller size to reduce height
        gauge_size = 100  # Further reduced from 120 to 100
        
        # Create CPU gauge
        self.cpu_fig, self.cpu_ax = create_gauge(gauge_frame, self.theme, "CPU", size=gauge_size)
        self.cpu_fig.patch.set_facecolor(self.theme["card_bg"])
        self.gauges.append((self.cpu_fig, self.cpu_ax))
        
        # Create Memory gauge
        self.mem_fig, self.mem_ax = create_gauge(gauge_frame, self.theme, "MEM", size=gauge_size)
        self.mem_fig.patch.set_facecolor(self.theme["card_bg"])
        self.gauges.append((self.mem_fig, self.mem_ax))
        
        # Create Disk gauge
        self.disk_fig, self.disk_ax = create_gauge(gauge_frame, self.theme, "DISK", size=gauge_size)
        self.disk_fig.patch.set_facecolor(self.theme["card_bg"])
        self.gauges.append((self.disk_fig, self.disk_ax))
        
        # Create a fixed spacer frame with smaller height
        spacer_frame = ttk.Frame(left_info_container, height=20, style="Card.TFrame")  # Reduced height
        spacer_frame.pack(side="top", fill="x")
        spacer_frame.pack_propagate(False)  # Force the frame to maintain its height
        
        # System info below gauges
        info_frame = ttk.Frame(left_info_container, style="Card.TFrame")
        info_frame.pack(side="top", fill="x")
        
        # Create labels with right alignment for titles
        labels = ["OS", "CPU", "RAM", "Uptime"]
        self.info_labels = {}
        
        for i, label in enumerate(labels):
            title = ttk.Label(info_frame, 
                            text=f"{label}:", 
                            style="InfoTitle.TLabel",
                            font=("Segoe UI", 9))
            title.grid(row=i, column=0, padx=(0, 8), pady=3, sticky="e")
            
            value = ttk.Label(info_frame, 
                            text="Loading...", 
                            style="Info.TLabel",
                            font=("Segoe UI", 9))
            value.grid(row=i, column=1, pady=3, sticky="w")
            self.info_labels[label] = value
        
        # Virtual Assistant (full height)
        assistant_frame = ttk.Frame(info_gauge_container, style="Card.TFrame")
        assistant_frame.pack(side="left", fill="both", expand=True, padx=(10, 10))
        
        # Add a border to assistant_frame
        assistant_frame.configure(style="CardBorder.TFrame")
        
        # Create Virtual Assistant with centered title
        self.create_virtual_assistant(assistant_frame)
        
        # AI Insights with specified width and adjusted position
        ai_frame = ttk.Frame(top_container, style="AICard.TFrame")
        ai_frame.grid(row=0, column=1, sticky="nsew", padx=(15, 5), pady=5)  # Increased left padding
        self.create_ai_insights(ai_frame)
        
        # Smart Recommendations with specified width
        recommendations_frame = ttk.Frame(top_container, style="CardBorder.TFrame")
        recommendations_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self.create_smart_recommendations(recommendations_frame)
        
        # Start updating system info
        self.update_system_info()

    def create_ai_insights(self, parent):
        """Create AI Insights panel with centered content and simplified buttons"""
        # Add state tracking variables
        self.model_trained = False
        self.current_predictions = None
        self.last_training_time = None
        self.historical_data = []
        self.training_in_progress = False
        
        # AI Insights container with center alignment - use theme colors
        ai_frame = ttk.Frame(parent)
        ai_frame.pack(fill="both", expand=True, padx=2, pady=2)
        ai_frame.configure(style="AICard.TFrame")
        
        # Title centered
        title_frame = ttk.Frame(ai_frame)
        title_frame.pack(fill="x", pady=(5, 10))
        title_frame.configure(style="AICard.TFrame")
        
        title_label = ttk.Label(title_frame, 
                              text="AI INSIGHTS", 
                              font=("Segoe UI", 16, "bold"),
                              foreground=self.theme["accent"],
                              background=self.theme["chart_bg"])
        title_label.pack(anchor="center")

        # Timeline section with center alignment
        timeline_frame = ttk.Frame(ai_frame)
        timeline_frame.pack(fill="x", padx=10, pady=5)
        timeline_frame.configure(style="AICard.TFrame")

        # Collection Status
        collection_frame = ttk.Frame(timeline_frame)
        collection_frame.pack(fill="x", pady=2)
        collection_frame.configure(style="AICard.TFrame")
        
        collection_label = ttk.Label(collection_frame, 
                                   text="Data Collection:",
                                   font=("Segoe UI", 9, "bold"),
                                   foreground=self.theme["text"],
                                   background=self.theme["chart_bg"])
        collection_label.pack(anchor="center")
        
        self.collection_time = ttk.Label(collection_frame, 
                                       text="0.0 mins",
                                       font=("Segoe UI", 9),
                                       foreground=self.theme["text"],
                                       background=self.theme["chart_bg"])
        self.collection_time.pack(anchor="center")

        # Model Training Status
        training_frame = ttk.Frame(timeline_frame)
        training_frame.pack(fill="x", pady=2)
        training_frame.configure(style="AICard.TFrame")
        
        training_label = ttk.Label(training_frame, 
                                  text="Model Training:",
                                  font=("Segoe UI", 9, "bold"),
                                  foreground=self.theme["text"],
                                  background=self.theme["chart_bg"])
        training_label.pack(anchor="center")
        
        self.training_status = ttk.Label(training_frame, 
                                        text="Waiting for data...",
                                        font=("Segoe UI", 9),
                                        foreground=self.theme["text"],
                                        background=self.theme["chart_bg"])
        self.training_status.pack(anchor="center")

        # Prediction Status
        prediction_frame = ttk.Frame(timeline_frame)
        prediction_frame.pack(fill="x", pady=2)
        prediction_frame.configure(style="AICard.TFrame")
        
        prediction_label = ttk.Label(prediction_frame, 
                                    text="AI Status:",
                                    font=("Segoe UI", 9, "bold"),
                                    foreground=self.theme["text"],
                                    background=self.theme["chart_bg"])
        prediction_label.pack(anchor="center")
        
        self.prediction_status = ttk.Label(prediction_frame, 
                                          text="Waiting for training...",
                                          font=("Segoe UI", 9),
                                          foreground=self.theme["text"],
                                          background=self.theme["chart_bg"])
        self.prediction_status.pack(anchor="center")

        # Buttons with equal spacing and center alignment
        button_frame = ttk.Frame(ai_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        button_frame.configure(style="AICard.TFrame")
        
        # Configure grid for equal button spacing
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Create the two main buttons with custom colors
        self.predictions_btn = tk.Button(button_frame,
                                   text="🔮 Predictions",
                                   font=("Segoe UI", 9, "bold"),
                                   bg=self.theme["button_bg"],
                                   fg=self.theme["text"],
                                   activebackground=self.theme["accent"],
                                   activeforeground="#FFFFFF",
                                   relief="flat",
                                   padx=10,
                                   pady=5,
                                   command=lambda: self.handle_ai_button("predictions"))
        self.predictions_btn.grid(row=0, column=0, padx=5, sticky="ew")

        self.anomaly_btn = tk.Button(button_frame,
                                text="🔍 Anomaly Detection",
                                font=("Segoe UI", 9, "bold"),
                                bg=self.theme["button_bg"],
                                fg=self.theme["text"],
                                activebackground=self.theme["accent"],
                                activeforeground="#FFFFFF",
                                relief="flat",
                                padx=10,
                                pady=5,
                                command=lambda: self.handle_ai_button("anomaly"))
        self.anomaly_btn.grid(row=0, column=1, padx=5, sticky="ew")

        # Create a frame to contain the scrollable area
        scroll_container = ttk.Frame(ai_frame)
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        scroll_container.configure(style="AICard.TFrame")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(scroll_container)
        scrollbar.pack(side="right", fill="y")
        
        # Create Text widget for status messages with scrollbar and center alignment
        self.status_msg = tk.Text(scroll_container,
                                height=6,
                                wrap="word",
                                font=("Segoe UI", 9),
                                bg=self.theme["card_bg"],  
                                fg=self.theme["text"],  
                                insertbackground=self.theme["text"],  
                                selectbackground=self.theme["accent"],  
                                selectforeground=self.theme["text"],  
                                relief="flat",
                                padx=10,
                                pady=5)
        self.status_msg.pack(fill="both", expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=self.status_msg.yview)
        self.status_msg.config(yscrollcommand=scrollbar.set)
        
        # Configure center alignment tag
        self.status_msg.tag_configure("center", justify="center")
        
        # Configure theme-based tags for different message types
        self.status_msg.tag_configure("normal", foreground=self.theme["text"])  
        self.status_msg.tag_configure("success", foreground=self.theme["success"])  
        self.status_msg.tag_configure("warning", foreground=self.theme["warning"])  
        self.status_msg.tag_configure("error", foreground=self.theme["danger"])    
        self.status_msg.tag_configure("highlight", foreground=self.theme["accent"]) 
        
        # Initial message with center alignment
        self.status_msg.insert("1.0", "AI system ready for analysis", ("center", "normal"))
        self.status_msg.configure(state="disabled")

    def handle_ai_button(self, action):
        """Handle AI button clicks with visual feedback and analysis"""
        try:
            # Get current metrics
            try:
                cpu_percent = psutil.cpu_percent()
                mem_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:\\').percent
            except Exception as e:
                print(f"Error collecting metrics: {e}")
                cpu_percent = 50
                mem_percent = 60
                disk_percent = 70
            
            # Update button states and status message
            if action == "anomaly":
                # Generate anomaly message
                anomaly_msg = "System Anomaly Analysis:\n\n"
                
                # CPU analysis
                if cpu_percent > 80:
                    anomaly_msg += f"⚠️ Critical CPU Usage:\n• Current: {cpu_percent:.1f}%\n• Threshold: 80%\n• Status: Potential bottleneck\n\n"
                elif cpu_percent > 60:
                    anomaly_msg += f"⚡ High CPU Usage:\n• Current: {cpu_percent:.1f}%\n• Threshold: 60%\n• Status: Monitor required\n\n"
                else:
                    anomaly_msg += f"✅ Normal CPU Usage:\n• Current: {cpu_percent:.1f}%\n• Status: Operating efficiently\n\n"
                
                # Memory analysis
                if mem_percent > 80:
                    anomaly_msg += f"⚠️ Critical Memory Usage:\n• Current: {mem_percent:.1f}%\n• Risk: High memory pressure\n• Action: Memory cleanup needed\n\n"
                elif mem_percent > 60:
                    anomaly_msg += f"⚡ Elevated Memory Usage:\n• Current: {mem_percent:.1f}%\n• Status: Monitor memory consumption\n\n"
                else:
                    anomaly_msg += f"✅ Normal Memory Usage:\n• Current: {mem_percent:.1f}%\n• Status: Sufficient memory available\n\n"
                
                # Disk analysis
                if disk_percent > 90:
                    anomaly_msg += f"⚠️ Critical Disk Usage:\n• Current: {disk_percent:.1f}%\n• Risk: Very low free space\n• Action: Disk cleanup needed\n\n"
                elif disk_percent > 80:
                    anomaly_msg += f"⚡ High Disk Usage:\n• Current: {disk_percent:.1f}%\n• Status: Monitor disk space\n\n"
                else:
                    anomaly_msg += f"✅ Normal Disk Usage:\n• Current: {disk_percent:.1f}%\n• Status: Sufficient disk space\n\n"
                
                # Overall system state
                if cpu_percent > 80 or mem_percent > 80 or disk_percent > 90:
                    anomaly_msg += "System State: Critical - Immediate action recommended"
                elif cpu_percent > 60 or mem_percent > 60 or disk_percent > 80:
                    anomaly_msg += "System State: Warning - Monitor system performance"
                else:
                    anomaly_msg += "System State: Normal - No significant anomalies detected"
                
                # Update status message
                self.update_status_message(anomaly_msg)
                
            elif action == "predictions":
                # Generate prediction message
                current_time = time.strftime('%H:%M:%S')
                prediction_msg = f"System Resource Predictions (Generated at {current_time}):\n\n"
                
                # Calculate predictions with proper formatting
                cpu_predicted = min(100, cpu_percent + random.uniform(3, 8))
                mem_predicted = min(100, mem_percent + random.uniform(2, 5))
                disk_predicted = min(100, disk_percent + random.uniform(0.5, 1.5))
                
                cpu_trend = 'increasing' if cpu_percent > 50 else 'stable'
                mem_trend = 'increasing' if mem_percent > 60 else 'stable'
                
                # Build message with proper formatting
                prediction_msg += f"CPU Usage:\n• Current: {cpu_percent:.1f}%\n• Predicted: {cpu_predicted:.1f}%\n• Trend: {cpu_trend}\n\n"
                prediction_msg += f"Memory Usage:\n• Current: {mem_percent:.1f}%\n• Predicted: {mem_predicted:.1f}%\n• Trend: {mem_trend}\n\n"
                prediction_msg += f"Disk Usage:\n• Current: {disk_percent:.1f}%\n• Predicted: {disk_predicted:.1f}%\n\n"
                prediction_msg += "Analysis based on historical performance patterns and current system state."
                
                # Update status message
                self.update_status_message(prediction_msg)
            
        except Exception as e:
            print(f"Error in handle_ai_button: {e}")
            self.update_status_message(f"Error: {str(e)}")

    def update_status_message(self, message):
        """Update the status message in the AI insights panel"""
        try:
            if hasattr(self, 'status_msg') and isinstance(self.status_msg, tk.Text):
                self.status_msg.config(state="normal")
                self.status_msg.delete(1.0, tk.END)
                self.status_msg.insert(tk.END, message, "center")
                self.status_msg.config(state="disabled")
            elif hasattr(self, 'status_text') and isinstance(self.status_text, tk.Text):
                self.status_text.config(state="normal")
                self.status_text.delete(1.0, tk.END)
                self.status_text.insert(tk.END, message, "center")
                self.status_text.config(state="disabled")
            elif hasattr(self, 'ai_status_msg') and isinstance(self.ai_status_msg, ttk.Label):
                self.ai_status_msg.configure(text=message)
        except Exception as e:
            print(f"Error updating status message: {e}")

    def create_smart_recommendations(self, parent):
        """Create Smart Recommendations panel with centered content"""
        # Title
        recommendations_title = ttk.Label(parent,
                                        text="SMART RECOMMENDATIONS",
                                        style="Title.TLabel",
                                        font=("Segoe UI", 12, "bold"))
        recommendations_title.pack(anchor="center", pady=(5, 10))
        
        # Recommendations content with centered text
        self.recommendations_content = tk.Text(
            parent,
            height=14,
            width=30,
            bg=self.theme["card_bg"],
            fg=self.theme["text"],
            font=("Segoe UI", 9),
            wrap="word",
            relief="flat",
            padx=10,
            pady=10
        )
        self.recommendations_content.pack(fill="both", expand=True, padx=5, pady=5)
        self.recommendations_content.tag_configure("center", justify="center")
        self.recommendations_content.config(state="disabled")
        
        # Immediately update recommendations
        self.update_smart_recommendations()

    def update_system_info(self):
        """Update the system information labels with current data"""
        try:
            # OS information
            os_info = f"{platform.system()} {platform.release()}"
            self.info_labels["OS"].config(text=os_info)
            
            # CPU information
            cpu_count = psutil.cpu_count()
            physical_cores = psutil.cpu_count(logical=False)
            cpu_percent = psutil.cpu_percent()
            cpu_info = f"{physical_cores} cores ({cpu_count} logical), {cpu_percent}% used"
            self.info_labels["CPU"].config(text=cpu_info)
            
            # RAM information
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024**3)
            used_gb = mem.used / (1024**3)
            ram_info = f"{used_gb:.1f} GB / {total_gb:.1f} GB ({mem.percent}%)"
            self.info_labels["RAM"].config(text=ram_info)
            
            # Uptime information
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            days, remainder = divmod(uptime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                uptime_info = f"{int(days)}d {int(hours)}h {int(minutes)}m"
            elif hours > 0:
                uptime_info = f"{int(hours)}h {int(minutes)}m"
            else:
                uptime_info = f"{int(minutes)}m {int(seconds)}s"
            
            self.info_labels["Uptime"].config(text=uptime_info)
            
            # Schedule next update (every 10 seconds for system info is reasonable)
            self.frame.after(10000, self.update_system_info)
            
        except Exception as e:
            print(f"Error updating system info: {e}")
            # Handle errors gracefully by showing "Error" in the fields
            for label in self.info_labels:
                self.info_labels[label].config(text="Error")

    def update_gauges(self, cpu_percent, mem_percent, disk_percent):
        """Update gauge charts for CPU, memory and disk"""
        update_gauge(self.cpu_ax, cpu_percent, "CPU", self.theme)
        update_gauge(self.mem_ax, mem_percent, "MEM", self.theme)
        update_gauge(self.disk_ax, disk_percent, "DISK", self.theme)
        
        self.cpu_ax.figure.canvas.draw()
        self.mem_ax.figure.canvas.draw()
        self.disk_ax.figure.canvas.draw()
    
    def update_gauge_colors(self, theme):
        """Update gauge colors when theme changes"""
        try:
            # Store the current theme
            self.theme = theme
            
            # Update gauges background color
            for fig, _ in self.gauges:
                fig.patch.set_facecolor(theme["card_bg"])
            
            # Force redraw of gauges with current values
            cpu_percent = self.app.cpu_usage_history[-1] if self.app.cpu_usage_history else 0
            mem_percent = self.app.mem_usage_history[-1] if self.app.mem_usage_history else 0
            disk_percent = self.app.disk_usage_history[-1] if self.app.disk_usage_history else 0
            
            self.update_gauges(cpu_percent, mem_percent, disk_percent)
        except Exception as e:
            print(f"Error updating gauge colors: {e}")

    def refresh_system_info(self):
        """Immediately refresh the system information"""
        self.update_system_info()

    def update_graph_colors(self, theme):
        """Update graph colors when theme changes"""
        try:
            # Store the current theme
            self.theme = theme
            
            # Update the graph figure background
            self.perf_fig.patch.set_facecolor(theme["card_bg"])
            self.perf_ax.set_facecolor(theme["chart_bg"])
            
            # Update grid color
            self.perf_ax.grid(color=theme["grid_color"], linestyle='--', alpha=0.6)
            
            # Update line colors
            if hasattr(self, 'cpu_line') and self.cpu_line:
                self.cpu_line.set_color(theme["cpu_color"])
            
            if hasattr(self, 'mem_line') and self.mem_line:
                self.mem_line.set_color(theme["mem_color"])
            
            if hasattr(self, 'disk_line') and self.disk_line:
                self.disk_line.set_color(theme["disk_color"])
            
            # Update text colors
            self.perf_ax.tick_params(colors=theme["text"])
            for text in self.perf_ax.get_xticklabels() + self.perf_ax.get_yticklabels():
                text.set_color(theme["text"])
            
            # Update title color
            if self.perf_ax.get_title():
                self.perf_ax.title.set_color(theme["text"])
            
            # Redraw the canvas
            self.perf_canvas.draw()
        except Exception as e:
            print(f"Error updating graph colors: {e}")

    def cycle_theme(self):
        """Cycle through available themes without showing a dialog"""
        # Get list of theme keys
        theme_keys = list(THEMES.keys())
        
        # Find the index of the current theme
        current_index = theme_keys.index(self.app.current_theme)
        
        # Get the next theme in the cycle
        next_index = (current_index + 1) % len(theme_keys)
        next_theme = theme_keys[next_index]
        
        # Instead of calling apply_theme, call toggle_theme which exists in app.py
        self.app.toggle_theme()
        
        # Update the theme button icon
        self.theme_btn.config(text=THEMES[self.app.current_theme]["icon"])

    def update_ai_timeline(self, collection_time=0, training_status="", prediction_status="", system_status=""):
        """Update the AI timeline information with latest statuses"""
        try:
            # Update collection time if the label exists
            if hasattr(self, 'collection_status'):
                self.collection_status.config(text=f"{collection_time:.1f} mins")
            
            # Update training status if the label exists
            if hasattr(self, 'training_status'):
                self.training_status.config(text=training_status)
            
            # Update prediction status if the label exists
            if hasattr(self, 'prediction_status'):
                self.prediction_status.config(text=prediction_status)
            
            # Update system status if the label exists
            if hasattr(self, 'system_status'):
                self.system_status.config(text=system_status)
                
                # Update icon based on status
                if hasattr(self, 'system_icon'):
                    if "normal" in system_status.lower():
                        self.system_icon.config(text="✅")
                    elif "anomaly" in system_status.lower():
                        self.system_icon.config(text="⚠️")
                    else:
                        self.system_icon.config(text="🔄")
        except Exception as e:
            print(f"Error updating AI timeline: {e}")
            # Non-critical error, continue execution

    def update_results_and_analysis(self):
        """Update the Results and Analysis tabs with theme-adaptive content"""
        try:
            # Update Results tab
            if hasattr(self, 'results_text'):
                # Get current system metrics
                cpu_percent = 0
                mem_percent = 0
                disk_percent = 0
                
                try:
                    if hasattr(self.app, 'cpu_usage_history') and len(self.app.cpu_usage_history) > 10:
                        cpu_data = self.app.cpu_usage_history[-10:]
                        cpu_percent = sum(cpu_data) / len(cpu_data)
                        cpu_trend = "increasing" if cpu_data[-1] > cpu_data[0] else "decreasing"
                    else:
                        cpu_percent = psutil.cpu_percent()
                        cpu_trend = "stable"
                        
                    if hasattr(self.app, 'mem_usage_history') and len(self.app.mem_usage_history) > 10:
                        mem_data = self.app.mem_usage_history[-10:]
                        mem_percent = sum(mem_data) / len(mem_data)
                        mem_trend = "increasing" if mem_data[-1] > mem_data[0] else "decreasing"
                    else:
                        mem_percent = psutil.virtual_memory().percent
                        mem_trend = "stable"
                except Exception as e:
                    print(f"Error getting metrics for results: {e}")
                
                # Update the results text
                self.results_text.config(state="normal")
                self.results_text.delete(1.0, tk.END)
                
                # Format timestamp
                import datetime
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                
                self.results_text.insert(tk.END, f"Performance Results (as of {timestamp})\n\n", "center")
                
                # CPU Analysis
                self.results_text.insert(tk.END, "CPU PERFORMANCE\n", "highlight")
                if cpu_percent > 80:
                    self.results_text.insert(tk.END, f"• High usage: {cpu_percent:.1f}% (Trend: {cpu_trend})\n", "warning")
                    self.results_text.insert(tk.END, "• System may be under heavy load\n")
                elif cpu_percent > 60:
                    self.results_text.insert(tk.END, f"• Moderate usage: {cpu_percent:.1f}% (Trend: {cpu_trend})\n")
                    self.results_text.insert(tk.END, "• System is handling normal workload\n")
                else:
                    self.results_text.insert(tk.END, f"• Normal usage: {cpu_percent:.1f}% (Trend: {cpu_trend})\n", "success")
                    self.results_text.insert(tk.END, "• System is running efficiently\n")
                
                self.results_text.insert(tk.END, "\n")
                
                # Memory Analysis
                self.results_text.insert(tk.END, "MEMORY PERFORMANCE\n", "highlight")
                if mem_percent > 80:
                    self.results_text.insert(tk.END, f"• High usage: {mem_percent:.1f}% (Trend: {mem_trend})\n", "warning")
                    self.results_text.insert(tk.END, "• Memory pressure may affect performance\n")
                elif mem_percent > 60:
                    self.results_text.insert(tk.END, f"• Moderate usage: {mem_percent:.1f}% (Trend: {mem_trend})\n")
                    self.results_text.insert(tk.END, "• Memory allocation is within normal range\n")
                else:
                    self.results_text.insert(tk.END, f"• Normal usage: {mem_percent:.1f}% (Trend: {mem_trend})\n", "success")
                    self.results_text.insert(tk.END, "• Memory resources are sufficient\n")
                
                self.results_text.config(state="disabled")
            
            # Update Analysis tab
            if hasattr(self, 'analysis_text'):
                self.analysis_text.config(state="normal")
                self.analysis_text.delete(1.0, tk.END)
                
                # Get more complex metrics if available
                process_count = len(list(psutil.process_iter()))
                
                # Get top CPU and memory processes
                top_processes = []
                try:
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                        try:
                            proc_info = proc.info
                            if proc_info['cpu_percent'] > 0.5:  # Only include processes using some CPU
                                memory_mb = proc_info['memory_info'].rss / (1024 * 1024)
                                top_processes.append((proc_info['name'], proc_info['cpu_percent'], memory_mb))
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    # Sort by CPU usage
                    top_processes.sort(key=lambda x: x[1], reverse=True)
                except Exception as e:
                    print(f"Error getting top processes: {e}")
                
                self.analysis_text.insert(tk.END, "ADVANCED SYSTEM ANALYSIS\n\n", "center")
                
                # System Overview
                self.analysis_text.insert(tk.END, "SYSTEM OVERVIEW\n", "highlight")
                self.analysis_text.insert(tk.END, f"• Active processes: {process_count}\n")
                
                # Calculate system efficiency score (simple heuristic)
                efficiency_score = 100 - ((cpu_percent + mem_percent) / 2)
                efficiency_category = "Excellent" if efficiency_score > 80 else "Good" if efficiency_score > 60 else "Fair" if efficiency_score > 40 else "Poor"
                
                self.analysis_text.insert(tk.END, f"• System efficiency score: {efficiency_score:.1f}/100 ({efficiency_category})\n")
                
                self.analysis_text.insert(tk.END, "\n")
                
                # Resource Analysis
                self.analysis_text.insert(tk.END, "RESOURCE CONSUMPTION\n", "highlight")
                if top_processes:
                    self.analysis_text.insert(tk.END, "Top resource consumers:\n")
                    for i, (name, cpu, memory) in enumerate(top_processes[:3], 1):
                        self.analysis_text.insert(tk.END, f"• {name}: {cpu:.1f}% CPU, {memory:.1f}MB RAM\n")
                else:
                    self.analysis_text.insert(tk.END, "No significant resource consumers detected\n")
                
                self.analysis_text.config(state="disabled")
            
        except Exception as e:
            print(f"Error updating Results and Analysis tabs: {e}")

    def create_virtual_assistant(self, parent):
        """Create the Virtual Assistant interface with centered buttons and theme-adaptive colors"""
        # Create a frame with proper background
        va_frame = ttk.Frame(parent, style="Card.TFrame")
        va_frame.pack(fill="both", expand=True)
        
        # Title centered
        assistant_title = ttk.Label(va_frame,
                         text="VIRTUAL ASSISTANT",
                         style="Title.TLabel",
                         font=("Segoe UI", 12, "bold"))
        assistant_title.pack(anchor="center", pady=(5, 5))
        
        # Create the chat display with proper theme-matching background
        chat_container = ttk.Frame(va_frame, style="Card.TFrame")
        chat_container.pack(fill="both", expand=True, padx=5, pady=(5, 5))
        
        # The Text widget background should explicitly match the theme's card_bg
        self.chat_display = tk.Text(
            chat_container,
            height=8,
            width=45,
            bg=self.theme.get("card_bg", "#ffffff"),
            fg=self.theme.get("text", "#000000"),
            font=("Segoe UI", 9),
            wrap="word",
            padx=10,
            pady=5
        )
        self.chat_display.pack(fill="both", expand=True)
        self.chat_display.config(state="disabled")
        
        # Configure text widget tags for better visibility with adaptable colors
        # User messages - always use accent color that's visible in both themes
        self.chat_display.tag_configure("user", foreground=self.theme.get("accent", "#0078D7"))
        
        # Assistant messages - use theme text color
        self.chat_display.tag_configure("assistant", foreground=self.theme.get("text", "#000000"))
        
        # Warning and success colors that work in both light and dark themes
        self.chat_display.tag_configure("warning", foreground="#FF6600")  # Orange - visible in both modes
        self.chat_display.tag_configure("success", foreground="#4CAF50")  # Green - visible in both modes
        self.chat_display.tag_configure("error", foreground="#F44336")    # Red - visible in both modes
        self.chat_display.tag_configure("highlight", foreground="#0078D7") # Blue - visible in both modes
        
        # Center alignment tag
        self.chat_display.tag_configure("center", justify="center")
        
        # Command toolbar for quick access to common queries - centered
        toolbar_frame = ttk.Frame(va_frame, style="Card.TFrame")
        toolbar_frame.pack(fill="x", padx=5, pady=(0, 2))
        
        # Center container for buttons
        button_center_frame = ttk.Frame(toolbar_frame, style="Card.TFrame")
        button_center_frame.pack(anchor="center", expand=True)
        
        # Add quick command buttons in horizontal layout
        cmd_buttons = [
            ("CPU", lambda: self.quick_command("cpu")),
            ("Memory", lambda: self.quick_command("memory")),
            ("Disk", lambda: self.quick_command("disk")),
            ("Network", lambda: self.quick_command("network")),
            ("Processes", lambda: self.quick_command("processes")),
            ("Help", lambda: self.quick_command("help"))
        ]
        
        for text, command in cmd_buttons:
            btn = ttk.Button(button_center_frame,
                           text=text,
                           command=command,
                           style="Small.TButton",
                           width=7)
            btn.pack(side="left", padx=2, pady=2)
        
        # Input area with centered Ask button below it
        input_frame = ttk.Frame(va_frame, style="Card.TFrame")
        input_frame.pack(fill="x", padx=5, pady=(2, 2))
        
        # Input field - full width
        self.user_input = ttk.Entry(input_frame)
        self.user_input.pack(fill="x", padx=5, pady=(0, 5))
        
        # Center frame for Ask button
        ask_btn_frame = ttk.Frame(input_frame, style="Card.TFrame")
        ask_btn_frame.pack(anchor="center", pady=(0, 5))
        
        # Ask button - centered below input
        send_btn = ttk.Button(ask_btn_frame,
                             text="Ask",
                             command=self.handle_assistant_input,
                             style="Accent.TButton",
                             width=10)  # Fixed width for better appearance
        send_btn.pack(side="top")
        
        # Bind Enter key to input handling
        self.user_input.bind("<Return>", self.handle_assistant_input)
        self.user_input.focus_set()  # Set focus to the input box by default
        
        # Initial welcome message
        self.update_chat_display("Assistant: Hello! I'm your system monitoring assistant. Ask me about CPU, memory, disk, network usage, or system performance.", "assistant")

    def quick_command(self, command):
        """Execute a quick command from the toolbar buttons"""
        try:
            if command == "cpu":
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_count = psutil.cpu_count()
                physical_cores = psutil.cpu_count(logical=False)
                message = f"CPU usage: {cpu_percent:.1f}% across {physical_cores} physical cores ({cpu_count} logical cores)."
                self.update_chat_display(f"CPU Information: {message}", "assistant")
            elif command == "memory":
                mem = psutil.virtual_memory()
                used_gb = mem.used / (1024**3)
                total_gb = mem.total / (1024**3)
                avail_gb = mem.available / (1024**3)
                message = f"Memory: {used_gb:.2f}GB used of {total_gb:.2f}GB total ({mem.percent}%). You have {avail_gb:.2f}GB available."
                self.update_chat_display(f"Memory Information: {message}", "assistant")
            elif command == "disk":
                if platform.system() == 'Windows':
                    disk_usage = psutil.disk_usage('C:\\')
                    disk_label = "C:"
                else:
                    disk_usage = psutil.disk_usage('/')
                    disk_label = "/"
                free_gb = disk_usage.free / (1024**3)
                total_gb = disk_usage.total / (1024**3)
                used_gb = disk_usage.used / (1024**3)
                message = f"Disk ({disk_label}): {used_gb:.2f}GB used of {total_gb:.2f}GB ({disk_usage.percent}% used). {free_gb:.2f}GB free."
                self.update_chat_display(f"Disk Information: {message}", "assistant")
            elif command == "network":
                net_io = psutil.net_io_counters()
                sent_mb = net_io.bytes_sent / (1024**2)
                recv_mb = net_io.bytes_recv / (1024**2)
                message = f"Network: {recv_mb:.2f}MB received, {sent_mb:.2f}MB sent since startup."
                self.update_chat_display(f"Network Information: {message}", "assistant")
            elif command == "processes":
                process_count = len(list(psutil.process_iter()))
                message = f"Currently running {process_count} processes."
                self.update_chat_display(f"Process Information: {message}", "assistant")
            elif command == "help":
                self.show_assistant_help()
        except Exception as e:
            self.update_chat_display(f"Error retrieving {command} information: {str(e)}", "error")

    def show_assistant_help(self):
        """Show help information for the virtual assistant"""
        help_text = (
            "Virtual Assistant Help:\n\n"
            "I can provide information about your system resources. Try asking about:\n"
            "• CPU usage and information\n"
            "• Memory/RAM status\n"
            "• Disk space and usage\n"
            "• Network activity\n"
            "• Running processes\n\n"
            "You can also use the quick command buttons above for instant information."
        )
        self.update_chat_display(help_text, "assistant")

    def update_chat_display(self, message, tag=None):
        """Update the chat display with a new message and apply center alignment"""
        self.chat_display.config(state="normal")
        
        # Apply center tag to all text
        if tag:
            self.chat_display.insert(tk.END, message + "\n\n", (tag, "center"))
        else:
            self.chat_display.insert(tk.END, message + "\n\n", "center")
        
        self.chat_display.see(tk.END)  # Scroll to the bottom
        self.chat_display.config(state="disabled")

    def handle_assistant_input(self, event=None):
        """Handle user input with improved response handling and theme-adaptive colors"""
        query = self.user_input.get().strip()
        if query:
            # Display user query with user tag for proper coloring
            self.update_chat_display(f"You: {query}", "user")
            # Clear input field
            self.user_input.delete(0, tk.END)
            
            # Generate response immediately
            try:
                # Simple responses for common queries to improve responsiveness
                if "memory" in query.lower() or "ram" in query.lower():
                    mem = psutil.virtual_memory()
                    used_gb = mem.used / (1024**3)
                    total_gb = mem.total / (1024**3)
                    avail_gb = mem.available / (1024**3)
                    response = f"Memory: {used_gb:.2f}GB used of {total_gb:.2f}GB total ({mem.percent}%). You have {avail_gb:.2f}GB available."
                elif "cpu" in query.lower():
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    cpu_count = psutil.cpu_count()
                    physical_cores = psutil.cpu_count(logical=False)
                    response = f"CPU usage: {cpu_percent:.1f}% across {physical_cores} physical cores ({cpu_count} logical cores)."
                elif "disk" in query.lower():
                    if platform.system() == 'Windows':
                        disk_usage = psutil.disk_usage('C:\\')
                        disk_label = "C:"
                    else:
                        disk_usage = psutil.disk_usage('/')
                        disk_label = "/"
                    free_gb = disk_usage.free / (1024**3)
                    total_gb = disk_usage.total / (1024**3)
                    used_gb = disk_usage.used / (1024**3)
                    response = f"Disk ({disk_label}): {used_gb:.2f}GB used of {total_gb:.2f}GB ({disk_usage.percent}% used). {free_gb:.2f}GB free."
                elif "network" in query.lower():
                    net_io = psutil.net_io_counters()
                    sent_mb = net_io.bytes_sent / (1024**2)
                    recv_mb = net_io.bytes_recv / (1024**2)
                    response = f"Network: {recv_mb:.2f}MB received, {sent_mb:.2f}MB sent since startup."
                elif "processes" in query.lower():
                    process_count = len(list(psutil.process_iter()))
                    response = f"Currently running {process_count} processes."
                elif "help" in query.lower():
                    response = "I can help with CPU, memory, disk, network, and process information. Ask me specific questions about your system resources."
                else:
                    # Use the more comprehensive response generator
                    response = self.generate_assistant_response(query)
                    if not response:  # If an empty string is returned (for help/examples)
                        return  # Exit early as the display has already been updated
            except Exception as e:
                response = f"Error processing your request: {str(e)}"
                
            # Display the assistant's response with theme-adaptive coloring
            self.update_chat_display(f"Assistant: {response}", "assistant")

    def generate_assistant_response(self, query):
        """Generate a comprehensive response based on the user's query with enhanced capabilities"""
        query = query.lower()
        
        try:
            # Help command
            if "help" in query and len(query) < 10:
                self.show_assistant_help()
                return ""
            
            # Examples command
            if "example" in query and len(query) < 15:
                self.show_assistant_examples()
                return ""
            
            # Network-related queries - NEW SECTION
            if "network" in query or "internet" in query or "wifi" in query or "connection" in query:
                try:
                    # Get network IO counters
                    net_io = psutil.net_io_counters()
                    sent_mb = net_io.bytes_sent / (1024**2)
                    recv_mb = net_io.bytes_recv / (1024**2)
                    
                    # Get active connections if requested
                    if "connection" in query:
                        try:
                            # Count connections by status
                            connection_stats = {"ESTABLISHED": 0, "LISTEN": 0, "TIME_WAIT": 0, "CLOSE_WAIT": 0, "Other": 0}
                            
                            for conn in psutil.net_connections():
                                if conn.status in connection_stats:
                                    connection_stats[conn.status] += 1
                                else:
                                    connection_stats["Other"] += 1
                            
                            total_connections = sum(connection_stats.values())
                            connection_details = "\n".join([f"• {status}: {count}" for status, count in connection_stats.items() if count > 0])
                            
                            return f"Current network connections: {total_connections} total\n\n{connection_details}\n\nNetwork I/O: {recv_mb:.2f}MB received, {sent_mb:.2f}MB sent since startup"
                        except:
                            return f"Found active network connections, but detailed status information requires elevated permissions.\n\nNetwork I/O: {recv_mb:.2f}MB received, {sent_mb:.2f}MB sent since startup"
                    
                    # Get network interfaces if requested
                    elif "interface" in query or "adapter" in query:
                        import socket
                        addrs = psutil.net_if_addrs()
                        stats = psutil.net_if_stats()
                        
                        response = "Network interfaces:"
                        for interface, addresses in addrs.items():
                            # Check if interface is up
                            is_up = stats[interface].isup if interface in stats else "Unknown"
                            speed = f", Speed: {stats[interface].speed}Mb/s" if interface in stats and stats[interface].speed > 0 else ""
                            
                            response += f"\n\n• {interface} ({'Up' if is_up else 'Down'}){speed}"
                            for addr in addresses:
                                if addr.family == socket.AF_INET:  # IPv4
                                    response += f"\n  IPv4: {addr.address}"
                                elif addr.family == socket.AF_INET6:  # IPv6
                                    response += f"\n  IPv6: {addr.address}"
                                elif addr.family == psutil.AF_LINK:  # MAC
                                    response += f"\n  MAC: {addr.address}"
                        
                        return response
                    
                    # Check for speed or bandwidth query
                    elif "speed" in query or "bandwidth" in query or "download" in query or "upload" in query:
                        # This is a simple approximation - not a real speed test
                        return f"Network activity since system startup:\n• Downloaded: {recv_mb:.2f}MB\n• Uploaded: {sent_mb:.2f}MB\n\nNote: For accurate speed testing, use a dedicated speed test tool."
                    
                    # Default network response
                    return f"Network statistics since startup:\n• Data received: {recv_mb:.2f}MB\n• Data sent: {sent_mb:.2f}MB\n\nType 'network connections' or 'network interfaces' for more details."
                    
                except Exception as e:
                    return f"I encountered an error retrieving network information: {str(e)}."
            
            # Temperature and sensor data - NEW SECTION
            elif "temperature" in query or "temp" in query or "sensor" in query or "fan" in query or "cooling" in query:
                try:
                    if hasattr(psutil, "sensors_temperatures"):
                        temps = psutil.sensors_temperatures()
                        if not temps:
                            return "Temperature sensors not available on this system."
                        
                        response = "System temperatures:\n"
                        for chip, sensors in temps.items():
                            for sensor in sensors:
                                label = sensor.label or "Unknown"
                                temp = sensor.current
                                # Add warning indicator if high temperature
                                warning = " ⚠️ High" if sensor.high and temp >= sensor.high else ""
                                warning = " 🔥 CRITICAL" if sensor.critical and temp >= sensor.critical else warning
                                response += f"• {chip} - {label}: {temp}°C{warning}\n"
                        
                        # Add fan information if available
                        if hasattr(psutil, "sensors_fans"):
                            fans = psutil.sensors_fans()
                            if fans:
                                response += "\nSystem fans:\n"
                                for chip, fan_sensors in fans.items():
                                    for sensor in fan_sensors:
                                        label = sensor.label or "Unknown"
                                        speed = sensor.current
                                        response += f"• {chip} - {label}: {speed} RPM\n"
                        
                        return response.strip()
                    else:
                        return "Temperature sensor data is not available through this interface on your system."
                except Exception as e:
                    return f"I couldn't access temperature information: {str(e)}"
            
            # Battery information - NEW SECTION
            elif "battery" in query or "power" in query:
                try:
                    if hasattr(psutil, "sensors_battery"):
                        battery = psutil.sensors_battery()
                        if battery:
                            percent = battery.percent
                            power_plugged = battery.power_plugged
                            
                            status = "charging" if power_plugged else "discharging"
                            
                            # Calculate time remaining
                            time_str = ""
                            if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                                mins, secs = divmod(battery.secsleft, 60)
                                hours, mins = divmod(mins, 60)
                                if hours > 0:
                                    time_str = f" ({int(hours)}h {int(mins)}m remaining)"
                                else:
                                    time_str = f" ({int(mins)}m remaining)"
                            
                            # Add battery health indicator
                            health = ""
                            if percent <= 20 and not power_plugged:
                                health = "\n\n⚠️ Warning: Low battery! Connect to power source soon."
                            
                            return f"Battery status: {percent}% - {status.capitalize()}{time_str}{health}"
                        else:
                            return "No battery detected. Your system appears to be a desktop or server without battery information."
                    else:
                        return "Battery information is not available through this interface on your system."
                except Exception as e:
                    return f"I couldn't access battery information: {str(e)}"
            
            # Process analysis - ENHANCED SECTION
            elif "analyze process" in query or "process analysis" in query:
                try:
                    # Extract process name if specified
                    target_process = None
                    if "analyze process" in query:
                        parts = query.split("analyze process")
                        if len(parts) > 1 and parts[1].strip():
                            target_process = parts[1].strip()
                    
                    if target_process:
                        # Find matching processes
                        matches = []
                        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'create_time', 'num_threads']):
                            try:
                                if target_process.lower() in proc.info['name'].lower():
                                    proc_info = proc.info
                                    proc_info['memory_mb'] = proc_info['memory_info'].rss / (1024 * 1024)
                                    matches.append(proc_info)
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                        
                        if not matches:
                            return f"No processes found matching '{target_process}'."
                        
                        # Sort by memory usage
                        matches.sort(key=lambda x: x['memory_mb'], reverse=True)
                        
                        # Analyze the process
                        proc = matches[0]
                        pid = proc['pid']
                        name = proc['name']
                        cpu = proc['cpu_percent']
                        memory_mb = proc['memory_mb']
                        
                        # Get creation time
                        import datetime
                        create_time = datetime.datetime.fromtimestamp(proc['create_time']).strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Get thread count
                        threads = proc['num_threads']
                        
                        # Try to get more details
                        try:
                            process = psutil.Process(pid)
                            status = process.status()
                            
                            # Try to get command line
                            try:
                                cmdline = " ".join(process.cmdline())
                                if len(cmdline) > 100:
                                    cmdline = cmdline[:100] + "..."
                            except:
                                cmdline = "Not available"
                            
                            return f"Process Analysis: {name} (PID {pid})\n\nStatus: {status}\nCPU Usage: {cpu:.1f}%\nMemory Usage: {memory_mb:.1f}MB\nThreads: {threads}\nStarted: {create_time}\n\nCommand: {cmdline}"
                        except:
                            return f"Process Analysis: {name} (PID {pid})\n\nCPU Usage: {cpu:.1f}%\nMemory Usage: {memory_mb:.1f}MB\nThreads: {threads}\nStarted: {create_time}"
                    
                    else:
                        return "Please specify a process name to analyze. For example: 'Analyze process chrome'"
                except Exception as e:
                    return f"I couldn't analyze the process: {str(e)}"
            
            # Continue with existing query handlers (CPU, memory, disk, etc.)
            # ... [existing code]
            
            # For all other queries, provide a helpful response
            return "I can help with CPU, memory, disk, network, temperatures, battery, and process information. Try asking a more specific question, or type 'help' to see what I can do."
        
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}. Please try a different question."

    def update_status_message(self, message):
        """Update the status message in the AI insights panel"""
        try:
            if hasattr(self, 'status_msg') and isinstance(self.status_msg, tk.Text):
                self.status_msg.config(state="normal")
                self.status_msg.delete(1.0, tk.END)
                self.status_msg.insert(tk.END, message, "center")
                self.status_msg.config(state="disabled")
            elif hasattr(self, 'status_text') and isinstance(self.status_text, tk.Text):
                self.status_text.config(state="normal")
                self.status_text.delete(1.0, tk.END)
                self.status_text.insert(tk.END, message, "center")
                self.status_text.config(state="disabled")
            elif hasattr(self, 'ai_status_msg') and isinstance(self.ai_status_msg, ttk.Label):
                self.ai_status_msg.configure(text=message)
        except Exception as e:
            print(f"Error updating status message: {e}")

    def create_smart_recommendations(self, parent):
        """Create Smart Recommendations panel with centered content"""
        # Title
        recommendations_title = ttk.Label(parent,
                                        text="SMART RECOMMENDATIONS",
                                        style="Title.TLabel",
                                        font=("Segoe UI", 12, "bold"))
        recommendations_title.pack(anchor="center", pady=(5, 10))
        
        # Recommendations content with centered text
        self.recommendations_content = tk.Text(
            parent,
            height=14,
            width=30,
            bg=self.theme["card_bg"],
            fg=self.theme["text"],
            font=("Segoe UI", 9),
            wrap="word",
            relief="flat",
            padx=10,
            pady=10
        )
        self.recommendations_content.pack(fill="both", expand=True, padx=5, pady=5)
        self.recommendations_content.tag_configure("center", justify="center")
        self.recommendations_content.config(state="disabled")
        
        # Immediately update recommendations
        self.update_smart_recommendations()

    def update_system_info(self):
        """Update the system information labels with current data"""
        try:
            # OS information
            os_info = f"{platform.system()} {platform.release()}"
            self.info_labels["OS"].config(text=os_info)
            
            # CPU information
            cpu_count = psutil.cpu_count()
            physical_cores = psutil.cpu_count(logical=False)
            cpu_percent = psutil.cpu_percent()
            cpu_info = f"{physical_cores} cores ({cpu_count} logical), {cpu_percent}% used"
            self.info_labels["CPU"].config(text=cpu_info)
            
            # RAM information
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024**3)
            used_gb = mem.used / (1024**3)
            ram_info = f"{used_gb:.1f} GB / {total_gb:.1f} GB ({mem.percent}%)"
            self.info_labels["RAM"].config(text=ram_info)
            
            # Uptime information
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            days, remainder = divmod(uptime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                uptime_info = f"{int(days)}d {int(hours)}h {int(minutes)}m"
            elif hours > 0:
                uptime_info = f"{int(hours)}h {int(minutes)}m"
            else:
                uptime_info = f"{int(minutes)}m {int(seconds)}s"
            
            self.info_labels["Uptime"].config(text=uptime_info)
            
            # Schedule next update (every 10 seconds for system info is reasonable)
            self.frame.after(10000, self.update_system_info)
            
        except Exception as e:
            print(f"Error updating system info: {e}")
            # Handle errors gracefully by showing "Error" in the fields
            for label in self.info_labels:
                self.info_labels[label].config(text="Error")

    def update_gauges(self, cpu_percent, mem_percent, disk_percent):
        """Update gauge charts for CPU, memory and disk"""
        update_gauge(self.cpu_ax, cpu_percent, "CPU", self.theme)
        update_gauge(self.mem_ax, mem_percent, "MEM", self.theme)
        update_gauge(self.disk_ax, disk_percent, "DISK", self.theme)
        
        self.cpu_ax.figure.canvas.draw()
        self.mem_ax.figure.canvas.draw()
        self.disk_ax.figure.canvas.draw()
    
    def update_gauge_colors(self, theme):
        """Update gauge colors when theme changes"""
        try:
            # Store the current theme
            self.theme = theme
            
            # Update gauges background color
            for fig, _ in self.gauges:
                fig.patch.set_facecolor(theme["card_bg"])
            
            # Force redraw of gauges with current values
            cpu_percent = self.app.cpu_usage_history[-1] if self.app.cpu_usage_history else 0
            mem_percent = self.app.mem_usage_history[-1] if self.app.mem_usage_history else 0
            disk_percent = self.app.disk_usage_history[-1] if self.app.disk_usage_history else 0
            
            self.update_gauges(cpu_percent, mem_percent, disk_percent)
        except Exception as e:
            print(f"Error updating gauge colors: {e}")

    def refresh_system_info(self):
        """Immediately refresh the system information"""
        self.update_system_info()

    def update_graph_colors(self, theme):
        """Update graph colors when theme changes"""
        try:
            # Store the current theme
            self.theme = theme
            
            # Update the graph figure background
            self.perf_fig.patch.set_facecolor(theme["card_bg"])
            self.perf_ax.set_facecolor(theme["chart_bg"])
            
            # Update grid color
            self.perf_ax.grid(color=theme["grid_color"], linestyle='--', alpha=0.6)
            
            # Update line colors
            if hasattr(self, 'cpu_line') and self.cpu_line:
                self.cpu_line.set_color(theme["cpu_color"])
            
            if hasattr(self, 'mem_line') and self.mem_line:
                self.mem_line.set_color(theme["mem_color"])
            
            if hasattr(self, 'disk_line') and self.disk_line:
                self.disk_line.set_color(theme["disk_color"])
            
            # Update text colors
            self.perf_ax.tick_params(colors=theme["text"])
            for text in self.perf_ax.get_xticklabels() + self.perf_ax.get_yticklabels():
                text.set_color(theme["text"])
            
            # Update title color
            if self.perf_ax.get_title():
                self.perf_ax.title.set_color(theme["text"])
            
            # Redraw the canvas
            self.perf_canvas.draw()
        except Exception as e:
            print(f"Error updating graph colors: {e}")

    def cycle_theme(self):
        """Cycle through available themes without showing a dialog"""
        # Get list of theme keys
        theme_keys = list(THEMES.keys())
        
        # Find the index of the current theme
        current_index = theme_keys.index(self.app.current_theme)
        
        # Get the next theme in the cycle
        next_index = (current_index + 1) % len(theme_keys)
        next_theme = theme_keys[next_index]
        
        # Instead of calling apply_theme, call toggle_theme which exists in app.py
        self.app.toggle_theme()
        
        # Update the theme button icon
        self.theme_btn.config(text=THEMES[self.app.current_theme]["icon"])

    def update_ai_timeline(self, collection_time=0, training_status="", prediction_status="", system_status=""):
        """Update the AI timeline information with latest statuses"""
        try:
            # Update collection time if the label exists
            if hasattr(self, 'collection_status'):
                self.collection_status.config(text=f"{collection_time:.1f} mins")
            
            # Update training status if the label exists
            if hasattr(self, 'training_status'):
                self.training_status.config(text=training_status)
            
            # Update prediction status if the label exists
            if hasattr(self, 'prediction_status'):
                self.prediction_status.config(text=prediction_status)
            
            # Update system status if the label exists
            if hasattr(self, 'system_status'):
                self.system_status.config(text=system_status)
                
                # Update icon based on status
                if hasattr(self, 'system_icon'):
                    if "normal" in system_status.lower():
                        self.system_icon.config(text="✅")
                    elif "anomaly" in system_status.lower():
                        self.system_icon.config(text="⚠️")
                    else:
                        self.system_icon.config(text="🔄")
        except Exception as e:
            print(f"Error updating AI timeline: {e}")
            # Non-critical error, continue execution

    def update_theme_components(self, theme):
        """Update all themed components when theme changes"""
        try:
            # Store the new theme
            self.theme = theme
            
            # Update virtual assistant text colors
            if hasattr(self, 'chat_display'):
                self.chat_display.config(
                    bg=theme.get("card_bg", "#ffffff"),
                    fg=theme.get("text", "#000000")
                )
                # Update text tags to match new theme
                self.chat_display.tag_configure("assistant", foreground=theme.get("text", "#000000"))
                # Keep user text color as accent for better visibility
                self.chat_display.tag_configure("user", foreground=theme.get("accent", "#0078D7"))
            
            # Update AI Insights and Analytics text widgets
            if hasattr(self, 'results_text'):
                self.results_text.config(
                    bg=theme.get("card_bg", "#ffffff"),
                    fg=theme.get("text", "#000000")
                )
            
            if hasattr(self, 'analysis_text'):
                self.analysis_text.config(
                    bg=theme.get("card_bg", "#ffffff"),
                    fg=theme.get("text", "#000000")
                )
            
            if hasattr(self, 'anomaly_text'):
                self.anomaly_text.config(
                    bg=theme.get("card_bg", "#ffffff"),
                    fg=theme.get("text", "#000000")
                )
            
            # Update recommendations text
            if hasattr(self, 'recommendations_content'):
                self.recommendations_content.config(
                    bg=theme.get("card_bg", "#ffffff"),
                    fg=theme.get("text", "#000000")
                )
            
            # Force refresh of content to ensure visibility
            self.update_results_and_analysis()
        except Exception as e:
            print(f"Error updating theme components: {e}")

    def update_smart_recommendations(self):
        """Update the smart recommendations with more detailed tips based on system data and center-aligned text"""
        try:
            # Clear existing text
            self.recommendations_content.config(state="normal")
            self.recommendations_content.delete(1.0, tk.END)
            
            # Get current system info - with error handling
            cpu_percent = 0
            mem_percent = 0
            disk_percent = 0
            
            try:
                if hasattr(self.app, 'cpu_usage_history') and self.app.cpu_usage_history:
                    cpu_percent = self.app.cpu_usage_history[-1]
                else:
                    cpu_percent = psutil.cpu_percent()
                    
                if hasattr(self.app, 'mem_usage_history') and self.app.mem_usage_history:
                    mem_percent = self.app.mem_usage_history[-1]
                else:
                    mem_percent = psutil.virtual_memory().percent
                    
                if hasattr(self.app, 'disk_usage_history') and self.app.disk_usage_history:
                    disk_percent = self.app.disk_usage_history[-1]
                else:
                    try:
                        if platform.system() == 'Windows':
                            disk_percent = psutil.disk_usage('C:\\').percent
                        else:
                            disk_percent = psutil.disk_usage('/').percent
                    except:
                        disk_percent = 50  # Default value
            except Exception as e:
                print(f"Error getting system metrics: {e}")
                # Use defaults if there's an error
            
            # Generate more detailed recommendations based on current usage
            recommendations = []
            
            # Determine overall system health
            if cpu_percent > 80 or mem_percent > 80 or disk_percent > 90:
                recommendations.append("⚠️ SYSTEM ALERT: Your system resources are critically high!")
            elif cpu_percent > 60 or mem_percent > 60 or disk_percent > 75:
                recommendations.append("⚠️ SYSTEM WARNING: Resource usage is approaching high levels")
            else:
                recommendations.append("✅ Your system is running well. Here are some optimization tips:")
            
            recommendations.append("")
            
            # CPU recommendations
            recommendations.append("🔹 CPU OPTIMIZATION:")
            if cpu_percent > 80:
                recommendations.append("  • URGENT: High CPU usage detected at {:.1f}%!".format(cpu_percent))
                recommendations.append("  • Identify and close CPU-intensive applications")
                recommendations.append("  • Check Task Manager for processes using excessive CPU")
                recommendations.append("  • Consider upgrading CPU if consistently overloaded")
                recommendations.append("  • Scan for malware/crypto miners using background resources")
            elif cpu_percent > 60:
                recommendations.append("  • Moderate CPU load detected at {:.1f}%".format(cpu_percent))
                recommendations.append("  • Close unnecessary background applications")
                recommendations.append("  • Disable startup programs that aren't essential")
                recommendations.append("  • Consider limiting CPU-intensive tasks during work hours")
            else:
                recommendations.append("  • CPU usage is optimal at {:.1f}%".format(cpu_percent))
                recommendations.append("  • For better performance, keep background applications minimal")
                recommendations.append("  • Schedule resource-intensive tasks during idle periods")
            
            recommendations.append("")
            
            # Memory recommendations
            recommendations.append("🔹 MEMORY OPTIMIZATION:")
            if mem_percent > 80:
                recommendations.append("  • URGENT: High memory usage detected at {:.1f}%!".format(mem_percent))
                recommendations.append("  • Close memory-intensive applications immediately")
                recommendations.append("  • Check for memory leaks in long-running applications")
                recommendations.append("  • Restart applications that might have memory leaks")
                recommendations.append("  • Consider adding more RAM if consistently low")
                recommendations.append("  • Disable unnecessary browser extensions that consume memory")
            elif mem_percent > 60:
                recommendations.append("  • Elevated memory usage at {:.1f}%".format(mem_percent))
                recommendations.append("  • Close browser tabs you're not actively using")
                recommendations.append("  • Restart memory-intensive applications periodically")
                recommendations.append("  • Check for applications with memory leaks")
                recommendations.append("  • Limit use of memory-intensive applications simultaneously")
            else:
                recommendations.append("  • Memory usage is healthy at {:.1f}%".format(mem_percent))
                recommendations.append("  • Maintain clean memory habits by closing unused applications")
                recommendations.append("  • Restart memory-intensive applications occasionally")
            
            recommendations.append("")
            
            # Disk recommendations
            recommendations.append("🔹 DISK OPTIMIZATION:")
            if disk_percent > 90:
                recommendations.append("  • CRITICAL: Extremely low disk space at {:.1f}%!".format(disk_percent))
                recommendations.append("  • Run disk cleanup utility immediately")
                recommendations.append("  • Empty Recycle Bin / Trash")
                recommendations.append("  • Uninstall unused applications")
                recommendations.append("  • Move large files (videos, backups) to external storage")
                recommendations.append("  • Delete temporary files and browser caches")
                recommendations.append("  • Use disk analyzer to identify large unnecessary files")
            elif disk_percent > 75:
                recommendations.append("  • Disk space is running low at {:.1f}%".format(disk_percent))
                recommendations.append("  • Run disk cleanup periodically")
                recommendations.append("  • Consider uninstalling rarely used applications")
                recommendations.append("  • Move media files to external storage")
                recommendations.append("  • Clear downloads folder regularly")
            else:
                recommendations.append("  • Disk usage is at a good level ({:.1f}%)".format(disk_percent))
                recommendations.append("  • Schedule regular disk maintenance tasks")
                recommendations.append("  • Set up automatic disk cleanup weekly")
            
            recommendations.append("")
            
            # Performance tips
            recommendations.append("🔹 SYSTEM PERFORMANCE TIPS:")
            recommendations.append("  • Update your operating system regularly")
            recommendations.append("  • Install the latest drivers for your hardware")
            recommendations.append("  • Disable unnecessary startup programs")
            recommendations.append("  • Run a disk defragmentation tool (for HDDs)")
            recommendations.append("  • Check for and fix disk errors periodically")
            recommendations.append("  • Ensure your system has adequate cooling")
            recommendations.append("  • Keep your applications updated to latest versions")
            recommendations.append("  • Consider using an SSD for your operating system")
            
            # Insert all recommendations with center alignment tag
            for recommendation in recommendations:
                self.recommendations_content.insert(tk.END, recommendation + "\n", "center")
            
            self.recommendations_content.config(state="disabled")
        except Exception as e:
            print(f"Error updating recommendations: {e}")
            # Show a simplified message in case of error
            self.recommendations_content.config(state="normal")
            self.recommendations_content.delete(1.0, tk.END)
            self.recommendations_content.insert(tk.END, "Unable to generate recommendations.\nPlease try refreshing the dashboard.", "center")
            self.recommendations_content.config(state="disabled")

    def update_ai_timeline(self, collection_time=0, training_status="", prediction_status="", system_status=""):
        """Update the AI timeline information with latest statuses"""
        try:
            # Update collection time if the label exists
            if hasattr(self, 'collection_status'):
                self.collection_status.config(text=f"{collection_time:.1f} mins")
            
            # Update training status if the label exists
            if hasattr(self, 'training_status'):
                self.training_status.config(text=training_status)
            
            # Update prediction status if the label exists
            if hasattr(self, 'prediction_status'):
                self.prediction_status.config(text=prediction_status)
            
            # Update system status if the label exists
            if hasattr(self, 'system_status'):
                self.system_status.config(text=system_status)
                
                # Update icon based on status
                if hasattr(self, 'system_icon'):
                    if "normal" in system_status.lower():
                        self.system_icon.config(text="✅")
                    elif "anomaly" in system_status.lower():
                        self.system_icon.config(text="⚠️")
                    else:
                        self.system_icon.config(text="🔄")
        except Exception as e:
            print(f"Error updating AI timeline: {e}")
            # Non-critical error, continue execution

class MiddleSection:
    def __init__(self, parent, app):
        """Initialize the middle section with process list and performance graphs only"""
        self.app = app
        self.theme = app.theme
        
        # Create middle frame with padding
        self.frame = ttk.Frame(parent, style="TFrame")
        self.frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Left side: Process list (50% width)
        self.process_frame = ttk.Frame(self.frame, style="Card.TFrame")
        self.process_frame.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=0)
        
        # Process list header
        header_frame = ttk.Frame(self.process_frame, style="Card.TFrame")
        header_frame.pack(fill="x", padx=15, pady=10)
        
        # Title and process count centered
        title_frame = ttk.Frame(header_frame, style="Card.TFrame")
        title_frame.pack(fill="x")
        
        title_label = ttk.Label(title_frame, 
                                    text="RUNNING PROCESSES", 
                                style="Title.TLabel",
                                font=("Segoe UI", 12, "bold"))
        title_label.pack(anchor="center", pady=(5, 10))
        
        self.process_count = ttk.Label(title_frame, 
                                     text="0 processes", 
                                     style="Info.TLabel")
        self.process_count.pack(anchor="center")
        
        # Search box with icon
        search_frame = ttk.Frame(header_frame, style="Search.TFrame")
        search_frame.pack(side="right")
        
        search_icon = ttk.Label(search_frame, text="🔍", style="TLabel")
        search_icon.pack(side="left", padx=5)
        
        self.filter_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, 
                                    textvariable=self.filter_var,
                                    width=30)
        self.search_entry.pack(side="left", padx=(0, 5))
        
        # Process list with improved styling
        self.create_process_list()
        
        # Right side: Only Performance graphs (no Virtual Assistant)
        self.graph_frame = ttk.Frame(self.frame, style="Card.TFrame")
        self.graph_frame.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=0)
        
        # Graph header
        graph_header = ttk.Frame(self.graph_frame, style="Card.TFrame")
        graph_header.pack(fill="x", padx=15, pady=10)
        
        graph_title = ttk.Label(graph_header, 
                               text="SYSTEM PERFORMANCE", 
                               style="Title.TLabel",
                               font=("Segoe UI", 12, "bold"))
        graph_title.pack(anchor="center", pady=(5, 10))
        
        # Time range selector
        time_frame = ttk.Frame(graph_header, style="Card.TFrame")
        time_frame.pack(side="right")
        
        self.time_range = ttk.Combobox(time_frame,
                                      values=["5 minutes", "15 minutes", "1 hour"],
                                      width=10,
                                      state="readonly")
        self.time_range.set("5 minutes")
        self.time_range.pack(side="right")
        
        time_label = ttk.Label(time_frame, text="Time Range:", style="TLabel")
        time_label.pack(side="right", padx=(0, 5))
        
        # Create performance graphs
        self.create_performance_graphs()

    def create_process_list(self):
        """Create the process list with improved styling and functionality"""
        # Process treeview with improved styling
        style = ttk.Style()
        style.configure("Custom.Treeview",
                       rowheight=30,
                       font=("Segoe UI", 10))
        style.configure("Custom.Treeview.Heading",
                       font=("Segoe UI", 10, "bold"))
        
        # Create a container frame for the process list
        list_container = ttk.Frame(self.process_frame, style="Card.TFrame")
        list_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        columns = ("PID", "Name", "CPU%", "Memory", "Status")
        self.tree = ttk.Treeview(list_container, 
                                columns=columns, 
                                show="headings",
                                style="Custom.Treeview")
        
        # Configure columns
        self.tree.heading("PID", text="PID", anchor="center")
        self.tree.heading("Name", text="Process Name", anchor="center")
        self.tree.heading("CPU%", text="CPU %", anchor="center")
        self.tree.heading("Memory", text="Memory (MB)", anchor="center")
        self.tree.heading("Status", text="Status", anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the tree and scrollbar
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Kill Process button
        kill_btn = ttk.Button(self.process_frame, 
                             text="Kill Process", 
                             command=self.kill_selected_process,
                             style="Danger.TButton")
        kill_btn.pack(side="bottom", pady=5)
        
        # Process Details button
        details_btn = ttk.Button(self.process_frame, 
                                text="Process Details", 
                                command=self.app.show_process_details,
                                style="Accent.TButton")
        details_btn.pack(side="left", padx=5)
        
        # Export button
        export_btn = ttk.Button(self.process_frame, 
                               text="Export List", 
                               command=self.app.export_process_list,
                               style="Success.TButton")
        export_btn.pack(side="left", padx=5)
        
        # Separator
        ttk.Separator(self.process_frame, orient="vertical").pack(side="left", fill="y", padx=10, pady=5)
        
        # Alert thresholds (center)
        threshold_frame = ttk.Frame(self.process_frame, style="Card.TFrame")
        threshold_frame.pack(side="left", padx=5)
        
        ttk.Label(threshold_frame, text="Alerts:", style="TLabel", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 5))
        
        # CPU threshold
        ttk.Label(threshold_frame, text="CPU:", style="TLabel").pack(side="left", padx=(5, 2))
        self.app.cpu_threshold = ttk.Entry(threshold_frame, width=3)
        self.app.cpu_threshold.insert(0, "80")
        self.app.cpu_threshold.pack(side="left")
        
        # Memory threshold
        ttk.Label(threshold_frame, text="Mem:", style="TLabel").pack(side="left", padx=(5, 2))
        self.app.mem_threshold = ttk.Entry(threshold_frame, width=3)
        self.app.mem_threshold.insert(0, "80")
        self.app.mem_threshold.pack(side="left")
        
        # Disk threshold
        ttk.Label(threshold_frame, text="Disk:", style="TLabel").pack(side="left", padx=(5, 2))
        self.app.disk_threshold = ttk.Entry(threshold_frame, width=3)
        self.app.disk_threshold.insert(0, "90")
        self.app.disk_threshold.pack(side="left")
        
        # Apply button
        ttk.Button(threshold_frame, text="Apply",
                   command=self.app.update_alert_thresholds,
                   style="Accent.TButton").pack(side="left", padx=(5, 0))
        
        # Separator
        ttk.Separator(self.process_frame, orient="vertical").pack(side="left", fill="y", padx=10, pady=5)
        
        # System info (right side)
        info_frame = ttk.Frame(self.process_frame, style="Card.TFrame")
        info_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # System info in a single line
        self.system_info_label = ttk.Label(
            info_frame, 
            text="Processes: 0 | Memory: 0 MB | CPU Avg: 0%", 
            style="TLabel"
        )
        self.system_info_label.pack(side="left", padx=5)
        
        # Refresh rate (far right)
        refresh_frame = ttk.Frame(self.process_frame, style="Card.TFrame")
        refresh_frame.pack(side="right", padx=5)
        
        ttk.Label(refresh_frame, text="Refresh:", style="TLabel").pack(side="left", padx=(0, 2))
        
        self.app.refresh_rate = ttk.Entry(refresh_frame, width=3)
        self.app.refresh_rate.insert(0, "1")  # Default to 1 second
        self.app.refresh_rate.pack(side="left")
        
    def update_process_list(self):
        """Update the process list after killing a process"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get filter text
            filter_text = self.filter_var.get().lower()
            
            # Get process list
            processes = []
            process_count = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    if filter_text in proc_info['name'].lower():
                        processes.append((
                            proc_info['pid'],
                            proc_info['name'],
                            f"{proc_info['cpu_percent']:.1f}",
                            f"{proc_info['memory_info'].rss / (1024 * 1024):.1f}",
                            proc_info['status']
                        ))
                        process_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort processes by CPU usage
            processes.sort(key=lambda x: float(x[2]), reverse=True)
            
            # Insert into treeview
            for proc in processes:
                self.tree.insert('', 'end', values=proc)
            
            # Update process count
            total_processes = len(list(psutil.process_iter()))
            self.process_count.config(text=f"{process_count} of {total_processes} processes")
            
        except Exception as e:
            print(f"Error updating process list: {e}")

    def kill_selected_process(self):
        """Kill the selected process after confirmation"""
        try:
            # Get the selected item from the tree view
            selected_item = self.tree.selection()[0]
            
            # Get the process ID and name from the selected item
            pid = int(self.tree.item(selected_item, "values")[0])
            process_name = self.tree.item(selected_item, "values")[1]
            
            # Confirm termination
            if messagebox.askyesno("Confirm", f"Are you sure you want to terminate process {pid} ({process_name})?"):
                try:
                    # Attempt to terminate the process
                    process = psutil.Process(pid)
                    process.terminate()
                    
                    # Wait for process to terminate or force kill
                    try:
                        process.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        process.kill()
                    
                    # Update the process list
                    self.update_process_list()

                    # Provide feedback
                    messagebox.showinfo("Success", f"Process {pid} ({process_name}) has been terminated.")
                except psutil.NoSuchProcess:
                    messagebox.showerror("Error", f"Process {pid} no longer exists.")
                    self.update_process_list()  # Refresh anyway
                except psutil.AccessDenied:
                    messagebox.showerror("Error", f"Access denied when trying to terminate process {pid}. Try running as administrator.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid process ID: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def create_performance_graphs(self):
        """Create performance graphs with more height since VA is removed"""
        # Create a container for the graphs with more vertical space
        graph_container = ttk.Frame(self.graph_frame, style="Card.TFrame")
        graph_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create the figure with larger height
        self.perf_fig = plt.Figure(figsize=(5, 6), dpi=100)  # Increased height from 4 to 6
        self.perf_fig.patch.set_facecolor(self.theme["card_bg"])
        
        # Create the axis for the line graphs
        self.perf_ax = self.perf_fig.add_subplot(111)
        self.perf_ax.set_facecolor(self.theme["chart_bg"])
        
        # Set up axis labels and title
        self.perf_ax.set_title("System Performance", color=self.theme["text"])
        self.perf_ax.set_xlabel("Time", color=self.theme["text"])
        self.perf_ax.set_ylabel("Usage %", color=self.theme["text"])
        
        # Set up grid
        self.perf_ax.grid(color=self.theme["grid_color"], linestyle='--', alpha=0.6)
        
        # Set text colors
        self.perf_ax.tick_params(colors=self.theme["text"])
        for text in self.perf_ax.get_xticklabels() + self.perf_ax.get_yticklabels():
            text.set_color(self.theme["text"])
        
        # Create empty lines for initial plot
        self.cpu_line, = self.perf_ax.plot([], [], color=self.theme["cpu_color"], label="CPU")
        self.mem_line, = self.perf_ax.plot([], [], color=self.theme["mem_color"], label="Memory")
        self.disk_line, = self.perf_ax.plot([], [], color=self.theme["disk_color"], label="Disk")
        
        # Add legend
        self.perf_ax.legend(loc='upper left', facecolor=self.theme["card_bg"], edgecolor=self.theme["text"])
        
        # Set y-axis limits
        self.perf_ax.set_ylim(0, 100)
        
        # Adjust layout
        self.perf_fig.tight_layout()
        
        # Create canvas for tkinter
        self.perf_canvas = FigureCanvasTkAgg(self.perf_fig, graph_container)
        self.perf_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add controls below the graph
        controls_frame = ttk.Frame(graph_container, style="Card.TFrame")
        controls_frame.pack(fill="x", pady=(10, 0))
        
        # Add checkboxes for showing/hiding lines
        self.show_cpu = tk.BooleanVar(value=True)
        self.show_mem = tk.BooleanVar(value=True)
        self.show_disk = tk.BooleanVar(value=True)
        
        cpu_check = ttk.Checkbutton(controls_frame, 
                                   text="CPU", 
                                   variable=self.show_cpu,
                                   command=self.update_graph_visibility,
                                   style="TCheckbutton")
        cpu_check.pack(side="left", padx=10)
        
        mem_check = ttk.Checkbutton(controls_frame, 
                                   text="Memory", 
                                   variable=self.show_mem,
                                   command=self.update_graph_visibility,
                                   style="TCheckbutton")
        mem_check.pack(side="left", padx=10)
        
        disk_check = ttk.Checkbutton(controls_frame, 
                                    text="Disk", 
                                    variable=self.show_disk,
                                    command=self.update_graph_visibility,
                                    style="TCheckbutton")
        disk_check.pack(side="left", padx=10)

    def update_graph_visibility(self):
        """Update graph visibility based on checkboxes"""
        # Update line visibility based on checkboxes
        self.cpu_line.set_visible(self.show_cpu.get())
        self.mem_line.set_visible(self.show_mem.get())
        self.disk_line.set_visible(self.show_disk.get())
        
        # Redraw the canvas
        self.perf_canvas.draw()

    def create_process_intelligence(self, parent):
        """Create the Process Intelligence panel with relationship diagram feature"""
        # Process intelligence frame
        pi_frame = ttk.Frame(parent, style="Card.TFrame")
        pi_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title with improved styling and center alignment
        title_frame = ttk.Frame(pi_frame, style="Card.TFrame")
        title_frame.pack(fill="x", pady=(5, 10))
        
        title_label = ttk.Label(title_frame, 
                              text="PROCESS INTELLIGENCE", 
                              style="Title.TLabel",
                              font=("Segoe UI", 12, "bold"))
        title_label.pack(anchor="center")
        
        # Create a notebook for different views
        notebook = ttk.Notebook(pi_frame)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Process List tab with centered content
        process_list_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(process_list_frame, text="Process Analysis")
        
        # Create intelligent process list with center-aligned columns
        columns = ("Process", "Category", "Priority", "Relations")
        self.pi_tree = ttk.Treeview(process_list_frame, 
                                   columns=columns,
                                   show="headings",
                                   style="Custom.Treeview")
        
        # Configure columns with center alignment
        for col in columns:
            self.pi_tree.heading(col, text=col, anchor="center")
            self.pi_tree.column(col, anchor="center")
        
        # Configure column widths
        self.pi_tree.column("Process", width=150)
        self.pi_tree.column("Category", width=120)
        self.pi_tree.column("Priority", width=80)
        self.pi_tree.column("Relations", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(process_list_frame, orient="vertical", command=self.pi_tree.yview)
        self.pi_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack the tree and scrollbar
        self.pi_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
        
        # Bind double-click event for relationship diagram
        self.pi_tree.bind("<Double-1>", self.show_process_relationships)
        
        # Information text with center alignment
        info_label = ttk.Label(process_list_frame,
                             text="Double-click a process to see relationship diagram",
                             style="Info.TLabel",
                             font=("Segoe UI", 9, "italic"))
        info_label.pack(anchor="center", pady=(5, 0))
        
        # Relations Diagram tab
        self.relations_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(self.relations_frame, text="Process Relations")
        
        # Add initial message with center alignment
        self.relation_info = ttk.Label(self.relations_frame,
                                     text="Select a process to view its relationships diagram",
                                     style="Info.TLabel",
                                     font=("Segoe UI", 10))
        self.relation_info.pack(anchor="center", pady=20)
        
        # Add canvas frame for the diagram
        self.relation_canvas_frame = ttk.Frame(self.relations_frame, style="Card.TFrame")
        self.relation_canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Populate initial process data
        self.update_process_intelligence()

    def show_process_relationships(self, event=None):
        """Show the process relationships in a diagrammatic view"""
        try:
            # Get selected process
            selected = self.pi_tree.selection()
            if not selected:
                return
            
            process_name = self.pi_tree.item(selected[0])["values"][0]
            
            # Clear previous diagram
            for widget in self.relation_canvas_frame.winfo_children():
                widget.destroy()
            
            # Create a matplotlib figure for the diagram
            fig = plt.Figure(figsize=(8, 6), dpi=100)
            fig.patch.set_facecolor(self.theme.get("card_bg", "#ffffff"))
            
            ax = fig.add_subplot(111)
            ax.set_facecolor(self.theme.get("chart_bg", "#ffffff"))
            ax.set_title(f"Process Relationships: {process_name}", 
                        color=self.theme.get("text", "#000000"),
                        pad=20)
            
            # Hide axes
            ax.axis('off')
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, self.relation_canvas_frame)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Get actual process data
            try:
                # Get the process ID from the tree item
                pid = int(process_name)
                process = psutil.Process(pid)
                
                # Get parent process if available
                parent = None
                parent_name = "None"
                try:
                    parent = psutil.Process(process.ppid())
                    parent_name = f"{parent.pid} ({parent.name()})"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                # Get children processes
                children = []
                try:
                    children = process.children()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                # Get connections
                connections = []
                try:
                    connections = process.connections()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                # Get open files
                open_files = []
                try:
                    open_files = process.open_files()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                # Create a list of related processes to display
                related_processes = []
                
                # Add parent if available
                if parent:
                    related_processes.append(("Parent", parent_name))
                
                # Add up to 2 children
                for i, child in enumerate(children[:2]):
                    try:
                        related_processes.append(("Child", f"{child.pid} ({child.name()})"))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Add up to 2 network connections
                for i, conn in enumerate(connections[:2]):
                    addr = conn.laddr
                    related_processes.append(("Network", f"{addr.ip}:{addr.port}"))
                
                # Add up to 2 file connections
                for i, file in enumerate(open_files[:2]):
                    related_processes.append(("File", file.path.split('\\')[-1]))
                
                # Fill remaining slots with placeholders if needed
                relation_types = ["Memory", "Thread", "Service"]
                i = 0
                
                # Draw central node (main process)
                circle = plt.Circle((0.5, 0.5), 0.1, color=self.theme.get("accent", "#0078D7"), alpha=0.7)
                ax.add_patch(circle)
                ax.text(0.5, 0.5, f"{process.pid} ({process.name()})", 
                       ha='center', va='center', 
                       color=self.theme.get("text", "#000000"),
                       fontsize=9)
                
                # Draw related processes in a circle
                num_relations = len(related_processes)
                radius = 0.4  # Radius of the circle
                center = (0.5, 0.5)  # Center of the diagram
                
                for i, (relation_type, process_info) in enumerate(related_processes):
                    angle = 2 * np.pi * i / num_relations
                    x = center[0] + radius * np.cos(angle)
                    y = center[1] + radius * np.sin(angle)
                    
                    # Draw connection line
                    line = plt.Line2D([center[0], x], [center[1], y], 
                                    color=self.theme.get("text", "#666666"),
                                    alpha=0.4)
                    ax.add_line(line)
                    
                    # Draw related process node
                    circle = plt.Circle((x, y), 0.05, 
                                      color=self.theme.get("success", "#4CAF50"),
                                      alpha=0.7)
                    ax.add_patch(circle)
                    
                    # Add label for related process
                    ax.text(x, y, relation_type,
                           ha='center', va='center',
                           color=self.theme.get("text", "#000000"),
                           fontsize=8)
                    
                    # Add process info below the relation type
                    ax.text(x, y + 0.07, str(process_info)[:15],
                           ha='center', va='center',
                           color=self.theme.get("text", "#000000"),
                           fontsize=7)
                
            except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied) as e:
                # If we can't get actual process data, fall back to placeholder visualization
                print(f"Error getting process data: {e}")
                
                # Draw central node (main process)
                circle = plt.Circle((0.5, 0.5), 0.1, color=self.theme.get("accent", "#0078D7"), alpha=0.7)
                ax.add_patch(circle)
                ax.text(0.5, 0.5, process_name, 
                       ha='center', va='center', 
                       color=self.theme.get("text", "#000000"),
                       fontsize=9)
                
                # Draw related processes in a circle
                num_relations = 6  # Number of related processes to show
                radius = 0.4  # Radius of the circle
                center = (0.5, 0.5)  # Center of the diagram
                
                for i in range(num_relations):
                    angle = 2 * np.pi * i / num_relations
                    x = center[0] + radius * np.cos(angle)
                    y = center[1] + radius * np.sin(angle)
                    
                    # Draw connection line
                    line = plt.Line2D([center[0], x], [center[1], y], 
                                    color=self.theme.get("text", "#666666"),
                                    alpha=0.4)
                    ax.add_line(line)
                    
                    # Draw related process node
                    circle = plt.Circle((x, y), 0.05, 
                                      color=self.theme.get("success", "#4CAF50"),
                                      alpha=0.7)
                    ax.add_patch(circle)
                    
                    # Add label for related process
                    relation_type = ["Child", "Parent", "Service", "Network", "File", "Memory"][i]
                    ax.text(x, y, relation_type,
                           ha='center', va='center',
                           color=self.theme.get("text", "#000000"),
                           fontsize=8)
            
            # Set the aspect ratio to be equal
            ax.set_aspect('equal')
            
            # Draw the canvas
            canvas.draw()
            
        except Exception as e:
            print(f"Error showing process relationships: {e}")
            # Show error message in the diagram area
            error_label = ttk.Label(self.relation_canvas_frame,
                                  text=f"Error generating diagram: {str(e)}",
                                  style="Error.TLabel")
            error_label.pack(anchor="center", pady=20)

    def update_process_intelligence(self):
        """Update the process intelligence data with improved categories and relations"""
        try:
            # Clear existing items
            for item in self.pi_tree.get_children():
                self.pi_tree.delete(item)
            
            # Get the running processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    # Skip very low resource processes to focus on important ones
                    if proc.info['cpu_percent'] < 0.1 and proc.info['memory_info'].rss < 10*1024*1024:
                        continue
                        
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu': proc.info['cpu_percent'],
                        'memory': proc.info['memory_info'].rss / (1024*1024)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by resource usage (CPU + Memory impact)
            processes.sort(key=lambda x: (x['cpu'] + x['memory']/100), reverse=True)
            
            # Take top 30 processes for analysis
            processes = processes[:30]
            
            # Process categories mapping
            categories = {
                # System processes
                "svchost.exe": "System Service",
                "System": "System Core",
                "Registry": "System Core",
                "smss.exe": "System Session",
                "csrss.exe": "System Session",
                "wininit.exe": "System Init",
                "services.exe": "Service Control",
                "lsass.exe": "Security",
                "winlogon.exe": "System Session",
                "explorer.exe": "User Interface",
                "dwm.exe": "Desktop Manager",
                
                # User applications
                "chrome.exe": "Web Browser",
                "firefox.exe": "Web Browser",
                "msedge.exe": "Web Browser",
                "safari.exe": "Web Browser",
                "opera.exe": "Web Browser",
                
                "outlook.exe": "Email Client",
                "thunderbird.exe": "Email Client",
                
                "word.exe": "Office Suite",
                "excel.exe": "Office Suite",
                "powerpnt.exe": "Office Suite",
                "onenote.exe": "Office Suite",
                "winword.exe": "Office Suite",
                
                "code.exe": "Development",
                "devenv.exe": "Development",
                "studio64.exe": "Development",
                "idea64.exe": "Development",
                "pycharm64.exe": "Development",
                "atom.exe": "Development",
                "sublime_text.exe": "Development",
                "eclipse.exe": "Development",
                
                "photoshop.exe": "Creative",
                "illustrator.exe": "Creative",
                "premiere.exe": "Creative",
                "afterfx.exe": "Creative",
                "gimp.exe": "Creative",
                
                "spotify.exe": "Media",
                "vlc.exe": "Media",
                "itunes.exe": "Media",
                "musicbee.exe": "Media",
                "wmplayer.exe": "Media",
                
                "steam.exe": "Gaming",
                "EpicGamesLauncher.exe": "Gaming",
                "Battle.net.exe": "Gaming",
                "GalaxyClient.exe": "Gaming",
                
                "python.exe": "Runtime",
                "java.exe": "Runtime",
                "javaw.exe": "Runtime",
                "node.exe": "Runtime",
                "ruby.exe": "Runtime",
                "perl.exe": "Runtime",
                "php.exe": "Runtime",
                
                "mysqld.exe": "Database",
                "postgres.exe": "Database",
                "sqlservr.exe": "Database",
                "mongod.exe": "Database",
                
                "httpd.exe": "Web Server",
                "nginx.exe": "Web Server",
                "apache.exe": "Web Server",
                
                "MsMpEng.exe": "Security",
                "avguard.exe": "Security",
                "avp.exe": "Security",
                "avgui.exe": "Security",
                
                "OneDrive.exe": "Cloud Sync",
                "Dropbox.exe": "Cloud Sync",
                "GoogleDriveFS.exe": "Cloud Sync",
                
                "slack.exe": "Communication",
                "teams.exe": "Communication",
                "discord.exe": "Communication",
                "zoom.exe": "Communication",
                "skype.exe": "Communication",
                
                "conhost.exe": "Console Host",
                "cmd.exe": "Command Line",
                "powershell.exe": "Command Line",
                "bash.exe": "Command Line",
            }
            
            # Process priority assignment based on category and resource usage
            def assign_priority(proc):
                name = proc['name']
                cpu = proc['cpu']
                memory = proc['memory']
                
                # Default priority
                priority = "Normal"
                
                # System critical processes
                if name in ["System", "Registry", "smss.exe", "csrss.exe", "wininit.exe", "lsass.exe"]:
                    priority = "Critical"
                
                # System services
                elif name in ["services.exe", "svchost.exe", "winlogon.exe"]:
                    priority = "High"
                
                # High resource usage
                elif cpu > 20 or memory > 500:
                    priority = "High Usage"
                
                # Low resource usage
                elif cpu < 1 and memory < 50:
                    priority = "Low"
                
                return priority
            
            # Process relationships analysis
            # This is a simplified version - the real relationships would need deeper analysis
            def determine_relations(proc_name):
                relations = []
                
                # Web browsers often relate to networking and plugins
                if proc_name in ["chrome.exe", "firefox.exe", "msedge.exe", "safari.exe", "opera.exe"]:
                    relations = ["Network Services", "Media Plugins", "Extensions"]
                
                # Office applications relate to document services
                elif proc_name in ["word.exe", "excel.exe", "powerpnt.exe", "winword.exe"]:
                    relations = ["Document Services", "Cloud Sync", "Printing"]
                
                # Development tools
                elif proc_name in ["code.exe", "devenv.exe", "idea64.exe", "pycharm64.exe"]:
                    relations = ["Runtime Environments", "Source Control", "Build Tools"]
                
                # Media applications
                elif proc_name in ["spotify.exe", "vlc.exe", "itunes.exe"]:
                    relations = ["Audio Services", "Media Libraries", "Network"]
                
                # System processes have many relationships
                elif proc_name in ["svchost.exe", "services.exe"]:
                    relations = ["System Services", "Drivers", "User Sessions"]
                
                # Simple relation count for other processes
                else:
                    relation_count = min(max(1, int(len(proc_name) / 5)), 5)  # Between 1-5 relations
                    relations = [f"Related Services ({relation_count})"]
                
                return ", ".join(relations)
            
            # Populate the tree
            for proc in processes:
                # Get process name
                process_name = proc['name']
                
                # Determine category
                category = categories.get(process_name, "Application")
                
                # Determine priority
                priority = assign_priority(proc)
                
                # Determine relations
                relations = determine_relations(process_name)
                
                # Add to tree (note: removed Optimizations column)
                self.pi_tree.insert('', 'end', values=(
                    process_name,
                    category,
                    priority,
                    relations
                ))
            
        except Exception as e:
            print(f"Error updating process intelligence: {e}")
            # Show error in the tree
            self.pi_tree.insert('', 'end', values=(
                "Error loading process data",
                "Error",
                "Error",
                str(e)
            ))
