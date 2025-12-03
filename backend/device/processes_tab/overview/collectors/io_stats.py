# Process I/O statistics collector - /proc/{pid}/io (typically requires root)

from typing import Dict, Optional
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")


class IOStatsCollector:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager

    def collect(self, device_serial: str, pid: int, has_root: bool = False) -> Optional[Dict]:
        try:
            io_data = self._get_io_stats(device_serial, pid, has_root)
            if not io_data:
                return None

            return {
                "rchar": io_data.get("rchar"),
                "wchar": io_data.get("wchar"),
                "syscr": io_data.get("syscr"),
                "syscw": io_data.get("syscw"),
                "read_bytes": io_data.get("read_bytes"),
                "write_bytes": io_data.get("write_bytes"),
                "cancelled_write_bytes": io_data.get("cancelled_write_bytes"),
                "available": True,
            }

        except Exception as e:
            logger.error(f"Failed to collect I/O stats for PID {pid}: {str(e)}")
            return None

    def _get_io_stats(self, device_serial: str, pid: int, has_root: bool) -> Optional[Dict]:
        if has_root:
            cmd = f"su -c 'cat /proc/{pid}/io' 2>/dev/null"
        else:
            cmd = f"cat /proc/{pid}/io 2>/dev/null"

        result = self.adb_manager.execute_shell(device_serial, cmd)

        if not result or "Permission denied" in result or not result.strip():
            # Try with su if initial attempt failed and we have root
            if has_root and "Permission denied" in (result or ""):
                result = self.adb_manager.execute_shell(
                    device_serial,
                    f"su -c 'cat /proc/{pid}/io 2>/dev/null'"
                )
            if not result or "Permission denied" in result or not result.strip():
                return None

        data = {}
        for line in result.strip().split("\n"):
            if ":" not in line:
                continue

            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            try:
                data[key] = int(value)
            except ValueError:
                continue

        return data if data else None

