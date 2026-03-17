import time
import subprocess
from typing import Optional
from core.logger import get_logger
from utils.frida_debug import FridaDebugLogger

logger = get_logger(__name__, "backend")

try:
    from core.log_streamer import log_streamer
    LOG_STREAMER_AVAILABLE = True
except ImportError:
    LOG_STREAMER_AVAILABLE = False
    logger.warning("Log streamer not available")


class FridaServerManager:
    def __init__(self, adb_manager=None):
        self.adb_manager = adb_manager
        self._version_cache = {}  # Cache version checks {device_serial: (timestamp, version)}
        self._version_cache_ttl = 30  # Cache TTL in seconds
        logger.info("FridaServerManager initialized")
    
    def check_frida_server_version(self, device_serial: str, force_refresh: bool = False) -> Optional[str]:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return None
            
            # Check cache first
            import time
            if not force_refresh and device_serial in self._version_cache:
                timestamp, cached_version = self._version_cache[device_serial]
                if time.time() - timestamp < self._version_cache_ttl:
                    logger.debug(f"Using cached Frida server version for {device_serial}: {cached_version}")
                    return cached_version
            
            # Use adb_manager's execute_shell instead of device.shell
            result = self.adb_manager.execute_shell(device_serial, "/data/local/tmp/frida-server --version")
            if result:
                version = result.strip()
                logger.info(f"Frida server version on {device_serial}: {version}")
                # Cache the result
                self._version_cache[device_serial] = (time.time(), version)
                return version
            
            logger.info(f"Frida server not found on {device_serial}")
            return None
        except Exception as e:
            logger.debug(f"Failed to check Frida server version on {device_serial}: {str(e)}")
            return None
    
    def is_frida_server_running(self, device_serial: str, use_cache: bool = False) -> bool:
        try:
            if not self.adb_manager:
                return False
            
            # Use pidof as the primary check (faster and more reliable)
            result = self.adb_manager.execute_shell(device_serial, "pidof frida-server")
            running = bool(result and result.strip())
            
            if running:
                logger.debug(f"Frida server is running on {device_serial}")
            else:
                logger.debug(f"Frida server is not running on {device_serial}")
            
            return running
        except Exception as e:
            logger.debug(f"Failed to check if Frida server is running: {str(e)}")
            return False
    
    def start_frida_server(self, device_serial: str, server_path: Optional[str] = None, 
                          check_permissions_func=None, set_permissions_func=None, 
                          discover_servers_func=None) -> bool:
        # Initialize debug logger
        device_info = None
        if self.adb_manager:
            device = self.adb_manager.get_device(device_serial)
            if device:
                try:
                    device_info = {
                        "serial": device_serial,
                        "model": self.adb_manager._get_property(device, "ro.product.model", "Unknown"),
                        "android_version": self.adb_manager._get_property(device, "ro.build.version.release", "Unknown"),
                        "architecture": self.adb_manager._get_property(device, "ro.product.cpu.abi", "Unknown"),
                        "has_root": self.adb_manager.check_root_access(device)
                    }
                except Exception:
                    pass
        
        debug_logger = FridaDebugLogger(device_serial, device_info)
        
        # Add device information to debug log
        if device_info:
            debug_logger.add_device_info("Serial", device_info.get("serial", "Unknown"))
            debug_logger.add_device_info("Model", device_info.get("model", "Unknown"))
            debug_logger.add_device_info("Android Version", device_info.get("android_version", "Unknown"))
            debug_logger.add_device_info("Architecture", device_info.get("architecture", "Unknown"))
            debug_logger.add_device_info("Root Access", "Yes" if device_info.get("has_root") else "No")
        
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "ADB manager not initialized", "error")
                debug_logger.add_startup_info("ERROR: ADB manager not initialized")
                debug_logger.set_result(False, "ADB manager not initialized")
                debug_logger.write()
                return False
            
            if self.is_frida_server_running(device_serial):
                logger.info(f"Frida server already running on {device_serial}")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "Frida server already running", "info")
                debug_logger.add_startup_info("Frida server already running")
                debug_logger.set_result(True, "Frida server was already running")
                debug_logger.write()
                return True
            
            # Device validation no longer needs device object
            # adb_manager will handle device validation internally
            
            # Discover server path if not provided
            if not server_path:
                logger.info(f"No server path provided, discovering Frida servers on {device_serial}")
                discovered = discover_servers_func(device_serial) if discover_servers_func else []
                debug_logger.add_discovered_servers(discovered)
                
                # Prefer standard location if it exists and is executable
                standard_path = "/data/local/tmp/frida-server"
                for server in discovered:
                    if server["path"] == standard_path and server["is_executable"]:
                        server_path = standard_path
                        break
                
                # Otherwise use first executable server found
                if not server_path:
                    for server in discovered:
                        if server["is_executable"]:
                            server_path = server["path"]
                            break
                
                # Default to standard location if nothing found
                if not server_path:
                    server_path = standard_path
                    logger.warning(f"No Frida server found, attempting to use default path: {server_path}")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "frida_server", f"Using default path: {server_path}", "warning")
                    debug_logger.add_startup_info(f"WARNING: No Frida server found, using default path: {server_path}")
                else:
                    logger.info(f"Using discovered Frida server at: {server_path}")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "frida_server", f"Using server at: {server_path}", "info")
                    debug_logger.add_startup_info(f"Using discovered Frida server at: {server_path}")
            
            debug_logger.add_frida_config("Server Path", server_path)
            
            # Check and fix permissions before starting
            if check_permissions_func and set_permissions_func:
                logger.info(f"Checking permissions for {server_path}")
                perm_check = check_permissions_func(device_serial, server_path)
                
                debug_logger.add_permission_info(f"Before Fix:")
                debug_logger.add_permission_info(f"  Exists: {perm_check.get('exists', False)}")
                debug_logger.add_permission_info(f"  Executable: {perm_check.get('is_executable', False)}")
                debug_logger.add_permission_info(f"  Permissions: {perm_check.get('permissions', 'unknown')}")
                if perm_check.get('owner_perms'):
                    debug_logger.add_permission_info(f"  Owner: {perm_check.get('owner_perms')}")
                    debug_logger.add_permission_info(f"  Group: {perm_check.get('group_perms')}")
                    debug_logger.add_permission_info(f"  Other: {perm_check.get('other_perms')}")
                if perm_check.get('selinux_context'):
                    debug_logger.add_permission_info(f"  SELinux: {perm_check.get('selinux_context')}")
                
                if perm_check.get("exists") and not perm_check.get("is_executable"):
                    logger.warning(f"Frida server at {server_path} is not executable, attempting to fix")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "frida_server", "Server not executable, fixing permissions", "warning")
                        log_streamer.add_log(device_serial, "frida_debug", f"Current permissions: {perm_check.get('permissions')}", "debug")
                    
                    debug_logger.add_permission_info("\nFix Attempted: Yes")
                    
                    fix_result = set_permissions_func(device_serial, server_path)
                    
                    if fix_result.get("success"):
                        logger.info(f"Successfully fixed permissions for {server_path}")
                        debug_logger.add_permission_info(f"Fix Result: Success (method: {fix_result.get('method_used')})")
                        debug_logger.add_permission_info(f"\nAfter Fix:")
                        debug_logger.add_permission_info(f"  Permissions: {fix_result.get('permissions_after')}")
                        if LOG_STREAMER_AVAILABLE:
                            log_streamer.add_log(device_serial, "frida_debug", f"Fixed permissions using {fix_result.get('method_used')}", "info")
                    else:
                        logger.error(f"Failed to fix permissions: {fix_result.get('message')}")
                        debug_logger.add_permission_info(f"Fix Result: Failed - {fix_result.get('message')}")
                        if LOG_STREAMER_AVAILABLE:
                            log_streamer.add_log(device_serial, "frida_debug", f"Failed to fix permissions: {fix_result.get('message')}", "error")
                elif not perm_check.get("exists"):
                    logger.error(f"Frida server does not exist at {server_path}")
                    debug_logger.add_permission_info("\nFix Attempted: No (file does not exist)")
                    debug_logger.add_startup_info(f"ERROR: Frida server does not exist at {server_path}")
                    debug_logger.set_result(False, "Frida server file does not exist")
                    debug_logger.write()
                    return False
                else:
                    logger.info(f"Frida server at {server_path} is already executable")
                    debug_logger.add_permission_info("\nFix Attempted: No (already executable)")
            
            logger.info(f"Starting Frida server on {device_serial} from {server_path}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_server", f"Starting Frida server from {server_path}", "info")
            
            # Check if device is an emulator
            is_emulator = False
            try:
                device_type = self.adb_manager.execute_shell(device_serial, "getprop ro.build.characteristics")
                kernel_qemu = self.adb_manager.execute_shell(device_serial, "getprop ro.kernel.qemu")
                if device_type and ("emulator" in device_type.lower() or (kernel_qemu and kernel_qemu.strip() == "1")):
                    is_emulator = True
                    logger.info(f"Device {device_serial} detected as emulator")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "frida_server", "Device detected as emulator", "info")
                    debug_logger.add_startup_info("Device Type: Emulator")
            except:
                pass
            
            if not is_emulator:
                debug_logger.add_startup_info("Device Type: Physical")
            
            # Select root strategy based on actual access
            has_root = self.adb_manager.check_root_access(device_serial)
            debug_logger.add_startup_info(f"Root Access (runtime): {'Yes' if has_root else 'No'}")

            # Use subprocess to start frida-server instead of ppadb's shell()
            # ppadb's device.shell() has issues with backgrounding processes
            start_command_root = f"su -c 'nohup {server_path} -v > /data/local/tmp/frida-server.log 2>&1 &'"
            start_command_nonroot = f"nohup {server_path} -v > /data/local/tmp/frida-server.log 2>&1 &"

            started_with_root = False

            if has_root:
                try:
                    # Use subprocess.Popen to properly background the process
                    cmd = ['adb', '-s', device_serial, 'shell', start_command_root]
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    started_with_root = True
                    logger.debug(f"Attempted to start Frida server with root via subprocess")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "frida_server", "Tried start with root privileges", "info")
                        log_streamer.add_log(device_serial, "adb_operations", f"shell: {start_command_root}", "info")
                    debug_logger.add_adb_operation(start_command_root, "Started via subprocess")
                    debug_logger.add_startup_info("Startup Attempt: With root privileges (via subprocess)")
                except Exception as e:
                    logger.debug(f"Root start failed: {str(e)}, will try without root")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "frida_server", "Root start failed, trying without root", "warning")
                    debug_logger.add_startup_info(f"Root start failed: {str(e)}")

            # Give the root attempt a moment to spawn the process
            time.sleep(2)

            # Check once if server started with root
            root_success = False
            if started_with_root:
                pidof_check = self.adb_manager.execute_shell(device_serial, "pidof frida-server")
                root_success = bool(pidof_check and pidof_check.strip())
                if root_success:
                    logger.info("Frida server started with root privileges")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "frida_server", "Server started with root", "info")
                    debug_logger.add_startup_info("Root start: Successful")

            # If root either was not used or did not result in a running server, try non-root as fallback
            if not has_root or not root_success:
                try:
                    # Use subprocess.Popen for non-root as well
                    cmd = ['adb', '-s', device_serial, 'shell', start_command_nonroot]
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    logger.debug(f"Attempted to start Frida server without root via subprocess")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "adb_operations", f"shell: {start_command_nonroot}", "info")
                    debug_logger.add_adb_operation(start_command_nonroot, "Started via subprocess")
                    debug_logger.add_startup_info("Startup Attempt: Without root privileges (via subprocess)")
                    time.sleep(2)
                except Exception as e2:
                    logger.error(f"Non-root start failed: {str(e2)}")
                    debug_logger.add_startup_info(f"Non-root start failed: {str(e2)}")
            
            # Check if process is running (single check with detailed logging)
            time.sleep(1)  # Give it a moment to start
            
            pidof_result = self.adb_manager.execute_shell(device_serial, "pidof frida-server")
            
            debug_logger.add_adb_operation("pidof frida-server", pidof_result if pidof_result else "No output")
            
            if pidof_result and pidof_result.strip():
                logger.info(f"Frida server started successfully on {device_serial} (PID: {pidof_result.strip()})")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", f"Frida server started successfully (PID: {pidof_result.strip()})", "info")
                debug_logger.add_startup_info(f"Process Check: Running (PID: {pidof_result.strip()})")
                debug_logger.set_result(True, "Frida server started successfully")
                debug_logger.write()
                return True
            else:
                logger.error(f"Frida server failed to start on {device_serial}")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "Frida server failed to start - check permissions and path", "error")
                debug_logger.add_startup_info("Process Check: Not running")
                
                # Additional diagnostics
                try:
                    test_exec = self.adb_manager.execute_shell(device_serial, f"test -x {server_path} && echo 'executable' || echo 'not executable'")
                    debug_logger.add_adb_operation(f"test -x {server_path}", test_exec)
                    
                    file_info = self.adb_manager.execute_shell(device_serial, f"file {server_path} 2>/dev/null")
                    if file_info:
                        debug_logger.add_adb_operation(f"file {server_path}", file_info)
                except Exception:
                    pass
                
                debug_logger.set_result(False, "Process not running after start attempt")
                debug_logger.write()
                return False
        except Exception as e:
            logger.error(f"Failed to start Frida server on {device_serial}: {str(e)}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_server", f"Failed to start: {str(e)}", "error")
            debug_logger.add_startup_info(f"Exception occurred: {str(e)}")
            debug_logger.set_result(False, f"Exception: {str(e)}")
            debug_logger.write()
            return False
    
    def stop_frida_server(self, device_serial: str) -> bool:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "ADB manager not initialized", "error")
                return False
            
            logger.info(f"Stopping Frida server on {device_serial}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_server", "Stopping Frida server...", "info")
            
            # Try with root first, then fallback
            try:
                # Prefer pidof when available
                pids = self.adb_manager.execute_shell(device_serial, "pidof frida-server")
                if pids and pids.strip():
                    self.adb_manager.execute_shell(device_serial, f"su -c 'kill -9 {pids.strip()}'")
                else:
                    self.adb_manager.execute_shell(device_serial, "su -c 'killall frida-server'")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "adb_operations", "shell: su -c 'kill -9 $(pidof frida-server)' or killall", "info")
            except:
                pids = self.adb_manager.execute_shell(device_serial, "pidof frida-server")
                if pids and pids.strip():
                    self.adb_manager.execute_shell(device_serial, f"kill -9 {pids.strip()}")
                else:
                    self.adb_manager.execute_shell(device_serial, "killall frida-server")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "adb_operations", "shell: kill -9 $(pidof frida-server) or killall", "info")
            
            time.sleep(1)
            
            if not self.is_frida_server_running(device_serial):
                logger.info(f"Frida server stopped successfully on {device_serial}")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "Frida server stopped successfully", "info")
                return True
            else:
                logger.warning(f"Frida server may still be running on {device_serial}")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "Frida server may still be running", "warning")
                return False
        except Exception as e:
            logger.error(f"Failed to stop Frida server on {device_serial}: {str(e)}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_server", f"Failed to stop: {str(e)}", "error")
            return False
    
    def restart_frida_server(self, device_serial: str, server_path: Optional[str] = None,
                            check_permissions_func=None, set_permissions_func=None,
                            discover_servers_func=None) -> bool:
        try:
            logger.info(f"Restarting Frida server on {device_serial}")
            self.stop_frida_server(device_serial)
            
            time.sleep(1)
            
            return self.start_frida_server(
                device_serial,
                server_path=server_path,
                check_permissions_func=check_permissions_func,
                set_permissions_func=set_permissions_func,
                discover_servers_func=discover_servers_func
            )
        except Exception as e:
            logger.error(f"Failed to restart Frida server on {device_serial}: {str(e)}")
            return False

