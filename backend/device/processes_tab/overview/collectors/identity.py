# Process identity collector - PID info, scheduling, timing

import re
from typing import Dict, Optional
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")

KERNEL_STATE_MAP = {
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

ANDROID_PROC_STATE_MAP = {
    0: "persistent",
    1: "persistent",
    2: "foreground",
    3: "foreground",
    4: "visible",
    5: "service",
    6: "bound",
    7: "visible",
    8: "background",
    9: "background",
    10: "background",
    11: "service",
    12: "receiver",
    13: "cached",
    14: "background",
    15: "cached",
    16: "cached",
    17: "cached",
    18: "cached",
    19: "cached",
    20: "cached",
}


class IdentityCollector:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager

    def collect(self, device_serial: str, pid: int) -> Optional[Dict]:
        try:
            stat_data = self._parse_stat(device_serial, pid)
            if not stat_data:
                return None

            status_data = self._parse_status(device_serial, pid)
            uptime = self._get_uptime(device_serial)
            clock_ticks = self._get_clock_ticks(device_serial)

            running_seconds = None
            if uptime and clock_ticks and stat_data.get("starttime"):
                boot_time_ticks = stat_data["starttime"]
                start_seconds = boot_time_ticks / clock_ticks
                running_seconds = int(uptime - start_seconds)
                if running_seconds < 0:
                    running_seconds = None

            kernel_state = KERNEL_STATE_MAP.get(stat_data.get("state", ""), "unknown")
            android_state = self._get_android_state(device_serial, pid)
            name = stat_data.get("name", "")
            is_kernel_thread = name.startswith("[") and name.endswith("]")

            return {
                "pid": pid,
                "name": name,
                "state": kernel_state,
                "kernel_state": kernel_state,
                "state_char": stat_data.get("state", ""),
                "android_state": android_state,
                "is_kernel_thread": is_kernel_thread,
                "ppid": stat_data.get("ppid"),
                "uid": status_data.get("uid"),
                "gid": status_data.get("gid"),
                "thread_count": status_data.get("threads", stat_data.get("num_threads")),
                "nice": stat_data.get("nice"),
                "priority": stat_data.get("priority"),
                "utime_ticks": stat_data.get("utime"),
                "stime_ticks": stat_data.get("stime"),
                "cpu_time_ticks": (stat_data.get("utime", 0) or 0) + (stat_data.get("stime", 0) or 0),
                "running_seconds": running_seconds,
                "cmdline": self._get_cmdline(device_serial, pid),
            }

        except Exception as e:
            logger.error(f"Failed to collect identity for PID {pid}: {str(e)}")
            return None

    def _get_android_state(self, device_serial: str, pid: int) -> Optional[str]:
        try:
            result = self.adb_manager.execute_shell(
                device_serial,
                f"dumpsys activity processes 2>/dev/null | grep -A5 'pid={pid}[^0-9]' | head -10"
            )
            if not result:
                return None

            for line in result.split("\n"):
                if "curProcState=" in line:
                    match = re.search(r"curProcState=(\d+)", line)
                    if match:
                        proc_state = int(match.group(1))
                        return ANDROID_PROC_STATE_MAP.get(proc_state, "background")

            return None
        except Exception as e:
            logger.debug(f"Failed to get Android state for PID {pid}: {e}")
            return None

    def _parse_stat(self, device_serial: str, pid: int) -> Optional[Dict]:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"cat /proc/{pid}/stat 2>/dev/null"
        )
        if not result or not result.strip():
            return None

        line = result.strip()
        # Format: pid (comm) state ppid pgrp session tty_nr tpgid flags ...
        # comm can contain spaces and parentheses, so parse carefully
        try:
            start = line.index("(")
            end = line.rindex(")")
            name = line[start + 1:end]
            rest = line[end + 2:].split()

            if len(rest) < 20:
                return None

            return {
                "name": name,
                "state": rest[0],
                "ppid": int(rest[1]),
                "pgrp": int(rest[2]),
                "session": int(rest[3]),
                "tty_nr": int(rest[4]),
                "tpgid": int(rest[5]),
                "flags": int(rest[6]),
                "minflt": int(rest[7]),
                "cminflt": int(rest[8]),
                "majflt": int(rest[9]),
                "cmajflt": int(rest[10]),
                "utime": int(rest[11]),
                "stime": int(rest[12]),
                "cutime": int(rest[13]),
                "cstime": int(rest[14]),
                "priority": int(rest[15]),
                "nice": int(rest[16]),
                "num_threads": int(rest[17]),
                "starttime": int(rest[19]),
            }
        except (ValueError, IndexError) as e:
            logger.debug(f"Failed to parse /proc/{pid}/stat: {e}")
            return None

    def _parse_status(self, device_serial: str, pid: int) -> Dict:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"cat /proc/{pid}/status 2>/dev/null"
        )
        if not result:
            return {}

        data = {}
        for line in result.strip().split("\n"):
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if key == "Uid":
                parts = value.split()
                if parts:
                    data["uid"] = int(parts[0])
            elif key == "Gid":
                parts = value.split()
                if parts:
                    data["gid"] = int(parts[0])
            elif key == "Threads":
                try:
                    data["threads"] = int(value)
                except ValueError:
                    pass

        return data

    def _get_uptime(self, device_serial: str) -> Optional[float]:
        result = self.adb_manager.execute_shell(
            device_serial,
            "cat /proc/uptime 2>/dev/null"
        )
        if not result:
            return None
        try:
            return float(result.strip().split()[0])
        except (ValueError, IndexError):
            return None

    def _get_clock_ticks(self, device_serial: str) -> Optional[int]:
        result = self.adb_manager.execute_shell(
            device_serial,
            "getconf CLK_TCK 2>/dev/null"
        )
        if not result:
            return 100  # Default on most Linux systems
        try:
            return int(result.strip())
        except ValueError:
            return 100

    def _get_cmdline(self, device_serial: str, pid: int) -> str:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"cat /proc/{pid}/cmdline 2>/dev/null | tr '\\0' ' '"
        )
        return result.strip() if result else ""

