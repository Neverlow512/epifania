from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from core.logger import get_logger

logger = get_logger(__name__, "backend")


class FridaDebugLogger:
    def __init__(self, device_serial: str, device_info: Optional[Dict] = None):
        self.device_serial = device_serial
        self.device_info = device_info or {}
        self.timestamp = datetime.now()
        
        # Debug log directory
        self.debug_dir = Path(__file__).parent.parent.parent / "logs" / "errors" / "frida-server" / "activation"
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        
        # Debug file path
        timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
        self.debug_file = self.debug_dir / f"{device_serial}_{timestamp_str}.log"
        
        # Data collection
        self.sections = {
            "device_info": [],
            "frida_config": [],
            "permissions": [],
            "adb_operations": [],
            "startup_process": [],
            "log_excerpts": []
        }
        
        self.result = None
        self.result_message = ""
        
        logger.info(f"FridaDebugLogger initialized for device {device_serial}")
    
    def add_device_info(self, key: str, value: str):
        self.sections["device_info"].append(f"- {key}: {value}")
    
    def add_frida_config(self, key: str, value: str):
        self.sections["frida_config"].append(f"- {key}: {value}")
    
    def add_permission_info(self, info: str):
        self.sections["permissions"].append(info)
    
    def add_adb_operation(self, command: str, output: Optional[str] = None):
        if output:
            self.sections["adb_operations"].append(f"Command: {command}\nOutput: {output}\n")
        else:
            self.sections["adb_operations"].append(f"Command: {command}")
    
    def add_startup_info(self, info: str):
        self.sections["startup_process"].append(info)
    
    def add_log_excerpt(self, log_type: str, message: str):
        self.sections["log_excerpts"].append(f"[{log_type}] {message}")
    
    def set_result(self, success: bool, message: str):
        self.result = "SUCCESS" if success else "FAILURE"
        self.result_message = message
    
    def add_discovered_servers(self, servers: List[Dict]):
        if not servers:
            self.add_frida_config("Discovered Servers", "None found")
            return
        
        for idx, server in enumerate(servers, 1):
            path = server.get("path", "unknown")
            perms = server.get("permissions", "unknown")
            executable = "Yes" if server.get("is_executable", False) else "No"
            version = server.get("version", "unknown")
            
            self.add_frida_config(
                f"Server {idx}",
                f"{path} (perms: {perms}, executable: {executable}, version: {version})"
            )
    
    def write(self):
        try:
            with open(self.debug_file, 'w') as f:
                f.write("=" * 70 + "\n")
                f.write("FRIDA SERVER ACTIVATION DEBUG LOG\n")
                f.write("=" * 70 + "\n\n")
                
                f.write(f"Timestamp: {self.timestamp.isoformat()}\n")
                f.write(f"Device: {self.device_serial}\n")
                f.write(f"Result: {self.result or 'UNKNOWN'}\n")
                if self.result_message:
                    f.write(f"Message: {self.result_message}\n")
                f.write("\n")
                
                # Device Information
                f.write("-" * 70 + "\n")
                f.write("[Device Information]\n")
                f.write("-" * 70 + "\n")
                if self.sections["device_info"]:
                    for line in self.sections["device_info"]:
                        f.write(f"{line}\n")
                else:
                    f.write("No device information available\n")
                f.write("\n")
                
                # Frida Server Configuration
                f.write("-" * 70 + "\n")
                f.write("[Frida Server Configuration]\n")
                f.write("-" * 70 + "\n")
                if self.sections["frida_config"]:
                    for line in self.sections["frida_config"]:
                        f.write(f"{line}\n")
                else:
                    f.write("No configuration information available\n")
                f.write("\n")
                
                # Permission Status
                f.write("-" * 70 + "\n")
                f.write("[Permission Status]\n")
                f.write("-" * 70 + "\n")
                if self.sections["permissions"]:
                    for line in self.sections["permissions"]:
                        f.write(f"{line}\n")
                else:
                    f.write("No permission information available\n")
                f.write("\n")
                
                # ADB Operations
                f.write("-" * 70 + "\n")
                f.write("[ADB Operations]\n")
                f.write("-" * 70 + "\n")
                if self.sections["adb_operations"]:
                    for line in self.sections["adb_operations"]:
                        f.write(f"{line}\n")
                else:
                    f.write("No ADB operations logged\n")
                f.write("\n")
                
                # Startup Process
                f.write("-" * 70 + "\n")
                f.write("[Startup Process]\n")
                f.write("-" * 70 + "\n")
                if self.sections["startup_process"]:
                    for line in self.sections["startup_process"]:
                        f.write(f"{line}\n")
                else:
                    f.write("No startup process information available\n")
                f.write("\n")
                
                # Log Excerpts
                f.write("-" * 70 + "\n")
                f.write("[Log Excerpts]\n")
                f.write("-" * 70 + "\n")
                if self.sections["log_excerpts"]:
                    for line in self.sections["log_excerpts"]:
                        f.write(f"{line}\n")
                else:
                    f.write("No log excerpts available\n")
                f.write("\n")
                
                f.write("=" * 70 + "\n")
                f.write("END OF DEBUG LOG\n")
                f.write("=" * 70 + "\n")
            
            logger.info(f"Debug log written to: {self.debug_file}")
            return str(self.debug_file)
            
        except Exception as e:
            logger.error(f"Failed to write debug log: {str(e)}")
            return None

