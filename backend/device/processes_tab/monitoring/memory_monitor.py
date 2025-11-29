# Memory monitoring for Android devices via ADB

from typing import Dict, Optional
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")


class MemoryMonitor:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager
        logger.info("MemoryMonitor initialized")
    
    def get_memory_stats(self, device_serial: str, focused_pid: Optional[int] = None) -> Dict:
        try:
            system_memory = self._get_system_memory(device_serial)
            
            result = {
                "total_mb": system_memory.get("total_mb", 0),
                "used_mb": system_memory.get("used_mb", 0),
                "free_mb": system_memory.get("free_mb", 0),
                "available_mb": system_memory.get("available_mb", 0),
                "buffers_mb": system_memory.get("buffers_mb", 0),
                "cached_mb": system_memory.get("cached_mb", 0)
            }
            
            if focused_pid:
                focused = self._get_process_memory(device_serial, focused_pid)
                if focused:
                    result["focused_process"] = focused
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get memory stats for {device_serial}: {str(e)}")
            return {
                "total_mb": 0,
                "used_mb": 0,
                "free_mb": 0,
                "available_mb": 0,
                "buffers_mb": 0,
                "cached_mb": 0
            }
    
    def _get_system_memory(self, device_serial: str) -> Dict:
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                "cat /proc/meminfo"
            )
            
            if not result:
                return {}
            
            meminfo = {}
            for line in result.strip().split('\n'):
                if ':' not in line:
                    continue
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Extract numeric value (in kB)
                parts = value.split()
                if parts:
                    try:
                        meminfo[key] = int(parts[0])
                    except ValueError:
                        continue
            
            total_kb = meminfo.get("MemTotal", 0)
            free_kb = meminfo.get("MemFree", 0)
            available_kb = meminfo.get("MemAvailable", free_kb)
            buffers_kb = meminfo.get("Buffers", 0)
            cached_kb = meminfo.get("Cached", 0)
            
            # Used = Total - Free - Buffers - Cached (approximation)
            used_kb = total_kb - free_kb - buffers_kb - cached_kb
            used_kb = max(0, used_kb)
            
            return {
                "total_mb": round(total_kb / 1024, 1),
                "used_mb": round(used_kb / 1024, 1),
                "free_mb": round(free_kb / 1024, 1),
                "available_mb": round(available_kb / 1024, 1),
                "buffers_mb": round(buffers_kb / 1024, 1),
                "cached_mb": round(cached_kb / 1024, 1)
            }
            
        except Exception as e:
            logger.error(f"Failed to get system memory for {device_serial}: {str(e)}")
            return {}
    
    def _get_process_memory(self, device_serial: str, pid: int) -> Optional[Dict]:
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                f"cat /proc/{pid}/status 2>/dev/null"
            )
            
            if not result:
                return None
            
            status = {}
            name = f"pid_{pid}"
            
            for line in result.strip().split('\n'):
                if ':' not in line:
                    continue
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == "Name":
                    name = value
                elif key in ("VmRSS", "VmSize", "VmPeak", "VmHWM"):
                    parts = value.split()
                    if parts:
                        try:
                            status[key] = int(parts[0])
                        except ValueError:
                            continue
            
            if not status:
                return None
            
            rss_kb = status.get("VmRSS", 0)
            vsz_kb = status.get("VmSize", 0)
            peak_kb = status.get("VmPeak", 0)
            hwm_kb = status.get("VmHWM", 0)
            
            return {
                "pid": pid,
                "name": name,
                "rss_mb": round(rss_kb / 1024, 2),
                "vsz_mb": round(vsz_kb / 1024, 2),
                "peak_mb": round(peak_kb / 1024, 2),
                "hwm_mb": round(hwm_kb / 1024, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get process memory for PID {pid}: {str(e)}")
            return None

