# StreamController Plugin Development Journal

## Project: Network Monitor Plugin
**Date:** February 13, 2026  
**Purpose:** Document key learnings for future StreamController plugin development

---

## Key Discoveries

### 1. Label Display System

**Critical Learning:** StreamController's label system has three predefined positions (Top, Center, Bottom) that users control via the UI, not the plugin code.

#### ✅ Correct Pattern:
```python
def update(self):
    text = "My Text"
    font_size = 16
    
    # Set ALL three positions - user chooses which to display via UI
    self.set_top_label(text=text, font_size=font_size)
    self.set_center_label(text=text, font_size=font_size)
    self.set_bottom_label(text=text, font_size=font_size)
```

#### ❌ Wrong Approaches Tried:
- Trying to configure label position in plugin settings (conflicts with StreamController's UI)
- Only calling one label method (won't show if user enables different position)
- Custom label positioning (not supported by API)

**Why It Works:** Users enable/disable label positions via the three-dot menu (⋮) → "Aa" button. The plugin provides text to all positions, StreamController shows only enabled ones.

### 2. Graph Display

**Critical Learning:** Graph actions must set `CONTROLS_KEY_IMAGE = True` to tell StreamController they control the button's background.

#### ✅ Correct Pattern:
```python
class MyGraphAction(ActionBase):
    CONTROLS_KEY_IMAGE = True  # Required!
    
    def show_graph(self):
        image = self.generate_graph()  # PIL Image
        # No size parameter!
        self.set_media(image=image)
```

#### ❌ Wrong Approaches Tried:
- Omitting `CONTROLS_KEY_IMAGE` → graph doesn't render
- Using `set_media(image=image, size=0.75)` → incorrect API
- Custom positioning parameters → not supported

**Key Findings:**
- Use `matplotlib` with `agg` backend for graph generation
- Generate PIL Images and pass directly to `set_media()`
- Use multiprocessing Queue for async graph rendering (prevents UI blocking)
- Graphs fill entire button background (no size parameter needed)

### 3. Action Configuration UI

**Pattern for Configuration Rows:**

```python
def get_config_rows(self) -> list:
    # SwitchRow for toggles
    self.toggle = Adw.SwitchRow(
        title="Option Name",
        subtitle="Description"
    )
    
    # SpinRow for numbers
    self.number = Adw.SpinRow.new_with_range(min_val, max_val, step)
    self.number.set_title("Number Setting")
    self.number.set_subtitle("Description")
    
    # ComboRow for dropdowns (needs StringList model)
    model = Gtk.StringList()
    model.append("Option 1")
    model.append("Option 2")
    self.combo = Adw.ComboRow(model=model, title="Choose")
    
    # Load saved values
    settings = self.get_settings()
    self.toggle.set_active(settings.get("key", default))
    self.number.set_value(settings.get("key", default))
    
    # Connect signals
    self.toggle.connect("notify::active", self.on_change)
    self.number.connect("changed", self.on_change)
    
    return [self.toggle, self.number, self.combo]

def on_change(self, *args):
    settings = self.get_settings()
    settings["key"] = self.toggle.get_active()
    settings["number"] = int(self.number.get_value())
    self.set_settings(settings)
    self.update()  # Refresh display
```

### 4. Plugin Structure

**Required Files:**
```
plugin_root/
├── main.py                    # Plugin registration
├── plugin.json                # Metadata
├── requirements.txt           # Dependencies
├── actions/
│   ├── __init__.py           # Empty or imports
│   └── ActionName/
│       ├── __init__.py       # Import action class
│       └── ActionName.py     # Action implementation
└── shared_modules.py          # Shared utilities
```

**main.py Pattern:**
```python
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

from .actions.MyAction.MyAction import MyAction

class MyPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        
        self.action_holder = ActionHolder(
            plugin_base=self,
            action_base=MyAction,
            action_id_suffix="MyAction",
            action_name="Display Name",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED
            }
        )
        self.add_action_holder(self.action_holder)
        
        self.register(
            plugin_name="My Plugin",
            github_repo="https://github.com/...",
            plugin_version="1.0.0",
            app_version="1.0.0-alpha"
        )
```

### 5. Action Lifecycle

**Critical Methods:**

```python
class MyAction(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = True  # Show config panel
        # Initialize instance variables
    
    def on_ready(self):
        # Called when action is added to a button
        # Initial display setup
        self.update()
    
    def on_tick(self):
        # Called periodically (every ~100ms)
        # Update dynamic data
        self.update()
    
    def on_key_down(self):
        # Called when button is pressed
        pass
    
    def on_key_up(self):
        # Called when button is released
        pass
    
    def on_removed_from_cache(self):
        # Cleanup when action is removed
        pass
```

### 6. Common Gotchas

#### Import Paths
- Actions use: `from plugins.plugin_id.module import Class`
- Main.py uses: `from src.backend.PluginManager.* import *`

#### Settings Persistence
```python
# Always get fresh settings
settings = self.get_settings()
# Modify
settings["key"] = value
# Always save
self.set_settings(settings)
```

#### Text with Newlines
```python
# Works correctly
text = f"Line 1\nLine 2"
self.set_center_label(text=text, font_size=16)
```

#### Graph Scaling
```python
# For fixed scale:
ax.set_ylim(0, max_value)

# For dynamic scale:
max_val = max(data_values) if data_values else 1
ax.set_ylim(0, max(max_val, 1))
```

### 7. Deployment Pattern

**Development Workflow:**
```bash
# 1. Edit code in source directory
cd /var/projects/plugin-name

# 2. Copy to StreamController plugins folder
rm -rf ~/.var/app/com.core447.StreamController/data/plugins/plugin_id
cp -r /var/projects/plugin-name ~/.var/app/com.core447.StreamController/data/plugins/plugin_id

# 3. Restart StreamController
pkill -9 -f StreamController
sleep 3
flatpak run com.core447.StreamController

# 4. Check logs for errors
tail -100 ~/.var/app/com.core447.StreamController/data/logs/logs.log | grep -i "plugin_name"
```

**Quick Update (single file):**
```bash
cp source_file.py installed_location/file.py
pkill -9 -f StreamController && sleep 3 && flatpak run com.core447.StreamController
```

### 8. Testing User Settings

**Enable Label Controls:**
1. Add action to button
2. Click three-dot menu (⋮) next to action in sidebar
3. Click "Aa" icon to enable label positions
4. Select Top/Center/Bottom positions to display

**Enable Image Control (for graphs):**
1. Add action to button
2. Click three-dot menu (⋮)
3. Click image icon to allow action to control background

### 9. Dependencies

**Network Monitoring:**
- `psutil` - System metrics (network I/O)
- Use rolling average for smooth display (collections.deque)

**Graph Generation:**
- `matplotlib` with `agg` backend (non-interactive)
- `PIL/Pillow` for image manipulation
- Multiprocessing Queue for async rendering

**UI Configuration:**
- `gi` (PyGObject) - GTK4, Adwaita widgets
- `Gtk.StringList`, `Adw.SwitchRow`, `Adw.SpinRow`, `Adw.ComboRow`

### 10. Best Practices from OSPlugin

Studied `com_core447_OSPlugin` for reference patterns:

**Text Actions:**
- Simple, focused functionality
- Minimal configuration
- Always update in `on_tick()`
- Use `set_center_label()` (user controls position)

**Graph Actions:**
- Set `CONTROLS_KEY_IMAGE = True`
- Use multiprocessing for graph generation
- Provide color/scale customization
- Clean up processes in `on_removed_from_cache()`

**Shared Utilities:**
- Singleton pattern for monitors (avoid duplicate instances)
- Format helpers for consistent display
- Separate graph base class for reusability

---

## Mistakes Made & Fixed

1. **Label Position Config** - Tried to add custom position selector → Removed, use StreamController's built-in
2. **Single Label Call** - Only called `set_center_label()` → Now call all three positions
3. **Graph Size Parameter** - Used `set_media(image=image, size=0.75)` → Removed size parameter
4. **Missing CONTROLS_KEY_IMAGE** - Graphs didn't render → Added class attribute
5. **Max Rate Range** - Started at 1 instead of 0 → Changed to allow 0 for auto mode
6. **Partial Updates** - Only deployed some files → Always deploy complete changes

---

## Success Patterns

### Singleton Monitor Pattern
```python
_network_monitor_instance = None

def get_network_monitor():
    global _network_monitor_instance
    if _network_monitor_instance is None:
        _network_monitor_instance = NetworkMonitor()
    return _network_monitor_instance
```

### Rolling Average
```python
from collections import deque

class Monitor:
    def __init__(self):
        self.measurements = deque(maxlen=5)  # 5-second window
    
    def update(self):
        current = self.get_current_value()
        self.measurements.append(current)
        return sum(self.measurements) / len(self.measurements)
```

### Multi-line Text
```python
# Combine metrics with newline separator
text = f"{upload_arrow}{upload_rate}\n{download_arrow}{download_rate}"
self.set_center_label(text=text, font_size=font_size)
```

---

## Final Plugin Structure

```
streamdeck-network/
├── main.py                           # Plugin registration
├── plugin.json                       # Metadata & action list
├── requirements.txt                  # psutil, matplotlib, Pillow
├── NetworkMonitor.py                 # Shared monitoring singleton
├── GraphBase.py                      # Base class for graph actions
├── NetworkCombinedGraph.py          # Combined upload/download graph
├── NetworkUploadGraph.py            # Upload graph
├── NetworkDownloadGraph.py          # Download graph
└── actions/
    ├── NetworkUpload/               # Upload rate text
    │   ├── __init__.py
    │   └── NetworkUpload.py
    ├── NetworkDownload/             # Download rate text
    │   ├── __init__.py
    │   └── NetworkDownload.py
    ├── NetworkCombined/             # Combined text (upload + download)
    │   ├── __init__.py
    │   └── NetworkCombined.py
    └── NetworkConnectionStatus/     # Connection indicator
        ├── __init__.py
        └── NetworkConnectionStatus.py
```

---

## Key Takeaways

1. **Follow OSPlugin patterns** - It's the reference implementation
2. **Set all three label positions** - Let users control visibility
3. **Add CONTROLS_KEY_IMAGE for graphs** - Required for background control
4. **Keep it simple** - Minimal config, clear functionality
5. **Test with real hardware** - StreamDeck behavior differs from preview
6. **Check logs frequently** - `~/.var/app/com.core447.StreamController/data/logs/logs.log`
7. **Deploy completely** - Copy all files, avoid partial updates
8. **Use multiprocessing for heavy tasks** - Keeps UI responsive

---

## Resources

- **OSPlugin Repository:** Best reference for patterns and API usage
- **StreamController Logs:** Essential for debugging
- **PyGObject Documentation:** For GTK4/Adwaita widgets
- **Matplotlib Documentation:** For graph generation

---

_This journal represents knowledge gained through iterative development, debugging, and studying the OSPlugin reference implementation._
