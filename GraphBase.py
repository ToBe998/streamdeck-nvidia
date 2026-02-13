"""
Base class for graph actions with support for dual-line graphs
"""

from threading import Thread
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

import matplotlib.pyplot as plt
import matplotlib
from multiprocessing import Process, Queue
# Use different backend to prevent errors with running plt in different threads
matplotlib.use('agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image
import io

# Import gtk
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gdk

# Import globals
import globals as gl
from src.Signals import Signals


class GraphBase(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.percentages_1: list[float] = []  # First line data
        self.percentages_2: list[float] = []  # Second line data (optional)

        self.task_queue = Queue()
        self.result_queue = Queue()
        self.process = GraphCreator(task_queue=self.task_queue, result_queue=self.result_queue)
        self.process.start()

        gl.signal_manager.connect_signal(Signals.AppQuit, self.stop_process)

    def stop_process(self, *args):
        self.task_queue.put((None, None, None))

    def set_percentages_length(self, length: int):
        """Ensure data lists have the correct length"""
        # First line
        if len(self.percentages_1) > length:
            self.percentages_1 = self.percentages_1[-length:]
        elif len(self.percentages_1) < length:
            for _ in range(length - len(self.percentages_1)):
                self.percentages_1.insert(0, 0)
        
        # Second line
        if len(self.percentages_2) > length:
            self.percentages_2 = self.percentages_2[-length:]
        elif len(self.percentages_2) < length:
            for _ in range(length - len(self.percentages_2)):
                self.percentages_2.insert(0, 0)

    def get_graph(self) -> Image:
        settings = self.get_settings()
        time_period = settings.get("time-period", 15)
        self.set_percentages_length(time_period)

        self.task_queue.put((settings, self.percentages_1, self.percentages_2))

        img = self.result_queue.get()
        return img

    def show_graph(self):
        image = self.get_graph()
        if image is None:
            return
        self.set_media(image=image)

    def get_config_rows(self) -> list:
        # Line 1 color
        self.line1_color_row = ColorRow()
        self.line1_color_row.color_label.set_label("Line 1 Color:")

        # Line 1 fill color
        self.fill1_color_row = ColorRow()
        self.fill1_color_row.color_label.set_label("Line 1 Fill:")

        # Line 2 color
        self.line2_color_row = ColorRow()
        self.line2_color_row.color_label.set_label("Line 2 Color:")

        # Line 2 fill color
        self.fill2_color_row = ColorRow()
        self.fill2_color_row.color_label.set_label("Line 2 Fill:")

        # Line width
        self.line_width_row = Adw.SpinRow.new_with_range(1, 10, 1)
        self.line_width_row.set_title("Line Width:")

        # Time period
        self.time_period_row = Adw.SpinRow.new_with_range(5, 60, 1)
        self.time_period_row.set_title("Time Period (s):")

        # Dynamic scaling
        self.dynamic_scaling_row = Adw.SwitchRow(title="Dynamic Y-axis Scaling:")

        # Load defaults
        settings = self.get_settings()

        self.line1_color_row.color_button.set_rgba(
            self.prepare_color(settings.get("line1-color", [0, 255, 0, 255]))
        )
        self.fill1_color_row.color_button.set_rgba(
            self.prepare_color(settings.get("fill1-color", [0, 255, 0, 100]))
        )
        self.line2_color_row.color_button.set_rgba(
            self.prepare_color(settings.get("line2-color", [255, 165, 0, 255]))
        )
        self.fill2_color_row.color_button.set_rgba(
            self.prepare_color(settings.get("fill2-color", [255, 165, 0, 100]))
        )

        self.line_width_row.set_value(settings.get("line-width", 3))
        self.time_period_row.set_value(settings.get("time-period", 15))
        self.dynamic_scaling_row.set_active(settings.get("dynamic-scaling", False))

        # Connect signals
        self.line1_color_row.color_button.connect("color-set", self.on_line1_color_change)
        self.fill1_color_row.color_button.connect("color-set", self.on_fill1_color_change)
        self.line2_color_row.color_button.connect("color-set", self.on_line2_color_change)
        self.fill2_color_row.color_button.connect("color-set", self.on_fill2_color_change)
        self.line_width_row.connect("changed", self.on_line_width_change)
        self.time_period_row.connect("changed", self.on_time_period_change)
        self.dynamic_scaling_row.connect("notify::active", self.on_dynamic_scaling_change)

        return [
            self.line1_color_row, self.fill1_color_row,
            self.line2_color_row, self.fill2_color_row,
            self.line_width_row, self.time_period_row,
            self.dynamic_scaling_row
        ]

    def prepare_color(self, color_values: list[int]) -> Gdk.RGBA:
        if len(color_values) == 3:
            color_values.append(255)
        color = Gdk.RGBA()
        color.parse(f"rgba({color_values[0]}, {color_values[1]}, {color_values[2]}, {color_values[3]})")
        return color

    def on_line1_color_change(self, button):
        color = self.line1_color_row.color_button.get_rgba()
        settings = self.get_settings()
        settings["line1-color"] = [
            round(color.red * 255),
            round(color.green * 255),
            round(color.blue * 255),
            round(color.alpha * 255)
        ]
        self.set_settings(settings)
        self.show_graph()

    def on_fill1_color_change(self, button):
        color = self.fill1_color_row.color_button.get_rgba()
        settings = self.get_settings()
        settings["fill1-color"] = [
            round(color.red * 255),
            round(color.green * 255),
            round(color.blue * 255),
            round(color.alpha * 255)
        ]
        self.set_settings(settings)
        self.show_graph()

    def on_line2_color_change(self, button):
        color = self.line2_color_row.color_button.get_rgba()
        settings = self.get_settings()
        settings["line2-color"] = [
            round(color.red * 255),
            round(color.green * 255),
            round(color.blue * 255),
            round(color.alpha * 255)
        ]
        self.set_settings(settings)
        self.show_graph()

    def on_fill2_color_change(self, button):
        color = self.fill2_color_row.color_button.get_rgba()
        settings = self.get_settings()
        settings["fill2-color"] = [
            round(color.red * 255),
            round(color.green * 255),
            round(color.blue * 255),
            round(color.alpha * 255)
        ]
        self.set_settings(settings)
        self.show_graph()

    def on_line_width_change(self, spin):
        settings = self.get_settings()
        settings["line-width"] = spin.get_value()
        self.set_settings(settings)
        self.show_graph()

    def on_time_period_change(self, spin):
        settings = self.get_settings()
        settings["time-period"] = int(spin.get_value())
        self.set_settings(settings)
        self.set_percentages_length(int(spin.get_value()))
        self.show_graph()

    def on_dynamic_scaling_change(self, switch, *args):
        settings = self.get_settings()
        settings["dynamic-scaling"] = switch.get_active()
        self.set_settings(settings)
        self.show_graph()

    def on_removed_from_cache(self) -> None:
        self.task_queue.put((None, None, None))


class ColorRow(Adw.PreferencesRow):
    def __init__(self):
        super().__init__()

        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            hexpand=True,
            margin_top=10,
            margin_bottom=10,
            margin_start=15,
            margin_end=15
        )
        self.set_child(self.main_box)

        self.color_label = Gtk.Label(label="Color:", hexpand=True, xalign=0)
        self.main_box.append(self.color_label)

        self.color_button = Gtk.ColorButton(use_alpha=True)
        self.main_box.append(self.color_button)


class GraphCreator(Process):
    def __init__(self, task_queue: Queue, result_queue: Queue):
        super().__init__(daemon=True, name="GraphCreator")
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            settings, percentages_1, percentages_2 = self.task_queue.get()
            if None in [settings, percentages_1, percentages_2]:
                break
            result = self.generate_graph(settings, percentages_1, percentages_2)
            self.result_queue.put(result)

    def generate_graph(self, settings: dict, percentages_1: list[float], percentages_2: list[float]):
        """Generate a dual-line graph"""
        # Get colors
        line1_color = self.conv_color_to_plt(settings.get("line1-color", [0, 255, 0, 255]))
        fill1_color = self.conv_color_to_plt(settings.get("fill1-color", [0, 255, 0, 100]))
        line2_color = self.conv_color_to_plt(settings.get("line2-color", [255, 165, 0, 255]))
        fill2_color = self.conv_color_to_plt(settings.get("fill2-color", [255, 165, 0, 100]))
        
        line_width = settings.get("line-width", 3)
        dynamic_scaling = settings.get("dynamic-scaling", False)

        # Create a new figure with a transparent background
        fig = plt.figure(figsize=(6, 6))
        fig.patch.set_alpha(0)
        fig.patch.set_facecolor('none')

        # Set the FigureCanvas to the backend
        canvas = FigureCanvas(fig)

        # Plot the data with a transparent background
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)

        # Plot both lines
        if percentages_1:
            ax.plot(percentages_1, color=line1_color, linewidth=line_width)
            ax.fill_between(
                range(len(percentages_1)),
                percentages_1,
                color=fill1_color[:3],
                alpha=fill1_color[3]
            )

        if percentages_2:
            ax.plot(percentages_2, color=line2_color, linewidth=line_width)
            ax.fill_between(
                range(len(percentages_2)),
                percentages_2,
                color=fill2_color[:3],
                alpha=fill2_color[3]
            )

        # Hide the spines
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Turn off the axis and set margins to zero
        ax.margins(0)
        ax.axis('off')

        # Set the y-axis to range from 0 to 100
        if not dynamic_scaling:
            ax.set_ylim(0, 100)

        # Draw the canvas and retrieve the buffer
        canvas.draw()
        buf = io.BytesIO()
        canvas.print_png(buf)

        # Convert buffer to a Pillow Image
        buf.seek(0)
        img = Image.open(buf)

        plt.close()  # Close the plot to free resources

        return img

    def conv_color_to_plt(self, color: list[int]) -> list[float]:
        """Convert RGB(A) 0-255 values to matplotlib 0-1 floats"""
        float_color: list[float] = []
        for c in color:
            float_color.append(c / 255)
        return float_color
