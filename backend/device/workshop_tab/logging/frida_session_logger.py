import logging
import shutil
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler
from core.log_paths import LOGS_WORKSHOP_FRIDA_SESSIONS
from core.logger import get_logger

logger = get_logger(__name__, "backend")


class FridaSessionLogger:
    def __init__(self):
        self._operations_loggers = {}
        self._aggregate_loggers = {}
        self._handlers = {}
    
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
    
    def create_session_logs(self, session_number: int) -> Path:
        session_folder = LOGS_WORKSHOP_FRIDA_SESSIONS / f"session_{session_number}"
        session_folder.mkdir(parents=True, exist_ok=True)
        
        ops_log_file = session_folder / "frida_operations.log"
        agg_log_file = session_folder / "session_aggregate.log"
        
        ops_log_file.touch(exist_ok=True)
        agg_log_file.touch(exist_ok=True)
        
        logger.info(f"Created session logs for session {session_number}: {session_folder}")
        
        return session_folder
    
    def get_operations_logger(self, session_number: int) -> logging.Logger:
        if session_number not in self._operations_loggers:
            session_folder = LOGS_WORKSHOP_FRIDA_SESSIONS / f"session_{session_number}"
            log_file = session_folder / "frida_operations.log"
            
            logger_name = f"frida.session.{session_number}.operations"
            ops_logger = logging.getLogger(logger_name)
            ops_logger.setLevel(logging.DEBUG)
            ops_logger.handlers = []
            
            handler = self._create_handler(log_file)
            ops_logger.addHandler(handler)
            
            self._operations_loggers[session_number] = ops_logger
            self._handlers[f"ops_{session_number}"] = handler
        
        return self._operations_loggers[session_number]
    
    def get_aggregate_logger(self, session_number: int) -> logging.Logger:
        if session_number not in self._aggregate_loggers:
            session_folder = LOGS_WORKSHOP_FRIDA_SESSIONS / f"session_{session_number}"
            log_file = session_folder / "session_aggregate.log"
            
            logger_name = f"frida.session.{session_number}.aggregate"
            agg_logger = logging.getLogger(logger_name)
            agg_logger.setLevel(logging.INFO)
            agg_logger.handlers = []
            
            handler = self._create_handler(log_file, level=logging.INFO)
            agg_logger.addHandler(handler)
            
            self._aggregate_loggers[session_number] = agg_logger
            self._handlers[f"agg_{session_number}"] = handler
        
        return self._aggregate_loggers[session_number]
    
    def log_health_check(self, session_number: int, status: str, details: str):
        ops_logger = self.get_operations_logger(session_number)
        if status == "healthy":
            ops_logger.debug(f"[HEALTH_CHECK] {status}: {details}")
        else:
            ops_logger.warning(f"[HEALTH_CHECK] {status}: {details}")
    
    def log_aggregate_event(self, session_number: int, event_type: str, message: str):
        agg_logger = self.get_aggregate_logger(session_number)
        agg_logger.info(f"[{event_type}] {message}")
    
    def cleanup_old_session_folders(self, keep_count: int = 10):
        if not LOGS_WORKSHOP_FRIDA_SESSIONS.exists():
            return
        
        session_folders = []
        for folder in LOGS_WORKSHOP_FRIDA_SESSIONS.iterdir():
            if folder.is_dir() and folder.name.startswith("session_"):
                try:
                    session_num = int(folder.name.split("_")[1])
                    session_folders.append((session_num, folder))
                except (IndexError, ValueError):
                    continue
        
        if len(session_folders) <= keep_count:
            return
        
        session_folders.sort(key=lambda x: x[0], reverse=True)
        
        folders_to_delete = session_folders[keep_count:]
        
        for session_num, folder in folders_to_delete:
            try:
                if session_num in self._operations_loggers:
                    del self._operations_loggers[session_num]
                if session_num in self._aggregate_loggers:
                    del self._aggregate_loggers[session_num]
                
                for key in [f"ops_{session_num}", f"agg_{session_num}"]:
                    if key in self._handlers:
                        self._handlers[key].close()
                        del self._handlers[key]
                
                shutil.rmtree(folder)
                logger.info(f"Cleaned up old session folder: {folder.name}")
            except Exception as e:
                logger.error(f"Failed to delete session folder {folder.name}: {e}")
    
    def close_session_loggers(self, session_number: int):
        if session_number in self._operations_loggers:
            del self._operations_loggers[session_number]
        if session_number in self._aggregate_loggers:
            del self._aggregate_loggers[session_number]
        
        for key in [f"ops_{session_number}", f"agg_{session_number}"]:
            if key in self._handlers:
                self._handlers[key].close()
                del self._handlers[key]


frida_session_logger = FridaSessionLogger()


def create_session_logs(session_number: int) -> Path:
    return frida_session_logger.create_session_logs(session_number)


def get_operations_logger(session_number: int) -> logging.Logger:
    return frida_session_logger.get_operations_logger(session_number)


def get_aggregate_logger(session_number: int) -> logging.Logger:
    return frida_session_logger.get_aggregate_logger(session_number)


def log_health_check(session_number: int, status: str, details: str):
    frida_session_logger.log_health_check(session_number, status, details)


def log_aggregate_event(session_number: int, event_type: str, message: str):
    frida_session_logger.log_aggregate_event(session_number, event_type, message)


def cleanup_old_session_folders(keep_count: int = 10):
    frida_session_logger.cleanup_old_session_folders(keep_count)
