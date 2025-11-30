# CPU monitoring for Android devices via ADB

from typing import Dict, List
from collections import defaultdict
import time
from core.logger import get_logger
from core.adb_manager import ADBManager
from device.processes_tab.monitoring.cache import device_metrics_cache

logger = get_logger(__name__, "device")


class CPUMonitor:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager
        self._previous_stats: Dict[str, Dict] = defaultdict(dict)
        self._previous_timestamps: Dict[str, float] = {}
        logger.info("CPUMonitor initialized")
    
    def get_cpu_stats(self, device_serial: str, top_n: int = 5) -> Dict:
        # Use cache to prevent race conditions from concurrent requests
        cache_key = f"cpu:{device_serial}:{top_n}"
        
        def compute():
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
        
        return device_metrics_cache.get_or_compute(cache_key, compute, ttl=1.5)
    
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
        # Primary: use top command for real-time CPU data
        consumers = self._parse_top_output(device_serial, top_n)
        if consumers:
            return consumers
        
        # Fallback: use ps command (widely supported, slightly smoothed values)
        return self._fallback_ps_consumers(device_serial, top_n)
    
    def _parse_top_output(self, device_serial: str, top_n: int = 5) -> List[Dict]:
        try:
            # Use top without -o flag to get full process info
            # -m limits output to top N+10 processes (buffer for parsing)
            result = self.adb_manager.execute_shell(
                device_serial,
                f"top -n 1 -b -m {top_n + 10} 2>/dev/null"
            )
            
            if not result:
                logger.debug("top command returned no output")
                return []
            
            consumers = []
            lines = result.strip().split('\n')
            in_process_section = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect header line containing PID
                if "PID" in line:
                    in_process_section = True
                    continue
                
                if not in_process_section:
                    continue
                
                parts = line.split()
                # Format: PID USER PR NI VIRT RES SHR S CPU% %MEM TIME+ ARGS...
                # Minimum 12 parts for a valid line with ARGS
                if len(parts) < 12:
                    continue
                
                try:
                    pid = int(parts[0])
                    
                    # Column 8 is CPU% (after PID USER PR NI VIRT RES SHR S)
                    cpu_percent = float(parts[8].replace('%', ''))
                    
                    # ARGS starts at column 11 - take first word as process name
                    args = ' '.join(parts[11:])
                    name = self._extract_process_name(args)
                    
                    consumers.append({
                        "pid": pid,
                        "name": name,
                        "cpu_percent": round(cpu_percent, 1)
                    })
                except (ValueError, IndexError):
                    continue
            
            # Sort by CPU and return top N
            consumers.sort(key=lambda x: x["cpu_percent"], reverse=True)
            return consumers[:top_n]
            
        except Exception as e:
            logger.debug(f"top parsing failed for {device_serial}: {str(e)}")
            return []
    
    def _extract_process_name(self, args: str) -> str:
        if not args:
            return "unknown"
        
        # Handle kernel threads like [kworker/u8:1]
        if args.startswith('[') and ']' in args:
            return args.split(']')[0] + ']'
        
        # Get first token (the executable)
        first_token = args.split()[0] if args.split() else args
        
        # Remove path prefix
        if '/' in first_token:
            first_token = first_token.split('/')[-1]
        
        return first_token
    
    def _fallback_ps_consumers(self, device_serial: str, top_n: int = 5) -> List[Dict]:
        # Fallback using ps - provides slightly smoothed CPU values but widely supported
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                f"ps -A -o PID,NAME,%CPU 2>/dev/null | sort -k3 -rn | head -{top_n + 5}"
            )
            
            if not result:
                logger.debug("ps fallback returned no output")
                return []
            
            consumers = []
            for line in result.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) < 3:
                    continue
                
                try:
                    pid = int(parts[0])
                    name = parts[1]
                    cpu_str = parts[2].replace('%', '')
                    cpu_percent = float(cpu_str)
                    
                    consumers.append({
                        "pid": pid,
                        "name": name,
                        "cpu_percent": round(cpu_percent, 1)
                    })
                except (ValueError, IndexError):
                    continue
            
            return consumers[:top_n]
            
        except Exception as e:
            logger.debug(f"ps fallback failed for {device_serial}: {str(e)}")
            return []

