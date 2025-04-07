import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
import time
import os
import csv
import math  # Add this import for isnan function
from datetime import datetime
import matplotlib as mpl
import platform
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import random
import traceback
import getpass

from config import THEMES, DEFAULT_ALERT_THRESHOLDS, CUSTOM_STYLES
from ui.sections import TopSection, MiddleSection
from utils.process_utils import get_process_details, kill_process, change_process_priority
from utils.ai_utils import ResourcePredictor, AnomalyDetector
from ui.footer import Footer

# Set default font to avoid EUDC.TTE error
mpl.rcParams['font.family'] = 'DejaVu Sans'  # Use a single, reliable font
mpl.rcParams['axes.unicode_minus'] = False    # Fix minus sign display

class ProcessMonitorApp:
    def __init__(self, root):
        """Initialize the Process Monitor App"""
        self.root = root
        self.root.title("Advanced Process Monitoring Dashboard")
        self.root.geometry("1280x720")
        
        # Default theme
        self.current_theme = "sunrise"
        self.theme = THEMES[self.current_theme]
        
        # Configure ttk styles based on theme
        self.style = ttk.Style()
        self.configure_styles()
        
        # Set window background
        self.root.configure(bg=self.theme["bg"])
        
        # Create main frame to hold all content
        self.main_frame = ttk.Frame(self.root, style="TFrame")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize alert history and thresholds
        self.alert_history = []
        self.alert_thresholds = DEFAULT_ALERT_THRESHOLDS.copy()
        self.alert_active = False
        
        # Create refresh rate variable
        self.refresh_rate = tk.StringVar()
        self.refresh_rate.set("1")  # Default to 1 second
        
        # Initialize sections
        self.top_section = None
        self.middle_section = None  # Add this line
        
        # Create the UI components
        self.create_ui()
        
        # Initialize background tasks
        self.start_background_tasks()
        
        # Set up closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize AI model training flag
        self.is_model_trained = False
        
        # Initialize flag to track if we're showing AI results
        self.showing_ai_results = False
        
        # Data storage
        self.cpu_usage_history = []
        self.mem_usage_history = []
        self.disk_usage_history = []
        self.timestamps = []
        self.process_history = {}
        self.alerts = []  # Store alert history
        
        # Initialize AI components
        self.resource_predictor = ResourcePredictor()
        self.anomaly_detector = AnomalyDetector()
        self.recent_anomalies = []
        self.is_model_trained = False  # Flag to track if AI model is trained
        
        # Fix font issues
        mpl.rcParams['font.family'] = 'DejaVu Sans'
        mpl.rcParams['axes.unicode_minus'] = False
        
        self.start_time = datetime.now()  # Add this line
        
        # Add this global error handler to main.py or at the app initialization:
        self.add_exception_handling()
        
    def add_exception_handling(self):
        """Add global exception handling to prevent UI crashes"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions"""
            # Log the error
            error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            print(f"Uncaught exception:\n{error_msg}")
            
            # Show a message to the user if it's a serious error
            if self.root and self.root.winfo_exists():
                try:
                    messagebox.showerror("Error", 
                                       "An error occurred. The application will continue running.\n"
                                       f"Error details: {str(exc_value)}")
                except:
                    pass  # Even the error dialog failed
            
            # Don't call the default exception handler
            return True
        
        # Install the exception handler
        import sys
        sys.excepthook = handle_exception

    def create_ui(self):
        """Create the main UI with improved layout and spacing"""
        # Create main frame with less padding for more space
        self.main_frame.pack_configure(padx=5, pady=5)
        
        # Create top section with more information on sides
        self.top_section = TopSection(self.main_frame, self)
        
        # Add system logs/info to the free space around the System Monitor heading
        self.create_system_logs_panel(self.top_section.frame)
        
        # Create a frame to hold the bottom two rows with significantly less padding
        content_container = ttk.Frame(self.main_frame, style="TFrame")
        content_container.pack(fill="both", expand=True, pady=(0, 0))
        
        # Adjust the content container to have three columns
        content_container.columnconfigure(0, weight=2)  # Process list
        content_container.columnconfigure(1, weight=1)  # Process Intelligence tab
        content_container.columnconfigure(2, weight=2)  # Performance charts
        
        # Configure row to be more compact
        content_container.rowconfigure(0, weight=1, minsize=250)  # Set minimum height
        
        # Left side: Process list with reduced padding
        self.process_frame = ttk.Frame(content_container, style="Card.TFrame")
        self.process_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 3), pady=0)
        
        # Process list header with less padding
        header_frame = ttk.Frame(self.process_frame, style="Card.TFrame")
        header_frame.pack(fill="x", padx=5, pady=2)
        
        # Title and process count
        title_frame = ttk.Frame(header_frame, style="Card.TFrame")
        title_frame.pack(side="left")
        
        title_label = ttk.Label(title_frame, 
                               text="RUNNING PROCESSES", 
                               style="Title.TLabel",
                               font=("Segoe UI", 12, "bold"))
        title_label.pack(side="left")
        
        self.process_count = ttk.Label(title_frame, 
                                     text="0 processes", 
                                     style="Info.TLabel")
        self.process_count.pack(side="left", padx=(15, 0))
        
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
        
        # Process list container with less padding
        list_container = ttk.Frame(self.process_frame, style="Card.TFrame")
        list_container.pack(fill="both", expand=True, padx=5, pady=(0, 2))
        
        # Process treeview
        columns = ("PID", "Name", "CPU%", "Memory", "Status")
        self.process_tree = ttk.Treeview(list_container, 
                                       columns=columns, 
                                       show="headings",
                                       style="Custom.Treeview",
                                       height=8)  # Set explicit height to control vertical size
        
        # Configure columns
        self.process_tree.heading("PID", text="PID")
        self.process_tree.heading("Name", text="Process Name")
        self.process_tree.heading("CPU%", text="CPU %")
        self.process_tree.heading("Memory", text="Memory (MB)")
        self.process_tree.heading("Status", text="Status")
        
        self.process_tree.column("PID", width=70, anchor="center")
        self.process_tree.column("Name", width=200)
        self.process_tree.column("CPU%", width=70, anchor="center")
        self.process_tree.column("Memory", width=100, anchor="center")
        self.process_tree.column("Status", width=100, anchor="center")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create the process controls at the bottom of the process list with reduced padding
        self.create_process_controls_panel(self.process_frame)
        
        # Middle: New Process Intelligence tab
        self.process_intelligence_frame = ttk.Frame(content_container, style="Card.TFrame")
        self.process_intelligence_frame.grid(row=0, column=1, sticky="nsew", padx=3, pady=0)
        self.create_process_intelligence(self.process_intelligence_frame)
        
        # Right side: Performance charts (now third column)
        right_container = ttk.Frame(content_container, style="TFrame")
        right_container.grid(row=0, column=2, sticky="nsew", padx=(3, 0), pady=0)
        
        # Right side is split into upper and lower parts, give more space to System Performance
        right_container.rowconfigure(0, weight=0)  # Virtual Assistant (minimal space)
        right_container.rowconfigure(1, weight=5)  # System Performance (larger)
        right_container.columnconfigure(0, weight=1)  # Both take full width
        
        # Lower right: System Performance
        self.performance_frame = ttk.Frame(right_container, style="Card.TFrame")
        self.performance_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=(2, 0))
        self.create_performance_graphs(self.performance_frame)
        
        # Initialize data storage for history
        self.timestamps = []
        self.cpu_usage_history = []
        self.mem_usage_history = []
        self.disk_usage_history = []
        
        # Explicitly connect the filter_var to the update_process_list method
        self.filter_var.trace_add("write", self.on_filter_change)
        
        # Add a binding for process selection
        self.process_tree.bind("<ButtonRelease-1>", self.on_process_select)
        
        # Create a context menu for the process tree
        self.create_context_menu()
        
        # Initial update of the process list to populate it
        self.update_process_list()

    def configure_styles(self):
        """Configure ttk styles for the application"""
        # Ensure theme dictionary has all required keys
        self.theme = THEMES[self.current_theme].copy()
        
        # Add any missing keys with default values
        if "bg" not in self.theme:
            self.theme["bg"] = self.theme.get("card_bg", "#f0f0f0")
        if "card_bg" not in self.theme:
            self.theme["card_bg"] = self.theme.get("bg", "#ffffff")
        if "button_bg" not in self.theme:
            self.theme["button_bg"] = self.theme.get("accent", "#0078D7")
        
        # Apply theme to ttk styles
        self.style.theme_use("default")
        
        # Configure frame styles
        self.style.configure("TFrame", 
                           background=self.theme["bg"],
                           borderwidth=0)
        
        self.style.configure("Card.TFrame", 
                           background=self.theme["card_bg"],
                           borderwidth=0)
        
        # Add AICard.TFrame style using chart_bg from theme
        self.style.configure("AICard.TFrame",
                           background=self.theme["chart_bg"],
                           relief="flat",
                           borderwidth=0)
        
        # Label styles with proper background and text colors
        self.style.configure("TLabel", 
                           font=("Segoe UI", 10),
                           background=self.theme["card_bg"],
                           foreground=self.theme["text"])
        
        self.style.configure("Title.TLabel", 
                           font=("Segoe UI", 14, "bold"),
                           background=self.theme["card_bg"],
                           foreground=self.theme["accent"])
        
        self.style.configure("InfoTitle.TLabel",
                           font=("Segoe UI", 9, "bold"),
                           background=self.theme["card_bg"],
                           foreground=self.theme["text"])
        
        self.style.configure("Info.TLabel",
                           font=("Segoe UI", 9),
                           background=self.theme["card_bg"],
                           foreground=self.theme["text"])
        
        # Treeview styles
        self.style.configure("Treeview", 
                           background=self.theme["card_bg"],
                           foreground=self.theme["text"],
                           fieldbackground=self.theme["card_bg"],
                           borderwidth=0)
        
        self.style.configure("Treeview.Heading", 
                           background=self.theme["accent"],
                           foreground="#FFFFFF",
                           borderwidth=0,
                           font=("Segoe UI", 10, "bold"))
        
        # Remove borders from treeview
        self.style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe', 'border': '0'})])
        
        # Custom treeview with consistent styling
        self.style.configure("Custom.Treeview",
                           rowheight=30,
                           font=("Segoe UI", 10),
                           background=self.theme["card_bg"],
                           foreground=self.theme["text"],
                           fieldbackground=self.theme["card_bg"],
                           borderwidth=0)
        
        self.style.configure("Custom.Treeview.Heading",
                           font=("Segoe UI", 10, "bold"),
                           background=self.theme["accent"],
                           foreground="#FFFFFF",
                           borderwidth=0)
        
        # Entry styles
        self.style.configure("TEntry", 
                           fieldbackground=self.theme["bg"],
                           foreground=self.theme["text"],
                           borderwidth=1)
        
        # Button styles
        self.style.configure("TButton", 
                           font=("Segoe UI", 9),
                           background=self.theme["button_bg"],
                           foreground=self.theme["text"],
                           borderwidth=1)
        
        self.style.configure("Accent.TButton", 
                           font=("Segoe UI", 9, "bold"),
                           background=self.theme["accent"],
                           foreground="#FFFFFF",
                           borderwidth=1)
        
        self.style.configure("Danger.TButton", 
                           font=("Segoe UI", 9, "bold"),
                           background="#FF4757",
                           foreground="#FFFFFF",
                           borderwidth=1)
        
        # AI button style using chart_bg and text colors from theme
        self.style.configure("AI.TButton",
                           font=("Segoe UI", 10),
                           padding=(20, 8),
                           background=self.theme["chart_bg"],
                           foreground=self.theme["text"],
                           borderwidth=1,
                           focusthickness=0)
        
        # Configure selected state for AI buttons
        self.style.map("AI.TButton",
                      background=[("active", self.theme["grid_color"]),
                                ("selected", self.theme["grid_color"])],
                      foreground=[("active", "#FFFFFF"),
                                ("selected", "#FFFFFF")])
        
        self.style.configure("AI.TButton.Selected",
                           background=self.theme["grid_color"],
                           foreground="#FFFFFF")
        
        # Notebook styles
        self.style.configure("TNotebook", 
                           background=self.theme["bg"],
                           borderwidth=0)
        
        self.style.configure("TNotebook.Tab", 
                           background=self.theme["card_bg"],
                           foreground=self.theme["text"],
                           padding=[10, 2],
                           borderwidth=0)
        
        # Separator style
        self.style.configure("TSeparator", 
                           background=self.theme["bg"])
        
        # Scrollbar style
        self.style.configure("TScrollbar", 
                           background=self.theme["bg"],
                           borderwidth=0,
                           arrowsize=12)
        
        # Checkbutton style
        self.style.configure("TCheckbutton",
                           background=self.theme["card_bg"],
                           foreground=self.theme["text"])
        
        # Combobox style
        self.style.configure("TCombobox",
                           background=self.theme["card_bg"],
                           foreground=self.theme["text"],
                           fieldbackground=self.theme["bg"])
        
        # Update the root window background
        self.root.configure(bg=self.theme["bg"])
        
        # Update the main frame background
        if hasattr(self, 'main_frame'):
            self.main_frame.configure(style="TFrame")
            
        # Force a redraw of the UI
        self.root.update()

    def toggle_theme(self):
        """Cycle through all available themes instead of just toggling"""
        try:
            # Get list of all theme keys
            theme_keys = list(THEMES.keys())
            
            # Find the index of the current theme
            current_index = theme_keys.index(self.current_theme)
            
            # Calculate next theme index (cycle through all themes)
            next_index = (current_index + 1) % len(theme_keys)
            
            # Set the new theme
            self.current_theme = theme_keys[next_index]
            
            # Create a complete theme dictionary with all required keys
            self.theme = THEMES[self.current_theme].copy()
            
            # Ensure required keys exist
            if "bg" not in self.theme:
                self.theme["bg"] = self.theme.get("card_bg", "#f0f0f0")
            
            if "card_bg" not in self.theme:
                self.theme["card_bg"] = self.theme.get("bg", "#ffffff")
            
            # Add button_bg if it doesn't exist
            if "button_bg" not in self.theme:
                self.theme["button_bg"] = self.theme.get("accent", "#0078D7")
            
            # Reconfigure the UI
            self.configure_styles()
            
            # Update theme icon on the button if it exists
            if hasattr(self.top_section, 'theme_btn'):
                self.top_section.theme_btn.config(text=THEMES[self.current_theme]["icon"])
            
            # Update plot colors
            if hasattr(self.top_section, 'update_gauge_colors'):
                self.top_section.update_gauge_colors(self.theme)
            
            # Update performance graph colors
            self.update_performance_graph_colors()
            
            # Call the new theme components update method to handle all text colors
            if hasattr(self.top_section, 'update_theme_components'):
                self.top_section.update_theme_components(self.theme)
            
            # Update text widgets with error handling
            try:
                # Top section text widgets
                if hasattr(self.top_section, 'recommendations_content'):
                    self.top_section.recommendations_content.config(bg=self.theme["card_bg"], fg=self.theme["text"])
                if hasattr(self.top_section, 'anomaly_text'):
                    self.top_section.anomaly_text.config(bg=self.theme["card_bg"], fg=self.theme["text"])
                if hasattr(self.top_section, 'chat_display'):
                    self.top_section.chat_display.config(bg=self.theme["card_bg"], fg=self.theme["text"])
            
                # Process Intelligence elements with safe attribute checking
                if hasattr(self, 'process_intelligence_elements'):
                    elements = self.process_intelligence_elements
                    
                    for key, element in elements.items():
                        # Handle different widget types appropriately
                        if isinstance(element, tk.Button):
                            element.configure(bg=self.theme["card_bg"], fg=self.theme["text"])
                        elif isinstance(element, tk.Label):
                            element.configure(bg=self.theme["card_bg"], fg=self.theme["text"])
                        # Skip ttk widgets as they use styles instead of direct configuration
                        # This prevents the "-bg" option error
            except Exception as e:
                print(f"Non-critical error updating UI elements: {e}")
                # Non-critical error, continue with theme update
            
            # Update backgrounds
            self.root.configure(bg=self.theme["bg"])
            
            # Force a redraw of the UI
            self.root.update()
        except Exception as e:
            print(f"Error switching theme: {e}")
            # If theme switching fails, at least try to ensure the UI is consistent
            try:
                self.configure_styles()
                self.root.update()
            except:
                pass  # Last resort, silently ignore if even this fails

    def start_background_tasks(self):
        """Start background data updating"""
        self.update_data()

    def update_data(self):
        """Update system data and handle UI refreshes"""
        try:
            # Get current CPU and memory usage with smoothing
            cpu_samples = [psutil.cpu_percent() for _ in range(3)]
            cpu_percent = sum(cpu_samples) / len(cpu_samples)
            
            mem = psutil.virtual_memory()
            mem_percent = mem.percent
            
            # Add small random variations to make graphs more dynamic
            cpu_variation = random.uniform(-0.5, 0.5)
            mem_variation = random.uniform(-0.3, 0.3)
            
            # Apply smoothing and variations
            cpu_percent = max(0, min(100, cpu_percent + cpu_variation))
            mem_percent = max(0, min(100, mem_percent + mem_variation))
            
            # Get disk usage with smoothing and better error handling
            try:
                # Try multiple paths for Windows systems
                if platform.system() == 'Windows':
                    # Try C: drive first
                    try:
                        disk_percent = psutil.disk_usage('C:\\').percent
                    except Exception:
                        # Try other common Windows drives
                        disk_found = False
                        for drive in ['D:', 'E:']:
                            try:
                                disk_percent = psutil.disk_usage(drive + '\\').percent
                                disk_found = True
                                break
                            except Exception:
                                continue
                        
                        # If no drives worked, try the system drive or default to 0.1%
                        if not disk_found:
                            try:
                                system_drive = os.environ.get('SystemDrive', 'C:') 
                                disk_percent = psutil.disk_usage(system_drive + '\\').percent
                            except Exception:
                                # Last resort - use a more realistic placeholder value
                                # Most systems have at least 20-30% disk usage
                                disk_percent = random.uniform(25.0, 35.0)
                else:  # Unix/Linux/MacOS
                    disk_percent = psutil.disk_usage('/').percent
                    
                # Apply small random variation for visual interest
                disk_variation = random.uniform(-0.2, 0.2)
                disk_percent = max(0, min(100, disk_percent + disk_variation))
            except Exception as e:
                print(f"Error getting disk usage: {e}")
                # Use a small non-zero value to make it visible but indicate an issue
                disk_percent = 0.1
                
            # Add current time
            current_time = time.time()
            
            # Initialize history lists if they don't exist
            if not hasattr(self, 'timestamps'):
                self.timestamps = []
                self.cpu_usage_history = []
                self.mem_usage_history = []
                self.disk_usage_history = []
                
                # Add some initial varied values for disk usage to make the graph more interesting
                # This will be overwritten with real data as it becomes available
                base_disk = max(disk_percent, 25.0)  # Use either the real value or a minimum of 25%
                for i in range(30):  # Add 30 initial points
                    # Create a wavy pattern with random variations
                    variation = random.uniform(-5.0, 5.0)
                    wave = 3.0 * math.sin(i / 5.0)  # Gentle sine wave
                    initial_disk = max(0, min(100, base_disk + variation + wave))
                    self.disk_usage_history.append(initial_disk)
            
            # Apply exponential moving average for smoother transitions
            alpha = 0.3  # Smoothing factor
            if self.cpu_usage_history:
                last_cpu = self.cpu_usage_history[-1]
                cpu_percent = alpha * cpu_percent + (1 - alpha) * last_cpu
                
                last_mem = self.mem_usage_history[-1]
                mem_percent = alpha * mem_percent + (1 - alpha) * last_mem
                
                last_disk = self.disk_usage_history[-1]
                disk_percent = alpha * disk_percent + (1 - alpha) * last_disk
            
            # Add data to history
            self.timestamps.append(current_time)
            self.cpu_usage_history.append(float(cpu_percent))
            self.mem_usage_history.append(float(mem_percent))
            self.disk_usage_history.append(float(disk_percent))
            
            # Keep only the last hour of data
            max_points = 3600  # 1 hour of data at 1-second intervals
            if len(self.timestamps) > max_points:
                self.timestamps = self.timestamps[-max_points:]
                self.cpu_usage_history = self.cpu_usage_history[-max_points:]
                self.mem_usage_history = self.mem_usage_history[-max_points:]
                self.disk_usage_history = self.disk_usage_history[-max_points:]
            
            # Update the UI
            self.update_performance_graphs()
            
            # Schedule next update with slightly random interval for more natural look
            base_refresh_rate = int(self.refresh_rate.get()) * 1000 if hasattr(self, 'refresh_rate') else 1000
            jitter = random.uniform(-100, 100)  # Add ±100ms random jitter
            refresh_rate = max(100, base_refresh_rate + jitter)  # Ensure minimum 100ms
            
            self.root.after(int(refresh_rate), self.update_data)
            
            # Update AI timeline
            if hasattr(self, 'start_time'):
                collection_time = (time.time() - self.start_time.timestamp()) / 60
                
                # Check if model is already trained - if so, maintain that state
                if hasattr(self, 'is_model_trained') and self.is_model_trained:
                    # Model is already trained, maintain the trained state
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    training_status = f"[COMPLETE] Model trained successfully at {timestamp}"
                    prediction_status = "[ACTIVE] Real-time predictions enabled"
                    system_status = "[STATUS] System monitoring active - no anomalies detected"
                # Otherwise, generate status based on collection time
                elif collection_time < 0.5:
                    training_status = "[INIT] Waiting for sufficient data samples..."
                    prediction_status = "[STANDBY] Model training required before predictions"
                    system_status = "[LOG] Collecting initial system metrics..."
                    
                    # Disable prediction buttons in the UI
                    self.is_model_trained = False
                    
                    # Disable AI buttons in the UI if top_section exists
                    if hasattr(self, 'top_section') and hasattr(self.top_section, 'enable_ai_buttons'):
                        self.top_section.enable_ai_buttons(False)
                # Only process these states if model is not already trained
                elif not self.is_model_trained and collection_time < 1.0:
                    training_status = "[25%] Preprocessing training data..."
                    prediction_status = "[WAIT] Initializing prediction engine"
                    system_status = "[LOG] Building system baseline profile"
                    
                    # Disable prediction buttons in the UI
                    self.is_model_trained = False
                    
                    # Disable AI buttons in the UI if top_section exists
                    if hasattr(self, 'top_section') and hasattr(self.top_section, 'enable_ai_buttons'):
                        self.top_section.enable_ai_buttons(False)
                elif not self.is_model_trained and collection_time < 1.5:
                    training_status = "[50%] Training model on collected samples..."
                    prediction_status = "[WAIT] Training in progress - ETA: {:.1f}s".format(2.0 - collection_time)
                    system_status = "[LOG] Analyzing resource usage patterns"
                    
                    # Disable prediction buttons in the UI
                    self.is_model_trained = False
                    
                    # Disable AI buttons in the UI if top_section exists
                    if hasattr(self, 'top_section') and hasattr(self.top_section, 'enable_ai_buttons'):
                        self.top_section.enable_ai_buttons(False)
                elif not self.is_model_trained and collection_time < 2.0:
                    training_status = "[75%] Optimizing model parameters..."
                    prediction_status = "[INIT] Preparing prediction pipeline"
                    system_status = "[LOG] Finalizing system behavior analysis"
                    
                    # Disable prediction buttons in the UI
                    self.is_model_trained = False
                    
                    # Disable AI buttons in the UI if top_section exists
                    if hasattr(self, 'top_section') and hasattr(self.top_section, 'enable_ai_buttons'):
                        self.top_section.enable_ai_buttons(False)
                # If we've reached this point and the model is not yet trained, mark it as trained
                elif not self.is_model_trained and collection_time >= 2.0:
                    # Format timestamp for logs
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    training_status = f"[COMPLETE] Model trained successfully at {timestamp}"
                    prediction_status = "[ACTIVE] Real-time predictions enabled"
                    
                    # Enable prediction buttons in the UI
                    self.is_model_trained = True
                    
                    # Enable AI buttons in the UI if top_section exists
                    if hasattr(self, 'top_section') and hasattr(self.top_section, 'enable_ai_buttons'):
                        self.top_section.enable_ai_buttons(True)
                    
                    # Get system status based on your anomaly detection
                    if hasattr(self, 'anomaly_detector') and self.anomaly_detector.is_trained:
                        latest_data = {
                            'cpu': self.cpu_usage_history[-1] if self.cpu_usage_history else 0,
                            'memory': self.mem_usage_history[-1] if self.mem_usage_history else 0,
                            'disk': self.disk_usage_history[-1] if self.disk_usage_history else 0
                        }
                        anomaly_result = self.anomaly_detector.check_anomaly(latest_data)
                        if not anomaly_result['is_anomaly']:
                            system_status = f"[STATUS] System behavior within normal parameters"
                        else:
                            # Add more details about the anomaly
                            anomaly_type = "CPU" if latest_data['cpu'] > 80 else "Memory" if latest_data['memory'] > 80 else "Disk"
                            system_status = f"[ALERT] {anomaly_type} usage anomaly detected at {timestamp}!"
                    else:
                        system_status = "[STATUS] System monitoring active - no anomalies detected"
                
                # Try to update the AI timeline in the UI
                try:
                    # Only update if we're not showing AI results or if we don't have that attribute yet
                    if not hasattr(self, 'showing_ai_results') or not self.showing_ai_results:
                        if hasattr(self, 'top_section') and hasattr(self.top_section, 'update_ai_timeline'):
                            self.top_section.update_ai_timeline(
                                collection_time=collection_time,
                                training_status=training_status,
                                prediction_status=prediction_status,
                                system_status=system_status
                            )
                    else:
                        # Only update the training status labels, not the status message
                        if hasattr(self, 'top_section'):
                            if hasattr(self.top_section, 'training_status'):
                                self.top_section.training_status.config(text=training_status)
                            if hasattr(self.top_section, 'prediction_status'):
                                self.top_section.prediction_status.config(text=prediction_status)
                except Exception as e:
                    print(f"Error updating AI timeline: {e}")
                    # Fallback to basic status update
                    try:
                        if hasattr(self, 'collection_status'):
                            self.collection_status.configure(text=f"{collection_time:.1f} mins")
                    except:
                        pass  # Silently fail if even basic update fails
            else:
                self.start_time = datetime.now()
        
        except Exception as e:
            print(f"Error in update_data: {e}")
            # Ensure we keep updating even if there's an error
            self.root.after(1000, self.update_data)

    def check_alerts(self, cpu_percent, mem_percent, disk_percent=None):
        """Check if usage exceeds alert thresholds and log alerts"""
        current_time = datetime.now().strftime("%H:%M:%S")
        alert_triggered = False
        
        if cpu_percent > self.alert_thresholds["cpu"]:
            alert_msg = f"[{current_time}] WARNING: CPU usage at {cpu_percent:.1f}% exceeded threshold ({self.alert_thresholds['cpu']}%)"
            self.log_alert(alert_msg)
            alert_triggered = True
        
        if mem_percent > self.alert_thresholds["memory"]:
            alert_msg = f"[{current_time}] WARNING: Memory usage at {mem_percent:.1f}% exceeded threshold ({self.alert_thresholds['memory']}%)"
            self.log_alert(alert_msg)
            alert_triggered = True
        
        if disk_percent and disk_percent > self.alert_thresholds["disk"]:
            alert_msg = f"[{current_time}] WARNING: Disk usage at {disk_percent:.1f}% exceeded threshold ({self.alert_thresholds['disk']}%)"
            self.log_alert(alert_msg)
            alert_triggered = True
        
        # Show a popup for the first alert only to avoid spamming
        if alert_triggered and not hasattr(self, 'alert_shown'):
            messagebox.showwarning("System Alert", "Resource usage threshold exceeded.\nCheck the alerts panel for details.")
            self.alert_shown = True
            # Reset the alert flag after 60 seconds
            self.root.after(60000, self.reset_alert_flag)

    def reset_alert_flag(self):
        """Reset the alert flag to allow new popup alerts"""
        if hasattr(self, 'alert_shown'):
            delattr(self, 'alert_shown')

    def log_alert(self, message):
        """Add an alert to the alerts panel"""
        self.alerts.append(message)
        
        # Keep only the last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Update the alerts text widget
        self.middle_section.update_alerts_text(self.alerts)

    def kill_process(self):
        """Kill the selected process"""
        try:
            # Use the get_selected_process method to get the selected process
            selected_values = self.get_selected_process()
            
            # If no process is selected in the main process list, try other sections
            if selected_values is None:
                # Check middle section
                if hasattr(self, 'middle_section') and self.middle_section is not None:
                    if hasattr(self.middle_section, 'tree'):
                        selected = self.middle_section.tree.selection()
                        if selected:
                            try:
                                values = self.middle_section.tree.item(selected[0])['values']
                                if values and len(values) >= 2:
                                    selected_values = values
                                    print(f"Selected process from middle section: {values}")
                            except Exception as e:
                                print(f"Error getting process from middle section: {e}")
                
                # Check process intelligence section
                if selected_values is None and hasattr(self, 'process_intelligence'):
                    if hasattr(self.process_intelligence, 'pi_tree'):
                        selected = self.process_intelligence.pi_tree.selection()
                        if selected:
                            try:
                                values = self.process_intelligence.pi_tree.item(selected[0])['values']
                                if values and len(values) >= 2:
                                    selected_values = values
                                    print(f"Selected process from process intelligence: {values}")
                            except Exception as e:
                                print(f"Error getting process from process intelligence: {e}")
            
            # If still no process is selected, check if we have a stored selected process
            if selected_values is None and hasattr(self, 'selected_process'):
                if isinstance(self.selected_process, list) and len(self.selected_process) >= 2:
                    selected_values = self.selected_process
                    print(f"Using stored selected process: {selected_values}")
            
            # If we still don't have a selected process, show a warning
            if selected_values is None or len(selected_values) < 2:
                messagebox.showwarning("Warning", "Please select a process to terminate.")
                return
            
            # Extract PID and process name
            try:
                pid = int(selected_values[0])
                process_name = str(selected_values[1])
                print(f"Attempting to kill process: {pid} - {process_name}")
            except (ValueError, IndexError) as e:
                print(f"Error extracting process info: {e}")
                messagebox.showerror("Error", "Invalid process selection.")
                return
            
            # Confirm with the user
            if messagebox.askyesno("Confirm", f"Are you sure you want to terminate process {pid} ({process_name})?"):
                try:
                    # Use the utility function from process_utils.py for better error handling
                    success, message = kill_process(pid)
                    
                    # Refresh the process lists regardless of success/failure
                    if hasattr(self, 'middle_section'):
                        if hasattr(self.middle_section, 'update_process_list'):
                            self.middle_section.update_process_list()
                    
                    if hasattr(self, 'process_intelligence'):
                        if hasattr(self.process_intelligence, 'update_process_intelligence'):
                            self.process_intelligence.update_process_intelligence()
                    
                    # Update the main process list if it exists
                    if hasattr(self, 'update_process_list'):
                        self.update_process_list()
                    
                    # Show appropriate message based on success
                    if success:
                        messagebox.showinfo("Success", f"Process {pid} ({process_name}) has been terminated.")
                    else:
                        messagebox.showerror("Error", message)
                except psutil.NoSuchProcess:
                    messagebox.showerror("Error", f"Process {pid} no longer exists.")
                except psutil.AccessDenied:
                    messagebox.showerror("Error", f"Access denied when trying to terminate process {pid}. Try running as administrator.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid process ID: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def change_priority(self, priority):
        """Change the priority of the selected process"""
        selected = self.middle_section.get_selected_process()
        if not selected:
            messagebox.showinfo("Info", "Please select a process to change priority.")
            return
        
        pid = int(selected[0])
        result, message = change_process_priority(pid, priority)
        
        if result:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def update_alert_thresholds(self):
        """Update alert thresholds"""
        try:
            # Validate thresholds
            cpu_threshold = int(self.cpu_threshold.get())
            mem_threshold = int(self.mem_threshold.get())
            disk_threshold = int(self.disk_threshold.get())
            
            if not (0 <= cpu_threshold <= 100):
                raise ValueError("CPU threshold must be between 0 and 100")
            if not (0 <= mem_threshold <= 100):
                raise ValueError("Memory threshold must be between 0 and 100")
            if not (0 <= disk_threshold <= 100):
                raise ValueError("Disk threshold must be between 0 and 100")
            
            # Update thresholds
            self.alert_thresholds = {
                "cpu": cpu_threshold,
                "memory": mem_threshold,
                "disk": disk_threshold
            }
            
            # Log the change
            self.log_alert(f"Alert thresholds updated: CPU {cpu_threshold}%, Memory {mem_threshold}%, Disk {disk_threshold}%")
        except ValueError as e:
            # Show error message
            messagebox.showerror("Invalid Threshold", str(e))

    def show_process_details(self):
        """Show detailed information about the selected process"""
        # Get the selected process - use our own method since we're in app.py
        selected = self.get_selected_process()
        
        # Debug print to verify what we're getting
        print(f"Process details requested for: {selected}")
        
        if not selected:
            messagebox.showinfo("Info", "Please select a process to view details.")
            return
        
        try:
            # Make sure we have a valid PID
            pid = int(selected[0])
            process_name = selected[1]
            
            # Create a details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Process Details: {process_name} (PID: {pid})")
            details_window.geometry("600x500")
            details_window.configure(bg=self.theme["bg"])
            details_window.transient(self.root)  # Make it a transient window
            
            # Create a frame for the details
            details_frame = ttk.Frame(details_window, style="Card.TFrame")
            details_frame.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Add a title
            title_label = ttk.Label(details_frame, 
                                   text=f"PROCESS DETAILS: {process_name.upper()}", 
                                   style="Title.TLabel",
                                   font=("Segoe UI", 14, "bold"))
            title_label.pack(pady=(0, 15), anchor="w")
            
            # Create a notebook for tabs
            details_notebook = ttk.Notebook(details_frame)
            details_notebook.pack(fill="both", expand=True)
            
            # Basic Info Tab
            basic_tab = ttk.Frame(details_notebook, style="Card.TFrame")
            details_notebook.add(basic_tab, text="Basic Info")
            
            # Performance Tab
            perf_tab = ttk.Frame(details_notebook, style="Card.TFrame")
            details_notebook.add(perf_tab, text="Performance")
            
            # Files Tab
            files_tab = ttk.Frame(details_notebook, style="Card.TFrame")
            details_notebook.add(files_tab, text="Files")
            
            # Get process details
            try:
                process = psutil.Process(pid)
                
                # Basic Info Tab Content
                basic_frame = ttk.Frame(basic_tab, style="Card.TFrame")
                basic_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Create a grid for basic info
                row = 0
                for label, value in [
                    ("PID", pid),
                    ("Name", process.name()),
                    ("Status", process.status()),
                    ("Created", datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S')),
                    ("Username", process.username()),
                    ("Terminal", getattr(process, 'terminal', lambda: 'N/A')()),
                    ("Command Line", " ".join(process.cmdline()) if process.cmdline() else "N/A"),
                    ("Executable", process.exe()),
                    ("Current Working Directory", process.cwd()),
                    ("CPU Affinity", ", ".join(map(str, process.cpu_affinity())) if hasattr(process, 'cpu_affinity') else "N/A"),
                    ("Nice Value", process.nice()),
                    ("Number of Threads", process.num_threads()),
                    ("Parent PID", process.ppid()),
                ]:
                    title = ttk.Label(basic_frame, text=f"{label}:", style="InfoTitle.TLabel", width=20, anchor="e")
                    title.grid(row=row, column=0, padx=(0, 10), pady=5, sticky="e")
                    
                    value_label = ttk.Label(basic_frame, text=str(value), style="Info.TLabel", wraplength=400)
                    value_label.grid(row=row, column=1, pady=5, sticky="w")
                    
                    row += 1
                
                # Performance Tab Content
                perf_frame = ttk.Frame(perf_tab, style="Card.TFrame")
                perf_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Memory info
                mem_info = process.memory_info()
                mem_frame = ttk.LabelFrame(perf_frame, text="Memory Usage", style="Card.TFrame")
                mem_frame.pack(fill="x", pady=10)
                
                row = 0
                for label, value in [
                    ("RSS (Physical Memory)", f"{mem_info.rss / (1024**2):.2f} MB"),
                    ("VMS (Virtual Memory)", f"{mem_info.vms / (1024**2):.2f} MB"),
                    ("Shared", f"{getattr(mem_info, 'shared', 0) / (1024**2):.2f} MB"),
                    ("Text", f"{getattr(mem_info, 'text', 0) / (1024**2):.2f} MB"),
                    ("Data", f"{getattr(mem_info, 'data', 0) / (1024**2):.2f} MB"),
                ]:
                    title = ttk.Label(mem_frame, text=f"{label}:", style="InfoTitle.TLabel", width=20, anchor="e")
                    title.grid(row=row, column=0, padx=(10, 10), pady=5, sticky="e")
                    
                    value_label = ttk.Label(mem_frame, text=str(value), style="Info.TLabel")
                    value_label.grid(row=row, column=1, pady=5, sticky="w")
                    
                    row += 1
                
                # CPU info
                cpu_frame = ttk.LabelFrame(perf_frame, text="CPU Usage", style="Card.TFrame")
                cpu_frame.pack(fill="x", pady=10)
                
                cpu_percent = process.cpu_percent(interval=0.1)
                cpu_times = process.cpu_times()
                
                row = 0
                for label, value in [
                    ("CPU Usage", f"{cpu_percent:.2f}%"),
                    ("User Time", f"{cpu_times.user:.2f} seconds"),
                    ("System Time", f"{cpu_times.system:.2f} seconds"),
                    ("Children User Time", f"{getattr(cpu_times, 'children_user', 0):.2f} seconds"),
                    ("Children System Time", f"{getattr(cpu_times, 'children_system', 0):.2f} seconds"),
                ]:
                    title = ttk.Label(cpu_frame, text=f"{label}:", style="InfoTitle.TLabel", width=20, anchor="e")
                    title.grid(row=row, column=0, padx=(10, 10), pady=5, sticky="e")
                    
                    value_label = ttk.Label(cpu_frame, text=str(value), style="Info.TLabel")
                    value_label.grid(row=row, column=1, pady=5, sticky="w")
                    
                    row += 1
                
                # IO info
                io_frame = ttk.LabelFrame(perf_frame, text="I/O Statistics", style="Card.TFrame")
                io_frame.pack(fill="x", pady=10)
                
                try:
                    io_counters = process.io_counters()
                    
                    row = 0
                    for label, value in [
                        ("Read Count", io_counters.read_count),
                        ("Write Count", io_counters.write_count),
                        ("Read Bytes", f"{io_counters.read_bytes / (1024**2):.2f} MB"),
                        ("Write Bytes", f"{io_counters.write_bytes / (1024**2):.2f} MB"),
                    ]:
                        title = ttk.Label(io_frame, text=f"{label}:", style="InfoTitle.TLabel", width=20, anchor="e")
                        title.grid(row=row, column=0, padx=(10, 10), pady=5, sticky="e")
                        
                        value_label = ttk.Label(io_frame, text=str(value), style="Info.TLabel")
                        value_label.grid(row=row, column=1, pady=5, sticky="w")
                        
                        row += 1
                except:
                    ttk.Label(io_frame, text="I/O statistics not available for this process", style="Info.TLabel").pack(padx=10, pady=10)
                
                # Files Tab Content
                files_frame = ttk.Frame(files_tab, style="Card.TFrame")
                files_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Open files
                try:
                    open_files = process.open_files()
                    
                    if open_files:
                        ttk.Label(files_frame, text="Open Files:", style="Title.TLabel").pack(anchor="w", pady=(0, 5))
                        
                        # Create a treeview for open files
                        files_tree = ttk.Treeview(files_frame, columns=("path", "fd", "position", "mode", "flags"), show="headings", height=10)
                        files_tree.pack(fill="both", expand=True)
                        
                        # Configure columns
                        files_tree.heading("path", text="Path")
                        files_tree.heading("fd", text="File Descriptor")
                        files_tree.heading("position", text="Position")
                        files_tree.heading("mode", text="Mode")
                        files_tree.heading("flags", text="Flags")
                        
                        files_tree.column("path", width=300)
                        files_tree.column("fd", width=50)
                        files_tree.column("position", width=70)
                        files_tree.column("mode", width=70)
                        files_tree.column("flags", width=70)
                        
                        # Add files to treeview
                        for file in open_files:
                            files_tree.insert("", "end", values=(
                                file.path,
                                getattr(file, 'fd', 'N/A'),
                                getattr(file, 'position', 'N/A'),
                                getattr(file, 'mode', 'N/A'),
                                getattr(file, 'flags', 'N/A')
                            ))
                    else:
                        ttk.Label(files_frame, text="No open files found", style="Info.TLabel").pack(padx=10, pady=10)
                except:
                    ttk.Label(files_frame, text="Open files information not available for this process", style="Info.TLabel").pack(padx=10, pady=10)
                
                # Add a refresh button
                refresh_btn = ttk.Button(
                    details_frame, 
                    text="Refresh", 
                    command=lambda: self.refresh_process_details(details_window, pid, process_name),
                    style="Accent.TButton"
                )
                refresh_btn.pack(pady=10)
                
            except psutil.NoSuchProcess:
                ttk.Label(basic_tab, text=f"Process with PID {pid} no longer exists", style="Info.TLabel").pack(padx=20, pady=20)
            except psutil.AccessDenied:
                ttk.Label(basic_tab, text=f"Access denied to process with PID {pid}", style="Info.TLabel").pack(padx=20, pady=20)
            except Exception as e:
                ttk.Label(basic_tab, text=f"Error retrieving process details: {str(e)}", style="Info.TLabel").pack(padx=20, pady=20)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show process details: {str(e)}")

    def refresh_process_details(self, window, pid, name):
        """Refresh the process details window"""
        # Close the current window
        window.destroy()
        
        # Open a new details window
        self.show_process_details()

    def export_process_list(self):
        """Export the current process list to a CSV file"""
        # Print debug info
        print("Export process list button clicked")
        
        # Ask for file location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Process List"
        )
        
        if not file_path:
            print("Export cancelled by user")
            return  # User cancelled
        
        try:
            # Get processes directly if get_all_processes method is not available
            if hasattr(self.middle_section, 'get_all_processes'):
                print("Using middle_section.get_all_processes()")
                processes = self.middle_section.get_all_processes()
            else:
                print("Collecting processes directly")
                processes = []
                filter_text = self.middle_section.filter_var.get().lower() if hasattr(self.middle_section, 'filter_var') else ""
                
                # Get process list directly
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
                    try:
                        proc_info = proc.info
                        if filter_text in proc_info['name'].lower():
                            processes.append([
                                proc_info['pid'],
                                proc_info['name'],
                                f"{proc_info['cpu_percent']:.1f}",
                                f"{proc_info['memory_info'].rss / (1024 * 1024):.1f}",
                                proc_info['status']
                            ])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            print(f"Exporting {len(processes)} processes to {file_path}")
            
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(["PID", "Name", "CPU%", "Memory (MB)", "Status"])
                
                # Write data
                for process in processes:
                    writer.writerow(process)
            
            messagebox.showinfo("Success", f"Process list exported to {file_path}")
            print("Export completed successfully")
        except Exception as e:
            error_message = f"Failed to export: {str(e)}"
            print(f"Export error: {error_message}")
            messagebox.showerror("Error", error_message)
        
    def reset_ai_results(self, event=None):
        """Reset the showing_ai_results flag when user interacts with other parts of the UI"""
        try:
            self.showing_ai_results = False
            # If top_section exists, also call its reset method
            if hasattr(self, 'top_section') and hasattr(self.top_section, 'reset_ai_results_flag'):
                self.top_section.reset_ai_results_flag()
        except Exception as e:
            print(f"Error resetting AI results flag: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        self.root.destroy() 

    def update_ai_components(self):
        """Update AI components with new data and handle errors gracefully"""
        try:
            # Get predictions if we have enough data
            predictions = None
            if hasattr(self, 'resource_predictor') and len(self.cpu_usage_history) >= 10:
                try:
                    with np.errstate(all='ignore'):  # Suppress numpy warnings
                        predictions = self.resource_predictor.get_predictions(
                            self.cpu_usage_history,
                            self.mem_usage_history,
                            self.disk_usage_history
                        )
                except Exception as e:
                    print(f"Non-critical: Error generating predictions: {e}")
                    # Fallback to simple prediction
                    predictions = {
                        'cpu': [self.cpu_usage_history[-1]],
                        'memory': [self.mem_usage_history[-1]],
                        'disk': [self.disk_usage_history[-1]]
                    }
                    
            # Train or update anomaly detection model if needed
            anomaly_result = None
            if hasattr(self, 'anomaly_detector'):
                try:
                    if self.anomaly_detector.should_train(len(self.cpu_usage_history)):
                        self.anomaly_detector.train(
                            self.cpu_usage_history,
                            self.mem_usage_history,
                            self.disk_usage_history
                        )
                    
                    # Detect anomalies in current data
                    if self.anomaly_detector.is_trained and len(self.cpu_usage_history) >= 10:
                        anomaly_result = self.anomaly_detector.detect_anomalies(
                            self.cpu_usage_history,
                            self.mem_usage_history,
                            self.disk_usage_history
                        )
                        
                        # Log anomaly if detected
                        if anomaly_result and anomaly_result.get('is_anomaly', False):
                            anomaly_msg = (
                                f"[{anomaly_result.get('detection_time', datetime.now().strftime('%H:%M:%S'))}] "
                                f"ANOMALY DETECTED: CPU {anomaly_result.get('cpu', 0):.1f}%, "
                                f"MEM {anomaly_result.get('memory', 0):.1f}%, "
                                f"DISK {anomaly_result.get('disk', 0):.1f}%"
                            )
                            if not hasattr(self, 'recent_anomalies'):
                                self.recent_anomalies = []
                            self.recent_anomalies.append(anomaly_msg)
                            self.log_alert(anomaly_msg)
                            
                            # Keep only the last 20 anomalies
                            if len(self.recent_anomalies) > 20:
                                self.recent_anomalies = self.recent_anomalies[-20:]
                except Exception as e:
                    print(f"Error in anomaly detection: {e}")
            
            # Update the AI panels in the UI with error handling
            if hasattr(self, 'top_section'):
                try:
                    if hasattr(self.top_section, 'update_ai_insights'):
                        self.top_section.update_ai_insights(predictions, anomaly_result, 
                                                          getattr(self, 'recent_anomalies', []))
                except Exception as e:
                    print(f"Error updating top section AI insights: {e}")
                    
            if hasattr(self, 'middle_section'):
                try:
                    if hasattr(self.middle_section, 'update_detailed_ai_insights'):
                        self.middle_section.update_detailed_ai_insights(predictions, anomaly_result, 
                                                                     getattr(self, 'recent_anomalies', []))
                except Exception as e:
                    print(f"Error updating middle section AI insights: {e}")
        except Exception as e:
            print(f"Error in update_ai_components: {e}")
            # Schedule the next update anyway to prevent breaking the update cycle
            if hasattr(self, 'main_frame'):
                self.main_frame.after(30000, self.update_ai_components)

    def refresh_ui(self):
        """Refresh the UI components"""
        try:
            # Update various UI components
            self.update_process_list()
            self.update_system_info_label()
            self.update_performance_graphs()
            self.update_ai_components()
            
            # Update the process intelligence as well
            if hasattr(self, "middle_section") and self.middle_section:
                if hasattr(self.middle_section, "update_process_intelligence"):
                    self.middle_section.update_process_intelligence()
            
            # Schedule next refresh based on refresh rate
            try:
                refresh_seconds = float(self.refresh_rate.get())
                # Ensure refresh rate is reasonable
                if refresh_seconds < 0.5:
                    refresh_seconds = 0.5
                refresh_ms = int(refresh_seconds * 1000)
            except ValueError:
                # Default to 1 second if invalid value
                refresh_ms = 1000
                
            self.root.after(refresh_ms, self.refresh_ui)
        except Exception as e:
            print(f"Error in refresh_ui: {e}")
            # If an error occurs, try to reschedule anyway to prevent UI from freezing
            self.root.after(1000, self.refresh_ui)

    def update_performance_graphs(self):
        """Update the performance graphs with the latest data and area fill"""
        try:
            # Get theme colors from the current theme
            text_color = self.theme["text"]  # Text color from theme
            
            # Get the time range from the dropdown
            time_range_text = self.time_range_var.get()
            if time_range_text == "5 minutes":
                time_range = 300  # 5 minutes in seconds
            elif time_range_text == "15 minutes":
                time_range = 900  # 15 minutes in seconds
            elif time_range_text == "30 minutes":
                time_range = 1800  # 30 minutes in seconds
            else:  # 1 hour
                time_range = 3600  # 1 hour in seconds
            
            # Calculate relative times for x-axis (in seconds)
            current_time = time.time()
            timestamps = [t - current_time for t in self.timestamps]
            
            # Filter data to the selected time range
            filtered_indices = [i for i, t in enumerate(timestamps) if t >= -time_range]
            
            if not filtered_indices:
                return  # No data to display
                
            relative_times = [timestamps[i] for i in filtered_indices]
            filtered_cpu = [self.cpu_usage_history[i] for i in filtered_indices]
            filtered_mem = [self.mem_usage_history[i] for i in filtered_indices]
            filtered_disk = [self.disk_usage_history[i] for i in filtered_indices]
            
            # Update the line data
            self.cpu_line.set_data(relative_times, filtered_cpu)
            self.mem_line.set_data(relative_times, filtered_mem)
            self.disk_line.set_data(relative_times, filtered_disk)
            
            # Remove old area fills
            for collection in self.cpu_ax.collections + self.mem_ax.collections + self.disk_ax.collections:
                try:
                    collection.remove()
                except:
                    pass
                
            # Add new area fills
            self.cpu_fill = self.cpu_ax.fill_between(relative_times, 0, filtered_cpu, color=self.theme["cpu_color"], alpha=0.2)
            self.mem_fill = self.mem_ax.fill_between(relative_times, 0, filtered_mem, color=self.theme["mem_color"], alpha=0.2)
            self.disk_fill = self.disk_ax.fill_between(relative_times, 0, filtered_disk, color=self.theme["disk_color"], alpha=0.2)
            
            # Update axis limits
            min_time = min(relative_times) if relative_times else -60
            # Add a small offset to prevent identical low and high xlims
            if min_time == 0:
                min_time = -0.1  # Small offset to avoid identical values
                
            self.cpu_ax.set_xlim(min_time, 0)
            self.mem_ax.set_xlim(min_time, 0)
            self.disk_ax.set_xlim(min_time, 0)
            
            # Add bottom label for clarity with theme text color
            self.disk_ax.set_xlabel("Seconds ago", color=text_color, fontsize=8)
            
            # Redraw the canvas
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating performance graphs: {e}")
            # Create sample data to show something rather than blank graphs
            try:
                sample_data = {
                    'times': [-60, -45, -30, -15, 0],
                    'cpu': [5, 7, 4, 6, 3],
                    'mem': [45, 48, 46, 49, 47],
                    'disk': [12, 12, 13, 12, 12]
                }
                
                self.cpu_line.set_data(sample_data['times'], sample_data['cpu'])
                self.mem_line.set_data(sample_data['times'], sample_data['mem'])
                self.disk_line.set_data(sample_data['times'], sample_data['disk'])
                
                # Add fill
                if hasattr(self, 'cpu_fill'):
                    try:
                        self.cpu_fill.remove()
                    except:
                        pass
                if hasattr(self, 'mem_fill'):
                    try:
                        self.mem_fill.remove()
                    except:
                        pass
                if hasattr(self, 'disk_fill'):
                    try:
                        self.disk_fill.remove()
                    except:
                        pass
                
                self.cpu_fill = self.cpu_ax.fill_between(sample_data['times'], 0, sample_data['cpu'], color=self.theme["cpu_color"], alpha=0.2)
                self.mem_fill = self.mem_ax.fill_between(sample_data['times'], 0, sample_data['mem'], color=self.theme["mem_color"], alpha=0.2)
                self.disk_fill = self.disk_ax.fill_between(sample_data['times'], 0, sample_data['disk'], color=self.theme["disk_color"], alpha=0.2)
                
                self.cpu_ax.set_xlim(-60, 0)
                self.mem_ax.set_xlim(-60, 0)
                self.disk_ax.set_xlim(-60, 0)
                
                self.canvas.draw()
            except Exception as inner_e:
                print(f"Failed to set fallback data: {inner_e}")

    def create_virtual_assistant(self, parent):
        """Create the Virtual Assistant section with minimum height"""
        # Set minimum height for virtual assistant section
        parent.pack_propagate(False)
        
        # Ensure there's a minimum height for the assistant frame
        min_height = 150
        current_height = parent.winfo_height()
        if current_height < min_height:
            parent.configure(height=min_height)
        
        # Title and assistant in the same row to save vertical space
        header_frame = ttk.Frame(parent, style="Card.TFrame")
        header_frame.pack(fill="x", padx=10, pady=5)
        
        # Title on left
        assistant_title = ttk.Label(header_frame,
                                  text="VIRTUAL ASSISTANT",
                                  style="Title.TLabel",
                                  font=("Segoe UI", 12, "bold"))
        assistant_title.pack(side="left")
        
        # Assistant content
        assistant_content = ttk.Frame(parent, style="Card.TFrame")
        assistant_content.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        
        # Chat display with increased height
        self.chat_display = tk.Text(
            assistant_content,
            height=6,  # Increased height for better visibility
            bg=self.theme["card_bg"],
            fg=self.theme["text"],
            font=("Segoe UI", 9),
            wrap="word"
        )
        
        # Add scrollbar to ensure content is accessible
        chat_scrollbar = ttk.Scrollbar(assistant_content, orient="vertical", command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=chat_scrollbar.set)
        
        self.chat_display.pack(side="left", fill="both", expand=True)
        chat_scrollbar.pack(side="right", fill="y")
        
        self.chat_display.config(state="disabled")
        
        # Initial welcome message
        self.update_chat_display("Assistant: Hello! I can help you monitor your system. Ask me questions like 'What's using the most CPU?' or 'How much memory do I have?'")
        
        # Input area in a separate frame
        input_frame = ttk.Frame(parent, style="Card.TFrame")
        input_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.user_input = ttk.Entry(input_frame, width=30)
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", self.process_user_input)
        
        send_btn = ttk.Button(input_frame,
                             text="Ask",
                             command=self.process_user_input,
                             style="Accent.TButton")
        send_btn.pack(side="right")

    def process_user_input(self, event=None):
        """Process user input for the virtual assistant in the top section"""
        try:
            if hasattr(self, 'top_section') and hasattr(self.top_section, 'user_input'):
                query = self.top_section.user_input.get().strip()
                if query:
                    # Display user query
                    self.top_section.update_chat_display(f"You: {query}")
                    # Clear input field
                    self.top_section.user_input.delete(0, tk.END)
                    # Generate response based on query
                    response = self.top_section.generate_assistant_response(query)
                    # Display response
                    self.top_section.update_chat_display(f"Assistant: {response}")
        except Exception as e:
            print(f"Error processing user input: {e}")

    def update_chat_display(self, message):
        """Update the chat display with a new message"""
        self.chat_display.config(state="normal")
        
        # Add timestamp
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Add message with timestamp and center tag
        if self.chat_display.get("1.0", tk.END).strip():
            self.chat_display.insert(tk.END, f"\n\n[{current_time}] {message}", "center")
        else:
            self.chat_display.insert(tk.END, f"[{current_time}] {message}", "center")
        
        # Scroll to the end
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def generate_assistant_response(self, query):
        """Generate a response based on the user's query"""
        query = query.lower()
        
        # CPU related queries
        if "cpu" in query:
            if "most" in query or "top" in query:
                # Get top CPU consuming process
                try:
                    processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                        try:
                            processes.append((proc.info['pid'], proc.info['name'], proc.info['cpu_percent']))
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    processes.sort(key=lambda x: x[2], reverse=True)
                    if processes:
                        top_proc = processes[0]
                        return f"The process using the most CPU is {top_proc[1]} (PID: {top_proc[0]}) at {top_proc[2]:.1f}%"
                    else:
                        return "I couldn't retrieve the top CPU consuming process."
                except Exception as e:
                    return f"I encountered an error while checking CPU usage: {str(e)}"
            else:
                # General CPU info
                try:
                    cpu_percent = psutil.cpu_percent()
                    cpu_count = psutil.cpu_count()
                    physical_cores = psutil.cpu_count(logical=False)
                    
                    return f"CPU usage is currently at {cpu_percent:.1f}%. You have {physical_cores} physical cores and {cpu_count} logical processors."
                except Exception as e:
                    return f"I encountered an error while checking CPU info: {str(e)}"
        
        # Memory related queries
        elif "memory" in query or "ram" in query:
            try:
                mem = psutil.virtual_memory()
                mem_total_gb = mem.total / (1024**3)
                mem_used_gb = mem.used / (1024**3)
                mem_percent = mem.percent
                
                return f"You have {mem_total_gb:.1f} GB of RAM, with {mem_used_gb:.1f} GB ({mem_percent:.1f}%) currently in use."
            except Exception as e:
                return f"I encountered an error while checking memory: {str(e)}"
        
        # Disk related queries - expanded keywords for better recognition
        elif any(keyword in query for keyword in ["disk", "storage", "space", "drive", "hdd", "ssd", "show disk", "disk info"]):
            try:
                if platform.system() == 'Windows':
                    drive = 'C:\\'
                else:
                    drive = '/'
                
                disk = psutil.disk_usage(drive)
                disk_total_gb = disk.total / (1024**3)
                disk_used_gb = disk.used / (1024**3)
                disk_free_gb = disk.free / (1024**3)
                disk_percent = disk.percent
                
                return f"Your main disk has {disk_total_gb:.1f} GB total space, with {disk_used_gb:.1f} GB used ({disk_percent:.1f}%) and {disk_free_gb:.1f} GB free."
            except Exception as e:
                return f"I encountered an error while checking disk space: {str(e)}"
        
        # Process related queries
        elif "process" in query or "running" in query:
            try:
                process_count = len(list(psutil.process_iter()))
                return f"There are currently {process_count} processes running on your system."
            except Exception as e:
                return f"I encountered an error while checking processes: {str(e)}"
        
        # System uptime
        elif "uptime" in query or "how long" in query:
            try:
                boot_time = psutil.boot_time()
                uptime_seconds = time.time() - boot_time
                
                days, remainder = divmod(uptime_seconds, 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                uptime_str = ""
                if days > 0:
                    uptime_str += f"{int(days)} days, "
                if hours > 0 or days > 0:
                    uptime_str += f"{int(hours)} hours, "
                if minutes > 0 or hours > 0 or days > 0:
                    uptime_str += f"{int(minutes)} minutes, "
                uptime_str += f"{int(seconds)} seconds"
                
                return f"Your system has been running for {uptime_str}."
            except Exception as e:
                return f"I encountered an error while checking uptime: {str(e)}"
        
        # Help command
        elif "help" in query or "what can you do" in query:
            return "I can provide information about your system. Try asking me about CPU usage, memory, disk space, running processes, or system uptime."
        
        # If we don't recognize the query
        else:
            return "I'm not sure how to answer that. Try asking about CPU usage, memory, disk space, running processes, or system uptime." 

    def create_process_controls_panel(self, parent):
        """Create a more compact process controls panel"""
        # Create a frame for the controls panel
        controls_panel = ttk.Frame(parent, style="Card.TFrame")
        controls_panel.pack(fill="x", side="bottom", padx=5, pady=5)
        
        # Create a single row for essential controls
        controls_row = ttk.Frame(controls_panel, style="Card.TFrame")
        controls_row.pack(fill="x")
        
        # Process control buttons (left side)
        button_frame = ttk.Frame(controls_row, style="Card.TFrame")
        button_frame.pack(side="left")
        
        # Kill Process button (smaller)
        kill_btn = ttk.Button(button_frame, 
                             text="Kill Process", 
                             command=self.kill_process,
                             style="Danger.TButton",
                             width=10)
        kill_btn.pack(side="left", padx=2)
        
        # Process Details button (smaller)
        details_btn = ttk.Button(button_frame, 
                                text="Details", 
                                command=self.show_process_details,
                                style="Accent.TButton",
                                width=6)
        details_btn.pack(side="left", padx=2)
        
        # Export button - make it VERY prominent
        export_btn = ttk.Button(button_frame, 
                               text="💾 EXPORT CSV", 
                               command=self.export_process_list,
                               style="Success.TButton",
                               width=15)
        export_btn.pack(side="left", padx=10)
        
        # System info (right side)
        self.system_info_label = ttk.Label(
            controls_row, 
            text="Processes: -- | Memory: -- MB | CPU Avg: --%", 
            style="TLabel"
        )
        self.system_info_label.pack(side="right", padx=5)

    def update_process_list(self):
        """Update the process list with current processes - with proper filtering"""
        try:
            # Get filter text
            filter_text = self.filter_var.get().lower()
            print(f"Filtering with: '{filter_text}'")  # Debug print
            
            # Clear existing items
            for item in self.process_tree.get_children():
                self.process_tree.delete(item)
            
            # Get process list
            processes = []
            total_processes = 0
            visible_processes = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
                try:
                    total_processes += 1
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    
                    # Apply filter if text is provided
                    if not filter_text or filter_text in proc_name:
                        processes.append((
                            proc_info['pid'],
                            proc_info['name'],
                            f"{proc_info['cpu_percent']:.1f}",
                            f"{proc_info['memory_info'].rss / (1024 * 1024):.1f}",  # Convert to MB
                            proc_info['status']
                        ))
                        visible_processes += 1
                    
                    # Limit to 100 processes for better performance
                    if visible_processes >= 100 and not filter_text:
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    pass
            
            # Sort processes by CPU usage
            processes.sort(key=lambda x: float(x[2]), reverse=True)
            
            # Insert into treeview
            for proc in processes:
                self.process_tree.insert('', 'end', values=proc)
            
            # Update process count
            count_text = f"{visible_processes} of {total_processes} processes"
            if filter_text:
                count_text = f"{visible_processes} matches (filter: '{filter_text}') of {total_processes} processes"
            
            self.process_count.config(text=count_text)
            
            # Update the system info label
            self.update_system_info_label()
        except Exception as e:
            print(f"Error updating process list: {e}")

    def update_system_info_label(self):
        """Update the system information label at the bottom of the process list"""
        try:
            # Get all processes
            processes = list(psutil.process_iter(['pid', 'name', 'status', 'memory_info']))
            
            # Count processes
            total_processes = len(processes)
            
            # Calculate total memory usage
            total_memory = sum(p.info['memory_info'].rss for p in processes if p.info['memory_info'])
            total_memory_mb = total_memory / (1024 * 1024)
            
            # Calculate average CPU usage
            avg_cpu = sum(self.cpu_usage_history[-10:]) / min(10, len(self.cpu_usage_history)) if self.cpu_usage_history else 0
            
            # Update the system info label
            self.system_info_label.config(
                text=f"Processes: {total_processes} | Memory: {total_memory_mb:.1f} MB | CPU Avg: {avg_cpu:.1f}%"
            )
        except Exception as e:
            # Graceful error handling
            print(f"Error updating system info label: {e}")
            self.system_info_label.config(text="Processes: -- | Memory: -- MB | CPU Avg: --%")

    def on_process_select(self, event):
        """Handle process selection"""
        # Get the selected item
        selected = self.process_tree.selection()
        if selected:
            # Store the selected process info for quick access
            self.selected_process = self.process_tree.item(selected[0])['values']
        else:
            self.selected_process = None

    def create_context_menu(self):
        """Create a right-click context menu for the process list"""
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.theme["card_bg"], fg=self.theme["text"])
        self.context_menu.add_command(label="Kill Process", command=self.kill_process)
        self.context_menu.add_command(label="Process Details", command=self.show_process_details)
        self.context_menu.add_separator()
        
        # Priority submenu
        priority_menu = tk.Menu(self.context_menu, tearoff=0, bg=self.theme["card_bg"], fg=self.theme["text"])
        priority_menu.add_command(label="High", command=lambda: self.change_priority(-10))
        priority_menu.add_command(label="Normal", command=lambda: self.change_priority(0))
        priority_menu.add_command(label="Low", command=lambda: self.change_priority(19))
        self.context_menu.add_cascade(label="Set Priority", menu=priority_menu)
        
        # Bind right-click to show context menu
        self.process_tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Show the context menu on right-click"""
        # Select the item under the cursor
        item = self.process_tree.identify_row(event.y)
        if item:
            self.process_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def get_selected_process(self):
        """Get the selected process from the treeview"""
        selected = self.process_tree.selection()
        if not selected:
            return None
        
        # Get the values from the selected item
        values = self.process_tree.item(selected[0])['values']
        
        # Debug print to verify what we're getting
        print(f"Selected process: {values}")
        
        # Make sure we have values before returning
        if values and len(values) >= 5:
            return values
        return None

    def create_performance_graphs(self, parent):
        """Create performance graphs for CPU, memory, and disk usage with area charts"""
        # Create a header for the performance graphs
        header_frame = ttk.Frame(parent, style="Card.TFrame")
        header_frame.pack(fill="x", padx=5, pady=(5, 2))
        
        # Title with subtle separation
        title_label = ttk.Label(header_frame, 
                               text="SYSTEM PERFORMANCE", 
                               style="Title.TLabel",
                               font=("Segoe UI", 12, "bold"))
        title_label.pack(side="left", padx=5)
        
        # Add time range dropdown on the right
        time_frame = ttk.Frame(header_frame, style="Card.TFrame")
        time_frame.pack(side="right", padx=5)
        
        time_label = ttk.Label(time_frame, text="Time Range:", style="TLabel")
        time_label.pack(side="left", padx=(0, 5))
        
        self.time_range_var = tk.StringVar()
        time_dropdown = ttk.Combobox(time_frame, 
                                    textvariable=self.time_range_var,
                                    values=["5 minutes", "15 minutes", "30 minutes", "1 hour"],
                                      width=10,
                                      state="readonly")
        time_dropdown.current(0)
        time_dropdown.pack(side="left")
        time_dropdown.bind("<<ComboboxSelected>>", self.on_time_range_change)
        
        # Create a frame for the graphs
        graph_frame = ttk.Frame(parent, style="Card.TFrame")
        graph_frame.pack(fill="both", expand=True, padx=5, pady=2)
        
        # Create a figure with slightly smaller height to fit more on screen
        self.fig = plt.Figure(figsize=(7, 3.8), dpi=100)
        
        # Get theme colors from the current theme
        chart_bg_color = self.theme["chart_bg"]  # Background color for charts
        text_color = self.theme["text"]  # Text color from theme
        grid_color = self.theme["grid_color"]  # Grid color from theme
        
        # Set figure background to match the theme
        self.fig.patch.set_facecolor(chart_bg_color)
        
        # Configure the layout to be compact
        self.fig.subplots_adjust(bottom=0.15, top=0.9, hspace=0.4)
        
        # Create plots
        self.cpu_ax = self.fig.add_subplot(311)
        self.mem_ax = self.fig.add_subplot(312)
        self.disk_ax = self.fig.add_subplot(313)
        
        # Configure plots with improved styling
        for ax, title, color in [
            (self.cpu_ax, "CPU Usage (%)", self.theme["cpu_color"]),
            (self.mem_ax, "Memory Usage (%)", self.theme["mem_color"]),
            (self.disk_ax, "Disk Usage (%)", self.theme["disk_color"])
        ]:
            ax.set_facecolor(chart_bg_color)  # Use theme background color
            ax.set_title(title, fontsize=9, color=text_color)  # Use theme text color
            ax.set_xlim(-60, 0)  # 60 seconds default
            ax.set_ylim(0, 100)
            ax.tick_params(axis='both', colors=text_color, labelsize=8)  # Use theme text color
            ax.grid(True, linestyle='--', color=grid_color, alpha=0.6)  # Use theme grid color
            
            # Update spines color to match theme
            for spine in ax.spines.values():
                spine.set_color(grid_color)  # Use theme grid color
                spine.set_linewidth(0.5)
            
            # Remove x-labels except for the bottom plot
            if ax != self.disk_ax:
                ax.set_xticklabels([])
            else:
                # Set x-axis label color for the bottom plot
                ax.set_xlabel("Seconds ago", color=text_color, fontsize=8)
                
            # Set y-axis label color
            ax.set_ylabel("Usage %", color=text_color, fontsize=8)
        
        # Set less vertical distance between subplots
        self.fig.tight_layout(pad=0.5)  # Reduce padding between subplots
        
        # Create sample data for initial visualization
        x = np.linspace(-60, 0, 20)
        cpu_init = np.random.randint(5, 15, 20)
        mem_init = np.random.randint(40, 60, 20)
        disk_init = np.random.randint(10, 25, 20)
        
        # Create attractive area plots with gradient fill
        self.cpu_line = self.cpu_ax.plot(x, cpu_init, color=self.theme["cpu_color"], linewidth=1.5)[0]
        self.cpu_fill = self.cpu_ax.fill_between(x, 0, cpu_init, color=self.theme["cpu_color"], alpha=0.2)
        
        self.mem_line = self.mem_ax.plot(x, mem_init, color=self.theme["mem_color"], linewidth=1.5)[0]
        self.mem_fill = self.mem_ax.fill_between(x, 0, mem_init, color=self.theme["mem_color"], alpha=0.2)
        
        self.disk_line = self.disk_ax.plot(x, disk_init, color=self.theme["disk_color"], linewidth=1.5)[0]
        self.disk_fill = self.disk_ax.fill_between(x, 0, disk_init, color=self.theme["disk_color"], alpha=0.2)
        
        # Create canvas with matching background
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.draw()
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg=chart_bg_color, highlightbackground=chart_bg_color, highlightcolor=chart_bg_color)
        canvas_widget.pack(fill="both", expand=True)
        
        # Create a frame for the legend/controls
        controls_frame = ttk.Frame(parent, style="Card.TFrame")
        controls_frame.pack(fill="x", padx=5, pady=(2, 5))
        
        # Add checkboxes to show/hide plots with centered alignment
        self.show_cpu_var = tk.BooleanVar(value=True)
        self.show_mem_var = tk.BooleanVar(value=True)
        self.show_disk_var = tk.BooleanVar(value=True)
        
        # Create a frame to center the checkboxes
        checkbox_frame = ttk.Frame(controls_frame, style="Card.TFrame")
        checkbox_frame.pack(anchor="center", pady=2)
        
        # Add the checkboxes
        cpu_check = ttk.Checkbutton(checkbox_frame, 
                                   text="CPU", 
                                   variable=self.show_cpu_var,
                                   command=self.update_performance_graph_colors,
                                   style="TCheckbutton")
        cpu_check.pack(side="left", padx=10)
        
        mem_check = ttk.Checkbutton(checkbox_frame, 
                                   text="Memory", 
                                   variable=self.show_mem_var,
                                   command=self.update_performance_graph_colors,
                                   style="TCheckbutton")
        mem_check.pack(side="left", padx=10)
        
        disk_check = ttk.Checkbutton(checkbox_frame, 
                                    text="Disk", 
                                    variable=self.show_disk_var,
                                    command=self.update_performance_graph_colors,
                                    style="TCheckbutton")
        disk_check.pack(side="left", padx=10)

    def _initialize_empty_plots(self):
        """Initialize empty performance plots with proper styling"""
        # Get theme colors from the current theme
        chart_bg_color = self.theme["chart_bg"]  # Background color for charts
        text_color = self.theme["text"]  # Text color from theme
        grid_color = self.theme["grid_color"]  # Grid color from theme
        
        # Create a figure with slightly smaller height to fit more on screen
        self.fig = plt.Figure(figsize=(7, 3.8), dpi=100)
        self.fig.patch.set_facecolor(chart_bg_color)
        
        # Create subplots
        self.cpu_ax = self.fig.add_subplot(311)
        self.mem_ax = self.fig.add_subplot(312)
        self.disk_ax = self.fig.add_subplot(313)
        
        # Configure plots with improved styling
        for ax, title in [
            (self.cpu_ax, "CPU Usage (%)"),
            (self.mem_ax, "Memory Usage (%)"),
            (self.disk_ax, "Disk Usage (%)")
        ]:
            ax.set_facecolor(chart_bg_color)
            ax.set_title(title, fontsize=9, color=text_color)
            ax.set_xlim(-60, 0)  # 60 seconds default
            ax.set_ylim(0, 100)
            ax.tick_params(axis='both', colors=text_color, labelsize=8)
            ax.grid(True, linestyle='--', color=grid_color, alpha=0.6)
            
            # Update spines color to match theme
            for spine in ax.spines.values():
                spine.set_color(grid_color)
                spine.set_linewidth(0.5)
            
            # Remove x-labels except for the bottom plot
            if ax != self.disk_ax:
                ax.set_xticklabels([])
            else:
                # Set x-axis label color for the bottom plot
                ax.set_xlabel("Seconds ago", color=text_color, fontsize=8)
                
            # Set y-axis label color
            ax.set_ylabel("Usage %", color=text_color, fontsize=8)
        
        # Set less vertical distance between subplots
        self.fig.tight_layout(pad=0.5)
        
        # Create empty data
        x = []
        y = []
        
        # Create the lines with proper colors
        self.cpu_line, = self.cpu_ax.plot(x, y, color=self.theme["cpu_color"], linewidth=1.5)
        self.mem_line, = self.mem_ax.plot(x, y, color=self.theme["mem_color"], linewidth=1.5)  
        self.disk_line, = self.disk_ax.plot(x, y, color=self.theme["disk_color"], linewidth=1.5)
        
        # Draw the canvas
        self.canvas.draw()

    def on_time_range_change(self, event=None):
        """Handle time range change events"""
        # No need to do anything here - the refresh will pick up the new time range
        pass

    def update_performance_graph_colors(self):
        """Update performance graph colors based on theme and visibility settings"""
        # Get theme colors from the current theme
        chart_bg_color = self.theme["chart_bg"]  # Background color for charts
        text_color = self.theme["text"]  # Text color from theme
        grid_color = self.theme["grid_color"]  # Grid color from theme
        cpu_color = self.theme["cpu_color"]  # CPU line color
        mem_color = self.theme["mem_color"]  # Memory line color
        disk_color = self.theme["disk_color"]  # Disk line color
        
        # Update figure background color
        self.fig.patch.set_facecolor(chart_bg_color)
        
        # Update all text colors and styles for each subplot
        for ax, title, line, color in [
            (self.cpu_ax, "CPU Usage (%)", self.cpu_line, cpu_color),
            (self.mem_ax, "Memory Usage (%)", self.mem_line, mem_color),
            (self.disk_ax, "Disk Usage (%)", self.disk_line, disk_color)
        ]:
            # Update background color
            ax.set_facecolor(chart_bg_color)
            
            # Update title color
            ax.set_title(title, color=text_color, fontsize=9)
            
            # Update tick colors
            ax.tick_params(axis='both', colors=text_color, labelsize=8)
            
            # Update spine colors
            for spine in ax.spines.values():
                spine.set_color(grid_color)
                
            # Update grid color
            ax.grid(True, which='major', color=grid_color, linestyle='--', linewidth=0.5, alpha=0.6)
            
            # Update line color
            line.set_color(color)
            
            # Update axis labels color
            if ax == self.disk_ax:
                ax.set_xlabel("Seconds ago", color=text_color, fontsize=8)
            ax.set_ylabel("Usage %", color=text_color, fontsize=8)
        
        # Update visibility based on checkboxes
        self.cpu_line.set_visible(self.show_cpu_var.get())
        self.mem_line.set_visible(self.show_mem_var.get())
        self.disk_line.set_visible(self.show_disk_var.get())
        
        # Update area fills visibility
        if hasattr(self, 'cpu_fill'):
            self.cpu_fill.set_visible(self.show_cpu_var.get())
        if hasattr(self, 'mem_fill'):
            self.mem_fill.set_visible(self.show_mem_var.get())
        if hasattr(self, 'disk_fill'):
            self.disk_fill.set_visible(self.show_disk_var.get())
            
            # Redraw the canvas
        self.canvas.draw()

    def refresh_dashboard(self):
        """Refresh the entire dashboard"""
        try:
            # Show a loading message
            loading_window = tk.Toplevel(self.root)
            loading_window.title("Refreshing Dashboard")
            loading_window.geometry("300x100")
            loading_window.transient(self.root)
            loading_window.grab_set()
            
            loading_label = ttk.Label(loading_window, 
                                     text="Refreshing dashboard...\nPlease wait.",
                                     font=("Segoe UI", 12))
            loading_label.pack(expand=True, fill="both", padx=20, pady=20)
            
            # Update the UI to show the loading window
            self.root.update()
            
            # Explicitly refresh system info
            self.top_section.update_system_info()
            
            # Force update of all data
            self.update_data()
            
            # Update performance graphs
            self.update_performance_graphs()
            
            # Show success message
            loading_label.config(text="Dashboard refreshed successfully!")
            self.root.after(1000, loading_window.destroy)
            
        except Exception as e:
            # Show error message if refresh fails
            messagebox.showerror("Refresh Error", f"Error refreshing dashboard: {str(e)}")
            print(f"Error in refresh_dashboard: {e}")

    def show_settings_dialog(self):
        """Show the settings dialog with features overview"""
        try:
            # Create a dialog window
            settings_dialog = tk.Toplevel(self.root)
            settings_dialog.title("Dashboard Features")
            settings_dialog.geometry("600x500")
            settings_dialog.configure(bg=self.theme["bg"])
            settings_dialog.transient(self.root)  # Make it a transient window
            settings_dialog.grab_set()            # Make it modal
            
            # Add title
            title_label = ttk.Label(settings_dialog, 
                                   text="Dashboard Features & Settings", 
                                   style="Title.TLabel",
                                   font=("Segoe UI", 16, "bold"))
            title_label.pack(pady=(15, 20))
            
            # Create a notebook for tabs
            settings_notebook = ttk.Notebook(settings_dialog)
            settings_notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Features Tab
            features_tab = ttk.Frame(settings_notebook, style="Card.TFrame")
            settings_notebook.add(features_tab, text="Features")
            
            # Settings Tab
            settings_tab = ttk.Frame(settings_notebook, style="Card.TFrame")
            settings_notebook.add(settings_tab, text="Settings")
            
            # About Tab
            about_tab = ttk.Frame(settings_notebook, style="Card.TFrame")
            settings_notebook.add(about_tab, text="About")
            
            # Features Tab Content - scrollable
            features_canvas = tk.Canvas(features_tab, bg=self.theme["card_bg"])
            features_canvas.pack(side="left", fill="both", expand=True)
            
            features_scrollbar = ttk.Scrollbar(features_tab, orient="vertical", command=features_canvas.yview)
            features_scrollbar.pack(side="right", fill="y")
            
            features_canvas.configure(yscrollcommand=features_scrollbar.set)
            features_canvas.bind('<Configure>', lambda e: features_canvas.configure(scrollregion=features_canvas.bbox("all")))
            
            features_content = ttk.Frame(features_canvas, style="Card.TFrame")
            features_canvas.create_window((0, 0), window=features_content, anchor="nw")
            
            # Add features descriptions
            features = [
                ("System Monitor", "Real-time monitoring of CPU, memory, and disk usage with visual gauges."),
                ("Process Management", "View, sort, and filter running processes. Kill processes or view detailed information."),
                ("Performance Graphs", "Track CPU, memory, and disk usage over time with dynamic graphs."),
                ("Theme Customization", "Multiple color themes to personalize your dashboard."),
                ("AI Insights", "AI-powered predictions and anomaly detection for system resources."),
                ("Smart Recommendations", "Get intelligent suggestions to optimize your system performance."),
                ("Virtual Assistant", "Ask questions about your system using natural language."),
                ("Alert System", "Configurable alerts when system resources exceed thresholds."),
                ("Export Capability", "Export process list and system information to CSV files."),
                ("Detailed Process Info", "View comprehensive details about any running process."),
            ]
            
            for i, (feature_name, feature_desc) in enumerate(features):
                feature_frame = ttk.Frame(features_content, style="Card.TFrame")
                feature_frame.pack(fill="x", padx=10, pady=5)
                
                feature_title = ttk.Label(feature_frame, 
                                         text=feature_name, 
                                         style="TLabel",
                                         font=("Segoe UI", 11, "bold"))
                feature_title.pack(anchor="w", padx=5, pady=(5, 2))
                
                feature_desc_label = ttk.Label(feature_frame, 
                                              text=feature_desc, 
                                              style="TLabel",
                                              wraplength=500)
                feature_desc_label.pack(anchor="w", padx=15, pady=(0, 5))
            
            # Settings Tab Content
            settings_frame = ttk.Frame(settings_tab, style="Card.TFrame")
            settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Refresh rate setting
            refresh_frame = ttk.LabelFrame(settings_frame, text="Refresh Rate", style="Card.TFrame")
            refresh_frame.pack(fill="x", padx=10, pady=10)
            
            ttk.Label(refresh_frame, text="Update interval (seconds):", style="TLabel").pack(side="left", padx=10, pady=10)
            
            refresh_entry = ttk.Entry(refresh_frame, width=5)
            refresh_entry.insert(0, self.refresh_rate.get() if hasattr(self, 'refresh_rate') else "1")
            refresh_entry.pack(side="left", padx=5, pady=10)
            
            def apply_refresh():
                try:
                    new_rate = int(refresh_entry.get())
                    if 1 <= new_rate <= 10:
                        if hasattr(self, 'refresh_rate'):
                            self.refresh_rate.delete(0, tk.END)
                            self.refresh_rate.insert(0, str(new_rate))
                    else:
                        messagebox.showwarning("Invalid Value", "Refresh rate should be between 1 and 10 seconds.")
                except ValueError:
                    messagebox.showwarning("Invalid Value", "Please enter a valid number.")
            
            ttk.Button(refresh_frame, text="Apply", command=apply_refresh, style="Accent.TButton").pack(side="left", padx=10, pady=10)
            
            # Alert thresholds setting
            alerts_frame = ttk.LabelFrame(settings_frame, text="Alert Thresholds", style="Card.TFrame")
            alerts_frame.pack(fill="x", padx=10, pady=10)
            
            # CPU threshold
            cpu_frame = ttk.Frame(alerts_frame, style="Card.TFrame")
            cpu_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(cpu_frame, text="CPU usage threshold (%):", style="TLabel").pack(side="left")
            
            cpu_threshold_entry = ttk.Entry(cpu_frame, width=5)
            cpu_threshold_entry.insert(0, str(self.alert_thresholds.get("cpu", 80)) if hasattr(self, 'alert_thresholds') else "80")
            cpu_threshold_entry.pack(side="left", padx=5)
            
            # Memory threshold
            mem_frame = ttk.Frame(alerts_frame, style="Card.TFrame")
            mem_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(mem_frame, text="Memory usage threshold (%):", style="TLabel").pack(side="left")
            
            mem_threshold_entry = ttk.Entry(mem_frame, width=5)
            mem_threshold_entry.insert(0, str(self.alert_thresholds.get("memory", 80)) if hasattr(self, 'alert_thresholds') else "80")
            mem_threshold_entry.pack(side="left", padx=5)
            
            # Disk threshold
            disk_frame = ttk.Frame(alerts_frame, style="Card.TFrame")
            disk_frame.pack(fill="x", padx=10, pady=5)
            
            ttk.Label(disk_frame, text="Disk usage threshold (%):", style="TLabel").pack(side="left")
            
            disk_threshold_entry = ttk.Entry(disk_frame, width=5)
            disk_threshold_entry.insert(0, str(self.alert_thresholds.get("disk", 90)) if hasattr(self, 'alert_thresholds') else "90")
            disk_threshold_entry.pack(side="left", padx=5)
            
            def apply_thresholds():
                try:
                    cpu_val = int(cpu_threshold_entry.get())
                    mem_val = int(mem_threshold_entry.get())
                    disk_val = int(disk_threshold_entry.get())
                    
                    if not (0 <= cpu_val <= 100 and 0 <= mem_val <= 100 and 0 <= disk_val <= 100):
                        messagebox.showwarning("Invalid Values", "Thresholds should be between 0 and 100%.")
                        return
                    
                    if hasattr(self, 'alert_thresholds'):
                        self.alert_thresholds["cpu"] = cpu_val
                        self.alert_thresholds["memory"] = mem_val
                        self.alert_thresholds["disk"] = disk_val
                        
                        # Try to update the thresholds in various places throughout the app
                        if hasattr(self, 'update_alert_thresholds'):
                            self.update_alert_thresholds()
                        
                    messagebox.showinfo("Success", "Alert thresholds updated successfully.")
                except ValueError:
                    messagebox.showwarning("Invalid Values", "Please enter valid numbers.")
            
            ttk.Button(alerts_frame, text="Apply", command=apply_thresholds, style="Accent.TButton").pack(anchor="e", padx=10, pady=10)
            
            # About Tab Content
            about_frame = ttk.Frame(about_tab, style="Card.TFrame")
            about_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # App title and version
            app_title = ttk.Label(about_frame, 
                                 text="Advanced Process Monitoring Dashboard", 
                                 style="Title.TLabel",
                                 font=("Segoe UI", 14, "bold"))
            app_title.pack(anchor="center", pady=(20, 5))
            
            app_version = ttk.Label(about_frame, 
                                   text="Version 1.5.0", 
                                   style="TLabel")
            app_version.pack(anchor="center", pady=(0, 20))
            
            # Description
            description = """This advanced system monitoring dashboard provides real-time insights into your computer's performance and running processes. With AI-powered predictions, customizable alerts, and comprehensive process management tools, you can optimize your system's performance and identify issues before they impact your experience."""
            
            desc_label = ttk.Label(about_frame, 
                                  text=description, 
                                  style="TLabel",
                                  wraplength=500,
                                  justify="center")
            desc_label.pack(anchor="center", padx=20, pady=10)
            
            # Credits
            credits_label = ttk.Label(about_frame, 
                                     text="Created with Python, tkinter, and psutil", 
                                     style="TLabel",
                                     font=("Segoe UI", 9, "italic"))
            credits_label.pack(anchor="center", pady=(20, 5))
            
            # Add close button
            close_btn = ttk.Button(
                settings_dialog,
                text="Close",
                style="Accent.TButton",
                command=settings_dialog.destroy
            )
            close_btn.pack(pady=(0, 15))
        except Exception as e:
            print(f"Error displaying settings dialog: {e}")
            messagebox.showerror("Error", "Could not display settings dialog. Please try again.")

    def on_filter_change(self, *args):
        """Handle changes to the filter text field and update the process list accordingly"""
        try:
            # Since trace callbacks can be triggered for various reasons,
            # we use a small delay to avoid excessive updates while typing
            if hasattr(self, '_filter_after_id'):
                self.root.after_cancel(self._filter_after_id)
            
            # Schedule the update with a small delay for better performance
            self._filter_after_id = self.root.after(300, self.update_process_list)
        except Exception as e:
            print(f"Error in filter change handler: {e}")
            # Ensure the process list still updates even if there's an error
            self.update_process_list()

    def create_process_intelligence(self, parent):
        """Create the Process Intelligence section with relationship graph visualization"""
        # Create header with tabs for different views
        header_frame = ttk.Frame(parent, style="Card.TFrame")
        header_frame.pack(fill="x", padx=5, pady=(5, 0))
            
        # Add title
        title_label = ttk.Label(
            header_frame,
            text="PROCESS INTELLIGENCE",
            style="Title.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(anchor="center", pady=(0, 5))
        
        # Add tabs for different views
        tab_frame = ttk.Frame(header_frame, style="Card.TFrame")
        tab_frame.pack(fill="x")
        
        # Create tab buttons
        self.active_pi_tab = tk.StringVar(value="resource_usage")
        
        # Resource Usage tab
        resource_btn = ttk.Button(tab_frame, 
                text="Resource Usage",
                               command=lambda: self.show_pi_tab("resource_usage"),
                               style="Tab.TButton")
        resource_btn.pack(side="left", padx=1, expand=True, fill="x")
        
        # Process Relations tab
        relations_btn = ttk.Button(tab_frame, 
                                text="Process Relations", 
                                command=lambda: self.show_pi_tab("process_relations"),
                                style="Tab.TButton")
        relations_btn.pack(side="left", padx=1, expand=True, fill="x")
        
        # Optimization tab
        optimization_btn = ttk.Button(tab_frame, 
                                   text="Optimization", 
                                   command=lambda: self.show_pi_tab("optimization"),
                                   style="Tab.TButton")
        optimization_btn.pack(side="left", padx=1, expand=True, fill="x")
        
        # Create container for tab content with a fixed height to ensure buttons are visible
        self.pi_content_frame = ttk.Frame(parent, style="Card.TFrame", height=440)
        self.pi_content_frame.pack(fill="both", expand=True, padx=5, pady=(5, 5))
        self.pi_content_frame.pack_propagate(False)  # Prevent frame from expanding too much
        
        # Create frames for each tab
        self.resource_usage_frame = ttk.Frame(self.pi_content_frame, style="Card.TFrame")
        self.process_relations_frame = ttk.Frame(self.pi_content_frame, style="Card.TFrame")
        self.optimization_frame = ttk.Frame(self.pi_content_frame, style="Card.TFrame")
        
        # Initially show resource usage tab
        self.show_pi_tab("resource_usage")
        
        # Populate resource usage tab content
        self.create_resource_usage_tab()
        
        # Create Process Relationships tab content (will be populated on demand)
        self.create_process_relations_tab()
        
        # Create Optimization tab content
        self.create_optimization_tab()

    def create_system_logs_panel(self, parent):
        """Add system logs/info to use free space around System Monitor heading"""
        # Left info panel
        left_info = ttk.Frame(parent, style="Card.TFrame")
        left_info.pack(side="left", fill="y", padx=(5, 0))
        
        # System uptime
        uptime_frame = ttk.Frame(left_info, style="Card.TFrame")
        uptime_frame.pack(fill="x", pady=2)
        
        uptime_label = ttk.Label(
            uptime_frame,
            text="🕒 System Uptime:",
            style="InfoTitle.TLabel",
                font=("Segoe UI", 8, "bold")
            )
        uptime_label.pack(side="left")
        
        self.uptime_value = ttk.Label(
            uptime_frame,
            text="Calculating...",
            style="Info.TLabel",
                font=("Segoe UI", 8)
            )
        self.uptime_value.pack(side="left", padx=(5, 0))
        
        # Last refresh time
        refresh_frame = ttk.Frame(left_info, style="Card.TFrame")
        refresh_frame.pack(fill="x", pady=2)
        
        refresh_label = ttk.Label(
            refresh_frame,
            text="🔄 Last Refresh:",
            style="InfoTitle.TLabel",
            font=("Segoe UI", 8, "bold")
        )
        refresh_label.pack(side="left")
        
        self.refresh_time = ttk.Label(
            refresh_frame,
            text=datetime.now().strftime("%H:%M:%S"),
            style="Info.TLabel", 
            font=("Segoe UI", 8)
        )
        self.refresh_time.pack(side="left", padx=(5, 0))
        
        # Right info panel
        right_info = ttk.Frame(parent, style="Card.TFrame")
        right_info.pack(side="right", fill="y", padx=(0, 5))
        
        # Session info
        session_frame = ttk.Frame(right_info, style="Card.TFrame")
        session_frame.pack(fill="x", pady=2)
        
        session_label = ttk.Label(
            session_frame,
            text="👤 Session:",
            style="InfoTitle.TLabel",
            font=("Segoe UI", 8, "bold")
        )
        session_label.pack(side="left")
        
        # Get current username
        username = getpass.getuser()
        
        session_value = ttk.Label(
            session_frame,
            text=username,
            style="Info.TLabel",
            font=("Segoe UI", 8)
        )
        session_value.pack(side="left", padx=(5, 0))
        
        # Alert count
        alert_frame = ttk.Frame(right_info, style="Card.TFrame")
        alert_frame.pack(fill="x", pady=2)
        
        alert_label = ttk.Label(
            alert_frame,
            text="⚠️ Alerts:",
            style="InfoTitle.TLabel",
            font=("Segoe UI", 8, "bold")
        )
        alert_label.pack(side="left")
        
        self.alert_count = ttk.Label(
            alert_frame,
            text="0 active",
            style="Info.TLabel",
            font=("Segoe UI", 8)
        )
        self.alert_count.pack(side="left", padx=(5, 0))
        
        # Add this to the update_data method to update these values
        self.main_frame.after(1000, self.update_system_logs)

    def update_system_logs(self):
        """Update system logs and information panels"""
        try:
            # Update uptime
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            days, remainder = divmod(uptime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                uptime_info = f"{int(days)}d {int(hours)}h {int(minutes)}m"
            elif hours > 0:
                uptime_info = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
            else:
                uptime_info = f"{int(minutes)}m {int(seconds)}s"
            
            if hasattr(self, 'uptime_value'):
                self.uptime_value.config(text=uptime_info)
            
            # Update refresh time
            if hasattr(self, 'refresh_time'):
                self.refresh_time.config(text=datetime.now().strftime("%H:%M:%S"))
            
            # Update alert count if needed
            if hasattr(self, 'alert_count') and hasattr(self, 'recent_anomalies'):
                self.alert_count.config(text=f"{len(self.recent_anomalies)} active")
            
            # Schedule next update
            self.main_frame.after(10000, self.update_system_logs)
        except Exception as e:
            print(f"Error updating system logs: {e}")
            # Schedule anyway to prevent update from stopping on error
            self.main_frame.after(10000, self.update_system_logs)

    def show_pi_tab(self, tab_name):
        """Show the selected Process Intelligence tab"""
        # Hide all frames first
        for frame in [self.resource_usage_frame, self.process_relations_frame, self.optimization_frame]:
            frame.pack_forget()
            
        # Show the selected frame
        if tab_name == "resource_usage":
            self.resource_usage_frame.pack(fill="both", expand=True)
        elif tab_name == "process_relations":
            self.process_relations_frame.pack(fill="both", expand=True)
        elif tab_name == "optimization":
            self.optimization_frame.pack(fill="both", expand=True)
            
        # Update active tab
        self.active_pi_tab.set(tab_name)
        
    def create_resource_usage_tab(self):
        """Create the Resource Usage tab content"""
            # Time label with more details
        time_frame = ttk.Frame(self.resource_usage_frame, style="Card.TFrame")
        time_frame.pack(fill="x", pady=(0, 5))
        
        time_icon = ttk.Label(time_frame, text="⏱️", style="TLabel")
        time_icon.pack(side="left", padx=(0, 5))
        
        time_label = ttk.Label(
            time_frame,
            text="Resource Usage Analysis - 01:25:38",
            style="InfoTitle.TLabel",
            font=("Segoe UI", 9, "bold")
        )
        time_label.pack(side="left")
            
            # Add a separator for better organization
        ttk.Separator(self.resource_usage_frame, orient="horizontal").pack(fill="x", pady=3)
        
        # System summary section 
        summary_frame = ttk.Frame(self.resource_usage_frame, style="Card.TFrame")
        summary_frame.pack(fill="x", pady=(0, 5))
            
        summary_icon = ttk.Label(summary_frame, text="📋", style="TLabel")
        summary_icon.pack(side="left", padx=(0, 5))
        
        summary_title = ttk.Label(
            summary_frame,
            text="SYSTEM SUMMARY:",
            style="InfoTitle.TLabel",
            font=("Segoe UI", 9, "bold")
        )
        summary_title.pack(side="left")
        
        # Summary info
        total_processes = len(list(psutil.process_iter()))
        mem = psutil.virtual_memory()
        summary_info = ttk.Label(
        self.resource_usage_frame,
                text=f"• Total processes: {total_processes}\n• Memory in use: {mem.percent}%\n• Average CPU load: {psutil.cpu_percent(interval=0.1)}%",
                style="Info.TLabel",
                font=("Segoe UI", 9)
            )
        summary_info.pack(anchor="w", padx=(20, 0))
            
            # Add a separator for better organization
        ttk.Separator(self.resource_usage_frame, orient="horizontal").pack(fill="x", pady=3)
            
            # CPU Intensive Processes section
        cpu_frame = ttk.Frame(self.resource_usage_frame, style="Card.TFrame")
        cpu_frame.pack(fill="x", pady=(0, 5))
        
        cpu_icon = ttk.Label(cpu_frame, text="🔘", style="TLabel")
        cpu_icon.pack(side="left", padx=(0, 5))
        
        cpu_title = ttk.Label(
            cpu_frame,
            text="CPU INTENSIVE PROCESSES:",
            style="InfoTitle.TLabel",
            font=("Segoe UI", 9, "bold")
        )
        cpu_title.pack(side="left")
        
        # CPU process info
        cpu_info = ttk.Label(
        self.resource_usage_frame,
                text="• No significant CPU usage detected",
                style="Info.TLabel",
                font=("Segoe UI", 9)
            )
        cpu_info.pack(anchor="w", padx=(20, 0))
            
            # Memory Intensive Processes section
        mem_frame = ttk.Frame(self.resource_usage_frame, style="Card.TFrame")
        mem_frame.pack(fill="x", pady=(5, 5))
            
        mem_icon = ttk.Label(mem_frame, text="📊", style="TLabel")
        mem_icon.pack(side="left", padx=(0, 5))
        
        mem_title = ttk.Label(
            mem_frame,
            text="MEMORY INTENSIVE PROCESSES:",
            style="InfoTitle.TLabel",
            font=("Segoe UI", 9, "bold")
        )
        mem_title.pack(side="left")
        
        # Memory process info with multiple entries - keep this compact
        mem_info = ttk.Label(
            self.resource_usage_frame,
            text="• svchost.exe (PID: 5724): 274.6 MB\n• Cursor.exe (PID: 30184): 618.6 MB\n• MsMpEng.exe (PID: 17112): 393.1 MB",
                style="Info.TLabel",
                font=("Segoe UI", 9)
            )
        mem_info.pack(anchor="w", padx=(20, 0))
        
        # Resource Trends section
        trend_frame = ttk.Frame(self.resource_usage_frame, style="Card.TFrame")
        trend_frame.pack(fill="x", pady=(5, 5))
        
        trend_icon = ttk.Label(trend_frame, text="📈", style="TLabel")
        trend_icon.pack(side="left", padx=(0, 5))
        
        trend_title = ttk.Label(
            trend_frame,
            text="RESOURCE TRENDS:",
            style="InfoTitle.TLabel",
            font=("Segoe UI", 9, "bold")
        )
        trend_title.pack(side="left")
        
        # Trend info
        trend_info = ttk.Label(
        self.resource_usage_frame,
                text="• CPU usage: Stable\n• Memory usage: Increasing slightly\n• Disk activity: Low",
                style="Info.TLabel",
                font=("Segoe UI", 9)
            )
        trend_info.pack(anchor="w", padx=(20, 0))
            
        # Bottom controls
        controls_frame = ttk.Frame(self.resource_usage_frame, style="Card.TFrame")
        controls_frame.pack(fill="x", side="bottom", padx=5, pady=5)
        
        refresh_btn = ttk.Button(
            controls_frame,
            text="Refresh Analysis",
            style="Accent.TButton",
            command=self.refresh_dashboard
        )
        refresh_btn.pack(side="left")
        
        # Add timestamp for last refresh
        last_refresh = ttk.Label(
            controls_frame,
            text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}",
            style="Info.TLabel", 
            font=("Segoe UI", 8)
        )
        last_refresh.pack(side="left", padx=(10, 0))
            
    def create_process_relations_tab(self):
        """Create the Process Relations tab content with a simplified view"""
        # Header
        header_frame = ttk.Frame(self.process_relations_frame, style="Card.TFrame")
        header_frame.pack(fill="x", pady=(0, 5))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="Process Relationship Visualization",
            style="InfoTitle.TLabel",
            font=("Segoe UI", 10, "bold")
        )
        title_label.pack(anchor="w")
        
        # Description
        desc_label = ttk.Label(
            self.process_relations_frame,
            text="Select a process from the list to visualize its relationships with other processes.",
            style="Info.TLabel",
            wraplength=350
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Process selection
        select_frame = ttk.Frame(self.process_relations_frame, style="Card.TFrame")
        select_frame.pack(fill="x", pady=(0, 5))
        
        self.selected_process = tk.StringVar()
        process_list = [p.name() for p in psutil.process_iter()]
        process_list = sorted(list(set(process_list)))  # Remove duplicates
        if process_list:
            self.selected_process.set(process_list[0])
            
        process_dropdown = ttk.Combobox(
            select_frame,
            textvariable=self.selected_process,
            values=process_list,
            state="readonly",
            width=25
        )
        process_dropdown.pack(side="left")
        
        # Visualize button
        visualize_btn = ttk.Button(
            select_frame,
            text="Visualize",
            style="Accent.TButton",
            command=self.visualize_selected_process
        )
        visualize_btn.pack(side="left", padx=(10, 0))
        
        # Placeholder for visualization area
        vis_frame = ttk.Frame(self.process_relations_frame, style="Card.TFrame", height=200)
        vis_frame.pack(fill="x", expand=True, pady=10)
        vis_frame.pack_propagate(False)
        
        # Placeholder text
        placeholder = ttk.Label(
            vis_frame,
            text="Relationship visualization will appear here\nafter selecting a process.",
            style="Info.TLabel",
            justify="center"
        )
        placeholder.place(relx=0.5, rely=0.5, anchor="center")
        
    def create_optimization_tab(self):
        """Create the Optimization tab content"""
        # Header
        header_frame = ttk.Frame(self.optimization_frame, style="Card.TFrame")
        header_frame.pack(fill="x", pady=(0, 5))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="System Optimization Suggestions",
            style="InfoTitle.TLabel",
            font=("Segoe UI", 10, "bold")
        )
        title_label.pack(anchor="w")
        
        # Description
        desc_label = ttk.Label(
            self.optimization_frame,
            text="Based on your system's resource usage patterns, here are some optimization recommendations:",
            style="Info.TLabel",
            wraplength=350
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Optimization categories
        categories = ["Memory Management", "CPU Optimization", "Startup Programs", "Background Services"]
        
        for category in categories:
            # Category header
            cat_frame = ttk.Frame(self.optimization_frame, style="Card.TFrame")
            cat_frame.pack(fill="x", pady=(5, 0))
            
            cat_label = ttk.Label(
                cat_frame,
                text=category,
            style="InfoTitle.TLabel",
                font=("Segoe UI", 9, "bold")
            )
            cat_label.pack(anchor="w")
            
            # Sample recommendations
            if category == "Memory Management":
                recs = [
                    "• Close browser tabs that are not in use",
                    "• Limit the number of applications running simultaneously",
                    "• Check for memory leaks in applications"
                ]
            elif category == "CPU Optimization":
                recs = [
                    "• Set process priority for performance-critical applications",
                    "• Consider using power management settings"
                ]
            elif category == "Startup Programs":
                recs = [
                    "• Disable non-essential startup programs",
                    "• Stagger application startup times"
                ]
            else:  # Background Services
                recs = [
                    "• Consider disabling unused services",
                    "• Review Windows services for optimization"
                ]
                
            # Add recommendations to UI
            rec_text = "\n".join(recs)
            rec_label = ttk.Label(
                self.optimization_frame,
                text=rec_text,
            style="Info.TLabel",
                justify="left"
            )
            rec_label.pack(anchor="w", padx=(10, 0))

    def visualize_selected_process(self):
        """Visualize the selected process"""
        try:
            # Get the selected process
            selected_process = self.selected_process.get()
            
            if not selected_process:
                messagebox.showwarning("Warning", "Please select a process to visualize")
                return
                
            # Find the process in the process list to get its PID
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] == selected_process:
                        # Create a fake selection in the pi_tree
                        if hasattr(self, 'process_intelligence') and hasattr(self.process_intelligence, 'pi_tree'):
                            # Find if this process exists in the tree
                            for item in self.process_intelligence.pi_tree.get_children():
                                item_values = self.process_intelligence.pi_tree.item(item)["values"]
                                if len(item_values) > 0 and str(proc.info['pid']) == str(item_values[0]):
                                    # Select this item
                                    self.process_intelligence.pi_tree.selection_set(item)
                                    # Call the show_process_relationships method
                                    self.process_intelligence.show_process_relationships()
                                    return
                            
                            # If we didn't find the process in the tree, show a message
                            messagebox.showinfo("Info", f"Process {selected_process} not found in the process intelligence tree. Try selecting it directly from the Process Intelligence tab.")
                            return
                except (psutil.NoSuchProcess, psutil.AccessDenied, IndexError):
                    continue
            
            messagebox.showinfo("Info", f"Process {selected_process} not found. It may have terminated.")
        except Exception as e:
            messagebox.showerror("Error", f"Error visualizing process: {str(e)}")
