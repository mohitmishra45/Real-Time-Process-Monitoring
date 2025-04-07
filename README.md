# Real-Time Process Monitoring Dashboard

### Authors: Sayandip Jana, Mohit Kumar Mishra, Anurag Pandey

A sophisticated, feature-rich system monitoring application built with Python that provides real-time insights into system performance with AI-powered analytics.

![Dashboard Screenshot](https://github.com/user-attachments/assets/0b60728d-59d7-4ea0-b62a-00d32fe18770)

## Features

### System Monitoring
- **Real-time Resource Tracking**: Monitor CPU, memory, disk, and network usage with beautiful gauges and graphs
- **Process Management**: View, filter, sort, and manage all running processes
- **Detailed Process Information**: Get comprehensive details about any process including memory usage, CPU utilization, threads, and more
- **Process Control**: Kill processes, change priorities, and manage system resources efficiently

### Data Visualization
- **Interactive Performance Graphs**: Track system performance over time with customizable time ranges (5 minutes, 15 minutes, 1 hour)
- **Resource Usage Gauges**: Visual indicators of current system resource utilization
- **Process Intelligence**: Visualize process relationships and dependencies with intelligent categorization
- **Customizable Themes**: Multiple theme options including Sunrise, Twilight, Midnight, and Forest

### Process Intelligence
- **Resource Usage Analysis**: Detailed breakdown of system resource consumption
- **Process Relations**: Visualization of relationships between processes
- **System Summary**:
  - Total process count
  - Memory usage statistics
  - CPU usage overview
- **Resource-Intensive Process Identification**:
  - CPU-intensive processes with usage statistics
  - Memory-intensive processes with detailed memory consumption
- **Resource Trends**: Tracking and analysis of usage patterns over time
- **Optimization Suggestions**: Recommendations for improving system performance

### AI Insights
- **Data Collection Tracking**: Shows how long metrics have been collected
- **Model Training Status**: Indicates AI model training progress
- **AI Status Monitoring**: Shows current state of AI components
- **Predictive Analytics**:
  - CPU usage predictions with current and forecasted values
  - Trend analysis (stable, increasing, decreasing)
- **Anomaly Detection**: Identifies unusual system behavior with detailed analysis
- **Interactive AI Buttons**: Dedicated buttons for predictions and anomaly detection

### Virtual Assistant
- **Conversational Interface**: Chat-based interaction for system queries
- **Quick Command Buttons**: One-click access to common information:
  - CPU details
  - Memory status
  - Disk information
  - Network statistics
  - Process lists
  - Help documentation
- **Natural Language Processing**: Ability to understand and respond to queries about system performance
- **Contextual Responses**: Provides relevant system information based on user questions

### Smart Recommendations
- **System Warnings**: Alerts when resource usage approaches high levels
- **Optimization Suggestions**:
  - CPU optimization recommendations
  - Memory optimization tips
  - Application management advice
- **Resource Management Tips**: Contextual advice based on current system state

## Technical Implementation

### Architecture
The application follows a modular architecture with clear separation of concerns:

```
ProcessMonitoringOs/
├── main.py              # Application entry point
├── config.py            # Configuration settings and themes
├── ui/                  # User interface components
│   ├── app.py           # Main application window
│   ├── sections.py      # UI sections (Top, Middle)
│   ├── footer.py        # Footer component
│   ├── gauges.py        # Resource usage gauges
│   └── graphs.py        # Performance graphs
├── utils/               # Utility functions
│   ├── process_utils.py # Process management utilities
│   └── ai_utils.py      # AI and ML components
```

### Key Components

#### UI Framework
- Built with **Tkinter** and **ttk** for a modern, responsive interface
- Custom-styled widgets with themed components:
  - Circular gauges with dynamic color changes
  - Custom buttons with hover effects
  - Tabular data with alternating row colors
  - Responsive charts with interactive elements
- Sectioned layout with three main areas:
  - Top section: System Monitor, AI Insights, Smart Recommendations
  - Middle section: Process List and System Performance graphs
  - Bottom section: Status bar and controls

#### Data Processing
- **psutil** for efficient system metrics collection:
  - CPU statistics (usage, cores, threads)
  - Memory information (used, available, percent)
  - Disk usage (free space, used space, percent)
  - Process details (PID, name, CPU%, memory usage)
- Real-time data processing with optimized update intervals
- Efficient data structures for storing historical performance data

#### AI & Machine Learning
- **Anomaly Detection**: Implemented using Isolation Forest algorithm from scikit-learn
  - Identifies unusual patterns in resource usage
  - Provides severity assessment of detected anomalies
- **Predictive Analytics**: Time-series forecasting with ARIMA models from statsmodels
  - Predicts future resource usage based on historical patterns
  - Calculates trend directions (stable, increasing, decreasing)
- **Process Intelligence**:
  - Categorizes processes by type and function
  - Identifies relationships between processes
  - Analyzes resource consumption patterns

#### Visualization
- **Matplotlib** for high-quality, customizable graphs and charts:
  - Line charts for temporal data
  - Bar charts for comparative analysis
  - Custom visualizations for process relationships
- Custom gauge widgets implemented with Tkinter canvas:
  - Dynamic color changes based on usage levels
  - Smooth animations for value transitions
  - Informative tooltips on hover
- Process list with sortable columns and search functionality

## Advanced Features

### Process Intelligence
The Process Intelligence feature provides deep insights into system processes:

- **System Summary**:
  - Total process count with active/inactive breakdown
  - Memory usage statistics across process categories
  - CPU utilization patterns by process type

- **Process Categorization**:
  - **System Processes**: Core OS components (e.g., System, Registry)
  - **Background Services**: Services running without user interaction
  - **User Applications**: Programs launched by the user
  - **Development Tools**: Programming and development utilities
  - **Media & Graphics**: Audio/video/graphics applications
  - **Network Services**: Internet and network-related processes

- **Resource Usage Analysis**:
  - Identifies CPU-intensive processes with usage statistics
  - Highlights memory-intensive processes with detailed memory consumption
  - Tracks resource usage trends over time

- **Process Relationships**:
  - Parent-child relationships between processes
  - Dependency mapping between related processes
  - Impact analysis of process termination

### AI Insights
The AI components provide sophisticated analysis and predictions:

- **Data Collection and Training**:
  - Continuous collection of system metrics
  - Periodic model training based on accumulated data
  - Status indicators for training progress

- **Anomaly Analysis**:
  - Multi-level anomaly detection (critical, warning, normal)
  - Detailed breakdown of detected anomalies by resource type
  - Severity assessment with recommended actions
  - Historical anomaly tracking for pattern recognition

- **Resource Predictions**:
  - Short-term forecasts of CPU, memory, and disk usage
  - Trend analysis with directional indicators
  - Confidence levels for predictions
  - Comparative analysis of predicted vs. actual values

- **Performance Optimization**:
  - Context-aware recommendations based on system state
  - Prioritized suggestions for resource management
  - Impact assessment of recommended actions

### Virtual Assistant
The integrated virtual assistant provides an intuitive interface for system interaction:

- **Conversational Capabilities**:
  - Natural language understanding for system queries
  - Contextual responses based on current system state
  - Helpful suggestions for common tasks

- **Information Retrieval**:
  - Detailed CPU information (usage, cores, threads)
  - Memory statistics (used, available, allocation)
  - Disk space analysis (free space, usage patterns)
  - Network activity monitoring (sent/received data)
  - Process information (running processes, resource usage)

- **Quick Commands**:
  - One-click buttons for common queries
  - Instant access to system information
  - Streamlined interface for frequent tasks

- **Help and Documentation**:
  - Built-in help system with usage examples
  - Troubleshooting suggestions
  - Feature explanations and tips

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Required packages:
  - **tkinter**: UI framework
  - **psutil**: System metrics collection
  - **matplotlib**: Data visualization
  - **numpy** & **pandas**: Data processing
  - **scikit-learn**: Machine learning components
  - **statsmodels**: Time series analysis

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Sayandip-Jana-1018/ProcessMonitoringOs.git
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Themes

The application features a vibrant, modern UI with a customizable color scheme:

- **Current Theme**: Bright theme with pink accent colors
- **UI Elements**:
  - Section headers with distinct color coding
  - Circular gauges with percentage indicators
  - Clean, readable fonts for all text elements
  - Consistent styling across all components

## Performance Considerations

- **Efficient Resource Usage**:
  - The application is optimized to use minimal resources while monitoring
  - Typical CPU usage is less than 2% during normal operation
  - Memory footprint is kept below 100MB

- **Data Management**:
  - Optimized data collection intervals (configurable)
  - Efficient storage of historical data
  - Automatic cleanup of old metrics to prevent memory leaks

- **Responsive UI**:
  - Background processing for intensive tasks
  - Non-blocking updates for performance graphs
  - Throttled refresh rates for smooth operation

## Customization

Users can customize various aspects of the application:

- **Display Options**:
  - Process list columns and sorting
  - Graph time ranges and visualization styles
  - Gauge appearance and thresholds

- **Monitoring Settings**:
  - Update intervals for metrics collection
  - Alert thresholds for resource usage
  - Process filtering and categorization rules

- **AI Components**:
  - Training frequency for ML models
  - Sensitivity settings for anomaly detection
  - Prediction horizon for forecasting

## Contributors

- Sayandip Jana
- Mohit Kumar Mishra
- Anurag Pandey

### Innovative Enhancements
Beyond the basics, consider these innovative additions:
- **Process Grouping**: Group processes by application or user in the `Treeview` for better organization.  
- **Snapshot Feature**: Save current process states to a CSV file for later comparison.  
- **Remote Monitoring (Future)**: Use `paramiko` for SSH to monitor remote machines.  
- **Predictive Alerts**: Forecast system overload based on trends and alert administrators.  

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Built with ❤️ and Python*
