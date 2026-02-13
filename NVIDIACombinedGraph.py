"""
NVIDIA GPU + VRAM Combined Graph Action
Displays GPU usage and VRAM usage as two lines on the same graph
"""

from plugins.com_streamcontroller_NVIDIAPlugin.GraphBase import GraphBase
from plugins.com_streamcontroller_NVIDIAPlugin.NVIDIAMonitor import get_nvidia_monitor
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

from PIL import Image


class NVIDIACombinedGraph(GraphBase):
    ACTION_NAME = "NVIDIA GPU + VRAM Graph"
    CONTROLS_KEY_IMAGE = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True
        self.monitor = get_nvidia_monitor()

    def on_ready(self):
        self.show_graph()

    def on_tick(self):
        # Append new data points
        # Line 1: GPU usage
        self.percentages_1.append(self.monitor.get_gpu_utilization())
        
        # Line 2: VRAM usage
        self.percentages_2.append(self.monitor.get_vram_usage_percent())
        
        # Update the graph
        self.show_graph()
