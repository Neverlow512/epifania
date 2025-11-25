import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from core.log_paths import (
    ensure_log_directories,
    LOG_CENTRAL,
    LOG_BACKEND,
    LOG_DEVICES,
    LOG_ERRORS
)


class EpifaniaLogger:
    def __init__(self):
        ensure_log_directories()
        
        self.central_log = LOG_CENTRAL
        self.backend_log = LOG_BACKEND
        self.device_log = LOG_DEVICES
        self.error_log = LOG_ERRORS
        
        self._setup_loggers()
    
    def _create_handler(self, log_file: Path, level=logging.INFO):
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,
            backupCount=5
        )
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        return handler
    
    def _setup_loggers(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        central_handler = self._create_handler(self.central_log)
        error_handler = self._create_handler(self.error_log, logging.ERROR)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(central_handler)
        root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str, category: str = "backend"):
        logger = logging.getLogger(name)
        
        if category == "device":
            category_handler = self._create_handler(self.device_log)
        else:
            category_handler = self._create_handler(self.backend_log)
        
        logger.addHandler(category_handler)
        return logger


epifania_logger = EpifaniaLogger()


def get_logger(name: str, category: str = "backend"):
    return epifania_logger.get_logger(name, category)

