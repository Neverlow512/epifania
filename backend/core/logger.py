import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


class EpifaniaLogger:
    def __init__(self, log_dir: str = "logs"):
        project_root = Path(__file__).parent.parent.parent
        self.log_dir = project_root / log_dir
        self.log_dir.mkdir(exist_ok=True)
        
        self.backend_dir = self.log_dir / "backend"
        self.backend_dir.mkdir(exist_ok=True)
        
        self.device_dir = self.log_dir / "device"
        self.device_dir.mkdir(exist_ok=True)
        
        self.server_dir = self.log_dir / "server"
        self.server_dir.mkdir(exist_ok=True)
        
        self.central_log = self.log_dir / "central.log"
        self.backend_log = self.backend_dir / "backend.log"
        self.device_log = self.device_dir / "device.log"
        self.error_log = self.backend_dir / "error.log"
        
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

