# Process file descriptors collector - FD list, limits, categorization

from typing import Dict, List, Optional
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")


class FilesCollector:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager

    def collect(self, device_serial: str, pid: int, has_root: bool = False) -> Optional[Dict]:
        try:
            fds = self._get_file_descriptors(device_serial, pid, has_root)
            limits = self._get_fd_limits(device_serial, pid)

            categorized = self._categorize_fds(fds)

            return {
                "count": len(fds),
                "max_fds": limits.get("max_open_files"),
                "soft_limit": limits.get("soft_limit"),
                "hard_limit": limits.get("hard_limit"),
                "categories": categorized,
                "fds": fds,
                "full_access": has_root or self._check_fd_access(device_serial, pid),
            }

        except Exception as e:
            logger.error(f"Failed to collect files for PID {pid}: {str(e)}")
            return None

    def _get_file_descriptors(self, device_serial: str, pid: int, has_root: bool) -> List[Dict]:
        if has_root:
            cmd = f"su -c 'ls -la /proc/{pid}/fd 2>/dev/null'"
        else:
            cmd = f"ls -la /proc/{pid}/fd 2>/dev/null"

        result = self.adb_manager.execute_shell(device_serial, cmd)
        if not result:
            return []

        fds = []
        for line in result.strip().split("\n"):
            if "->" not in line:
                continue

            parts = line.split("->")
            if len(parts) != 2:
                continue

            left_parts = parts[0].strip().split()
            if not left_parts:
                continue

            fd_str = left_parts[-1]
            try:
                fd_num = int(fd_str)
            except ValueError:
                continue

            target = parts[1].strip()
            fd_type = self._determine_fd_type(target)

            fds.append({
                "fd": fd_num,
                "target": target,
                "type": fd_type,
            })

        fds.sort(key=lambda x: x["fd"])
        return fds

    def _determine_fd_type(self, target: str) -> str:
        if target.startswith("socket:"):
            return "socket"
        elif target.startswith("pipe:"):
            return "pipe"
        elif target.startswith("anon_inode:"):
            subtype = target.replace("anon_inode:", "").strip("[]")
            if "event" in subtype.lower():
                return "eventfd"
            elif "epoll" in subtype.lower():
                return "epoll"
            elif "signalfd" in subtype.lower():
                return "signalfd"
            elif "timerfd" in subtype.lower():
                return "timerfd"
            return "anon_inode"
        elif target.startswith("/dev/"):
            return "device"
        elif target.startswith("/proc/"):
            return "proc"
        elif target.startswith("/sys/"):
            return "sysfs"
        elif target == "/dev/null":
            return "null"
        elif target == "/dev/zero":
            return "zero"
        elif target.startswith("/"):
            return "file"
        else:
            return "other"

    def _categorize_fds(self, fds: List[Dict]) -> Dict[str, int]:
        categories = {}
        for fd in fds:
            fd_type = fd.get("type", "other")
            categories[fd_type] = categories.get(fd_type, 0) + 1
        return categories

    def _get_fd_limits(self, device_serial: str, pid: int) -> Dict:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"cat /proc/{pid}/limits 2>/dev/null | grep 'Max open files'"
        )
        if not result:
            return {}

        try:
            parts = result.strip().split()
            # Format: Max open files            1024                 1048576              files
            soft_idx = None
            hard_idx = None

            for i, part in enumerate(parts):
                if part.isdigit():
                    if soft_idx is None:
                        soft_idx = i
                    else:
                        hard_idx = i
                        break

            if soft_idx is not None and hard_idx is not None:
                return {
                    "soft_limit": int(parts[soft_idx]),
                    "hard_limit": int(parts[hard_idx]),
                    "max_open_files": int(parts[hard_idx]),
                }
        except (ValueError, IndexError):
            pass

        return {}

    def _check_fd_access(self, device_serial: str, pid: int) -> bool:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"ls /proc/{pid}/fd 2>&1 | head -1"
        )
        if not result:
            return False
        return "Permission denied" not in result

