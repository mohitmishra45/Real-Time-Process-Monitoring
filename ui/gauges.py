import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import psutil
import platform
import os
from matplotlib.patches import Wedge
import shutil  # Added import for shutil

def create_gauge(parent, theme, label, size=120):
    """Create a more modern and visually appealing gauge chart"""
    fig = plt.Figure(figsize=(size/100, size/100), dpi=100)
    fig.patch.set_facecolor(theme["card_bg"])
    fig.subplots_adjust(0, 0, 1, 1)
    
    # Create subplot with equal aspect ratio
    ax = fig.add_subplot(111, aspect='equal')
    ax.set_facecolor(theme["card_bg"])
    
    # Define colors based on the type of gauge
    if label == "CPU":
        color = "#FF4757"  # Red
        highlight = "#FF6B81"
        gradient_top = "#FF8A8A"
    elif label == "MEM":
        color = "#2E86DE"  # Blue
        highlight = "#54A0FF"
        gradient_top = "#7CB9FF"
    else:  # DISK
        color = "#26C281"  # Green
        highlight = "#2ECC71"
        gradient_top = "#5FE3A4"
    
    # Create the gauge background (semi-circle)
    theta1, theta2 = 210, -30  # Semi-circle from bottom left to bottom right
    w = Wedge((0.5, 0.45), 0.35, theta1, theta2, width=0.1, 
              color=theme["grid_color"], alpha=0.2, linewidth=0)
    ax.add_artist(w)
    
    # Store references for updating
    ax.user_data = {
        "color": color,
        "highlight": highlight,
        "gradient_top": gradient_top,
        "theta1": theta1,
        "theta2": theta2,
        "label": label
    }
    
    # Add percentage and label texts
    if label == "CPU":
        val_color = "#FF4757"
    elif label == "MEM":
        val_color = "#2E86DE"
    else:
        val_color = "#26C281"
        
    # Add label at top
    label_text = ax.text(0.5, 0.75, label,
                        ha='center', va='center',
                        color=color,
                        fontsize=12,
                        fontweight='bold')
    
    # Add percentage text
    value_text = ax.text(0.5, 0.45, "0%",
                        ha='center', va='center',
                        color=val_color,
                        fontsize=14,
                        fontweight='bold')
    
    # Add info text
    if label == "CPU":
        cpu_count = psutil.cpu_count()
        info_text = ax.text(0.5, 0.2, f"{cpu_count} threads",
                           ha='center', va='center',
                           color=color,
                           fontsize=8)
    elif label == "MEM":
        mem = psutil.virtual_memory()
        used_gb = mem.used / (1024**3)
        total_gb = mem.total / (1024**3)
        info_text = ax.text(0.5, 0.2, f"{used_gb:.1f}/{total_gb:.1f}GB",
                           ha='center', va='center',
                           color=color,
                           fontsize=8)
    else:  # DISK
        try:
            path = 'C:\\' if platform.system() == 'Windows' else '/'
            total, used, free = shutil.disk_usage(path)
            free_gb = free / (1024**3)
            info_text = ax.text(0.5, 0.2, f"{free_gb:.1f}GB free",
                               ha='center', va='center',
                               color=color,
                               fontsize=8)
        except Exception:
            info_text = ax.text(0.5, 0.2, "N/A",
                               ha='center', va='center',
                               color=color,
                               fontsize=8)
    
    # Set limits and remove axes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    canvas = FigureCanvasTkAgg(fig, parent)
    canvas.get_tk_widget().pack(side="left", padx=5)
    
    return fig, ax

