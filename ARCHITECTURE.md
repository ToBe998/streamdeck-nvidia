# NVIDIA GPU Monitor Plugin - Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         StreamController                                 │
│                     (Flatpak Application)                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Loads Plugin
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      main.py (NVIDIAPlugin)                             │
│─────────────────────────────────────────────────────────────────────────│
│  • Registers plugin with StreamController                              │
│  • Creates ActionHolders for each action                               │
│  • Defines input support (Key, Dial, Touchscreen)                      │
└─────────────────────────────────────────────────────────────────────────┘
                    │                              │
                    │                              │
        ┌───────────▼───────────┐      ┌──────────▼──────────┐
        │   NVIDIAMetrics       │      │ NVIDIACombinedGraph │
        │   (Text Action)       │      │  (Graph Action)     │
        └───────────────────────┘      └─────────────────────┘
                    │                              │
                    │                              │
                    │                   ┌──────────▼──────────┐
                    │                   │    GraphBase        │
                    │                   │                     │
                    │                   │ • Dual-line support │
                    │                   │ • Color config UI   │
                    │                   │ • Async rendering   │
                    │                   └──────────┬──────────┘
                    │                              │
                    │                   ┌──────────▼──────────┐
                    │                   │   GraphCreator      │
                    │                   │   (Process)         │
                    │                   │                     │
                    │                   │ • matplotlib plots  │
                    │                   │ • PNG buffer        │
                    │                   │ • PIL Image         │
                    │                   └─────────────────────┘
                    │                              │
                    └──────────┬───────────────────┘
                               │
                               │ Uses
                               ▼
                    ┌──────────────────────┐
                    │   NVIDIAMonitor      │
                    │   (Singleton)        │
                    │──────────────────────│
                    │ get_nvidia_monitor() │
                    │──────────────────────│
                    │ • get_gpu_util()     │
                    │ • get_vram_usage%()  │
                    │ • get_vram_used_mb() │
                    │ • get_vram_total_mb()│
                    │ • get_temperature()  │
                    └──────────┬───────────┘
                               │
                               │ Uses pynvml
                               ▼
                    ┌──────────────────────┐
                    │    NVIDIA Driver     │
                    │    (nvml library)    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    NVIDIA GPU        │
                    │  (Physical Hardware) │
                    └──────────────────────┘
```

## Component Interaction Flow

### Text Action Update Cycle
```
on_tick() [Every ~100ms]
    │
    ├─► get_settings()
    │   ├─ top-metric: "gpu-usage"
    │   ├─ center-metric: "vram-usage"
    │   └─ bottom-metric: "temperature"
    │
    ├─► get_nvidia_monitor()
    │   ├─ get_gpu_utilization() ──► 45.2%
    │   ├─ get_vram_usage_percent() ──► 62.8%
    │   └─ get_temperature() ──► 68°C
    │
    └─► Update Display
        ├─ set_top_label("45%", font_size=16)
        ├─ set_center_label("63%", font_size=16)
        └─ set_bottom_label("68°C", font_size=16)
```

### Graph Action Update Cycle
```
on_tick() [Every ~100ms]
    │
    ├─► get_nvidia_monitor()
    │   ├─ get_gpu_utilization() ──► 45.2%
    │   └─ get_vram_usage_percent() ──► 62.8%
    │
    ├─► Append Data
    │   ├─ percentages_1.append(45.2)  [GPU]
    │   └─ percentages_2.append(62.8)  [VRAM]
    │
    └─► show_graph()
        │
        ├─► get_settings()
        │   ├─ line1-color: [0, 255, 0, 255]
        │   ├─ fill1-color: [0, 255, 0, 100]
        │   ├─ line2-color: [255, 165, 0, 255]
        │   ├─ fill2-color: [255, 165, 0, 100]
        │   ├─ line-width: 3
        │   ├─ time-period: 15
        │   └─ dynamic-scaling: False
        │
        ├─► task_queue.put(settings, percentages_1, percentages_2)
        │
        ├─► [GraphCreator Process]
        │   ├─ Create matplotlib figure
        │   ├─ Plot line 1 (GPU) with green color
        │   ├─ Fill line 1 with green alpha
        │   ├─ Plot line 2 (VRAM) with orange color
        │   ├─ Fill line 2 with orange alpha
        │   ├─ Set ylim(0, 100)
        │   ├─ Render to PNG buffer
        │   └─ Convert to PIL Image
        │
        ├─► result_queue.get()
        │   └─ [PIL Image Object]
        │
        └─► set_media(image=PIL_Image)
