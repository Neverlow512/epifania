import os
import requests
import gzip
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from core.logger import get_logger

logger = get_logger(__name__, "backend")

# Import log_streamer for operation logging
try:
    from core.log_streamer import log_streamer
    LOG_STREAMER_AVAILABLE = True
except ImportError:
    LOG_STREAMER_AVAILABLE = False
    logger.warning("Log streamer not available")


class Installer:
    def __init__(self, adb_manager=None):
        self.frida_release_url = "https://api.github.com/repos/frida/frida/releases"
        self.cache_dir = Path(__file__).parent.parent / "frida_servers"
        self.cache_dir.mkdir(exist_ok=True)
        self.adb_manager = adb_manager
        logger.info(f"Installer initialized with cache directory: {self.cache_dir}")
    
    def get_architecture_mapping(self, android_abi: str) -> str:
        mapping = {
            "armeabi-v7a": "arm",
            "armeabi": "arm",
            "arm64-v8a": "arm64",
            "x86": "x86",
            "x86_64": "x86_64"
        }
        arch = mapping.get(android_abi, android_abi)
        logger.debug(f"Mapped Android ABI {android_abi} to Frida architecture {arch}")
        return arch
    
    def fetch_available_versions(self, limit: int = 10) -> List[Dict[str, str]]:
        try:
            logger.info("Fetching available Frida versions from GitHub")
            response = requests.get(self.frida_release_url, timeout=10)
            response.raise_for_status()
            
            releases = response.json()
            versions = []
            
            for release in releases[:limit]:
                version = release.get("tag_name", "").replace("v", "")
                if version:
                    versions.append({
                        "version": version,
                        "name": release.get("name", version),
                        "published_at": release.get("published_at", ""),
                        "prerelease": release.get("prerelease", False)
                    })
            
            logger.info(f"Found {len(versions)} Frida versions")
            return versions
        except Exception as e:
            logger.error(f"Failed to fetch Frida versions: {str(e)}")
            return []
    
    def get_cached_versions(self) -> Dict[str, List[str]]:
        try:
            cached = {}
            
            if not self.cache_dir.exists():
                return cached
            
            for version_dir in self.cache_dir.iterdir():
                if version_dir.is_dir():
                    version = version_dir.name
                    architectures = []
                    
                    for arch_dir in version_dir.iterdir():
                        if arch_dir.is_dir() and (arch_dir / "frida-server").exists():
                            architectures.append(arch_dir.name)
                    
                    if architectures:
                        cached[version] = architectures
            
            logger.info(f"Found {len(cached)} cached Frida versions")
            return cached
        except Exception as e:
            logger.error(f"Failed to list cached versions: {str(e)}")
            return {}
    
    def check_frida_server_version(self, device_serial: str) -> Optional[str]:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return None
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                return None
            
            result = device.shell("/data/local/tmp/frida-server --version")
            if result:
                version = result.strip()
                logger.info(f"Frida server version on {device_serial}: {version}")
                return version
            
            logger.info(f"Frida server not found on {device_serial}")
            return None
        except Exception as e:
            logger.debug(f"Failed to check Frida server version on {device_serial}: {str(e)}")
            return None
    
    def is_frida_server_running(self, device_serial: str) -> bool:
        try:
            if not self.adb_manager:
                return False
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                return False
            
            # Prefer pidof when available
            result = device.shell("pidof frida-server")
            running = bool(result and result.strip())
            if not running:
                # Fallback to ps variants
                result = device.shell("ps -A | grep frida-server | grep -v grep")
                if not result:
                    result = device.shell("ps | grep frida-server | grep -v grep")
                running = bool(result and "frida-server" in result)
            
            if running:
                logger.info(f"Frida server is running on {device_serial}")
            else:
                logger.info(f"Frida server is not running on {device_serial}")
            
            return running
        except Exception as e:
            logger.debug(f"Failed to check if Frida server is running: {str(e)}")
            return False
    
    def download_frida_server(self, version: str, architecture: str) -> Optional[Path]:
        try:
            cache_path = self.cache_dir / version / architecture
            cache_path.mkdir(parents=True, exist_ok=True)
            
            frida_binary = cache_path / "frida-server"
            
            if frida_binary.exists():
                logger.info(f"Frida server {version} for {architecture} already cached")
                return frida_binary
            
            download_url = f"https://github.com/frida/frida/releases/download/{version}/frida-server-{version}-android-{architecture}.xz"
            
            logger.info(f"Downloading Frida server from {download_url}")
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            compressed_file = cache_path / f"frida-server-{version}-android-{architecture}.xz"
            
            with open(compressed_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Decompressing Frida server")
            
            import lzma
            with lzma.open(compressed_file, 'rb') as f_in:
                with open(frida_binary, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            compressed_file.unlink()
            
            frida_binary.chmod(0o755)
            
            logger.info(f"Successfully downloaded and cached Frida server {version} for {architecture}")
            return frida_binary
        except Exception as e:
            logger.error(f"Failed to download Frida server {version} for {architecture}: {str(e)}")
            return None
    
    def install_frida_server(self, device_serial: str, version: str, architecture: str) -> bool:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", "ADB manager not initialized", "error")
                return False
            
            logger.info(f"Installing Frida server {version} on {device_serial}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Starting installation of Frida {version} for {architecture}", "info")
            
            frida_binary = self.download_frida_server(version, architecture)
            if not frida_binary:
                logger.error("Failed to download Frida server")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", "Failed to download Frida server", "error")
                return False
            
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Downloaded Frida server to {frida_binary}", "info")
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", f"Device {device_serial} not found", "error")
                return False
            
            logger.info(f"Pushing Frida server to device")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", "Pushing Frida server to /data/local/tmp/frida-server", "info")
                log_streamer.add_log(device_serial, "adb_operations", f"push {frida_binary} /data/local/tmp/frida-server", "info")
            
            device.push(str(frida_binary), "/data/local/tmp/frida-server")
            
            logger.info(f"Setting executable permissions")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", "Setting executable permissions", "info")
                log_streamer.add_log(device_serial, "adb_operations", "shell: chmod 755 /data/local/tmp/frida-server", "info")
            
            device.shell("chmod 755 /data/local/tmp/frida-server")
            
            logger.info(f"Successfully installed Frida server {version} on {device_serial}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Successfully installed Frida server {version}", "info")
            return True
        except Exception as e:
            logger.error(f"Failed to install Frida server on {device_serial}: {str(e)}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Installation failed: {str(e)}", "error")
            return False
    
    def push_cached_server(self, device_serial: str, version: str, architecture: str) -> bool:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return False
            
            cache_path = self.cache_dir / version / architecture / "frida-server"
            
            if not cache_path.exists():
                logger.error(f"Cached Frida server not found: {cache_path}")
                return False
            
            logger.info(f"Pushing cached Frida server {version} to {device_serial}")
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                return False
            
            device.push(str(cache_path), "/data/local/tmp/frida-server")
            device.shell("chmod 755 /data/local/tmp/frida-server")
            
            logger.info(f"Successfully pushed cached Frida server to {device_serial}")
            return True
        except Exception as e:
            logger.error(f"Failed to push cached Frida server: {str(e)}")
            return False
    
    def start_frida_server(self, device_serial: str, server_path: Optional[str] = None) -> bool:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "ADB manager not initialized", "error")
                return False
            
            if self.is_frida_server_running(device_serial):
                logger.info(f"Frida server already running on {device_serial}")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "Frida server already running", "info")
                return True
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", f"Device {device_serial} not found", "error")
                return False
            
            # Discover server path if not provided
            if not server_path:
                logger.info(f"No server path provided, discovering Frida servers on {device_serial}")
                discovered = self.discover_frida_servers(device_serial)
                
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
                else:
                    logger.info(f"Using discovered Frida server at: {server_path}")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "frida_server", f"Using server at: {server_path}", "info")
            
            logger.info(f"Starting Frida server on {device_serial} from {server_path}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_server", f"Starting Frida server from {server_path}", "info")
            
            # Check if device is an emulator
            is_emulator = False
            try:
                device_type = device.shell("getprop ro.build.characteristics")
                kernel_qemu = device.shell("getprop ro.kernel.qemu")
                if "emulator" in device_type.lower() or kernel_qemu.strip() == "1":
                    is_emulator = True
                    logger.info(f"Device {device_serial} detected as emulator")
                    if LOG_STREAMER_AVAILABLE:
                        log_streamer.add_log(device_serial, "frida_server", "Device detected as emulator", "info")
            except:
                pass
            
            # Try to start with root privileges first, fallback to non-root
            try:
                result = device.shell(f"su -c 'sh -c \"{server_path} >/dev/null 2>&1 &\"'")
                logger.debug(f"Attempted to start Frida server with root: {result}")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "Tried start with root privileges", "info")
                    log_streamer.add_log(device_serial, "adb_operations", f"shell: su -c '{server_path} >/dev/null 2>&1 &'", "info")
            except:
                logger.debug("Root start failed, trying without root")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "Root start failed, trying without root", "warning")
                result = device.shell(f"sh -c \"{server_path} >/dev/null 2>&1 &\"")
                logger.debug(f"Attempted to start Frida server without root: {result}")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "adb_operations", f"shell: {server_path} >/dev/null 2>&1 &", "info")
            
            import time
            time.sleep(2)
            
            if self.is_frida_server_running(device_serial):
                logger.info(f"Frida server started successfully on {device_serial}")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "Frida server started successfully", "info")
                return True
            else:
                logger.error(f"Frida server failed to start on {device_serial}")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "Frida server failed to start - check permissions and path", "error")
                return False
        except Exception as e:
            logger.error(f"Failed to start Frida server on {device_serial}: {str(e)}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_server", f"Failed to start: {str(e)}", "error")
            return False
    
    def stop_frida_server(self, device_serial: str) -> bool:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", "ADB manager not initialized", "error")
                return False
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_server", f"Device {device_serial} not found", "error")
                return False
            
            logger.info(f"Stopping Frida server on {device_serial}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_server", "Stopping Frida server...", "info")
            
            # Try with root first, then fallback
            try:
                # Prefer pidof when available
                pids = device.shell("pidof frida-server")
                if pids and pids.strip():
                    device.shell(f"su -c 'kill -9 {pids.strip()}'")
                else:
                    device.shell("su -c 'killall frida-server'")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "adb_operations", "shell: su -c 'kill -9 $(pidof frida-server)' or killall", "info")
            except:
                pids = device.shell("pidof frida-server")
                if pids and pids.strip():
                    device.shell(f"kill -9 {pids.strip()}")
                else:
                    device.shell("killall frida-server")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "adb_operations", "shell: kill -9 $(pidof frida-server) or killall", "info")
            
            import time
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
    
    def restart_frida_server(self, device_serial: str) -> bool:
        try:
            logger.info(f"Restarting Frida server on {device_serial}")
            self.stop_frida_server(device_serial)
            
            import time
            time.sleep(1)
            
            return self.start_frida_server(device_serial)
        except Exception as e:
            logger.error(f"Failed to restart Frida server on {device_serial}: {str(e)}")
            return False
    
    def discover_frida_servers(self, device_serial: str) -> List[Dict]:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return []
            
            logger.info(f"Discovering Frida servers on {device_serial}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", "Scanning device for Frida servers", "info")
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                return []
            
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
                    check_result = device.shell(f"test -f {path} && echo 'exists' || echo 'not_found'")
                    
                    if not check_result or 'not_found' in check_result:
                        logger.debug(f"Path {path} does not exist")
                        continue
                    
                    logger.info(f"Found file at {path}, getting details")
                    
                    # Get file details using ls -l
                    ls_result = device.shell(f"ls -l {path}")
                    
                    if not ls_result or "No such file" in ls_result:
                        logger.warning(f"File exists but ls failed for {path}")
                        continue
                    
                    # Parse ls -l output
                    parts = ls_result.strip().split()
                    if len(parts) >= 5:
                        permissions = parts[0]
                        size = parts[4] if len(parts) > 4 else "unknown"
                        file_path = path  # Use the original path we checked
                    else:
                        logger.warning(f"Could not parse ls output for {path}: {ls_result}")
                        # Still add it with unknown details
                        permissions = "unknown"
                        size = "unknown"
                        file_path = path
                    
                    # Check if it's executable by checking permissions string
                    # Format: -rwxr-xr-x means owner has execute permission at position 3
                    is_executable = False
                    if permissions != "unknown" and len(permissions) >= 4:
                        is_executable = permissions[3] == 'x'
                    
                    # Try to get version
                    version = None
                    try:
                        version_result = device.shell(f"{file_path} --version 2>/dev/null")
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
    
    def remove_frida_servers(self, device_serial: str, paths: List[str]) -> Dict:
        try:
            if not self.adb_manager:
                logger.error("ADB manager not initialized")
                return {"success": False, "message": "ADB manager not initialized", "removed": []}
            
            logger.info(f"Removing Frida servers from {device_serial}: {paths}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Removing {len(paths)} Frida server(s)", "info")
            
            device = self.adb_manager.get_device(device_serial)
            if not device:
                logger.error(f"Device {device_serial} not found")
                return {"success": False, "message": "Device not found", "removed": []}
            
            # First, stop any running Frida servers
            if self.is_frida_server_running(device_serial):
                logger.info("Stopping running Frida server before cleanup")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", "Stopping running Frida server", "info")
                self.stop_frida_server(device_serial)
                
                import time
                time.sleep(1)
            
            removed = []
            failed = []
            
            for path in paths:
                try:
                    # Try with root first
                    try:
                        result = device.shell(f"su -c 'rm -f {path}'")
                        if LOG_STREAMER_AVAILABLE:
                            log_streamer.add_log(device_serial, "adb_operations", f"shell: su -c 'rm -f {path}'", "info")
                    except:
                        result = device.shell(f"rm -f {path}")
                        if LOG_STREAMER_AVAILABLE:
                            log_streamer.add_log(device_serial, "adb_operations", f"shell: rm -f {path}", "info")
                    
                    # Verify removal
                    check = device.shell(f"ls {path} 2>/dev/null")
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
                
                logger.info(f"Permissions for {path}: {permissions}, executable: {is_executable}")
                return {
                    "exists": True,
                    "is_executable": is_executable,
                    "permissions": permissions,
                    "path": path
                }
            
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
            
            # Try with root first, fallback to non-root
            try:
                device.shell(f"su -c 'chmod 755 {path}'")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "adb_operations", f"shell: su -c 'chmod 755 {path}'", "info")
            except:
                device.shell(f"chmod 755 {path}")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "adb_operations", f"shell: chmod 755 {path}", "info")
            
            # Verify permissions were set
            import time
            time.sleep(0.5)
            
            perm_check = self.check_permissions(device_serial, path)
            if perm_check.get("is_executable"):
                message = f"Successfully set executable permissions for {path}"
                logger.info(message)
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", message, "info")
                return {"success": True, "message": message, "permissions": perm_check.get("permissions")}
            else:
                message = f"Permissions may not have been set correctly for {path}"
                logger.warning(message)
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(device_serial, "frida_install", message, "warning")
                return {"success": False, "message": message}
            
        except Exception as e:
            logger.error(f"Failed to set permissions for {path} on {device_serial}: {str(e)}")
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(device_serial, "frida_install", f"Permission setting failed: {str(e)}", "error")
            return {"success": False, "message": str(e)}