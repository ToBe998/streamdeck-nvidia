#!/bin/bash
# Installation script for NVIDIA GPU Monitor Plugin

set -e

PLUGIN_NAME="com_streamcontroller_NVIDIAPlugin"
SOURCE_DIR="/var/projects/streamdeck-nvidia"
TARGET_DIR="$HOME/.var/app/com.core447.StreamController/data/plugins/$PLUGIN_NAME"

echo "🚀 Installing NVIDIA GPU Monitor Plugin for StreamController"
echo ""

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: Source directory not found: $SOURCE_DIR"
    exit 1
fi

# Create plugins directory if it doesn't exist
mkdir -p "$(dirname "$TARGET_DIR")"

# Remove old version if exists
if [ -d "$TARGET_DIR" ]; then
    echo "📦 Removing old version..."
    rm -rf "$TARGET_DIR"
fi

# Copy new version (exclude dev files)
echo "📋 Copying plugin files..."
mkdir -p "$TARGET_DIR"
mkdir -p "$TARGET_DIR/actions/NVIDIAMetrics"

# Copy only plugin source files
for f in main.py GraphBase.py NVIDIAMonitor.py NVIDIACombinedGraph.py NVIDIAGPUGraph.py NVIDIAVRAMGraph.py NVIDIALogo.py pynvml.py libnvidia-ml.so.1 nvidia_logo.png plugin.json requirements.txt __init__.py; do
    [ -f "$SOURCE_DIR/$f" ] && cp "$SOURCE_DIR/$f" "$TARGET_DIR/$f"
done
cp "$SOURCE_DIR/actions/__init__.py" "$TARGET_DIR/actions/" 2>/dev/null || true
cp "$SOURCE_DIR/actions/NVIDIAMetrics/__init__.py" "$TARGET_DIR/actions/NVIDIAMetrics/" 2>/dev/null || true
cp "$SOURCE_DIR/actions/NVIDIAMetrics/NVIDIAMetrics.py" "$TARGET_DIR/actions/NVIDIAMetrics/"

echo "✅ Plugin files copied successfully"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
echo "   (This may take a moment...)"
flatpak run --command=pip com.core447.StreamController install \
    nvidia-ml-py3 matplotlib Pillow 2>&1 | grep -E "(Successfully|already satisfied|Requirement)" || true

echo ""
echo "✅ Dependencies installed"
echo ""

# Restart StreamController
echo "🔄 Restarting StreamController..."
pkill -9 -f StreamController 2>/dev/null || true
sleep 2
flatpak run com.core447.StreamController &

echo ""
echo "✅ Installation complete!"
echo ""
echo "📌 Next steps:"
echo "   1. Wait for StreamController to start"
echo "   2. Add 'NVIDIA GPU Metrics' or 'NVIDIA GPU + VRAM Graph' to a button"
echo "   3. Configure via the three-dot menu (⋮)"
echo ""
echo "   For text display: Enable labels with Aa button"
echo "   For graph display: Enable image control with image icon"
echo ""
echo "💡 Check logs if issues occur:"
echo "   tail -100 ~/.var/app/com.core447.StreamController/data/logs/logs.log"
echo ""
