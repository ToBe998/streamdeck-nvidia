from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

# Import gtk modules
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

import sys
import os

# Add plugin to sys.paths
sys.path.append(os.path.dirname(__file__))

from .NVIDIACombinedGraph import NVIDIACombinedGraph
from .NVIDIAGPUGraph import NVIDIAGPUGraph
from .NVIDIAVRAMGraph import NVIDIAVRAMGraph
from .actions.NVIDIAMetrics.NVIDIAMetrics import NVIDIAMetrics


class NVIDIAPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        
        # Text action showing configurable GPU metrics
        self.nvidia_metrics_holder = ActionHolder(
            plugin_base=self,
            action_base=NVIDIAMetrics,
            action_id_suffix="NVIDIAMetrics",
            action_name="NVIDIA GPU Metrics",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED
            }
        )
        self.add_action_holder(self.nvidia_metrics_holder)
        
        # GPU-only graph
        self.nvidia_gpu_graph_holder = ActionHolder(
            plugin_base=self,
            action_base=NVIDIAGPUGraph,
            action_id_suffix="NVIDIAGPUGraph",
            action_name="NVIDIA GPU Usage Graph",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED
            }
        )
        self.add_action_holder(self.nvidia_gpu_graph_holder)
        
        # VRAM-only graph
        self.nvidia_vram_graph_holder = ActionHolder(
            plugin_base=self,
            action_base=NVIDIAVRAMGraph,
            action_id_suffix="NVIDIAVRAMGraph",
            action_name="NVIDIA VRAM Usage Graph",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED
            }
        )
        self.add_action_holder(self.nvidia_vram_graph_holder)
        
        # Combined graph showing GPU and VRAM usage
        self.nvidia_combined_graph_holder = ActionHolder(
            plugin_base=self,
            action_base=NVIDIACombinedGraph,
            action_id_suffix="NVIDIACombinedGraph",
            action_name="NVIDIA GPU + VRAM Graph",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED
            }
        )
        self.add_action_holder(self.nvidia_combined_graph_holder)
        
        # Register plugin
        self.register(
            plugin_name="NVIDIA GPU Monitor",
            github_repo="https://github.com/StreamController/NVIDIAPlugin",
            plugin_version="1.0.0",
            app_version="1.0.0-alpha"
        )
