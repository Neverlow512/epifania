from typing import Dict, Optional
from core.adb_manager import ADBManager
from core.logger import get_logger

logger = get_logger(__name__, "device")


class InspectionContext:
    def __init__(self, adb_manager: ADBManager, device_serial: str, pid: int, has_root: bool = False):
        self.adb_manager = adb_manager
        self.device_serial = device_serial
        self.pid = pid
        self.has_root = has_root
        self._proc_files: Dict[str, Optional[str]] = {}
        self._system_files: Dict[str, Optional[str]] = {}
        self._commands: Dict[str, Optional[str]] = {}
    
    def read_proc_file(self, filename: str, use_root: bool = False) -> Optional[str]:
        cache_key = f"{filename}:root={use_root}"
        
        if cache_key not in self._proc_files:
            path = f"/proc/{self.pid}/{filename}"
            if use_root and self.has_root:
                cmd = f"su -c 'cat {path}' 2>/dev/null"
            else:
                cmd = f"cat {path} 2>/dev/null"
            
            logger.debug(f"[ADB CALL] Reading {path}")
            result = self.adb_manager.execute_shell(self.device_serial, cmd)
            self._proc_files[cache_key] = result if result else None
        else:
            logger.debug(f"[CACHE HIT] /proc/{self.pid}/{filename}")
        
        return self._proc_files[cache_key]
    
    def read_system_file(self, path: str) -> Optional[str]:
        if path not in self._system_files:
            logger.debug(f"[ADB CALL] Reading {path}")
            result = self.adb_manager.execute_shell(
                self.device_serial,
                f"cat {path} 2>/dev/null"
            )
            self._system_files[path] = result if result else None
        else:
            logger.debug(f"[CACHE HIT] {path}")
        
        return self._system_files[path]
    
    def execute_command(self, command: str, cache_key: Optional[str] = None) -> Optional[str]:
        if cache_key:
            if cache_key not in self._commands:
                logger.debug(f"[ADB CALL] {command}")
                result = self.adb_manager.execute_shell(self.device_serial, command)
                self._commands[cache_key] = result if result else None
            else:
                logger.debug(f"[CACHE HIT] {cache_key}")
            return self._commands[cache_key]
        else:
            logger.debug(f"[ADB CALL] {command}")
            return self.adb_manager.execute_shell(self.device_serial, command)
    
    def list_directory(self, path: str, use_root: bool = False) -> Optional[str]:
        cache_key = f"ls:{path}:root={use_root}"
        if use_root and self.has_root:
            cmd = f"su -c 'ls -la {path}' 2>/dev/null"
        else:
            cmd = f"ls -la {path} 2>/dev/null"
        return self.execute_command(cmd, cache_key)
    
    def get_clock_ticks(self) -> int:
        result = self.execute_command("getconf CLK_TCK 2>/dev/null", "clock_ticks")
        return int(result.strip()) if result else 100
    
    def get_uptime(self) -> Optional[float]:
        result = self.read_system_file("/proc/uptime")
        if result:
            parts = result.strip().split()
            return float(parts[0]) if parts else None
        return None

