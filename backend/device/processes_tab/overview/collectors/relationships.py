# Process relationships collector - parent/children process tree

from typing import Dict, List, Optional
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")


class RelationshipsCollector:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager

    def collect(self, device_serial: str, pid: int) -> Optional[Dict]:
        try:
            # Get parent info from the target process
            parent_pid = self._get_parent_pid(device_serial, pid)
            parent_info = None
            if parent_pid and parent_pid != pid:
                parent_info = self._get_process_basic_info(device_serial, parent_pid)

            # Find children by scanning all processes
            children = self._find_children(device_serial, pid)

            # Calculate tree depth (how many ancestors until init/pid 1)
            tree_depth = self._calculate_tree_depth(device_serial, pid)

            return {
                "parent_pid": parent_pid,
                "parent": parent_info,
                "children_count": len(children),
                "children": children[:50],  # Limit children list
                "tree_depth": tree_depth,
                "truncated": len(children) > 50,
            }

        except Exception as e:
            logger.error(f"Failed to collect relationships for PID {pid}: {str(e)}")
            return None

    def _get_parent_pid(self, device_serial: str, pid: int) -> Optional[int]:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"cat /proc/{pid}/stat 2>/dev/null"
        )
        if not result:
            return None

        try:
            line = result.strip()
            end = line.rindex(")")
            rest = line[end + 2:].split()
            if len(rest) > 1:
                return int(rest[1])
        except (ValueError, IndexError):
            pass

        return None

    def _get_process_basic_info(self, device_serial: str, pid: int) -> Optional[Dict]:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"cat /proc/{pid}/stat 2>/dev/null"
        )
        if not result:
            return None

        try:
            line = result.strip()
            start = line.index("(")
            end = line.rindex(")")
            name = line[start + 1:end]
            rest = line[end + 2:].split()

            state = rest[0] if rest else ""

            return {
                "pid": pid,
                "name": name,
                "state": state,
            }
        except (ValueError, IndexError):
            return {"pid": pid, "name": "", "state": ""}

    def _find_children(self, device_serial: str, parent_pid: int) -> List[Dict]:
        # Get all processes with their PPIDs in a single command
        result = self.adb_manager.execute_shell(
            device_serial,
            "cat /proc/[0-9]*/stat 2>/dev/null"
        )
        if not result:
            return []

        children = []
        for line in result.strip().split("\n"):
            if not line.strip():
                continue

            try:
                # Parse: pid (name) state ppid ...
                start = line.index("(")
                end = line.rindex(")")

                pid_str = line[:start].strip()
                pid = int(pid_str)

                name = line[start + 1:end]
                rest = line[end + 2:].split()

                if len(rest) < 2:
                    continue

                ppid = int(rest[1])

                if ppid == parent_pid and pid != parent_pid:
                    children.append({
                        "pid": pid,
                        "name": name,
                        "state": rest[0],
                    })

            except (ValueError, IndexError):
                continue

        children.sort(key=lambda c: c["pid"])
        return children

    def _calculate_tree_depth(self, device_serial: str, pid: int, max_depth: int = 20) -> int:
        depth = 0
        current_pid = pid

        visited = set()

        while current_pid and current_pid > 1 and depth < max_depth:
            if current_pid in visited:
                break
            visited.add(current_pid)

            parent = self._get_parent_pid(device_serial, current_pid)
            if parent is None or parent == current_pid:
                break

            current_pid = parent
            depth += 1

        return depth

