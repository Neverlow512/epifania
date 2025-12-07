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

