"""
NVIDIA Logo Action.
Displays the NVIDIA logo on a black background with no graph data.
"""

from src.backend.PluginManager.ActionBase import ActionBase

from PIL import Image
import os


class NVIDIALogo(ActionBase):
    ACTION_NAME = "NVIDIA Logo"
    CONTROLS_KEY_IMAGE = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logo_image = None  # Cached rendered image

    def on_ready(self):
        self.show_logo()

    def on_tick(self):
        # Only render once and cache
        if self.logo_image is None:
            self.show_logo()

    def show_logo(self):
        plugin_dir = self.plugin_base.PATH
        logo_path = os.path.join(plugin_dir, "nvidia_logo.png")

        if not os.path.exists(logo_path):
            return

        if self.logo_image is None:
            # Build logo image: black background + brightened logo
            logo = Image.open(logo_path).convert("RGBA")

            # Create 72x72 output (StreamDeck button size)
            size = 72
            final = Image.new("RGBA", (size, size), (0, 0, 0, 255))

            # Resize logo to fill the button
            logo = logo.resize((size, size), Image.Resampling.LANCZOS)

            # Brighten logo for visibility on dark background
            if logo.mode == 'RGBA':
                r, g, b, a = logo.split()
                brightness = 1.8
                r = r.point(lambda x: min(255, int(x * brightness)))
                g = g.point(lambda x: min(255, int(x * brightness)))
                b = b.point(lambda x: min(255, int(x * brightness)))
                a = a.point(lambda x: int(x * 0.5))  # 50% opacity
                logo = Image.merge('RGBA', (r, g, b, a))

            # Paste logo centered on black background
            final.paste(logo, (0, 0), logo)
            self.logo_image = final

        self.set_media(image=self.logo_image)
