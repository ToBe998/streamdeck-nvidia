# Quick Reference Card - NVIDIA GPU Monitor Plugin

## Installation (One Command)
```bash
/var/projects/streamdeck-nvidia/install.sh
```

## Manual Installation
```bash
# Copy plugin
cp -r /var/projects/streamdeck-nvidia ~/.var/app/com.core447.StreamController/data/plugins/com_streamcontroller_NVIDIAPlugin

# Install dependencies  
flatpak run --command=pip com.core447.StreamController install nvidia-ml-py3 matplotlib Pillow

# Restart
pkill -9 -f StreamController && sleep 3 && flatpak run com.core447.StreamController
```

## Actions Quick Guide

### 📊 NVIDIA GPU Metrics (Text)
**Metrics Available:**
- GPU Usage %
- VRAM Usage %
- VRAM Used (MB)
- Total VRAM (MB)
- Temperature (°C)

**Setup:**
1. Add to button
2. ⋮ menu → Aa button → Enable labels
3. Configure metrics in settings

### 📈 NVIDIA GPU + VRAM Graph
**Lines:**
- Green: GPU Usage %
- Orange: VRAM Usage %

**Setup:**
1. Add to button
2. ⋮ menu → Image icon → Enable
3. Customize colors in settings

## Configuration Options Summary

### Text Action
| Setting | Options |
|---------|---------|
| Top Label | None, GPU%, VRAM%, VRAM Used, VRAM Total, Temp |
| Center Label | None, GPU%, VRAM%, VRAM Used, VRAM Total, Temp |
| Bottom Label | None, GPU%, VRAM%, VRAM Used, VRAM Total, Temp |
| Font Size | 8-48pt |

### Graph Action
| Setting | Range/Options |
|---------|--------------|
| Line 1 Color | Color picker (GPU line) |
| Line 1 Fill | Color picker with alpha (GPU fill) |
| Line 2 Color | Color picker (VRAM line) |
| Line 2 Fill | Color picker with alpha (VRAM fill) |
| Line Width | 1-10 |
| Time Period | 5-60 seconds |
| Dynamic Scaling | On/Off |

## Testing GPU Access
```bash
# Verify NVIDIA GPU is accessible
nvidia-smi

# Check plugin logs
tail -100 ~/.var/app/com.core447.StreamController/data/logs/logs.log | grep -i nvidia
```

## File Structure
```
com_streamcontroller_NVIDIAPlugin/
├── main.py                    # Plugin entry point
├── NVIDIAMonitor.py          # GPU metrics collector
├── GraphBase.py              # Graph rendering base
├── NVIDIACombinedGraph.py    # Combined graph action
└── actions/
    └── NVIDIAMetrics/        # Text metrics action
        └── NVIDIAMetrics.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No GPU data | Run `nvidia-smi` to verify driver |
| Graph not visible | Enable image control (⋮ → image icon) |
| Labels not showing | Enable labels (⋮ → Aa button) |
| Plugin errors | Check logs at `~/.var/.../logs/logs.log` |

## Update Plugin
```bash
# After making changes
/var/projects/streamdeck-nvidia/install.sh
```

## Key Design Patterns Used

✅ Singleton monitor (shared GPU access)  
✅ Multiprocessing graphs (non-blocking UI)  
✅ All three label positions set (user controls visibility)  
✅ CONTROLS_KEY_IMAGE for graph background  
✅ Proper settings persistence  
✅ GTK4/Adwaita configuration UI  

---
**Based on:** OSPlugin architecture  
**License:** GPL-3.0  
**Requirements:** NVIDIA GPU with drivers, StreamController 1.0.0+
