# Process file descriptors collector - FD list, limits, categorization

from typing import Dict, List, Optional
from core.logger import get_logger
from device.contexts import InspectionContext

logger = get_logger(__name__, "device")


class FilesCollector:
    def collect(self, ctx: InspectionContext) -> Optional[Dict]:
        try:
            fds = self._get_file_descriptors(ctx)
            limits = self._get_fd_limits(ctx)

            categorized = self._categorize_fds(fds)

            return {
                "count": len(fds),
                "max_fds": limits.get("max_open_files"),
                "soft_limit": limits.get("soft_limit"),
                "hard_limit": limits.get("hard_limit"),
                "categories": categorized,
                "fds": fds,
                "full_access": ctx.has_root or self._check_fd_access(ctx),
            }

        except Exception as e:
            logger.error(f"Failed to collect files for PID {ctx.pid}: {str(e)}")
            return None

    def _get_file_descriptors(self, ctx: InspectionContext) -> List[Dict]:
        result = ctx.list_directory(f"/proc/{ctx.pid}/fd", use_root=ctx.has_root)
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

    def _get_fd_limits(self, ctx: InspectionContext) -> Dict:
        result = ctx.read_proc_file("limits")
        if not result:
            return {}

        try:
            for line in result.strip().split("\n"):
                if "Max open files" in line:
                    parts = line.strip().split()
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

    def _check_fd_access(self, ctx: InspectionContext) -> bool:
        result = ctx.execute_command(
            f"ls /proc/{ctx.pid}/fd 2>&1 | head -1",
            cache_key="fd_access_check"
        )
        if not result:
            return False
        return "Permission denied" not in result

