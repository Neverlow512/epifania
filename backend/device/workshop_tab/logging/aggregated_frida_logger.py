import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from core.log_paths import LOGS_WORKSHOP_FRIDA
from core.logger import get_logger

logger = get_logger(__name__, "backend")


class AggregatedFridaLogger:
    def __init__(self):
        self._log_file = LOGS_WORKSHOP_FRIDA / "live_session.log"
        self._lock = threading.Lock()
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        LOGS_WORKSHOP_FRIDA.mkdir(parents=True, exist_ok=True)
        if not self._log_file.exists():
            self._log_file.touch()
    
    def log(self, session_number: int, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} - [S{session_number}] {level} - {message}\n"
        
        with self._lock:
            try:
                with open(self._log_file, "a", encoding="utf-8") as f:
                    f.write(log_line)
            except Exception as e:
                logger.error(f"Failed to write to aggregated log: {e}")
    
    def log_session_start(self, session_number: int, device_id: str, pid: int):
        self.log(session_number, "INFO", f"[SESSION_START] Attached to PID {pid} on device {device_id}")
    
    def log_session_lost(self, session_number: int, reason: str, progress: Optional[str] = None):
        msg = f"[SESSION_LOST] {reason}"
        if progress:
            msg += f" - Progress: {progress}"
        self.log(session_number, "ERROR", msg)
    
    def log_session_detached(self, session_number: int, reason: str):
        self.log(session_number, "WARNING", f"[DETACHED] {reason}")
    
    def log_operation_start(self, session_number: int, operation: str, item_count: int, package_id: str = ""):
        pkg_info = f" [{package_id}]" if package_id else ""
        self.log(session_number, "INFO", f"[OPERATION_START] {operation}{pkg_info} - {item_count} classes")
    
    def log_operation_progress(self, session_number: int, operation: str, current: int, total: int, class_name: str):
        short_name = class_name.split(".")[-1] if "." in class_name else class_name
        self.log(session_number, "DEBUG", f"[PROGRESS] {operation} [{current}/{total}] {short_name}")
    
    def log_operation_complete(self, session_number: int, operation: str, success_count: int, total: int, 
                                duration: float = 0, extra_stats: Optional[Dict[str, Any]] = None):
        rate = (success_count / total * 100) if total > 0 else 0
        msg = f"[OPERATION_COMPLETE] {operation} - {success_count}/{total} ({rate:.1f}%)"
        if duration > 0:
            throughput = total / duration if duration > 0 else 0
            msg += f" - {duration:.2f}s ({throughput:.1f} classes/sec)"
        if extra_stats:
            for key, value in extra_stats.items():
                msg += f" - {key}: {value}"
        self.log(session_number, "INFO", msg)
    
    def log_class_scanned(self, session_number: int, class_name: str, success: bool, 
                          is_from_apk: bool = False, loader_type: str = None, error: str = None):
        short_name = class_name.split(".")[-1] if "." in class_name else class_name
        if success:
            source = "APK" if is_from_apk else "System"
            loader = f" ({loader_type})" if loader_type else ""
            self.log(session_number, "DEBUG", f"[SCAN] {short_name} -> {source}{loader}")
        else:
            err_msg = f": {error}" if error else ""
            self.log(session_number, "WARNING", f"[SCAN_FAIL] {short_name}{err_msg}")
    
    def log_class_extracted(self, session_number: int, class_name: str, success: bool, 
                            method_count: int = 0, error: str = None, error_type: str = None):
        short_name = class_name.split(".")[-1] if "." in class_name else class_name
        if success:
            self.log(session_number, "DEBUG", f"[EXTRACT] {short_name} -> {method_count} methods")
        else:
            # Distinguish between unable to load class vs method extraction failure
            if error_type in ["UNABLE_TO_LOAD", "CLASS_NOT_FOUND"]:
                err_info = f" [{error_type}]" if error_type else ""
                err_msg = f": {error}" if error else ""
                self.log(session_number, "WARNING", f"[LOAD_FAIL] {short_name}{err_info}{err_msg}")
            else:
                err_info = f" [{error_type}]" if error_type else ""
                err_msg = f": {error}" if error else ""
                self.log(session_number, "WARNING", f"[EXTRACT_FAIL] {short_name}{err_info}{err_msg}")
    
    def log_class_modifier_scanned(self, session_number: int, class_name: str, success: bool,
                                   modifiers: Optional[Dict[str, bool]] = None, error: str = None):
        short_name = class_name.split(".")[-1] if "." in class_name else class_name
        if success and modifiers:
            active = [k.replace("is_", "") for k, v in modifiers.items() if v]
            mod_str = ", ".join(active) if active else "none"
            self.log(session_number, "DEBUG", f"[MODIFIERS] {short_name} -> {mod_str}")
        elif not success:
            err_msg = f": {error}" if error else ""
            self.log(session_number, "WARNING", f"[MODIFIERS_FAIL] {short_name}{err_msg}")
    
    def log_extraction_summary(self, session_number: int, total_classes: int, total_methods: int,
                               success_count: int, error_count: int, duration: float):
        success_rate = (success_count / total_classes * 100) if total_classes > 0 else 0
        avg_methods = (total_methods / success_count) if success_count > 0 else 0
        self.log(session_number, "INFO", 
                 f"[SUMMARY] Extracted {total_methods} methods from {success_count}/{total_classes} classes "
                 f"({success_rate:.1f}% success, avg {avg_methods:.1f} methods/class) "
                 f"- {error_count} errors in {duration:.2f}s")
    
    def log_scan_summary(self, session_number: int, operation: str, total: int, 
                         from_apk: int, from_system: int, errors: int, duration: float):
        self.log(session_number, "INFO",
                 f"[SUMMARY] {operation}: {total} classes ({from_apk} APK, {from_system} System, {errors} errors) "
                 f"in {duration:.2f}s")
    
    def log_error(self, session_number: int, operation: str, error: str, class_name: str = None):
        if class_name:
            short_name = class_name.split(".")[-1] if "." in class_name else class_name
            self.log(session_number, "ERROR", f"[ERROR] {operation} - {short_name}: {error}")
        else:
            self.log(session_number, "ERROR", f"[ERROR] {operation}: {error}")
    
    def log_warning(self, session_number: int, message: str):
        self.log(session_number, "WARNING", message)
    
    def log_info(self, session_number: int, message: str):
        self.log(session_number, "INFO", message)
    
    def log_debug(self, session_number: int, message: str):
        self.log(session_number, "DEBUG", message)
    
    def log_health_check(self, session_number: int, status: str, details: str):
        level = "DEBUG" if status == "healthy" else "WARNING"
        self.log(session_number, level, f"[HEALTH_CHECK] {status}: {details}")
    
    def log_health_degradation(self, session_number: int, reason: str, severity: str = "WARNING"):
        level = "ERROR" if severity == "ERROR" else "WARNING"
        self.log(session_number, level, f"[HEALTH_DEGRADED] {reason}")
    
    def log_health_recovery(self, session_number: int, details: str):
        self.log(session_number, "INFO", f"[HEALTH_RECOVERED] {details}")
    
    def log_discovery_start(self, session_number: int, package_id: str, pid: int, filter_mode: str):
        self.log(session_number, "INFO", f"[DISCOVERY_START] Package: {package_id}, PID: {pid}, Filter: {filter_mode}")
    
    def log_discovery_phase(self, session_number: int, phase: str, message: str, progress_pct: int = 0):
        self.log(session_number, "INFO", f"[DISCOVERY_PHASE] {phase} ({progress_pct}%) - {message}")
    
    def log_discovery_complete(self, session_number: int, stats: Dict[str, Any]):
        classes = stats.get("total_classes", 0)
        methods = stats.get("total_methods", 0)
        duration = stats.get("duration", 0)
        self.log(session_number, "INFO", 
                 f"[DISCOVERY_COMPLETE] {classes} classes, {methods} methods in {duration:.1f}s")
    
    def log_discovery_cancelled(self, session_number: int, reason: str, phase: str):
        self.log(session_number, "WARNING", f"[DISCOVERY_CANCELLED] Phase: {phase}, Reason: {reason}")
    
    def log_script_loaded(self, session_number: int, script_name: str, script_type: str = "operation"):
        self.log(session_number, "DEBUG", f"[SCRIPT_LOADED] {script_name} ({script_type})")
    
    def log_script_unloaded(self, session_number: int, script_name: str):
        self.log(session_number, "DEBUG", f"[SCRIPT_UNLOADED] {script_name}")
    
    def log_script_error(self, session_number: int, script_name: str, error: str):
        self.log(session_number, "ERROR", f"[SCRIPT_ERROR] {script_name}: {error}")
    
    def log_native_discovery_start(self, session_number: int):
        self.log(session_number, "INFO", f"[NATIVE_DISCOVERY_START]")
    
    def log_native_discovery_complete(self, session_number: int, stats: Dict[str, Any]):
        modules = stats.get("module_count", 0)
        exports = stats.get("export_count", 0)
        duration = stats.get("duration", 0)
        self.log(session_number, "INFO", 
                 f"[NATIVE_DISCOVERY_COMPLETE] {modules} modules, {exports} exports in {duration:.1f}s")
    
    def log_native_module(self, session_number: int, module_name: str, export_count: int):
        self.log(session_number, "DEBUG", f"[NATIVE_MODULE] {module_name} -> {export_count} exports")
    
    def log_performance_metric(self, session_number: int, operation: str, metric_name: str, value: Any):
        self.log(session_number, "DEBUG", f"[PERFORMANCE] {operation} - {metric_name}: {value}")
    
    def clear(self) -> bool:
        with self._lock:
            try:
                with open(self._log_file, "w", encoding="utf-8") as f:
                    f.write("")
                logger.info("Aggregated Frida log cleared")
                return True
            except Exception as e:
                logger.error(f"Failed to clear aggregated log: {e}")
                return False
    
    def get_logs(self, max_lines: int = 1000) -> List[str]:
        with self._lock:
            try:
                if not self._log_file.exists():
                    return []
                
                with open(self._log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                if len(lines) > max_lines:
                    lines = lines[-max_lines:]
                
                return [line.rstrip("\n") for line in lines]
            except Exception as e:
                logger.error(f"Failed to read aggregated log: {e}")
                return []


aggregated_frida_logger = AggregatedFridaLogger()
