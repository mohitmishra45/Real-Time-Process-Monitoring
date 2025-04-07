import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime

def create_performance_graphs(parent, theme):
    """Create performance graphs with improved styling"""
    # Create figure and subplots with adjusted size and spacing
    fig, axes = plt.subplots(3, 1, figsize=(8, 6), dpi=100, sharex=True)
    fig.patch.set_facecolor(theme["chart_bg"])  # Use theme chart background
    
    # Add more padding between subplots
    plt.subplots_adjust(hspace=0.3)
    
    # Configure each subplot
    for i, ax in enumerate(axes):
        ax.set_facecolor(theme["chart_bg"])  # Use theme chart background
        ax.grid(True, linestyle='--', alpha=0.6, color=theme["grid_color"])  # Use theme grid color
        ax.tick_params(colors=theme["text"], labelsize=8)  # Use theme text color
        
        # Set titles with improved visibility
        if i == 0:
            ax.set_title("CPU Usage (%)", color=theme["text"], fontsize=10, pad=10)
        elif i == 1:
            ax.set_title("Memory Usage (%)", color=theme["text"], fontsize=10, pad=10)
        else:
            ax.set_title("Disk Usage (%)", color=theme["text"], fontsize=10, pad=10)
        
        # Set y-axis limits and ticks
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        
        # Set y-axis label
        ax.set_ylabel("%", color=theme["text"], fontsize=8)
        
        # Style the spines
        for spine in ax.spines.values():
            spine.set_color(theme["grid_color"])  # Use theme grid color
            spine.set_linewidth(0.5)
    
    # Create canvas with matching background
    canvas = FigureCanvasTkAgg(fig, parent)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.configure(bg=theme["chart_bg"], highlightbackground=theme["chart_bg"], highlightcolor=theme["chart_bg"])
    canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)
    
    return fig, axes, canvas

def update_performance_graphs(axes, timestamps, cpu_history, mem_history, disk_history, theme):
    """Update performance graphs with current data"""
    try:
        # Clear axes
        for ax in axes:
            ax.clear()
            ax.set_facecolor(theme["chart_bg"])  # Use theme chart background
            ax.grid(True, linestyle='--', alpha=0.6, color=theme["grid_color"])  # Use theme grid color
            ax.tick_params(colors=theme["text"], labelsize=8)  # Use theme text color
            ax.set_ylim(0, 100)
            ax.set_yticks([0, 25, 50, 75, 100])
        
        # Set titles
        axes[0].set_title("CPU Usage (%)", color=theme["text"], fontsize=10, pad=10)
        axes[1].set_title("Memory Usage (%)", color=theme["text"], fontsize=10, pad=10)
        axes[2].set_title("Disk Usage (%)", color=theme["text"], fontsize=10, pad=10)
        
        # Check if we have enough data
        if not timestamps or len(timestamps) < 2:
            for ax in axes:
                ax.text(0.5, 0.5, "Collecting data...", 
                       horizontalalignment='center',
                       verticalalignment='center',
                       transform=ax.transAxes,
                       color=theme["text"],  # Use theme text color
                       fontsize=10)
            return
        
        # Convert timestamps to formatted strings
        formatted_times = [t.strftime("%H:%M:%S") for t in timestamps]
        x = range(len(formatted_times))
        
        # Plot data with enhanced styling using theme colors
        # CPU Graph
        axes[0].plot(x, cpu_history, color=theme["cpu_color"], linewidth=2, label='CPU')
        axes[0].fill_between(x, 0, cpu_history, color=theme["cpu_color"], alpha=0.2)
        
        # Memory Graph
        axes[1].plot(x, mem_history, color=theme["mem_color"], linewidth=2, label='Memory')
        axes[1].fill_between(x, 0, mem_history, color=theme["mem_color"], alpha=0.2)
        
        # Disk Graph
        axes[2].plot(x, disk_history, color=theme["disk_color"], linewidth=2, label='Disk')
        axes[2].fill_between(x, 0, disk_history, color=theme["disk_color"], alpha=0.2)
        
        # Set x-axis ticks and labels
        if len(formatted_times) > 10:
            # Show fewer ticks if there are many data points
            tick_indices = np.linspace(0, len(formatted_times) - 1, 5, dtype=int)
            tick_labels = [formatted_times[i] for i in tick_indices]
            
            for ax in axes:
                ax.set_xticks(tick_indices)
                ax.set_xticklabels(tick_labels)
        else:
            for ax in axes:
                ax.set_xticks(range(len(formatted_times)))
                ax.set_xticklabels(formatted_times)
        
        # Add legends with theme-based colors
        for i, ax in enumerate(axes):
            if i == 0:
                label = 'CPU'
                color = theme["cpu_color"]
            elif i == 1:
                label = 'Memory'
                color = theme["mem_color"]
            else:
                label = 'Disk'
                color = theme["disk_color"]
                
            ax.legend([label], loc='upper right', facecolor=theme["chart_bg"], 
                     edgecolor=theme["grid_color"], fontsize=8)
        
        # Set x-axis label for bottom subplot
        axes[-1].set_xlabel("Time", color=theme["text"], fontsize=8)
        
        # Update layout
        plt.tight_layout()
        
    except Exception as e:
        print(f"Error updating performance graphs: {e}")
        import traceback
        traceback.print_exc()
    
    # Draw the figure
    canvas.draw()
    
    return fig, axes