def update_gauge(ax, percent, label, theme):
    """Update gauge with new percentage and enhanced visual effects"""
    try:
        # Clear the axis but keep the background
        artists_to_remove = []
        for artist in ax.get_children():
            if not isinstance(artist, plt.Text):
                artists_to_remove.append(artist)
                
        # Remove artists safely with error handling
        for artist in artists_to_remove:
            try:
                artist.remove()
            except Exception:
                # Silently handle any "cannot remove artist" errors
                pass
                
        # Get or set default values for gauge appearance
        if label == "CPU":
            color = "#FF4757"  # Red
            highlight = "#FF6B81"
        elif label == "MEM":
            color = "#2E86DE"  # Blue
            highlight = "#54A0FF"
        else:  # DISK
            color = "#26C281"  # Green
            highlight = "#2ECC71"
            
        # Determine color based on percentage for warning levels
        if percent >= 80:
            gauge_color = "#FF4757"  # Warning red
            text_color = "#FF4757"
        elif percent >= 60:
            gauge_color = "#FFAA00"  # Warning orange
            text_color = "#FFAA00"
        else:
            gauge_color = color
            text_color = color
        
        # Create background circle
        background_circle = plt.Circle((0.5, 0.5), 0.4, color=theme["grid_color"], alpha=0.2)
        ax.add_patch(background_circle)
        
        # Calculate angle for progress
        angle = (percent / 100.0) * 360.0
        
        # Create progress arc
        progress = plt.matplotlib.patches.Arc((0.5, 0.5), 0.8, 0.8,
                                           theta1=-90, theta2=angle-90,
                                           color=gauge_color, linewidth=4)
        ax.add_patch(progress)
        
        # Update existing text or create new text
        found_percent_text = False
        found_label_text = False
        found_info_text = False
        
        for text in ax.texts:
            text_content = text.get_text()
            # Update percentage text
            if "%" in text_content:
                text.set_text(f"{percent:.1f}%")
                text.set_color(text_color)
                found_percent_text = True
            # Update label text
            elif label in text_content:
                found_label_text = True
            # Update info text
            elif any(info_marker in text_content for info_marker in ["threads", "GB", "free"]):
                if label == "CPU":
                    cpu_count = psutil.cpu_count()
                    text.set_text(f"{cpu_count} threads")
                elif label == "MEM":
                    mem = psutil.virtual_memory()
                    used_gb = mem.used / (1024**3)
                    total_gb = mem.total / (1024**3)
                    text.set_text(f"{used_gb:.1f}/{total_gb:.1f}GB")
                elif label == "DISK":
                    try:
                        # Try to get the system drive for Windows
                        if platform.system() == 'Windows':
                            # Try system drive first
                            system_drive = os.environ.get('SystemDrive', 'C:')
                            try:
                                total, used, free = shutil.disk_usage(system_drive + '\\')
                            except Exception:
                                # Try other common drives if system drive fails
                                disk_found = False
                                for drive in ['C:', 'D:', 'E:']:
                                    try:
                                        total, used, free = shutil.disk_usage(drive + '\\')
                                        disk_found = True
                                        break
                                    except Exception:
                                        continue
                            
                                if not disk_found:
                                    # If all drives fail, raise exception to be caught below
                                    raise FileNotFoundError("No valid disk found")
                        else:  # Unix/Linux/MacOS
                            total, used, free = shutil.disk_usage('/')
                            
                        # Calculate and display used space instead of free space
                        used_gb = used / (1024**3)
                        total_gb = total / (1024**3)
                        text.set_text(f"{used_gb:.1f}/{total_gb:.1f}GB used")
                    except Exception as e:
                        print(f"Error getting disk info for gauge: {e}")
                        text.set_text("Disk N/A")
                text.set_color(text_color)
                found_info_text = True
                
        # Create texts if they don't exist
        if not found_percent_text:
            ax.text(0.5, 0.5, f"{percent:.1f}%",
                    ha='center', va='center',
                    color=text_color,
                    fontsize=12,
                    fontweight='bold')
            
        if not found_label_text:
            ax.text(0.5, 0.25, label,
                    ha='center', va='center',
                    color=text_color,
                    fontsize=10,
                    fontweight='bold')
            
        if not found_info_text:
            if label == "CPU":
                cpu_count = psutil.cpu_count()
                ax.text(0.5, 0.15, f"{cpu_count} threads",
                        ha='center', va='center',
                        fontsize=7,
                        color=text_color)
            elif label == "MEM":
                mem = psutil.virtual_memory()
                used_gb = mem.used / (1024**3)
                total_gb = mem.total / (1024**3)
                ax.text(0.5, 0.15, f"{used_gb:.1f}/{total_gb:.1f}GB",
                        ha='center', va='center',
                        fontsize=7,
                        color=text_color)
            elif label == "DISK":
                try:
                    # Try to get the system drive for Windows
                    if platform.system() == 'Windows':
                        # Try system drive first
                        system_drive = os.environ.get('SystemDrive', 'C:')
                        try:
                            total, used, free = shutil.disk_usage(system_drive + '\\')
                        except Exception:
                            # Try other common drives if system drive fails
                            disk_found = False
                            for drive in ['C:', 'D:', 'E:']:
                                try:
                                    total, used, free = shutil.disk_usage(drive + '\\')
                                    disk_found = True
                                    break
                                except Exception:
                                    continue
                            
                            if not disk_found:
                                # If all drives fail, raise exception to be caught below
                                raise FileNotFoundError("No valid disk found")
                    else:  # Unix/Linux/MacOS
                        total, used, free = shutil.disk_usage('/')
                        
                    # Calculate and display used space instead of free space
                    used_gb = used / (1024**3)
                    total_gb = total / (1024**3)
                    ax.text(0.5, 0.15, f"{used_gb:.1f}/{total_gb:.1f}GB used",
                            ha='center', va='center',
                            fontsize=7,
                            color=text_color)
                except Exception as e:
                    print(f"Error getting disk info for gauge creation: {e}")
                    ax.text(0.5, 0.15, "Disk N/A",
                            ha='center', va='center',
                            fontsize=7,
                            color=text_color)
        
        # Set limits and remove axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
    except Exception as e:
        # More informative error message with label
        print(f"Error updating {label} gauge: {e}")
