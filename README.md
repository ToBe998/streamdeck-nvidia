# NVIDIA GPU Monitor Plugin for StreamController

Monitor NVIDIA GPU metrics on your StreamDeck with real-time usage graphs and text displays.

## Features

### 📊 NVIDIA GPU Metrics (Text Display)
Display any of these metrics in Top, Center, or Bottom label positions:
- **GPU Usage %** - Current GPU utilization percentage
- **VRAM Usage %** - Current video memory usage percentage  
- **VRAM Used (MB)** - Amount of VRAM currently in use
- **Total VRAM (MB)** - Total available video memory
- **Temperature (°C)** - Current GPU temperature

**Configuration Options:**
- Choose different metrics for each label position (Top, Center, Bottom)
- Adjustable font size (8-48pt)
- All labels can be toggled via StreamController's label controls (⋮ menu → Aa button)

### 📈 NVIDIA GPU + VRAM Combined Graph
Dual-line graph showing GPU usage and VRAM usage over time.

**Configuration Options:**
- **Line 1 Color** - GPU usage line color (default: green)
- **Line 1 Fill** - GPU usage fill color with alpha
- **Line 2 Color** - VRAM usage line color (default: orange)
- **Line 2 Fill** - VRAM usage fill color with alpha
- **Line Width** - Thickness of graph lines (1-10)
- **Time Period** - Historical data window (5-60 seconds)
- **Dynamic Y-axis Scaling** - Auto-scale based on max values

## Installation

### Prerequisites
- StreamController installed (version 1.0.0+)
- NVIDIA GPU with driver installed
- Python 3.8 or higher

### Install Plugin

1. **Copy plugin to StreamController plugins directory:**
   ```bash
   cp -r /var/projects/streamdeck-nvidia ~/.var/app/com.core447.StreamController/data/plugins/com_streamcontroller_NVIDIAPlugin
   ```

2. **Install Python dependencies:**
   ```bash
   # If using Flatpak StreamController
   flatpak run --command=pip com.core447.StreamController install nvidia-ml-py3 matplotlib Pillow
   
   # Or install in your Python environment
   pip install -r requirements.txt
   ```

3. **Restart StreamController:**
   ```bash
   pkill -9 -f StreamController
   sleep 3
   flatpak run com.core447.StreamController
   ```

## Usage

### Adding GPU Metrics Text Display

1. Drag "NVIDIA GPU Metrics" action onto a button
2. Click the three-dot menu (⋮) next to the action
3. Click the "Aa" button to enable label positions
4. Select which positions (Top/Center/Bottom) to show
5. Configure which metric appears in each position via action settings

### Adding GPU + VRAM Graph

1. Drag "NVIDIA GPU + VRAM Graph" action onto a button
2. Click the three-dot menu (⋮) next to the action
3. Click the image icon to allow the action to control the button background
4. Customize colors and time period in action settings
5. The graph shows:
   - **Line 1 (Green):** GPU Usage %
   - **Line 2 (Orange):** VRAM Usage %

## Troubleshooting

### "Failed to initialize NVIDIA GPU monitoring"
- Ensure NVIDIA drivers are installed: `nvidia-smi`
- Check that `nvidia-ml-py3` is installed properly
- Verify you have an NVIDIA GPU

### Graph not showing
- Make sure `CONTROLS_KEY_IMAGE` is enabled (three-dot menu → image icon)
- Check StreamController logs: `~/.var/app/com.core447.StreamController/data/logs/logs.log`

### No data updating
- Verify GPU is accessible: `nvidia-smi` in terminal
- Check plugin logs for errors
- Ensure the action is added to an active page

## Development

### Project Structure
```
streamdeck-nvidia/
├── main.py                          # Plugin registration
├── plugin.json                      # Plugin metadata
├── requirements.txt                 # Python dependencies
├── NVIDIAMonitor.py                # Singleton GPU metrics monitor
├── GraphBase.py                    # Base class for graph actions
├── NVIDIACombinedGraph.py         # Combined GPU+VRAM graph
└── actions/
    └── NVIDIAMetrics/              # Text metrics action
        ├── __init__.py
        └── NVIDIAMetrics.py
```

### Testing Changes

```bash
# Copy updated files
cp -r /var/projects/streamdeck-nvidia/* ~/.var/app/com.core447.StreamController/data/plugins/com_streamcontroller_NVIDIAPlugin/

# Restart StreamController
pkill -9 -f StreamController && sleep 3 && flatpak run com.core447.StreamController

# Check logs
tail -100 ~/.var/app/com.core447.StreamController/data/logs/logs.log | grep -i nvidia
```

## Credits

Based on the [OSPlugin](https://github.com/StreamController/OSPlugin) architecture and patterns.

## License

GPL-3.0 License - see LICENSE file for details
