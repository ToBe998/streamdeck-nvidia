"""
NVIDIA VRAM Usage Graph Action
Displays VRAM usage as a single-line graph with NVIDIA logo background
"""

from plugins.com_streamcontroller_NVIDIAPlugin.GraphBase import GraphBase
from plugins.com_streamcontroller_NVIDIAPlugin.NVIDIAMonitor import get_nvidia_monitor
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

from PIL import Image


class NVIDIAVRAMGraph(GraphBase):
    ACTION_NAME = "NVIDIA VRAM Usage Graph"
    CONTROLS_KEY_IMAGE = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True
        self.monitor = get_nvidia_monitor()
        self.single_line_mode = True  # Only one line

    def on_ready(self):
        self.show_graph()

    def on_tick(self):
        # Append new data point for VRAM usage only
        self.percentages_1.append(self.monitor.get_vram_usage_percent())
        
        # Update the graph
        self.show_graph()
