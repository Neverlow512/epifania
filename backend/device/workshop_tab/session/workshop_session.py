# Workshop session management - exclusive browser tab lock per device
import time
import threading
from typing import Dict, Any, Optional, Tuple
from core.logger import get_logger

logger = get_logger(__name__, "device")


class WorkshopSession:
    def __init__(self, session_timeout: float = 30.0):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._session_timeout = session_timeout
    
    def acquire(self, device_id: str, client_id: str) -> Tuple[bool, str]:
        with self._lock:
            current_time = time.time()
            session = self._sessions.get(device_id)
            
            if session:
                elapsed = current_time - session["last_seen"]
                if elapsed > self._session_timeout:
                    logger.info(f"Workshop session expired for {device_id}, releasing lock")
                    del self._sessions[device_id]
                    session = None
                elif session["client_id"] != client_id:
                    remaining = int(self._session_timeout - elapsed)
                    return False, f"Workshop locked by another tab (expires in {remaining}s)"
            
            if session is None:
                self._sessions[device_id] = {
                    "client_id": client_id,
                    "last_seen": current_time,
                    "acquired_at": current_time
                }
                logger.info(f"Workshop session acquired for {device_id} by {client_id}")
                return True, "Session acquired"
            
            session["last_seen"] = current_time
            return True, "Session refreshed"
    
    def heartbeat(self, device_id: str, client_id: str) -> Tuple[bool, str]:
        with self._lock:
            session = self._sessions.get(device_id)
            
            if not session:
                return False, "No active session"
            
            if session["client_id"] != client_id:
                return False, "Session owned by another client"
            
            current_time = time.time()
            if (current_time - session["last_seen"]) > self._session_timeout:
                del self._sessions[device_id]
                return False, "Session expired"
            
            session["last_seen"] = current_time
            return True, "Heartbeat received"
    
    def release(self, device_id: str, client_id: str) -> Tuple[bool, str]:
        with self._lock:
            session = self._sessions.get(device_id)
            
            if not session:
                return True, "No session to release"
            
            if session["client_id"] != client_id:
                return False, "Cannot release session owned by another client"
            
            del self._sessions[device_id]
            logger.info(f"Workshop session released for {device_id} by {client_id}")
            return True, "Session released"
    
    def get_session_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            session = self._sessions.get(device_id)
            if not session:
                return None
            
            current_time = time.time()
            elapsed = current_time - session["last_seen"]
            
            if elapsed > self._session_timeout:
                del self._sessions[device_id]
                return None
            
            return {
                "client_id": session["client_id"],
                "acquired_at": session["acquired_at"],
                "last_seen": session["last_seen"],
                "expires_in": int(self._session_timeout - elapsed)
            }
    
    def is_locked(self, device_id: str) -> bool:
        return self.get_session_info(device_id) is not None
    
    def is_owner(self, device_id: str, client_id: str) -> bool:
        with self._lock:
            session = self._sessions.get(device_id)
            if not session:
                return False
            
            current_time = time.time()
            if (current_time - session["last_seen"]) > self._session_timeout:
                del self._sessions[device_id]
                return False
            
            return session["client_id"] == client_id
    
    def cleanup_expired(self):
        with self._lock:
            current_time = time.time()
            expired = [
                device_id
                for device_id, session in self._sessions.items()
                if (current_time - session["last_seen"]) > self._session_timeout
            ]
            for device_id in expired:
                logger.info(f"Cleaning up expired workshop session for {device_id}")
                del self._sessions[device_id]
            return len(expired)


workshop_session = WorkshopSession(session_timeout=30.0)

