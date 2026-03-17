# Process I/O statistics collector - /proc/{pid}/io (typically requires root)

from typing import Dict, Optional
from core.logger import get_logger
from device.contexts import InspectionContext

logger = get_logger(__name__, "device")


class IOStatsCollector:
    def collect(self, ctx: InspectionContext) -> Optional[Dict]:
        try:
            io_data, error_reason = self._get_io_stats(ctx)
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
            logger.error(f"Failed to collect I/O stats for PID {ctx.pid}: {str(e)}")
            return None

    def _get_io_stats(self, ctx: InspectionContext) -> tuple:
        check_result = ctx.execute_command(
            f"ls /proc/{ctx.pid}/io 2>&1",
            cache_key="io_check"
        )
        
        if check_result and "No such file" in check_result:
            return None, "kernel_not_supported"

        result = ctx.read_proc_file("io", use_root=ctx.has_root)

        if result and "Permission denied" in result:
            return None, "permission_denied"

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

