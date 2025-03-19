## Overview

This project consists of two primary Python files that implement a graphical user interface (GUI) for monitoring system resource usage (CPU, memory, disk), with options to control system processes and configure alerts based on thresholds. The GUI is built using **Tkinter** for the interface and **Matplotlib** for rendering graphical gauges. Additionally, the system makes use of **psutil** to gather system performance data.

### Features:
- **Footer Section**: A footer UI component that offers control over system processes, system alerts, and refresh rate configuration.
- **System Gauges**: Graphical representation of system resources like CPU, memory, and disk usage, updated dynamically.
- **Customizable Alerts**: Allows users to set custom threshold values for CPU, memory, and disk usage to trigger alerts.
- **Refresh Rate**: Provides the option to configure the update interval for system data.
  
---

## Files

### 1. **Footer Class**

The `Footer` class is responsible for creating the footer section of the user interface. It includes several widgets such as buttons and labels to interact with the system:

#### Key Components:
- **Process Controls**: 
  - `Kill Process`: Button to terminate a system process.
  - `Process Details`: Button to view process details.
  - `Export Process List`: Button to export a list of running processes.
  
- **System Alerts**:
  - Input fields to set custom thresholds for CPU, memory, and disk usage.
  - `Apply` button to apply these threshold values.
  
- **Refresh Rate**:
  - Input field to set the update interval for system resource monitoring.
  
The `Footer` class interacts with the `app` object to trigger actions like killing processes, showing process details, and exporting data.

#### Methods:
- **`apply_thresholds()`**: Applies custom thresholds for CPU, memory, and disk.
- **`get_refresh_rate()`**: Retrieves the refresh rate value set by the user.

### 2. **System Gauges**

The functions `create_gauge` and `update_gauge` are responsible for creating and updating graphical gauges that show the current usage of CPU, memory, and disk.

#### Key Components:
- **`create_gauge(parent, theme, label)`**:
  - Creates a gauge widget for the specified system resource (CPU, memory, or disk).
  - The function uses Matplotlib to draw a circular gauge with customizable colors based on usage levels.

- **`update_gauge(ax, percent, label, theme)`**:
  - Updates the gauge to reflect the current usage of the selected system resource.
  - The gauge color changes depending on usage:
    - **Green** for less than 60%
    - **Yellow** for 60-80%
    - **Red** for above 80%
  - Displays additional information such as CPU core count, memory usage, and free disk space.

### 3. **Utility Functions**

Several utility functions are provided to modify colors for visual effects:
- **`darken_color(hex_color)`**: Darkens a given hex color.
- **`lighten_color(hex_color)`**: Lightens a given hex color.
- **`blend_colors(color1, color2, ratio)`**: Blends two colors based on the given ratio.

These utilities are used to adjust the appearance of the gauges and interface elements dynamically.

---

## Requirements

- Python 3.x
- **Tkinter**: For creating the GUI.
- **Matplotlib**: For rendering gauges.
- **psutil**: For retrieving system performance data.
- **platform**: For platform-specific disk handling.
- **os**: For environment-related tasks.

Install required packages using `pip`:
```bash
pip install matplotlib psutil
```

---

## Usage

1. **Integrating the Footer Class**: 
   - The `Footer` class is designed to be used within an application that uses Tkinter for the main interface. 
   - Create an instance of the `Footer` class and pass the main window (`root`) and the app object that contains the logic for handling processes and alerts.

2. **System Resource Monitoring**:
   - Gauges for CPU, memory, and disk usage are automatically created and updated based on system data retrieved via the `psutil` library.
   - The refresh rate can be configured by the user to update the gauges at the desired interval.

3. **Interacting with Buttons**:
   - The buttons in the footer (Kill Process, Process Details, and Export Process List) allow users to control system processes and view relevant information.

4. **Setting Thresholds**:
   - Users can input custom thresholds for CPU, memory, and disk usage, and these values can trigger alerts when the resource usage exceeds the set limits.

---

## Customization

You can customize the appearance and functionality by modifying the following parts:

1. **Colors and Themes**: 
   - Modify the theme dictionary in the app to change colors for the gauges and UI elements.
   
2. **Thresholds**: 
   - Change the default values for CPU, memory, and disk usage thresholds.

3. **Refresh Rate**: 
   - Adjust the refresh rate input field to change how frequently system resource data is updated.

---

## Example

Here is a basic example of how the `Footer` class can be used in a Tkinter application:

```python
import tkinter as tk

class MyApp:
    def __init__(self, root):
        self.root = root
        self.theme = {
            "cpu_color": "#28a745",
            "mem_color": "#17a2b8",
            "disk_color": "#ffc107",
            "accent": "#007bff",
            "warning": "#f39c12",
            "danger": "#e74c3c",
            "grid_color": "#ecf0f1",
            "text": "#ffffff"
        }
        self.footer = Footer(self.root, self)
        
    def kill_process(self):
        print("Process killed!")
    
    def show_process_details(self):
        print("Showing process details!")
    
    def export_process_list(self):
        print("Exporting process list!")

root = tk.Tk()
app = MyApp(root)
root.mainloop()
```

This example initializes a simple Tkinter application with a footer and some basic functionality for controlling processes.

---

## Conclusion

This project provides an interactive interface to monitor system resources and manage processes, allowing users to set alerts and customize thresholds. The code integrates Tkinter for the GUI, Matplotlib for graphical gauges, and psutil for system monitoring.

