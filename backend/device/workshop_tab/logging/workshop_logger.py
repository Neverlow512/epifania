# Workshop-specific logging with per-discovery and per-session log files
import logging
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
from core.log_paths import (
    ensure_log_directories,
    LOGS_WORKSHOP_DISCOVERY,
    LOGS_WORKSHOP_FRIDA,
    LOGS_WORKSHOP_CATEGORIZATION,
    LOGS_WORKSHOP_ERRORS
)


class WorkshopLogger:
    def __init__(self):
        ensure_log_directories()
        self._loggers = {}
        self._file_handlers = {}
    
    def _create_handler(self, log_file: Path, level=logging.DEBUG):
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,
            backupCount=5
        )
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        return handler
    
    def _get_or_create_logger(self, name: str, log_file: Path) -> logging.Logger:
        key = str(log_file)
        if key not in self._loggers:
            logger = logging.getLogger(f"workshop.{name}")
            logger.setLevel(logging.DEBUG)
            handler = self._create_handler(log_file)
            logger.addHandler(handler)
            self._loggers[key] = logger
            self._file_handlers[key] = handler
        return self._loggers[key]
    
    def get_discovery_logger(self, package_id: str, timestamp: str = None) -> logging.Logger:
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_package = package_id.replace(".", "_")
        log_file = LOGS_WORKSHOP_DISCOVERY / f"{safe_package}_{timestamp}.log"
        return self._get_or_create_logger(f"discovery.{package_id}", log_file)
    
    def get_frida_logger(self, device_id: str) -> logging.Logger:
        safe_device = device_id.replace(":", "_")
        log_file = LOGS_WORKSHOP_FRIDA / f"session_{safe_device}.log"
        return self._get_or_create_logger(f"frida.{device_id}", log_file)
    
    def get_categorization_logger(self, package_id: str, timestamp: str = None) -> logging.Logger:
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_package = package_id.replace(".", "_")
        log_file = LOGS_WORKSHOP_CATEGORIZATION / f"{safe_package}_{timestamp}.log"
        return self._get_or_create_logger(f"categorization.{package_id}", log_file)
    
    def get_error_logger(self) -> logging.Logger:
        log_file = LOGS_WORKSHOP_ERRORS / "workshop_errors.log"
        return self._get_or_create_logger("errors", log_file)
    
    def get_operation_logger(self, package_id: str, session_folder: Path, operation_type: str, operation_timestamp: str) -> logging.Logger:
        # Create operation type subdirectory
        op_dir = session_folder / operation_type
        op_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file: {operation_type}/{timestamp}.log
        log_file = op_dir / f"{operation_timestamp}.log"
        
        # Create unique logger name
        logger_name = f"operation.{package_id}.{operation_type}.{operation_timestamp}"
        return self._get_or_create_logger(logger_name, log_file)
    
    def close_logger(self, log_file: Path):
        key = str(log_file)
        if key in self._file_handlers:
            handler = self._file_handlers[key]
            handler.close()
            if key in self._loggers:
                self._loggers[key].removeHandler(handler)
            del self._file_handlers[key]
            del self._loggers[key]


workshop_logger = WorkshopLogger()


def get_discovery_logger(package_id: str, timestamp: str = None) -> logging.Logger:
    return workshop_logger.get_discovery_logger(package_id, timestamp)


def get_frida_logger(device_id: str) -> logging.Logger:
    return workshop_logger.get_frida_logger(device_id)


def get_categorization_logger(package_id: str, timestamp: str = None) -> logging.Logger:
    return workshop_logger.get_categorization_logger(package_id, timestamp)


def get_error_logger() -> logging.Logger:
    return workshop_logger.get_error_logger()


def read_discovery_logs(package_id: str, timestamp: str = None):
    safe_package = package_id.replace(".", "_")
    
    if timestamp:
        log_file = LOGS_WORKSHOP_DISCOVERY / f"{safe_package}_{timestamp}.log"
        if log_file.exists():
            return _parse_log_file(log_file), str(log_file)
    
    # Find the most recent log file for this package
    pattern = f"{safe_package}_*.log"
    log_files = sorted(LOGS_WORKSHOP_DISCOVERY.glob(pattern), reverse=True)
    
    if log_files:
        return _parse_log_file(log_files[0]), str(log_files[0])
    
    return [], None


def _parse_log_file(log_file: Path):
    logs = []
    try:
        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse: 2025-12-14 02:29:21 - INFO - Message
                parts = line.split(' - ', 2)
                if len(parts) >= 3:
                    logs.append({
                        "timestamp": parts[0],
                        "level": parts[1],
                        "message": parts[2]
                    })
                else:
                    logs.append({
                        "timestamp": "",
                        "level": "INFO",
                        "message": line
                    })
    except Exception as e:
        logs.append({
            "timestamp": "",
            "level": "ERROR",
            "message": f"Failed to read log file: {e}"
        })
    
    return logs


def list_discovery_logs(package_id: str = None):
    if package_id:
        safe_package = package_id.replace(".", "_")
        pattern = f"{safe_package}_*.log"
    else:
        pattern = "*.log"
    
    log_files = sorted(LOGS_WORKSHOP_DISCOVERY.glob(pattern), reverse=True)
    
    result = []
    for log_file in log_files[:50]:  # Limit to 50 most recent
        name = log_file.stem
        parts = name.rsplit('_', 2)
        if len(parts) >= 2:
            pkg = parts[0].replace('_', '.')
            ts = '_'.join(parts[1:])
        else:
            pkg = name
            ts = ""
        
        result.append({
            "file": str(log_file),
            "package_id": pkg,
            "timestamp": ts,
            "size": log_file.stat().st_size
        })
    
    return result

