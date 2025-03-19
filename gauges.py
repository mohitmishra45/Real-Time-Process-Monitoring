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