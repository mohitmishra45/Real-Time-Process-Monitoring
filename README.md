import tkinter as tk
from tkinter import ttk

class Footer:
    def __init__(self, root, app):
        """Initialize the footer with process controls and system alerts"""
        self.app = app
        self.theme = app.theme
        self.root = root
        
        self.frame = ttk.Frame(root, style="Card.TFrame")
        
      
        self.frame.pack(side="bottom", fill="x", padx=15, pady=(0, 15))
        
       
        self.container = ttk.Frame(self.frame, style="Card.TFrame")
        self.container.pack(fill="x", padx=10, pady=10)
        
        
        process_frame = ttk.Frame(self.container, style="Card.TFrame")
        process_frame.pack(side="left", fill="y", padx=(0, 20))
        
        
        process_title = ttk.Label(process_frame, 
                                 text="PROCESS CONTROLS", 
                                 style="Title.TLabel",
                                 font=("Segoe UI", 12, "bold"))
        process_title.pack(anchor="w", pady=(0, 10))
        
        
        button_frame = ttk.Frame(process_frame, style="Card.TFrame")
        button_frame.pack(fill="x")
        
        
        kill_btn = ttk.Button(button_frame, 
                             text="Kill Process", 
                             command=self.app.kill_process,
                             style="Danger.TButton")
        kill_btn.pack(side="left", padx=(0, 10))
        
        
        details_btn = ttk.Button(button_frame, 
                                text="Process Details", 
                                command=self.app.show_process_details,
                                style="Accent.TButton")
        details_btn.pack(side="left", padx=(0, 10))
        
       
        export_btn = ttk.Button(button_frame, 
                               text="Export Process List", 
                               command=self.app.export_process_list,
                               style="Success.TButton")
        export_btn.pack(side="left")
        
        
        alert_frame = ttk.Frame(self.container, style="Card.TFrame")
        alert_frame.pack(side="left", fill="y", expand=True, padx=20)
        
        
        alert_title = ttk.Label(alert_frame, 
                               text="SYSTEM ALERTS", 
                               style="Title.TLabel",
                               font=("Segoe UI", 12, "bold"))
        alert_title.pack(anchor="w", pady=(0, 10))
        
        
        threshold_frame = ttk.Frame(alert_frame, style="Card.TFrame")
        threshold_frame.pack(fill="x", pady=(0, 10))
        
        
        ttk.Label(threshold_frame, text="CPU:", style="TLabel").pack(side="left", padx=(0, 5))
        self.cpu_threshold = ttk.Entry(threshold_frame, width=5)
        self.cpu_threshold.insert(0, "80")
        self.cpu_threshold.pack(side="left", padx=(0, 10))
        
        
        ttk.Label(threshold_frame, text="Memory:", style="TLabel").pack(side="left", padx=(0, 5))
        self.mem_threshold = ttk.Entry(threshold_frame, width=5)
        self.mem_threshold.insert(0, "80")
        self.mem_threshold.pack(side="left", padx=(0, 10))
        
        
        ttk.Label(threshold_frame, text="Disk:", style="TLabel").pack(side="left", padx=(0, 5))
        self.disk_threshold = ttk.Entry(threshold_frame, width=5)
        self.disk_threshold.insert(0, "90")
        self.disk_threshold.pack(side="left", padx=(0, 10))
        
        
        ttk.Button(threshold_frame, text="Apply",
                   command=self.apply_thresholds,
                   style="Accent.TButton").pack(side="left")
        
        
        refresh_frame = ttk.Frame(self.container, style="Card.TFrame")
        refresh_frame.pack(side="right", fill="y", padx=(20, 0))
        
        
        refresh_title = ttk.Label(refresh_frame, 
                                 text="REFRESH RATE", 
                                 style="Title.TLabel",
                                 font=("Segoe UI", 12, "bold"))
        refresh_title.pack(anchor="w", pady=(0, 10))
        
        
        rate_frame = ttk.Frame(refresh_frame, style="Card.TFrame")
        rate_frame.pack(fill="x")
        
        ttk.Label(rate_frame, text="Update interval (seconds):", style="TLabel").pack(side="left", padx=(0, 10))
        
        self.refresh_rate = ttk.Entry(rate_frame, width=5)
        self.refresh_rate.insert(0, "1")  
        self.refresh_rate.pack(side="left")
    
    def apply_thresholds(self):
       
        try:
            cpu_threshold = int(self.cpu_threshold.get())
            mem_threshold = int(self.mem_threshold.get())
            disk_threshold = int(self.disk_threshold.get())
            self.app.update_alert_thresholds(cpu_threshold, mem_threshold, disk_threshold)
        except ValueError:
            
            pass
    
    def get_refresh_rate(self):
       
        try:
            return int(self.refresh_rate.get())
        except ValueError:
            return 1  

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import psutil
import platform
import os

