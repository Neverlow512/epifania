import time
import threading
from typing import Dict, Any, Optional, Tuple
from core.logger import get_logger

logger = get_logger(__name__, "device")


class PollingSession:
    def __init__(self, session_timeout: float = 10.0):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._session_timeout = session_timeout
    
    def register(self, device_id: str, client_id: str, interval_ms: int) -> Tuple[bool, str, int]:
        with self._lock:
            current_time = time.time()
            session = self._sessions.get(device_id)
            
            if session and (current_time - session["last_seen"]) > self._session_timeout:
                logger.info(f"Packages session expired for device {device_id}, clearing")
                del self._sessions[device_id]
                session = None
            
            if session is None:
                self._sessions[device_id] = {
                    "primary_client": client_id,
                    "interval_ms": interval_ms,
                    "last_seen": current_time,
                    "clients": {client_id: current_time}
                }
                logger.info(f"New packages primary session for {device_id}: client={client_id}, interval={interval_ms}ms")
                return True, "Primary session established", interval_ms
            
            session["clients"][client_id] = current_time
            # TODO: Review - secondary clients updating last_seen may be unnecessary since
            # promotion logic uses clients[primary_client] timestamp, not last_seen.
            # last_seen is only used for clearing abandoned sessions. Consider restricting
            # this update to primary client only for clearer semantics.
            session["last_seen"] = current_time
            
            primary_client = session["primary_client"]
            primary_last_seen = session["clients"].get(primary_client)
            if primary_last_seen is None or (current_time - primary_last_seen) > self._session_timeout:
                old_primary = primary_client
                session["primary_client"] = client_id
                session["interval_ms"] = interval_ms
                if old_primary in session["clients"]:
                    del session["clients"][old_primary]
                logger.info(f"Packages: {old_primary} expired, promoted {client_id} to primary for {device_id}")
                return True, "Primary session established", interval_ms
            
            if session["primary_client"] == client_id:
                session["interval_ms"] = interval_ms
                return True, "Interval updated", interval_ms
            
            active_interval = session["interval_ms"]
            if interval_ms != active_interval:
                return False, f"Another tab is controlling the polling interval ({active_interval}ms). Close other tabs to change the interval.", active_interval
            
            return False, "Secondary session (read-only)", active_interval
    
    def heartbeat(self, device_id: str, client_id: str) -> Optional[int]:
        with self._lock:
            session = self._sessions.get(device_id)
            if not session:
                return None
            
            current_time = time.time()
            session["clients"][client_id] = current_time
            
            if session["primary_client"] == client_id:
                session["last_seen"] = current_time
            else:
                primary_last_seen = session["clients"].get(session["primary_client"])
                if primary_last_seen and (current_time - primary_last_seen) > self._session_timeout:
                    old_primary = session["primary_client"]
                    session["primary_client"] = client_id
                    session["last_seen"] = current_time
                    logger.info(
                        f"[PACKAGES PRIMARY PROMOTED] Device {device_id}: "
                        f"{old_primary} (expired) -> {client_id} (now primary)"
                    )
            
            return session["interval_ms"]
    
    def unregister(self, device_id: str, client_id: str):
        with self._lock:
            session = self._sessions.get(device_id)
            if not session:
                return
            
            if client_id in session["clients"]:
                del session["clients"][client_id]
            
            if session["primary_client"] == client_id:
                if session["clients"]:
                    new_primary = next(iter(session["clients"]))
                    session["primary_client"] = new_primary
                    logger.info(f"Packages: Promoted {new_primary} to primary for {device_id}")
                else:
                    del self._sessions[device_id]
                    logger.info(f"Packages session cleared for {device_id}")
    
    def get_session_info(self, device_id: str) -> Optional[Dict]:
        with self._lock:
            session = self._sessions.get(device_id)
            if not session:
                return None
            return {
                "primary_client": session["primary_client"],
                "interval_ms": session["interval_ms"],
                "client_count": len(session["clients"])
            }


packages_polling_session = PollingSession(session_timeout=15.0)

