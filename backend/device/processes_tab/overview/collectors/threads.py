# Process threads collector - thread list with names, states, CPU time

from typing import Dict, List, Optional
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")

THREAD_STATE_MAP = {
    "R": "running",
    "S": "sleeping",
    "D": "disk_sleep",
    "Z": "zombie",
    "T": "traced",
    "t": "tracing_stop",
    "W": "paging",
    "X": "dead",
    "x": "dead",
    "K": "wakekill",
    "P": "parked",
    "I": "idle",
}


class ThreadsCollector:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager

    def collect(self, device_serial: str, pid: int) -> Optional[Dict]:
        try:
            thread_ids = self._get_thread_ids(device_serial, pid)
            if thread_ids is None:
                return None

            threads = []
            for tid in thread_ids:
                thread_info = self._get_thread_info(device_serial, pid, tid)
                if thread_info:
                    threads.append(thread_info)

            threads.sort(key=lambda t: t["tid"])

            main_thread = next((t for t in threads if t["tid"] == pid), None)

            return {
                "count": len(threads),
                "threads": threads,
                "main_thread_tid": pid if main_thread else None,
            }

        except Exception as e:
            logger.error(f"Failed to collect threads for PID {pid}: {str(e)}")
            return None

    def _get_thread_ids(self, device_serial: str, pid: int) -> Optional[List[int]]:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"ls /proc/{pid}/task 2>/dev/null"
        )
        if not result or "No such file" in result:
            return None

        tids = []
        for tid_str in result.strip().split():
            try:
                tids.append(int(tid_str))
            except ValueError:
                continue
        return tids

    def _get_thread_info(self, device_serial: str, pid: int, tid: int) -> Optional[Dict]:
        # Batch fetch comm and stat in one command for efficiency
        result = self.adb_manager.execute_shell(
            device_serial,
            f"cat /proc/{pid}/task/{tid}/comm 2>/dev/null; echo '---SEPARATOR---'; cat /proc/{pid}/task/{tid}/stat 2>/dev/null"
        )
        if not result:
            return {"tid": tid, "name": "", "state": "unknown", "state_char": ""}

        parts = result.split("---SEPARATOR---")
        name = parts[0].strip() if parts else ""
        stat_line = parts[1].strip() if len(parts) > 1 else ""

        state_char = ""
        utime = 0
        stime = 0

        if stat_line:
            try:
                start = stat_line.index("(")
                end = stat_line.rindex(")")
                rest = stat_line[end + 2:].split()
                if rest:
                    state_char = rest[0]
                if len(rest) > 12:
                    utime = int(rest[11])
                    stime = int(rest[12])
            except (ValueError, IndexError):
                pass

        return {
            "tid": tid,
            "name": name,
            "state": THREAD_STATE_MAP.get(state_char, "unknown"),
            "state_char": state_char,
            "utime_ticks": utime,
            "stime_ticks": stime,
            "cpu_time_ticks": utime + stime,
            "is_main": tid == pid,
        }