```

## Configuration UI Flow

### Text Action Settings
```
User opens settings
    │
    ├─► get_config_rows()
    │   │
    │   ├─ Create ComboRow "Top Label Metric"
    │   │   └─ Options: None, GPU%, VRAM%, VRAM Used, VRAM Total, Temp
    │   │
    │   ├─ Create ComboRow "Center Label Metric"
    │   │   └─ Options: None, GPU%, VRAM%, VRAM Used, VRAM Total, Temp
    │   │
    │   ├─ Create ComboRow "Bottom Label Metric"
    │   │   └─ Options: None, GPU%, VRAM%, VRAM Used, VRAM Total, Temp
    │   │
    │   └─ Create SpinRow "Font Size" (8-48)
    │
    └─► Connect Signals
        ├─ top_metric_row.connect("notify::selected", on_metric_change)
        ├─ center_metric_row.connect("notify::selected", on_metric_change)
        ├─ bottom_metric_row.connect("notify::selected", on_metric_change)
        └─ font_size_row.connect("changed", on_font_size_change)

User changes setting
    │
    ├─► Signal triggered
    │   └─ on_metric_change() or on_font_size_change()
    │
    ├─► Update settings
    │   ├─ settings = get_settings()
    │   ├─ settings["top-metric"] = new_value
    │   └─ set_settings(settings)
    │
    └─► update()
        └─ Display refreshes immediately
```

### Graph Action Settings
```
User opens settings
    │
    ├─► get_config_rows()
    │   │
    │   ├─ Create ColorRow "Line 1 Color" (GPU)
    │   ├─ Create ColorRow "Line 1 Fill" (GPU fill)
    │   ├─ Create ColorRow "Line 2 Color" (VRAM)
    │   ├─ Create ColorRow "Line 2 Fill" (VRAM fill)
    │   ├─ Create SpinRow "Line Width" (1-10)
    │   ├─ Create SpinRow "Time Period" (5-60s)
    │   └─ Create SwitchRow "Dynamic Y-axis"
    │
    └─► Connect Signals
        ├─ line1_color.connect("color-set", on_line1_color_change)
        ├─ fill1_color.connect("color-set", on_fill1_color_change)
        ├─ line2_color.connect("color-set", on_line2_color_change)
        ├─ fill2_color.connect("color-set", on_fill2_color_change)
        ├─ line_width.connect("changed", on_line_width_change)
        ├─ time_period.connect("changed", on_time_period_change)
        └─ dynamic_scaling.connect("notify::active", on_dynamic_scaling_change)

User picks color
    │
    ├─► Signal: on_line1_color_change()
    │   │
    │   ├─ Get RGBA from color button
    │   │   └─ rgba(0, 255, 0, 255) → [0, 255, 0, 255]
    │   │
    │   ├─ Update settings
    │   │   ├─ settings = get_settings()
    │   │   ├─ settings["line1-color"] = [0, 255, 0, 255]
    │   │   └─ set_settings(settings)
    │   │
    │   └─► show_graph()
    │       └─ Graph re-renders with new color
    │
    └─► Display updates immediately
