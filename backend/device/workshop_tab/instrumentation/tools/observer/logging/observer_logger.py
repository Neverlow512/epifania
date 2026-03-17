import logging
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler
from core.logger import get_logger
from device.workshop_tab.instrumentation.tools.observer.logging.log_paths import (
    get_observer_session_path,
    generate_session_name,
    INSTRUMENTATION_LOGS_ROOT
)

logger = get_logger(__name__, "backend")


class ObserverLogger:
    def __init__(self):
        self._operations_loggers = {}
        self._aggregated_loggers = {}
        self._console_loggers = {}
        self._hook_loggers = {}
        self._handlers = {}
    
    def _create_handler(self, log_file: Path, level=logging.DEBUG):
        handler = RotatingFileHandler(
            log_file,
            maxBytes=50*1024*1024,
            backupCount=3
        )
        handler.setLevel(level)
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        return handler
    
    def create_observer_session(self, app_package: str, session_name: str) -> Path:
        session_path = get_observer_session_path(app_package, session_name)
        session_path.mkdir(parents=True, exist_ok=True)
        
        (session_path / "hooks").mkdir(exist_ok=True)
        
        (session_path / "frida_operations.log").touch()
        (session_path / "aggregated.log").touch()
        (session_path / "console_raw.log").touch()
        (session_path / "summary.log").touch()
        
        logger.info(f"Created observer session logs for {app_package} session {session_name}: {session_path}")
        
        return session_path
    
    def get_operations_logger(self, session_path: Path) -> logging.Logger:
        key = f"ops_{session_path}"
        if key not in self._operations_loggers:
            log_file = session_path / "frida_operations.log"
            logger_name = f"observer.{session_path.name}.operations"
            ops_logger = logging.getLogger(logger_name)
            ops_logger.setLevel(logging.DEBUG)
            ops_logger.handlers = []
            
            handler = self._create_handler(log_file)
            ops_logger.addHandler(handler)
            
            self._operations_loggers[key] = ops_logger
            self._handlers[key] = handler
        
        return self._operations_loggers[key]
    
    def get_aggregated_logger(self, session_path: Path) -> logging.Logger:
        key = f"agg_{session_path}"
        if key not in self._aggregated_loggers:
            log_file = session_path / "aggregated.log"
            logger_name = f"observer.{session_path.name}.aggregated"
            agg_logger = logging.getLogger(logger_name)
            agg_logger.setLevel(logging.INFO)
            agg_logger.handlers = []
            
            handler = self._create_handler(log_file, level=logging.INFO)
            agg_logger.addHandler(handler)
            
            self._aggregated_loggers[key] = agg_logger
            self._handlers[key] = handler
        
        return self._aggregated_loggers[key]
    
    def get_console_logger(self, session_path: Path) -> logging.Logger:
        key = f"console_{session_path}"
        if key not in self._console_loggers:
            log_file = session_path / "console_raw.log"
            logger_name = f"observer.{session_path.name}.console"
            console_logger = logging.getLogger(logger_name)
            console_logger.setLevel(logging.DEBUG)
            console_logger.handlers = []
            
            handler = self._create_handler(log_file)
            console_logger.addHandler(handler)
            
            self._console_loggers[key] = console_logger
            self._handlers[key] = handler
        
        return self._console_loggers[key]
    
    def get_hook_logger(self, session_path: Path, hook_id: str, class_name: str = "", method_name: str = "") -> logging.Logger:
        key = f"hook_{session_path}_{hook_id}"
        if key not in self._hook_loggers:
            if class_name and method_name:
                safe_class = class_name.replace(".", "_").replace("$", "_")
                class_dir = session_path / "hooks" / safe_class
                class_dir.mkdir(parents=True, exist_ok=True)
                log_file = class_dir / f"{method_name}_{hook_id}.log"
            else:
                log_file = session_path / "hooks" / f"{hook_id}.log"
                log_file.parent.mkdir(parents=True, exist_ok=True)
            
            logger_name = f"observer.{session_path.name}.hook.{hook_id}"
            hook_logger = logging.getLogger(logger_name)
            hook_logger.setLevel(logging.INFO)
            hook_logger.handlers = []
            
            handler = self._create_handler(log_file, level=logging.INFO)
            hook_logger.addHandler(handler)
            
            self._hook_loggers[key] = hook_logger
            self._handlers[key] = handler
        
        return self._hook_loggers[key]
    
    def update_summary(self, session_path: Path, stats_dict: Dict[str, Any]):
        summary_file = session_path / "summary.log"
        try:
            with open(summary_file, 'w') as f:
                json.dump(stats_dict, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to update summary log: {e}")
    
    def write_metadata(self, session_path: Path, metadata_dict: Dict[str, Any]):
        metadata_file = session_path / "metadata.json"
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata_dict, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write metadata: {e}")
    
    def cleanup_old_observer_sessions(self, app_package: str, keep_count: int = 10):
        safe_package = app_package.replace(".", "_")
        package_dir = INSTRUMENTATION_LOGS_ROOT / safe_package
        
        if not package_dir.exists():
            return
        
        session_folders = []
        for date_folder in package_dir.iterdir():
            if date_folder.is_dir():
                for session_folder in date_folder.iterdir():
                    if session_folder.is_dir():
                        try:
                            session_num = int(session_folder.name)
                            mtime = session_folder.stat().st_mtime
                            session_folders.append((mtime, session_num, session_folder))
                        except (ValueError, OSError):
                            continue
        
        if len(session_folders) <= keep_count:
            return
        
        session_folders.sort(key=lambda x: x[0], reverse=True)
        folders_to_delete = session_folders[keep_count:]
        
        for _, session_num, folder in folders_to_delete:
            try:
                shutil.rmtree(folder)
                logger.info(f"Cleaned up old observer session folder: {folder.name}")
            except Exception as e:
                logger.error(f"Failed to delete observer session folder {folder.name}: {e}")
    
    def close_session_loggers(self, session_path: Path):
        keys_to_remove = []
        for key in list(self._handlers.keys()):
            if str(session_path) in key:
                try:
                    self._handlers[key].close()
                except:
                    pass
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            self._handlers.pop(key, None)
            self._operations_loggers.pop(key, None)
            self._aggregated_loggers.pop(key, None)
            self._console_loggers.pop(key, None)
            self._hook_loggers.pop(key, None)


observer_logger = ObserverLogger()


def create_observer_session(app_package: str, session_name: str) -> Path:
    return observer_logger.create_observer_session(app_package, session_name)


def get_operations_logger(session_path: Path) -> logging.Logger:
    return observer_logger.get_operations_logger(session_path)


def get_aggregated_logger(session_path: Path) -> logging.Logger:
    return observer_logger.get_aggregated_logger(session_path)


def get_console_logger(session_path: Path) -> logging.Logger:
    return observer_logger.get_console_logger(session_path)


def get_hook_logger(session_path: Path, hook_id: str, class_name: str = "", method_name: str = "") -> logging.Logger:
    return observer_logger.get_hook_logger(session_path, hook_id, class_name, method_name)


def update_summary(session_path: Path, stats_dict: Dict[str, Any]):
    observer_logger.update_summary(session_path, stats_dict)


def write_metadata(session_path: Path, metadata_dict: Dict[str, Any]):
    observer_logger.write_metadata(session_path, metadata_dict)


def cleanup_old_observer_sessions(app_package: str, keep_count: int = 10):
    observer_logger.cleanup_old_observer_sessions(app_package, keep_count)


async def read_observer_logs(session_path: Path, log_file: str) -> Dict[str, Any]:
    if log_file == "summary":
        summary_file = session_path / "summary.log"
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                return json.load(f)
        return {}
    elif log_file == "metadata":
        metadata_file = session_path / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)
        return {}
    elif log_file.startswith("hook_"):
        hook_log = session_path / "hooks" / f"{log_file}.log"
        if hook_log.exists():
            with open(hook_log, 'r') as f:
                return {"lines": f.readlines()}
        return {"lines": []}
    else:
        log_map = {
            "operations": "frida_operations.log",
            "aggregated": "aggregated.log",
            "console": "console_raw.log"
        }
        log_filename = log_map.get(log_file, f"{log_file}.log")
        log_path = session_path / log_filename
        if log_path.exists():
            with open(log_path, 'r') as f:
                return {"lines": f.readlines()}
        return {"lines": []}
