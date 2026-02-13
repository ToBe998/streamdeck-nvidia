"""
Singleton monitor for NVIDIA GPU metrics using pynvml
"""

import pynvml
from loguru import logger as log


class NVIDIAMonitor:
    """Singleton monitor for NVIDIA GPU metrics"""
    
    def __init__(self):
        self.initialized = False
        self.handle = None
        try:
            pynvml.nvmlInit()
            # Get first GPU (index 0)
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            self.initialized = True
            log.info("NVIDIA GPU monitoring initialized successfully")
        except Exception as e:
            log.error(f"Failed to initialize NVIDIA GPU monitoring: {e}")
            self.initialized = False
    
    def get_gpu_utilization(self) -> float:
        """Get current GPU usage percentage (0-100)"""
        if not self.initialized:
            return 0.0
        try:
            utilization = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            return float(utilization.gpu)
        except Exception as e:
            log.error(f"Failed to get GPU utilization: {e}")
            return 0.0
    
    def get_vram_usage_percent(self) -> float:
        """Get current VRAM usage percentage (0-100)"""
        if not self.initialized:
            return 0.0
        try:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            return (mem_info.used / mem_info.total) * 100
        except Exception as e:
            log.error(f"Failed to get VRAM usage: {e}")
            return 0.0
    
    def get_vram_used_mb(self) -> int:
        """Get current VRAM used in MB"""
        if not self.initialized:
            return 0
        try:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            return int(mem_info.used / (1024 * 1024))
        except Exception as e:
            log.error(f"Failed to get VRAM used: {e}")
            return 0
    
    def get_vram_total_mb(self) -> int:
        """Get total VRAM in MB"""
        if not self.initialized:
            return 0
        try:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            return int(mem_info.total / (1024 * 1024))
        except Exception as e:
            log.error(f"Failed to get total VRAM: {e}")
            return 0
    
    def get_temperature(self) -> int:
        """Get current GPU temperature in Celsius"""
        if not self.initialized:
            return 0
        try:
            temp = pynvml.nvmlDeviceGetTemperature(self.handle, pynvml.NVML_TEMPERATURE_GPU)
            return int(temp)
        except Exception as e:
            log.error(f"Failed to get GPU temperature: {e}")
            return 0
    
    def __del__(self):
        """Cleanup on destruction"""
        if self.initialized:
            try:
                pynvml.nvmlShutdown()
            except:
                pass


# Singleton instance
_nvidia_monitor_instance = None

def get_nvidia_monitor() -> NVIDIAMonitor:
    """Get or create the singleton NVIDIA monitor instance"""
    global _nvidia_monitor_instance
    if _nvidia_monitor_instance is None:
        _nvidia_monitor_instance = NVIDIAMonitor()
    return _nvidia_monitor_instance