def update_performance_graphs(axes, timestamps, cpu_history, mem_history, disk_history, theme):
    """Update performance graphs with current data"""
    # Clear axes
    for ax in axes:
        ax.clear()
        ax.set_facecolor(theme["chart_bg"])  # Use theme chart background
        ax.grid(True, linestyle='--', alpha=0.7, color=theme["grid_color"])  # Use theme grid color
        ax.tick_params(colors=theme["text"], labelsize=8)  # Use theme text color
        ax.set_ylim(0, 100)
    
    # Set titles
    axes[0].set_title("CPU Usage (%)", color=theme["text"], fontsize=10)
    axes[1].set_title("Memory Usage (%)", color=theme["text"], fontsize=10)
    axes[2].set_title("Disk Usage (%)", color=theme["text"], fontsize=10)
    
    # Format timestamps for x-axis
    if timestamps and len(timestamps) > 1:
        formatted_times = [t.strftime("%H:%M:%S") for t in timestamps]
        
        # Plot data with proper styling
        if cpu_history and len(cpu_history) > 1:
            # Add small random variations to make the graph more interesting if values are too similar
            if max(cpu_history) - min(cpu_history) < 1:
                cpu_history = [v + np.random.uniform(-0.5, 0.5) for v in cpu_history]
                cpu_history = [max(0, min(100, v)) for v in cpu_history]  # Clamp values
            
            axes[0].plot(formatted_times, cpu_history, color=theme["cpu_color"], linewidth=2)
            # Add a light fill below the line
            axes[0].fill_between(formatted_times, 0, cpu_history, color=theme["cpu_color"], alpha=0.2)
        
        if mem_history and len(mem_history) > 1:
            # Add small random variations to make the graph more interesting if values are too similar
            if max(mem_history) - min(mem_history) < 1:
                mem_history = [v + np.random.uniform(-0.5, 0.5) for v in mem_history]
                mem_history = [max(0, min(100, v)) for v in mem_history]  # Clamp values
                
            axes[1].plot(formatted_times, mem_history, color=theme["mem_color"], linewidth=2)
            # Add a light fill below the line
            axes[1].fill_between(formatted_times, 0, mem_history, color=theme["mem_color"], alpha=0.2)
        
        if disk_history and len(disk_history) > 1:
            # Add small random variations to make the graph more interesting if values are too similar
            if max(disk_history) - min(disk_history) < 1:
                disk_history = [v + np.random.uniform(-0.5, 0.5) for v in disk_history]
                disk_history = [max(0, min(100, v)) for v in disk_history]  # Clamp values
                
            axes[2].plot(formatted_times, disk_history, color=theme["disk_color"], linewidth=2)
            # Add a light fill below the line
            axes[2].fill_between(formatted_times, 0, disk_history, color=theme["disk_color"], alpha=0.2)
        
        # Set x-axis ticks
        if len(formatted_times) > 10:
            # Show fewer ticks if there are many data points
            tick_indices = np.linspace(0, len(formatted_times) - 1, 5, dtype=int)
            tick_labels = [formatted_times[i] for i in tick_indices]
            
            for ax in axes:
                ax.set_xticks(tick_indices)
                ax.set_xticklabels(tick_labels)
        else:
            for ax in axes:
                ax.set_xticks(range(len(formatted_times)))
                ax.set_xticklabels(formatted_times)
    
    # Set y-axis labels
    for ax in axes:
        ax.set_ylabel("%", color=theme["text"], fontsize=8)
    
    # Set x-axis label for bottom subplot
    axes[-1].set_xlabel("Time", color=theme["text"], fontsize=8)
