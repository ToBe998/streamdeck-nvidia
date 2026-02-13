"""
NVIDIA GPU Metrics Text Action
Displays configurable GPU metrics in top/center/bottom labels
"""

from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.PluginManager.PluginBase import PluginBase

# Import gtk modules
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from plugins.com_streamcontroller_NVIDIAPlugin.NVIDIAMonitor import get_nvidia_monitor


class NVIDIAMetrics(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True
        self.monitor = get_nvidia_monitor()

    def on_ready(self):
        self.update()

    def on_tick(self):
        self.update()

    def update(self):
        settings = self.get_settings()
        
        # Get metric choices for each label position
        top_metric = settings.get("top-metric", "none")
        center_metric = settings.get("center-metric", "gpu-usage")
        bottom_metric = settings.get("bottom-metric", "none")
        
        font_size = settings.get("font-size", 16)
        
        # Update each label position
        self.set_top_label(text=self.get_metric_text(top_metric), font_size=font_size)
        self.set_center_label(text=self.get_metric_text(center_metric), font_size=font_size)
        self.set_bottom_label(text=self.get_metric_text(bottom_metric), font_size=font_size)

    def get_metric_text(self, metric: str) -> str:
        """Get formatted text for the specified metric"""
        if metric == "none":
            return ""
        elif metric == "gpu-usage":
            return f"{round(self.monitor.get_gpu_utilization())}%"
        elif metric == "vram-usage":
            return f"{round(self.monitor.get_vram_usage_percent())}%"
        elif metric == "vram-total":
            return f"{self.monitor.get_vram_total_mb()} MB"
        elif metric == "temperature":
            return f"{self.monitor.get_temperature()}°C"
        elif metric == "vram-used":
            return f"{self.monitor.get_vram_used_mb()} MB"
        else:
            return ""

    def get_config_rows(self) -> list:
        # Create metric dropdown options
        metric_options = Gtk.StringList()
        metric_options.append("None")
        metric_options.append("GPU Usage %")
        metric_options.append("VRAM Usage %")
        metric_options.append("VRAM Used (MB)")
        metric_options.append("Total VRAM (MB)")
        metric_options.append("Temperature (°C)")

        # Top label metric selector
        self.top_metric_row = Adw.ComboRow(
            model=metric_options,
            title="Top Label Metric"
        )

        # Center label metric selector
        self.center_metric_row = Adw.ComboRow(
            model=metric_options,
            title="Center Label Metric"
        )

        # Bottom label metric selector
        self.bottom_metric_row = Adw.ComboRow(
            model=metric_options,
            title="Bottom Label Metric"
        )

        # Font size selector
        self.font_size_row = Adw.SpinRow.new_with_range(8, 48, 1)
        self.font_size_row.set_title("Font Size")

        # Load saved settings
        settings = self.get_settings()
        
        # Map metric names to indices
        metric_map = {
            "none": 0,
            "gpu-usage": 1,
            "vram-usage": 2,
            "vram-used": 3,
            "vram-total": 4,
            "temperature": 5
        }
        
        top_metric = settings.get("top-metric", "none")
        center_metric = settings.get("center-metric", "gpu-usage")
        bottom_metric = settings.get("bottom-metric", "none")
        
        self.top_metric_row.set_selected(metric_map.get(top_metric, 0))
        self.center_metric_row.set_selected(metric_map.get(center_metric, 1))
        self.bottom_metric_row.set_selected(metric_map.get(bottom_metric, 0))
        
        self.font_size_row.set_value(settings.get("font-size", 16))

        # Connect signals
        self.top_metric_row.connect("notify::selected", self.on_metric_change)
        self.center_metric_row.connect("notify::selected", self.on_metric_change)
        self.bottom_metric_row.connect("notify::selected", self.on_metric_change)
        self.font_size_row.connect("changed", self.on_font_size_change)

        return [
            self.top_metric_row,
            self.center_metric_row,
            self.bottom_metric_row,
            self.font_size_row
        ]

    def on_metric_change(self, *args):
        settings = self.get_settings()
        
        # Map indices back to metric names
        index_to_metric = {
            0: "none",
            1: "gpu-usage",
            2: "vram-usage",
            3: "vram-used",
            4: "vram-total",
            5: "temperature"
        }
        
        settings["top-metric"] = index_to_metric.get(self.top_metric_row.get_selected(), "none")
        settings["center-metric"] = index_to_metric.get(self.center_metric_row.get_selected(), "gpu-usage")
        settings["bottom-metric"] = index_to_metric.get(self.bottom_metric_row.get_selected(), "none")
        
        self.set_settings(settings)
        self.update()

    def on_font_size_change(self, spin):
        settings = self.get_settings()
        settings["font-size"] = int(spin.get_value())
        self.set_settings(settings)
        self.update()
