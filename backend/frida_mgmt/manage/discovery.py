import time
from typing import List, Dict
from core.logger import get_logger

logger = get_logger(__name__, "backend")

try:
    from core.log_streamer import log_streamer
    LOG_STREAMER_AVAILABLE = True
except ImportError:
    LOG_STREAMER_AVAILABLE = False
    logger.warning("Log streamer not available")


class FridaDiscovery:
    def __init__(self, adb_manager=None):
        self.adb_manager = adb_manager
        logger.info("FridaDiscovery initialized")
    
    def discover_frida_servers(self, device_serial: str) -> List[Dict]:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return []
            
            logger.info(f"Discovering Frida servers on {device_serial}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", "Scanning device for Frida servers", "info")
            
            discovered_servers = []
            
            # Common locations to check (non-wildcard first)
            search_paths = [
                "/data/local/tmp/frida-server",
                "/system/bin/frida-server",
                "/system/xbin/frida-server",
                "/sbin/frida-server",
                "/data/local/frida-server"
            ]
            
            for path in search_paths:
                try:
                    # First check if file exists
                    check_result = self.adb_manager.execute_shell(device_serial, f"test -f {path} && echo 'exists' || echo 'not_found'")
                    
                    if not check_result or 'not_found' in check_result:
                        logger.debug(f"Path {path} does not exist")
                        continue
                    
                    logger.info(f"Found file at {path}, getting details")
                    
                    # Get file details using ls -l
                    ls_result = self.adb_manager.execute_shell(device_serial, f"ls -l {path}")
                    
                    if not ls_result or "No such file" in ls_result:
                        logger.warning(f"File exists but ls failed for {path}")
                        continue
                    
                    # Parse ls -l output
                    parts = ls_result.strip().split()
                    if len(parts) >= 5:
                        permissions = parts[0]
                        size = parts[4] if len(parts) > 4 else "unknown"
                        file_path = path
                    else:
                        logger.warning(f"Could not parse ls output for {path}: {ls_result}")
                        permissions = "unknown"
                        size = "unknown"
                        file_path = path
                    
                    # Check if it's executable by checking permissions string
                    is_executable = False
                    if permissions != "unknown" and len(permissions) >= 4:
                        is_executable = permissions[3] == 'x'
                    
                    # Try to get version
                    version = None
                    try:
                        version_result = self.adb_manager.execute_shell(device_serial, f"{file_path} --version 2>/dev/null")
                        if version_result and version_result.strip() and "not found" not in version_result.lower():
                            version = version_result.strip().split('\n')[0]
                            # Validate it looks like a version
                            if ':' in version and version.count('.') < 2:
                                version = None
                    except Exception as e:
                        logger.debug(f"Failed to get version for {file_path}: {str(e)}")
                    
                    server_info = {
                        "path": file_path,
                        "permissions": permissions,
                        "size": size,
                        "is_executable": is_executable,
                        "version": version
                    }
                    
                    discovered_servers.append(server_info)
                    logger.info(f"Added Frida server: {file_path}, executable={is_executable}, version={version}, permissions={permissions}")
                    
                except Exception as e:
                    logger.error(f"Error checking path {path}: {str(e)}")
                    continue
            
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(
                    device_serial, 
                    "frida_install", 
                    f"Found {len(discovered_servers)} Frida server(s)", 
                    "info"
                )
            
            logger.info(f"Discovered {len(discovered_servers)} Frida server(s) on {device_serial}")
            return discovered_servers
            
        except Exception as e:
            logger.error(f"Failed to discover Frida servers on {device_serial}: {str(e)}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Discovery failed: {str(e)}", "error")
            return []
    
    def remove_frida_servers(self, device_serial: str, paths: List[str], is_running_func=None, stop_server_func=None) -> Dict:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return {"success": False, "message": "ADB manager not initialized", "removed": []}
            
            logger.info(f"Removing Frida servers from {device_serial}: {paths}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Removing {len(paths)} Frida server(s)", "info")
            
            # First, stop any running Frida servers
            if is_running_func and stop_server_func:
                if is_running_func(device_serial):
                    logger.info("Stopping running Frida server before cleanup")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "frida_install", "Stopping running Frida server", "info")
                    stop_server_func(device_serial)
                    time.sleep(1)
            
            removed = []
            failed = []
            
            for path in paths:
                try:
                    # Try with root first
                    try:
                        result = self.adb_manager.execute_shell(device_serial, f"su -c 'rm -f {path}'")
                        if LOG_STREAMER_AVAILABLE:
                            log_streamer.add_log(device_serial, "adb_operations", f"shell: su -c 'rm -f {path}'", "info")
                    except:
                        result = self.adb_manager.execute_shell(device_serial, f"rm -f {path}")
                        if LOG_STREAMER_AVAILABLE:
                            log_streamer.add_log(device_serial, "adb_operations", f"shell: rm -f {path}", "info")
                    
                    # Verify removal
                    check = self.adb_manager.execute_shell(device_serial, f"ls {path} 2>/dev/null")
                    if not check or "No such file" in check:
                        removed.append(path)
                        logger.info(f"Successfully removed {path}")
                        if LOG_STREAMER_AVAILABLE:
                            log_streamer.add_log(device_serial, "frida_install", f"Removed: {path}", "info")
                    else:
                        failed.append(path)
                        logger.warning(f"Failed to verify removal of {path}")
                        
                except Exception as e:
                    failed.append(path)
                    logger.error(f"Failed to remove {path}: {str(e)}")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "frida_install", f"Failed to remove {path}: {str(e)}", "error")
            
            success = len(removed) > 0 and len(failed) == 0
            message = f"Successfully removed {len(removed)} server(s)"
            if failed:
                message += f", failed to remove {len(failed)} server(s)"
            
            return {
                "success": success,
                "message": message,
                "removed": removed,
                "failed": failed
            }
            
        except Exception as e:
            logger.error(f"Failed to remove Frida servers from {device_serial}: {str(e)}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Cleanup failed: {str(e)}", "error")
            return {"success": False, "message": str(e), "removed": []}

