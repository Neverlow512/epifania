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
            io_data, error_reason = self._get_io_stats(device_serial, pid, has_root)
            if not io_data:
                if error_reason:
                    return {"available": False, "error": error_reason}
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

    def _get_io_stats(self, device_serial: str, pid: int, has_root: bool) -> tuple:
        # First check if the io file exists at all (kernel support)
        check_cmd = f"ls /proc/{pid}/io 2>&1"
        check_result = self.adb_manager.execute_shell(device_serial, check_cmd)
        
        if check_result and "No such file" in check_result:
            # Kernel doesn't have CONFIG_TASK_IO_ACCOUNTING enabled
            return None, "kernel_not_supported"

        # Try with su first if we believe we have root
        if has_root:
            cmd = f"su -c 'cat /proc/{pid}/io' 2>&1"
        else:
            cmd = f"cat /proc/{pid}/io 2>&1"

        result = self.adb_manager.execute_shell(device_serial, cmd)

        # Check for permission denied
        if result and "Permission denied" in result:
            # Try with su as fallback
            result = self.adb_manager.execute_shell(
                device_serial,
                f"su -c 'cat /proc/{pid}/io' 2>&1"
            )
            if not result or "Permission denied" in result:
                return None, "permission_denied"

        # Check for file not found (process may have died or kernel doesn't support)
        if result and "No such file" in result:
            return None, "kernel_not_supported"

        if not result or not result.strip():
            return None, "unknown"

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

        return (data, None) if data else (None, "parse_error")

