# Session manager for workshop operations logging
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any
from core.log_paths import LOGS_WORKSHOP_OPERATIONS
from core.logger import get_logger

logger = get_logger(__name__, "device")


class WorkshopSession:
    def __init__(self, device_id: str, package_id: str, session_timestamp: str, session_folder: Path):
        self.device_id = device_id
        self.package_id = package_id
        self.session_timestamp = session_timestamp
        self.session_folder = session_folder
        self.operation_counts = {"scan_classloader": 0, "extract_methods": 0}
        self.session_logger: Optional[logging.Logger] = None
        self.total_classes_scanned = 0
        self.total_classes_extracted = 0
        self.total_scan_duration = 0.0
        self.total_extract_duration = 0.0
        self.total_scan_errors = 0
        self.total_extract_errors = 0
        self.operations_log = []
    
    def increment_operation(self, operation_type: str) -> int:
        self.operation_counts[operation_type] = self.operation_counts.get(operation_type, 0) + 1
        return self.operation_counts[operation_type]
    
    def record_operation(self, operation_type: str, metrics: Dict[str, Any]):
        self.operations_log.append({
            "type": operation_type,
            "timestamp": datetime.now().isoformat(),
            "classes": metrics["total"],
            "duration": metrics["duration"],
            "success": metrics["success_count"],
            "errors": metrics["error_count"],
            "throughput": metrics["throughput"],
            "cancelled": metrics["cancelled"]
        })
        
        if operation_type == "scan_classloader":
            self.total_classes_scanned += metrics["success_count"]
            self.total_scan_duration += metrics["duration"]
            self.total_scan_errors += metrics["error_count"]
        elif operation_type == "extract_methods":
            self.total_classes_extracted += metrics["success_count"]
            self.total_extract_duration += metrics["duration"]
            self.total_extract_errors += metrics["error_count"]


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, WorkshopSession] = {}
        self._lock = threading.Lock()
        self._backend_start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"SessionManager initialized with timestamp: {self._backend_start_time}")
    
    def _get_session_key(self, device_id: str, package_id: str) -> str:
        return f"{device_id}_{package_id}"
    
    def get_or_create_session(self, device_id: str, package_id: str) -> WorkshopSession:
        key = self._get_session_key(device_id, package_id)
        
        with self._lock:
            if key not in self._sessions:
                # Create new session
                safe_package = package_id.replace(".", "_")
                session_folder_name = f"{safe_package}_session_{self._backend_start_time}"
                session_folder = LOGS_WORKSHOP_OPERATIONS / session_folder_name
                session_folder.mkdir(parents=True, exist_ok=True)
                
                session = WorkshopSession(device_id, package_id, self._backend_start_time, session_folder)
                self._sessions[key] = session
                
                # Create session.log
                session_log_file = session_folder / "session.log"
                session_logger = self._create_session_logger(session_log_file)
                session.session_logger = session_logger
                
                session_logger.info(f"[SESSION START] Package: {package_id}")
                session_logger.info(f"  Device: {device_id}")
                session_logger.info(f"  Timestamp: {self._backend_start_time}")
                session_logger.info("=" * 60)
                
                logger.info(f"Created new session: {session_folder_name}")
            
            return self._sessions[key]
    
    def _create_session_logger(self, log_file: Path) -> logging.Logger:
        logger_name = f"workshop.session.{log_file.parent.name}"
        session_logger = logging.getLogger(logger_name)
        session_logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        session_logger.handlers = []
        
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        session_logger.addHandler(handler)
        
        return session_logger
    
    def get_session_folder(self, device_id: str, package_id: str) -> Path:
        session = self.get_or_create_session(device_id, package_id)
        return session.session_folder
    
    def log_to_session(self, device_id: str, package_id: str, message: str, level: str = "INFO"):
        session = self.get_or_create_session(device_id, package_id)
        if session.session_logger:
            if level == "ERROR":
                session.session_logger.error(message)
            elif level == "WARNING":
                session.session_logger.warning(message)
            elif level == "DEBUG":
                session.session_logger.debug(message)
            else:
                session.session_logger.info(message)
    
    def increment_operation_count(self, device_id: str, package_id: str, operation_type: str) -> int:
        session = self.get_or_create_session(device_id, package_id)
        return session.increment_operation(operation_type)
    
    def record_operation_metrics(self, device_id: str, package_id: str, operation_type: str, metrics: Dict[str, Any]):
        session = self.get_or_create_session(device_id, package_id)
        session.record_operation(operation_type, metrics)
    
    def generate_session_summary(self, device_id: str, package_id: str):
        key = self._get_session_key(device_id, package_id)
        
        with self._lock:
            if key not in self._sessions:
                return
            
            session = self._sessions[key]
            
            if not session.session_logger or len(session.operations_log) == 0:
                return
            
            session.session_logger.info("")
            session.session_logger.info("=" * 60)
            session.session_logger.info("SESSION SUMMARY")
            session.session_logger.info("=" * 60)
            session.session_logger.info(f"Package: {package_id}")
            session.session_logger.info(f"Device: {device_id}")
            session.session_logger.info(f"Session Duration: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            session.session_logger.info("")
            session.session_logger.info(f"Total Operations: {len(session.operations_log)}")
            session.session_logger.info(f"  - scan_classloader: {session.operation_counts.get('scan_classloader', 0)}")
            session.session_logger.info(f"  - extract_methods: {session.operation_counts.get('extract_methods', 0)}")
            session.session_logger.info("")
            
            if session.total_classes_scanned > 0:
                scan_throughput = session.total_classes_scanned / session.total_scan_duration if session.total_scan_duration > 0 else 0
                session.session_logger.info("Scan ClassLoader Performance:")
                session.session_logger.info(f"  Classes Scanned: {session.total_classes_scanned}")
                session.session_logger.info(f"  Total Duration: {session.total_scan_duration:.2f}s")
                session.session_logger.info(f"  Throughput: {scan_throughput:.2f} classes/sec")
                session.session_logger.info(f"  Errors: {session.total_scan_errors}")
                session.session_logger.info("")
            
            if session.total_classes_extracted > 0:
                extract_throughput = session.total_classes_extracted / session.total_extract_duration if session.total_extract_duration > 0 else 0
                session.session_logger.info("Extract Methods Performance:")
                session.session_logger.info(f"  Classes Extracted: {session.total_classes_extracted}")
                session.session_logger.info(f"  Total Duration: {session.total_extract_duration:.2f}s")
                session.session_logger.info(f"  Throughput: {extract_throughput:.2f} classes/sec")
                session.session_logger.info(f"  Errors: {session.total_extract_errors}")
                session.session_logger.info("")
            
            session.session_logger.info("=" * 60)
    
    def generate_all_summaries(self):
        with self._lock:
            for key, session in self._sessions.items():
                try:
                    self.generate_session_summary(session.device_id, session.package_id)
                except Exception as e:
                    logger.error(f"Failed to generate summary for {key}: {e}")


session_manager = SessionManager()
