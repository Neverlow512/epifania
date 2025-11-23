import time
from typing import Dict
from core.logger import get_logger

logger = get_logger(__name__, "backend")

try:
    from core.log_streamer import log_streamer
    LOG_STREAMER_AVAILABLE = True
except ImportError:
    LOG_STREAMER_AVAILABLE = False
    logger.warning("Log streamer not available")


class FridaPermissions:
    def __init__(self, adb_manager=None):
        self.adb_manager = adb_manager
        logger.info("FridaPermissions initialized")
    
    def check_permissions(self, device_serial: str, path: str = "/data/local/tmp/frida-server") -> Dict:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return {"exists": False, "is_executable": False, "permissions": None}
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                return {"exists": False, "is_executable": False, "permissions": None}
            
            result = device.shell(f"ls -la {path} 2>/dev/null")
            
            if not result or "No such file" in result:
                logger.info(f"File does not exist: {path}")
                return {"exists": False, "is_executable": False, "permissions": None, "path": path}
            
            # Parse permissions from ls -la output
            parts = result.strip().split()
            if len(parts) > 0:
                permissions = parts[0]
                is_executable = "x" in permissions
                
                # Parse detailed permissions
                owner_perms = permissions[1:4] if len(permissions) >= 4 else "---"
                group_perms = permissions[4:7] if len(permissions) >= 7 else "---"
                other_perms = permissions[7:10] if len(permissions) >= 10 else "---"
                
                # Try to get SELinux context
                selinux_context = None
                try:
                    selinux_result = device.shell(f"ls -Z {path} 2>/dev/null")
                    if selinux_result and "u:object_r:" in selinux_result:
                        selinux_parts = selinux_result.strip().split()
                        if len(selinux_parts) > 0:
                            selinux_context = selinux_parts[0]
                except Exception:
                    pass
                
                logger.info(f"Permissions for {path}: {permissions}, executable: {is_executable}")
                result_dict = {
                    "exists": True,
                    "is_executable": is_executable,
                    "permissions": permissions,
                    "owner_perms": owner_perms,
                    "group_perms": group_perms,
                    "other_perms": other_perms,
                    "path": path
                }
                
                if selinux_context:
                    result_dict["selinux_context"] = selinux_context
                
                return result_dict
            
            return {"exists": True, "is_executable": False, "permissions": "unknown", "path": path}
            
        except Exception as e:
            logger.error(f"Failed to check permissions for {path} on {device_serial}: {str(e)}")
            return {"exists": False, "is_executable": False, "permissions": None, "error": str(e)}
    
    def set_permissions(self, device_serial: str, path: str = "/data/local/tmp/frida-server") -> Dict:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", "ADB manager not initialized", "error")
                return {"success": False, "message": "ADB manager not initialized"}
            
            logger.info(f"Setting permissions for {path} on {device_serial}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Setting executable permissions for {path}", "info")
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                return {"success": False, "message": "Device not found"}
            
            # Check if file exists first
            check = device.shell(f"ls {path} 2>/dev/null")
            if not check or "No such file" in check:
                message = f"File does not exist: {path}"
                logger.warning(message)
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", message, "warning")
                return {"success": False, "message": message}
            
            # Get permissions before fixing
            perm_before = self.check_permissions(device_serial, path)
            
            # Try with root first, fallback to non-root
            chmod_success = False
            method_used = None
            
            try:
                device.shell(f"su -c 'chmod 755 {path}'")
                method_used = "root"
                chmod_success = True
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "adb_operations", f"shell: su -c 'chmod 755 {path}'", "info")
            except Exception as e:
                logger.debug(f"Root chmod failed: {str(e)}, trying without root")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_debug", f"Root chmod failed: {str(e)}", "debug")
                try:
                    device.shell(f"chmod 755 {path}")
                    method_used = "non-root"
                    chmod_success = True
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "adb_operations", f"shell: chmod 755 {path}", "info")
                except Exception as e2:
                    logger.error(f"Non-root chmod also failed: {str(e2)}")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "frida_debug", f"Non-root chmod failed: {str(e2)}", "error")
                    return {
                        "success": False,
                        "message": f"Failed to set permissions: {str(e2)}",
                        "permissions_before": perm_before.get("permissions"),
                        "method_attempted": "both (root and non-root)"
                    }
            
            # Verify permissions were set
            time.sleep(0.5)
            
            perm_check = self.check_permissions(device_serial, path)
            if perm_check.get("is_executable"):
                message = f"Successfully set executable permissions for {path} using {method_used}"
                logger.info(message)
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", message, "info")
                return {
                    "success": True,
                    "message": message,
                    "permissions_before": perm_before.get("permissions"),
                    "permissions_after": perm_check.get("permissions"),
                    "method_used": method_used
                }
            else:
                message = f"Permissions may not have been set correctly for {path}"
                logger.warning(message)
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", message, "warning")
                return {
                    "success": False,
                    "message": message,
                    "permissions_before": perm_before.get("permissions"),
                    "permissions_after": perm_check.get("permissions"),
                    "method_used": method_used
                }
            
        except Exception as e:
            logger.error(f"Failed to set permissions for {path} on {device_serial}: {str(e)}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Permission setting failed: {str(e)}", "error")
            return {"success": False, "message": str(e)}

