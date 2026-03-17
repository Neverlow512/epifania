import threading
import time
from typing import Dict, Any, Optional, Tuple
from core.logger import get_logger
from device.workshop_tab.logging.frida_session_logger import get_operations_logger
from device.workshop_tab.logging.aggregated_frida_logger import aggregated_frida_logger

logger = get_logger(__name__, "backend")


class SessionHealthMonitor:
    def __init__(self):
        self._monitor_threads: Dict[str, threading.Thread] = {}
        self._stop_events: Dict[str, threading.Event] = {}
        self._health_status: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._frida = None
    
    def _get_frida(self):
        if self._frida is None:
            import frida
            self._frida = frida
        return self._frida
    
    def _classify_polling_error(self, exception: Exception) -> Tuple[str, str]:
        frida = self._get_frida()
        error_str = str(exception)
        
        if isinstance(exception, frida.InvalidOperationError):
            if "destroyed" in error_str or "script has been destroyed" in error_str:
                return ("agent_crashed", error_str)
            elif "detached" in error_str:
                return ("session_detached", error_str)
        elif isinstance(exception, frida.TransportError):
            return ("transport_error", error_str)
        
        return ("unknown_error", error_str)
    
    def _monitor_loop(self, device_id: str, session, session_number: int, interval: float):
        ops_logger = get_operations_logger(session_number)
        
        ops_logger.info(f"[HEALTH_MONITOR] Started polling (interval: {interval}s)")
        
        while not self._stop_events[device_id].is_set():
            try:
                script = session.create_script("rpc.exports = { ping: () => Process.id };")
                script.load()
                result = script.exports_sync.ping()
                script.unload()
                
                ops_logger.debug(f"[HEALTH_POLL] Session healthy (PID: {result})")
                
                with self._lock:
                    self._health_status[device_id] = {"healthy": True, "reason": None}
                
            except Exception as e:
                error_type, reason = self._classify_polling_error(e)
                ops_logger.error(f"[HEALTH_POLL] Session unhealthy: {error_type} - {reason}")
                
                # Log health degradation to aggregated logger
                aggregated_frida_logger.log_health_degradation(session_number, f"{error_type}: {reason}", "ERROR")
                
                with self._lock:
                    self._health_status[device_id] = {"healthy": False, "reason": error_type}
                
                break
            
            self._stop_events[device_id].wait(interval)
        
        ops_logger.info("[HEALTH_MONITOR] Polling stopped")
    
    def start_monitoring(self, device_id: str, session, session_number: int, item_count: int):
        with self._lock:
            if device_id in self._monitor_threads:
                logger.debug(f"Health monitor already running for {device_id}")
                return
            
            interval = 2.0 if item_count < 100 else 5.0
            
            self._stop_events[device_id] = threading.Event()
            self._health_status[device_id] = {"healthy": True, "reason": None}
            
            thread = threading.Thread(
                target=self._monitor_loop,
                args=(device_id, session, session_number, interval),
                daemon=True
            )
            thread.start()
            
            self._monitor_threads[device_id] = thread
            
            logger.info(f"Started health monitoring for {device_id} (interval: {interval}s, items: {item_count})")
    
    def stop_monitoring(self, device_id: str):
        with self._lock:
            if device_id not in self._stop_events:
                return
            
            self._stop_events[device_id].set()
            
            if device_id in self._monitor_threads:
                thread = self._monitor_threads[device_id]
                del self._monitor_threads[device_id]
            
            del self._stop_events[device_id]
            
            if device_id in self._health_status:
                del self._health_status[device_id]
            
            logger.info(f"Stopped health monitoring for {device_id}")
    
    def is_session_healthy(self, device_id: str) -> bool:
        with self._lock:
            if device_id not in self._health_status:
                return True
            
            return self._health_status[device_id].get("healthy", True)
    
    def get_failure_reason(self, device_id: str) -> Optional[str]:
        with self._lock:
            if device_id not in self._health_status:
                return None
            
            return self._health_status[device_id].get("reason")


session_health_monitor = SessionHealthMonitor()