def create_gauge(parent, theme, label):
    
    fig, ax = plt.subplots(figsize=(1.8, 1.8), dpi=100)  
    fig.patch.set_facecolor('none')  
    fig.patch.set_alpha(0.0)  
    ax.set_facecolor('none')  
    
    
    ax.set_xlim(-1, 1)
    ax.set_ylim(-0.5, 1)
    ax.axis('off')
    
    
    canvas = FigureCanvasTkAgg(fig, parent)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.configure(highlightthickness=0)  
    canvas_widget.pack(side="left", padx=2, pady=2)  
    
   
    canvas.draw()
    
    return fig, ax

def update_gauge(ax, percent, label, theme):
    
    try:
        
        if not (isinstance(percent, (int, float)) and np.isfinite(percent)):
            print(f"Warning: Invalid percent value for {label} gauge: {percent}")
            percent = 0  

        
        ax.clear()
        
        
        if label == "CPU":
            base_color = theme["cpu_color"]
        elif label == "MEM":
            base_color = theme["mem_color"]
        elif label == "DISK":
            base_color = theme["disk_color"]
        else:
            base_color = theme["accent"]
            
        
        if percent < 60:
            color = base_color
        elif percent < 80:
            color = theme["warning"]
        else:
            color = theme["danger"]
        
       
        sizes = [percent, 100-percent]
        colors = [color, theme["grid_color"]]
        
        
        wedges, _ = ax.pie(sizes, colors=colors, startangle=90, 
                     counterclock=False, wedgeprops={'edgecolor': 'none', 
                                                    'linewidth': 1, 
                                                    'antialiased': True,
                                                    'alpha': 0.9})  
        
       
        centre_circle = plt.Circle((0,0), 0.70, fc='none')  
        ax.add_patch(centre_circle)
        
        
        ax.text(0, 0.05, f"{percent:.1f}%", 
                ha='center', va='center', 
                fontsize=14, fontweight='bold',
                color=theme["text"])
        
        
        ax.text(0, -0.2, label, 
                ha='center', va='center', 
                fontsize=10, fontweight='bold',
                color=theme["text"])
        
       
        if label == "CPU":
            try:
                cpu_count = psutil.cpu_count()
                ax.text(0, -0.4, f"{cpu_count} threads", 
                        ha='center', va='center', 
                        fontsize=8, color=theme["text"])
            except Exception as e:
                print(f"Error getting CPU details: {e}")
        
        elif label == "MEM":
            try:
                mem = psutil.virtual_memory()
                used_gb = mem.used / (1024**3)
                total_gb = mem.total / (1024**3)
                ax.text(0, -0.4, f"{used_gb:.1f}/{total_gb:.1f}GB", 
                        ha='center', va='center', 
                        fontsize=8, color=theme["text"])
            except Exception as e:
                print(f"Error getting memory details: {e}")
        
        elif label == "DISK":
            try:
                if platform.system() == 'Windows':
                    try:
                        disk = psutil.disk_usage('C:\\')
                    except:
                        system_drive = os.environ.get('SystemDrive', 'C:')
                        disk = psutil.disk_usage(f"{system_drive}\\")
                else:
                    disk = psutil.disk_usage('/')
                
                free_gb = disk.free / (1024**3)
                ax.text(0, -0.4, f"{free_gb:.1f}GB free", 
                        ha='center', va='center', 
                        fontsize=8, color=theme["text"])
            except Exception as e:
                print(f"Error getting disk details: {e}")
        
       
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.axis('off')
        
    except Exception as e:
        print(f"Error updating gauge: {e}")
        
        ax.clear()
        ax.text(0, 0, f"{label}: {percent:.1f}%", 
                ha='center', va='center', 
                fontsize=12, 
                color=theme["text"])
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.axis('off')

def darken_color(hex_color):
    """Utility function to darken a color for 3D effects"""
    try:
        
        h = hex_color.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        
        darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
        
        
        return '#{:02x}{:02x}{:02x}'.format(*darkened)
    except (ValueError, IndexError):
        return hex_color

def lighten_color(hex_color):
    
    try:
        
        h = hex_color.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        
        lightened = tuple(min(255, int(c * 1.2)) for c in rgb)
        
        
        return '#{:02x}{:02x}{:02x}'.format(*lightened)
    except (ValueError, IndexError):
        return hex_color

def blend_colors(color1, color2, ratio):
   
    try:
       
        h1 = color1.lstrip('#')
        rgb1 = tuple(int(h1[i:i+2], 16) for i in (0, 2, 4))
        
        h2 = color2.lstrip('#')
        rgb2 = tuple(int(h2[i:i+2], 16) for i in (0, 2, 4))
        
        
        blended = tuple(int(r1 + (r2 - r1) * ratio) for r1, r2 in zip(rgb1, rgb2))
        
        
        return '#{:02x}{:02x}{:02x}'.format(*blended)
    except (ValueError, IndexError):
        return color1 
