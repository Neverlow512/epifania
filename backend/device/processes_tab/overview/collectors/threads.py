# Process threads collector - thread list with names, states, CPU time

from typing import Dict, List, Optional
from core.logger import get_logger
from device.contexts import InspectionContext

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
    def collect(self, ctx: InspectionContext) -> Optional[Dict]:
        try:
            thread_ids = self._get_thread_ids(ctx)
            if thread_ids is None:
                return None

            threads = []
            for tid in thread_ids:
                thread_info = self._get_thread_info(ctx, tid)
                if thread_info:
                    threads.append(thread_info)

            threads.sort(key=lambda t: t["tid"])

            main_thread = next((t for t in threads if t["tid"] == ctx.pid), None)

            return {
                "count": len(threads),
                "threads": threads,
                "main_thread_tid": ctx.pid if main_thread else None,
            }

        except Exception as e:
            logger.error(f"Failed to collect threads for PID {ctx.pid}: {str(e)}")
            return None

    def _get_thread_ids(self, ctx: InspectionContext) -> Optional[List[int]]:
        result = ctx.list_directory(f"/proc/{ctx.pid}/task")
        if not result or "No such file" in result:
            return None

        tids = []
        for line in result.strip().split("\n"):
            parts = line.split()
            if parts:
                tid_str = parts[-1]
                try:
                    tids.append(int(tid_str))
                except ValueError:
                    continue
        return tids

    def _get_thread_info(self, ctx: InspectionContext, tid: int) -> Optional[Dict]:
        result = ctx.execute_command(
            f"cat /proc/{ctx.pid}/task/{tid}/comm 2>/dev/null; echo '---SEPARATOR---'; cat /proc/{ctx.pid}/task/{tid}/stat 2>/dev/null",
            cache_key=f"thread_{tid}"
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
            "is_main": tid == ctx.pid,
        }

