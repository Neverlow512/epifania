# Frida session manager - attach/detach to running processes
import threading
from typing import Dict, Any, Optional, Callable
from core.logger import get_logger
from device.workshop_tab.logging.workshop_logger import get_frida_logger

logger = get_logger(__name__, "backend")


class FridaSessionManager:
    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._frida = None
    
    def _get_frida(self):
        if self._frida is None:
            import frida
            self._frida = frida
        return self._frida
    
    def attach(
        self,
        device_id: str,
        pid: int,
        on_detached: Optional[Callable] = None
    ) -> Dict[str, Any]:
        frida_log = get_frida_logger(device_id)
        
        with self._lock:
            existing = self._sessions.get(device_id)
            if existing and existing.get("pid") == pid:
                frida_log.info(f"Reusing existing session for PID {pid}")
                return {
                    "success": True,
                    "message": "Already attached to this process",
                    "session_reused": True,
                    "pid": pid
                }
            
            if existing:
                frida_log.info(f"Detaching from previous PID {existing.get('pid')} before attaching to {pid}")
                self._detach_internal(device_id, frida_log)
        
        try:
            frida = self._get_frida()
            frida_log.info(f"Getting Frida device: {device_id}")
            
            device = frida.get_device(device_id, timeout=10)
            frida_log.info(f"Device found: {device.name} ({device.type})")
            
            frida_log.info(f"Attaching to PID {pid}")
            session = device.attach(pid)
            
            def detached_handler(reason, crash):
                frida_log.warning(f"Session detached: {reason}")
                with self._lock:
                    if device_id in self._sessions:
                        del self._sessions[device_id]
                if on_detached:
                    on_detached(device_id, pid, reason, crash)
            
            session.on('detached', detached_handler)
            
            with self._lock:
                self._sessions[device_id] = {
                    "device": device,
                    "session": session,
                    "pid": pid,
                    "device_name": device.name
                }
            
            frida_log.info(f"Successfully attached to PID {pid}")
            logger.info(f"Frida attached to PID {pid} on {device_id}")
            
            return {
                "success": True,
                "message": f"Attached to PID {pid}",
                "session_reused": False,
                "pid": pid,
                "device_name": device.name
            }
            
        except Exception as e:
            error_msg = str(e)
            frida_log.error(f"Failed to attach to PID {pid}: {error_msg}")
            logger.error(f"Frida attach failed for {device_id}: {error_msg}")
            
            return {
                "success": False,
                "message": f"Failed to attach: {error_msg}",
                "pid": pid
            }
    
    def detach(self, device_id: str) -> Dict[str, Any]:
        frida_log = get_frida_logger(device_id)
        
        with self._lock:
            session_info = self._sessions.get(device_id)
            if not session_info:
                return {
                    "success": True,
                    "message": "No active session to detach"
                }
            
            pid = session_info.get("pid")
            result = self._detach_internal(device_id, frida_log)
            
            if result:
                logger.info(f"Frida detached from PID {pid} on {device_id}")
                return {
                    "success": True,
                    "message": f"Detached from PID {pid}",
                    "pid": pid
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to detach cleanly",
                    "pid": pid
                }
    
    def _detach_internal(self, device_id: str, frida_log) -> bool:
        session_info = self._sessions.get(device_id)
        if not session_info:
            return True
        
        try:
            session = session_info.get("session")
            if session:
                frida_log.info(f"Detaching from PID {session_info.get('pid')}")
                session.detach()
            
            del self._sessions[device_id]
            return True
            
        except Exception as e:
            frida_log.error(f"Error during detach: {e}")
            if device_id in self._sessions:
                del self._sessions[device_id]
            return False
    
    def get_status(self, device_id: str) -> Dict[str, Any]:
        with self._lock:
            session_info = self._sessions.get(device_id)
            
            if not session_info:
                return {
                    "attached": False,
                    "pid": None,
                    "device_name": None
                }
            
            session = session_info.get("session")
            is_valid = False
            try:
                if session:
                    is_valid = session.is_detached == False
            except:
                pass
            
            if not is_valid:
                del self._sessions[device_id]
                return {
                    "attached": False,
                    "pid": None,
                    "device_name": None,
                    "note": "Session was invalidated"
                }
            
            return {
                "attached": True,
                "pid": session_info.get("pid"),
                "device_name": session_info.get("device_name")
            }
    
    def get_session(self, device_id: str):
        with self._lock:
            session_info = self._sessions.get(device_id)
            if session_info:
                return session_info.get("session")
            return None
    
    def get_device(self, device_id: str):
        with self._lock:
            session_info = self._sessions.get(device_id)
            if session_info:
                return session_info.get("device")
            return None
    
    def is_attached(self, device_id: str) -> bool:
        status = self.get_status(device_id)
        return status.get("attached", False)
    
    def cleanup_all(self):
        with self._lock:
            device_ids = list(self._sessions.keys())
        
        for device_id in device_ids:
            self.detach(device_id)
        
        logger.info("Cleaned up all Frida sessions")


frida_session_manager = FridaSessionManager()

