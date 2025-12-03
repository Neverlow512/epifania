# Process memory collector - PSS/USS via smaps_rollup, status, dumpsys meminfo

from typing import Dict, Optional, Tuple
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")


class MemoryCollector:
    def __init__(self, adb_manager: ADBManager):
        self.adb_manager = adb_manager

    def collect(self, device_serial: str, pid: int) -> Optional[Dict]:
        try:
            status_memory = self._get_status_memory(device_serial, pid)
            if not status_memory:
                return None

            smaps_memory, smaps_available = self._get_smaps_rollup(device_serial, pid)
            dumpsys_memory, dumpsys_available = self._get_dumpsys_meminfo(device_serial, pid)

            result = {
                "rss_kb": status_memory.get("rss_kb", 0),
                "vsz_kb": status_memory.get("vsz_kb", 0),
                "peak_kb": status_memory.get("peak_kb", 0),
                "hwm_kb": status_memory.get("hwm_kb", 0),
                "swap_kb": status_memory.get("swap_kb", 0),
                "pss_kb": None,
                "uss_kb": None,
                "private_clean_kb": None,
                "private_dirty_kb": None,
                "shared_clean_kb": None,
                "shared_dirty_kb": None,
                "smaps_available": smaps_available,
                "dumpsys_available": dumpsys_available,
            }

            if smaps_memory:
                result["pss_kb"] = smaps_memory.get("pss_kb")
                result["uss_kb"] = smaps_memory.get("uss_kb")
                result["private_clean_kb"] = smaps_memory.get("private_clean_kb")
                result["private_dirty_kb"] = smaps_memory.get("private_dirty_kb")
                result["shared_clean_kb"] = smaps_memory.get("shared_clean_kb")
                result["shared_dirty_kb"] = smaps_memory.get("shared_dirty_kb")
                if smaps_memory.get("swap_kb"):
                    result["swap_kb"] = smaps_memory["swap_kb"]

            if dumpsys_memory:
                result["dumpsys"] = dumpsys_memory

            return result

        except Exception as e:
            logger.error(f"Failed to collect memory for PID {pid}: {str(e)}")
            return None

    def _get_status_memory(self, device_serial: str, pid: int) -> Optional[Dict]:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"cat /proc/{pid}/status 2>/dev/null"
        )
        if not result:
            return None

        data = {}
        for line in result.strip().split("\n"):
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            kb_value = self._parse_kb_value(value)
            if kb_value is None:
                continue

            if key == "VmRSS":
                data["rss_kb"] = kb_value
            elif key == "VmSize":
                data["vsz_kb"] = kb_value
            elif key == "VmPeak":
                data["peak_kb"] = kb_value
            elif key == "VmHWM":
                data["hwm_kb"] = kb_value
            elif key == "VmSwap":
                data["swap_kb"] = kb_value

        return data if data else None

    def _get_smaps_rollup(self, device_serial: str, pid: int) -> Tuple[Optional[Dict], bool]:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"cat /proc/{pid}/smaps_rollup 2>/dev/null"
        )
        if not result or "No such file" in result or "Permission denied" in result:
            return None, False

        data = {}
        for line in result.strip().split("\n"):
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            kb_value = self._parse_kb_value(value)
            if kb_value is None:
                continue

            if key == "Pss":
                data["pss_kb"] = kb_value
            elif key == "Private_Clean":
                data["private_clean_kb"] = kb_value
            elif key == "Private_Dirty":
                data["private_dirty_kb"] = kb_value
            elif key == "Shared_Clean":
                data["shared_clean_kb"] = kb_value
            elif key == "Shared_Dirty":
                data["shared_dirty_kb"] = kb_value
            elif key == "Swap":
                data["swap_kb"] = kb_value

        if data:
            private_clean = data.get("private_clean_kb", 0) or 0
            private_dirty = data.get("private_dirty_kb", 0) or 0
            data["uss_kb"] = private_clean + private_dirty

        return (data, True) if data else (None, False)

    def _get_dumpsys_meminfo(self, device_serial: str, pid: int) -> Tuple[Optional[Dict], bool]:
        result = self.adb_manager.execute_shell(
            device_serial,
            f"dumpsys meminfo {pid} 2>/dev/null | head -100"
        )
        if not result or "No process found" in result or not result.strip():
            return None, False

        data = {
            "total_pss_kb": None,
            "total_private_dirty_kb": None,
            "total_private_clean_kb": None,
            "total_swap_pss_kb": None,
            "java_heap_kb": None,
            "native_heap_kb": None,
            "code_kb": None,
            "stack_kb": None,
            "graphics_kb": None,
            "system_kb": None,
        }

        lines = result.strip().split("\n")
        in_summary = False

        for line in lines:
            line_stripped = line.strip()

            if "TOTAL" in line_stripped and not in_summary:
                parts = line_stripped.split()
                # TOTAL line format varies, try to extract PSS
                for i, part in enumerate(parts):
                    if part == "TOTAL" and i + 1 < len(parts):
                        try:
                            data["total_pss_kb"] = int(parts[i + 1])
                        except ValueError:
                            pass
                        break

            if "App Summary" in line_stripped:
                in_summary = True
                continue

            if in_summary:
                if "Java Heap:" in line_stripped:
                    data["java_heap_kb"] = self._extract_summary_value(line_stripped)
                elif "Native Heap:" in line_stripped:
                    data["native_heap_kb"] = self._extract_summary_value(line_stripped)
                elif "Code:" in line_stripped:
                    data["code_kb"] = self._extract_summary_value(line_stripped)
                elif "Stack:" in line_stripped:
                    data["stack_kb"] = self._extract_summary_value(line_stripped)
                elif "Graphics:" in line_stripped:
                    data["graphics_kb"] = self._extract_summary_value(line_stripped)
                elif "System:" in line_stripped:
                    data["system_kb"] = self._extract_summary_value(line_stripped)
                elif "TOTAL PSS:" in line_stripped:
                    data["total_pss_kb"] = self._extract_summary_value(line_stripped)
                elif "TOTAL SWAP PSS:" in line_stripped:
                    data["total_swap_pss_kb"] = self._extract_summary_value(line_stripped)

        has_data = any(v is not None for v in data.values())
        return (data, True) if has_data else (None, False)

    def _extract_summary_value(self, line: str) -> Optional[int]:
        parts = line.split()
        for part in parts:
            try:
                return int(part)
            except ValueError:
                continue
        return None

    def _parse_kb_value(self, value: str) -> Optional[int]:
        parts = value.split()
        if not parts:
            return None
        try:
            return int(parts[0])
        except ValueError:
            return None