```

## Multiprocessing Architecture

```
┌──────────────────────────┐
│   Main Process           │
│   (StreamController)     │
│──────────────────────────│
│                          │
│  ┌────────────────────┐  │
│  │  NVIDIAMetrics     │  │     Runs in main process
│  │  (Text Action)     │  │     No multiprocessing needed
│  └────────────────────┘  │     Direct label updates
│                          │
│  ┌────────────────────┐  │
│  │ NVIDIACombined     │  │
│  │ Graph              │  │
│  │                    │  │
│  │ task_queue    ────╋──┼──► Queue ──┐
│  │ result_queue  ◄───╋──┼──◄ Queue ◄─┘
│  └────────────────────┘  │            │
│                          │            │
└──────────────────────────┘            │
                                        │
                                        │
┌──────────────────────────┐            │
│   GraphCreator Process   │◄───────────┘
│   (Separate Process)     │
│──────────────────────────│
│                          │
│  while True:             │
│    settings, data1, ───► │  Get from task_queue
│    data2 = queue.get()   │
│                          │
│    if None: break        │
│                          │
│    img = generate_graph( │  matplotlib rendering
│      settings,           │  - Create figure
│      data1,              │  - Plot lines
│      data2               │  - Fill areas
│    )                     │  - Render to PNG
│                          │  - Convert to PIL
│                          │
│    result_queue.put(img) │  Send PIL Image back
│                          │
└──────────────────────────┘

Benefits:
• Graph rendering doesn't block UI
• Main thread stays responsive
• Heavy matplotlib operations isolated
• Clean process shutdown on plugin unload
```

## Data Flow Summary

```
NVIDIA GPU Hardware
        │
        │ NVML API
        ▼
   pynvml Library
        │
        │ Python Bindings
        ▼
  NVIDIAMonitor (Singleton)
        │
        ├──────────────┬──────────────┐
        │              │              │
        ▼              ▼              ▼
  GPU Usage%    VRAM Usage%    Temperature
        │              │              │
        ├──────────────┴──────────────┤
        │                             │
        ▼                             ▼
  NVIDIAMetrics              NVIDIACombinedGraph
  (Text Display)             (Dual-Line Graph)
        │                             │
        ▼                             ▼
  set_top_label()            set_media(PIL_Image)
  set_center_label()
  set_bottom_label()
        │                             │
        └──────────────┬──────────────┘
                       │
                       ▼
              StreamController UI
                       │
                       ▼
              StreamDeck Hardware
```

## Plugin Lifecycle

```
StreamController Starts
        │
        ▼
Load Plugins
        │
        ├─► Import main.py
        │   └─► NVIDIAPlugin.__init__()
        │       ├─ Create ActionHolders
        │       ├─ register() plugin
        │       └─ Plugin ready
        │
        └─► Plugin appears in sidebar

User Drags Action to Button
        │
        ▼
Action Instance Created
        │
        ├─► NVIDIAMetrics.__init__()  or  NVIDIACombinedGraph.__init__()
        │   ├─ Call super().__init__()
        │   ├─ Set has_configuration = True
        │   └─ Get monitor: get_nvidia_monitor()
        │       └─ Returns singleton instance
        │
        ▼
on_ready() Called
        │
        ├─► Initial update/display
        │   └─ Graph: show_graph()
        │       └─ Starts GraphCreator process
        │
        └─► Action visible on button

Continuous Updates (Every ~100ms)
        │
        ▼
on_tick() Called
        │
        ├─► NVIDIAMetrics:
        │   └─ Update all three labels
        │
        └─► NVIDIACombinedGraph:
            ├─ Append new data points
            └─ Render updated graph

User Removes Action
        │
        ▼
on_removed_from_cache() Called
        │
        └─► GraphBase:
            ├─ Send (None, None, None) to task_queue
            └─ GraphCreator process exits cleanly

StreamController Exits
        │
        ▼
AppQuit Signal
        │
        └─► stop_process()
            └─ Cleanup all processes
```
