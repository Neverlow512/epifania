# CPU monitoring for Android devices via ADB

from typing import Dict, List, Optional
from collections import defaultdict
import time
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")


class CPUMonitor:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager
        self._previous_stats: Dict[str, Dict] = defaultdict(dict)
        self._previous_timestamps: Dict[str, float] = {}
        logger.info("CPUMonitor initialized")
    
    def get_cpu_stats(self, device_serial: str, top_n: int = 5) -> Dict:
        try:
            overall = self._get_overall_cpu(device_serial)
            top_consumers = self._get_top_consumers(device_serial, top_n)
            
            return {
                "overall_percent": overall,
                "top_consumers": top_consumers
            }
        except Exception as e:
            logger.error(f"Failed to get CPU stats for {device_serial}: {str(e)}")
            return {
                "overall_percent": 0.0,
                "top_consumers": []
            }
    
    def _get_overall_cpu(self, device_serial: str) -> float:
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                "cat /proc/stat | head -1"
            )
            
            if not result:
                return 0.0
            
            parts = result.strip().split()
            if len(parts) < 5 or parts[0] != "cpu":
                return 0.0
            
            # cpu user nice system idle iowait irq softirq steal guest guest_nice
            user = int(parts[1])
            nice = int(parts[2])
            system = int(parts[3])
            idle = int(parts[4])
            iowait = int(parts[5]) if len(parts) > 5 else 0
            irq = int(parts[6]) if len(parts) > 6 else 0
            softirq = int(parts[7]) if len(parts) > 7 else 0
            steal = int(parts[8]) if len(parts) > 8 else 0
            
            total = user + nice + system + idle + iowait + irq + softirq + steal
            idle_total = idle + iowait
            
            current_time = time.time()
            prev = self._previous_stats.get(device_serial, {})
            prev_time = self._previous_timestamps.get(device_serial, 0)
            
            self._previous_stats[device_serial] = {
                "total": total,
                "idle": idle_total
            }
            self._previous_timestamps[device_serial] = current_time
            
            if not prev or "total" not in prev:
                return 0.0
            
            total_diff = total - prev["total"]
            idle_diff = idle_total - prev["idle"]
            
            if total_diff <= 0:
                return 0.0
            
            cpu_percent = ((total_diff - idle_diff) / total_diff) * 100
            return round(max(0.0, min(100.0, cpu_percent)), 1)
            
        except Exception as e:
            logger.error(f"Failed to get overall CPU for {device_serial}: {str(e)}")
            return 0.0
    
    def _get_top_consumers(self, device_serial: str, top_n: int = 5) -> List[Dict]:
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                "top -n 1 -b -o %CPU 2>/dev/null | head -20"
            )
            
            if not result:
                return self._fallback_top_consumers(device_serial, top_n)
            
            consumers = []
            lines = result.strip().split('\n')
            in_process_section = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect header line (PID is typically first column)
                if "PID" in line and ("CPU" in line or "%CPU" in line):
                    in_process_section = True
                    continue
                
                if not in_process_section:
                    continue
                
                parts = line.split()
                if len(parts) < 9:
                    continue
                
                try:
                    pid = int(parts[0])
                    # CPU% position varies by Android version, usually index 8 or 9
                    cpu_str = None
                    for i, p in enumerate(parts):
                        if '%' in p or (p.replace('.', '').isdigit() and i > 4):
                            cpu_str = p.replace('%', '')
                            break
                    
                    if cpu_str is None:
                        cpu_str = parts[8] if len(parts) > 8 else "0"
                    
                    cpu_percent = float(cpu_str.replace('%', ''))
                    name = parts[-1]
                    
                    if cpu_percent > 0:
                        consumers.append({
                            "pid": pid,
                            "name": name,
                            "cpu_percent": round(cpu_percent, 1)
                        })
                except (ValueError, IndexError):
                    continue
            
            consumers.sort(key=lambda x: x["cpu_percent"], reverse=True)
            return consumers[:top_n]
            
        except Exception as e:
            logger.error(f"Failed to get top CPU consumers for {device_serial}: {str(e)}")
            return []
    
    def _fallback_top_consumers(self, device_serial: str, top_n: int = 5) -> List[Dict]:
        # Fallback using ps if top is not available
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                "ps -A -o PID,NAME,%CPU 2>/dev/null | sort -k3 -rn | head -10"
            )
            
            if not result:
                return []
            
            consumers = []
            for line in result.strip().split('\n')[1:]:
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        pid = int(parts[0])
                        name = parts[1]
                        cpu_percent = float(parts[2].replace('%', ''))
                        if cpu_percent > 0:
                            consumers.append({
                                "pid": pid,
                                "name": name,
                                "cpu_percent": round(cpu_percent, 1)
                            })
                    except (ValueError, IndexError):
                        continue
            
            return consumers[:top_n]
            
        except Exception as e:
            logger.debug(f"Fallback CPU consumers failed: {str(e)}")
            return []

