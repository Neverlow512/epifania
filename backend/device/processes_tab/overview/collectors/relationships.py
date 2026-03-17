# Process relationships collector - parent/children process tree

from typing import Dict, List, Optional
from core.logger import get_logger
from device.contexts import InspectionContext

logger = get_logger(__name__, "device")


class RelationshipsCollector:
    def collect(self, ctx: InspectionContext) -> Optional[Dict]:
        try:
            parent_pid = self._get_parent_pid(ctx)
            parent_info = None
            if parent_pid and parent_pid != ctx.pid:
                parent_info = self._get_process_basic_info(ctx, parent_pid)

            children = self._find_children(ctx)

            tree_depth = self._calculate_tree_depth(ctx)

            return {
                "parent_pid": parent_pid,
                "parent": parent_info,
                "children_count": len(children),
                "children": children[:50],
                "tree_depth": tree_depth,
                "truncated": len(children) > 50,
            }

        except Exception as e:
            logger.error(f"Failed to collect relationships for PID {ctx.pid}: {str(e)}")
            return None

    def _get_parent_pid(self, ctx: InspectionContext) -> Optional[int]:
        result = ctx.read_proc_file("stat")
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

    def _get_process_basic_info(self, ctx: InspectionContext, pid: int) -> Optional[Dict]:
        result = ctx.execute_command(
            f"cat /proc/{pid}/stat 2>/dev/null",
            cache_key=f"proc_stat_{pid}"
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

    def _find_children(self, ctx: InspectionContext) -> List[Dict]:
        result = ctx.execute_command(
            "cat /proc/[0-9]*/stat 2>/dev/null",
            cache_key="all_proc_stats"
        )
        if not result:
            return []

        children = []
        for line in result.strip().split("\n"):
            if not line.strip():
                continue

            try:
                start = line.index("(")
                end = line.rindex(")")

                pid_str = line[:start].strip()
                pid = int(pid_str)

                name = line[start + 1:end]
                rest = line[end + 2:].split()

                if len(rest) < 2:
                    continue

                ppid = int(rest[1])

                if ppid == ctx.pid and pid != ctx.pid:
                    children.append({
                        "pid": pid,
                        "name": name,
                        "state": rest[0],
                    })

            except (ValueError, IndexError):
                continue

        children.sort(key=lambda c: c["pid"])
        return children

    def _calculate_tree_depth(self, ctx: InspectionContext, max_depth: int = 20) -> int:
        depth = 0
        current_pid = ctx.pid

        visited = set()

        while current_pid and current_pid > 1 and depth < max_depth:
            if current_pid in visited:
                break
            visited.add(current_pid)

            temp_ctx_result = ctx.execute_command(
                f"cat /proc/{current_pid}/stat 2>/dev/null",
                cache_key=f"proc_stat_depth_{current_pid}"
            )
            
            if not temp_ctx_result:
                break

            try:
                line = temp_ctx_result.strip()
                end = line.rindex(")")
                rest = line[end + 2:].split()
                if len(rest) > 1:
                    parent = int(rest[1])
                    if parent == current_pid:
                        break
                    current_pid = parent
                    depth += 1
                else:
                    break
            except (ValueError, IndexError):
                break

        return depth

