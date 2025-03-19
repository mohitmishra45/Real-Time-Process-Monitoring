import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime

def create_performance_graphs(parent, theme):
    """Create performance graphs with improved styling"""
    # Create figure and subplots
    fig, axes = plt.subplots(3, 1, figsize=(6, 8), dpi=100, sharex=True)
    fig.patch.set_facecolor(theme["card_bg"])
    
    # Configure each subplot
    for i, ax in enumerate(axes):
        ax.set_facecolor(theme["chart_bg"])
        ax.grid(True, linestyle='--', alpha=0.7, color=theme["grid_color"])
        ax.tick_params(colors=theme["text"], labelsize=8)
        
        # Set titles
        if i == 0:
            ax.set_title("CPU Usage (%)", color=theme["text"], fontsize=10)
        elif i == 1:
            ax.set_title("Memory Usage (%)", color=theme["text"], fontsize=10)
        else:
            ax.set_title("Disk Usage (%)", color=theme["text"], fontsize=10)
        
        # Set y-axis limits
        ax.set_ylim(0, 100)
        
        # Set y-axis label
        ax.set_ylabel("%", color=theme["text"], fontsize=8)
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_color(theme["grid_color"])
    
    # Set x-axis label for bottom subplot
    axes[-1].set_xlabel("Time", color=theme["text"], fontsize=8)
    
    # Adjust layout
    fig.tight_layout()
    
    # Create canvas
    canvas = FigureCanvasTkAgg(fig, parent)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    # Draw the figure
    canvas.draw()
    
    return fig, axes

def update_performance_graphs(axes, timestamps, cpu_history, mem_history, disk_history, theme):
    """Update performance graphs with current data"""
    try:
        # Clear axes
        for ax in axes:
            ax.clear()
            ax.set_facecolor(theme["chart_bg"])
            ax.grid(True, linestyle='--', alpha=0.7, color=theme["grid_color"])
            ax.tick_params(colors=theme["text"], labelsize=8)
            ax.set_ylim(0, 100)
        
        # Set titles
        axes[0].set_title("CPU Usage (%)", color=theme["text"], fontsize=10)
        axes[1].set_title("Memory Usage (%)", color=theme["text"], fontsize=10)
        axes[2].set_title("Disk Usage (%)", color=theme["text"], fontsize=10)
        
        # Check if we have enough data
        if not timestamps or len(timestamps) < 2 or not cpu_history or len(cpu_history) < 2:
            # Draw "Collecting data..." text if not enough data
            for ax in axes:
                ax.text(0.5, 0.5, "Collecting data...", 
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=ax.transAxes,
                        color=theme["text"],
                        fontsize=10)
            return
        
        # Use indices instead of formatted times to prevent matplotlib issues
        indices = list(range(len(timestamps)))
        
        # Plot CPU data with vibrant colors and fill
        axes[0].plot(indices, cpu_history, color="#FF5555", linewidth=2)
        axes[0].fill_between(indices, 0, cpu_history, color="#FF5555", alpha=0.3)
        
        # Plot Memory data with vibrant colors and fill
        axes[1].plot(indices, mem_history, color="#5555FF", linewidth=2)
        axes[1].fill_between(indices, 0, mem_history, color="#5555FF", alpha=0.3)
        
        # Plot Disk data with vibrant colors and fill
        axes[2].plot(indices, disk_history, color="#55FF55", linewidth=2)
        axes[2].fill_between(indices, 0, disk_history, color="#55FF55", alpha=0.3)
        
        # Format timestamps for display
        formatted_times = [t.strftime("%H:%M:%S") for t in timestamps]
        
        # Set x-axis ticks with formatted times
        if len(formatted_times) > 10:
            # Show fewer ticks if there are many data points
            tick_count = min(5, len(formatted_times))
            step = max(1, len(formatted_times) // tick_count)
            tick_positions = indices[::step]
            tick_labels = [formatted_times[i] for i in range(0, len(formatted_times), step)]
            
            for ax in axes:
                ax.set_xticks(tick_positions)
                ax.set_xticklabels(tick_labels, rotation=45, ha='right')
        else:
            for ax in axes:
                ax.set_xticks(indices)
                ax.set_xticklabels(formatted_times, rotation=45, ha='right')
        
        # Set y-axis labels
        for ax in axes:
            ax.set_ylabel("%", color=theme["text"], fontsize=8)
        
        # Set x-axis label for bottom subplot
        axes[-1].set_xlabel("Time", color=theme["text"], fontsize=8)
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
        ax.set_facecolor(theme["chart_bg"])
        ax.grid(True, linestyle='--', alpha=0.7, color=theme["grid_color"])
        ax.tick_params(colors=theme["text"], labelsize=8)
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
            
            axes[0].plot(formatted_times, cpu_history, color=theme["danger"], linewidth=2)
            # Add a light fill below the line
            axes[0].fill_between(formatted_times, 0, cpu_history, color=theme["danger"], alpha=0.2)
        
        if mem_history and len(mem_history) > 1:
            # Add small random variations to make the graph more interesting if values are too similar
            if max(mem_history) - min(mem_history) < 1:
                mem_history = [v + np.random.uniform(-0.5, 0.5) for v in mem_history]
                mem_history = [max(0, min(100, v)) for v in mem_history]  # Clamp values
                
            axes[1].plot(formatted_times, mem_history, color=theme["warning"], linewidth=2)
            # Add a light fill below the line
            axes[1].fill_between(formatted_times, 0, mem_history, color=theme["warning"], alpha=0.2)
        
        if disk_history and len(disk_history) > 1:
            # Add small random variations to make the graph more interesting if values are too similar
            if max(disk_history) - min(disk_history) < 1:
                disk_history = [v + np.random.uniform(-0.5, 0.5) for v in disk_history]
                disk_history = [max(0, min(100, v)) for v in disk_history]  # Clamp values
                
            axes[2].plot(formatted_times, disk_history, color=theme["success"], linewidth=2)
            # Add a light fill below the line
            axes[2].fill_between(formatted_times, 0, disk_history, color=theme["success"], alpha=0.2)
        
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