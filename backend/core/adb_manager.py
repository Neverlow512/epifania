import subprocess
import re
from typing import List, Dict, Optional
from core.logger import get_logger

try:
    from core.log_streamer import log_streamer
    LOG_STREAMER_AVAILABLE = True
except Exception:
    LOG_STREAMER_AVAILABLE = False

logger = get_logger(__name__, "device")


class ADBManager:
    def __init__(self, host: str = "127.0.0.1", port: int = 5037):
        self.host = host
        self.port = port
        logger.info(f"ADBManager initialized (using native adb, server at {self.host}:{self.port})")
        self._verify_adb_available()
    
    def _verify_adb_available(self):
        """Verify adb command is available in PATH"""
        try:
            result = subprocess.run(
                ['adb', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_info = result.stdout.strip().split('\n')[0]
                logger.info(f"ADB available: {version_info}")
            else:
                logger.error("ADB command not responding properly")
                raise RuntimeError("ADB command not responding properly")
        except FileNotFoundError:
            logger.error("ADB command not found in PATH")
            raise RuntimeError("ADB command not found - please install Android SDK Platform Tools")
        except subprocess.TimeoutExpired:
            logger.error("ADB command timed out")
            raise RuntimeError("ADB command timed out")
        except Exception as e:
            logger.error(f"Failed to verify ADB: {str(e)}")
            raise RuntimeError(f"ADB verification failed: {str(e)}")
    
    def _validate_serial(self, serial: str) -> bool:
        """Validate device serial format to prevent command injection"""
        if not serial:
            return False
        # Allow alphanumeric, dots, colons, dashes, underscores
        pattern = r'^[a-zA-Z0-9\.\:\-\_]+$'
        return bool(re.match(pattern, serial))
    
    def _run_adb_command(self, args: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """
        Run adb command with secure subprocess (no shell=True)
        
        Args:
            args: Command arguments as list (e.g., ['adb', 'devices'])
            timeout: Command timeout in seconds
            
        Returns:
            CompletedProcess object with stdout, stderr, returncode
        """
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired as e:
            logger.error(f"ADB command timed out: {' '.join(args)}")
            raise TimeoutError(f"Command timed out after {timeout}s")
        except Exception as e:
            logger.error(f"ADB command failed: {str(e)}")
            raise
    
    def _run_shell_command(self, serial: str, command: str, timeout: int = 30) -> Optional[str]:
        """
        Run shell command on device using adb shell
        
        Args:
            serial: Device serial number
            command: Shell command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Command output as string, or None on error
        """
        if not self._validate_serial(serial):
            logger.error(f"Invalid device serial format: {serial}")
            return None
        
        try:
            result = self._run_adb_command(
                ['adb', '-s', serial, 'shell', command],
                timeout=timeout
            )
            return result.stdout
        except Exception as e:
            logger.error(f"Shell command failed on {serial}: {str(e)}")
            return None
    
    def _parse_device_list(self, output: str) -> List[Dict[str, str]]:
        """Parse output from 'adb devices -l' command"""
        devices = []
        lines = output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('List of devices') or line.startswith('*'):
                continue
            
            parts = line.split()
            if len(parts) < 2:
                continue
            
            serial = parts[0]
            state = parts[1]
            
            # Parse additional info (product, model, device, transport_id)
            device_info = {
                'serial': serial,
                'state': state,
                'product': None,
                'model': None,
                'device': None,
                'transport_id': None
            }
            
            # Parse key:value pairs
            for part in parts[2:]:
                if ':' in part:
                    key, value = part.split(':', 1)
                    if key in device_info:
                        device_info[key] = value
            
            devices.append(device_info)
        
        return devices
    
    def list_devices(self) -> List[Dict[str, str]]:
        """List all connected ADB devices with their properties"""
        try:
            logger.info("Listing ADB devices")
            result = self._run_adb_command(['adb', 'devices', '-l'], timeout=10)
            
            if result.returncode != 0:
                logger.error(f"Failed to list devices: {result.stderr}")
                return []
            
            device_list_raw = self._parse_device_list(result.stdout)
            device_list = []
            
            for dev in device_list_raw:
                serial = dev['serial']
                if dev['state'] != 'device':
                    logger.warning(f"Device {serial} is in state: {dev['state']}")
                    # Still add it but with limited info
                    device_list.append({
                        "id": serial,
                        "name": serial,
                        "type": "unknown",
                        "brand": "Unknown",
                        "model": "Unknown",
                        "android_version": "Unknown",
                        "sdk_version": "Unknown",
                        "architecture": "Unknown",
                        "serial": serial,
                        "state": dev['state'],
                        "has_root": False,
                        "manufacturer": "Unknown"
                    })
                    continue
                
                device_info = self._get_device_info(serial)
                device_list.append(device_info)
            
            logger.info(f"Found {len(device_list)} ADB device(s)")
            return device_list
        except Exception as e:
            logger.error(f"Failed to list ADB devices: {str(e)}")
            return []
    
    def _get_device_info(self, serial: str) -> Dict[str, str]:
        """Get detailed information about a device"""
        try:
            # Get device properties
            brand = self._get_property(serial, "ro.product.brand", "Unknown")
            model = self._get_property(serial, "ro.product.model", "Unknown")
            android_version = self._get_property(serial, "ro.build.version.release", "Unknown")
            sdk_version = self._get_property(serial, "ro.build.version.sdk", "Unknown")
            abi = self._get_property(serial, "ro.product.cpu.abi", "Unknown")
            manufacturer = self._get_property(serial, "ro.product.manufacturer", "Unknown")
            characteristics = self._get_property(serial, "ro.build.characteristics", "")
            hardware = self._get_property(serial, "ro.hardware", "")
            kernel_qemu = self._get_property(serial, "ro.kernel.qemu", "0")
            boot_qemu = self._get_property(serial, "ro.boot.qemu", "0")
            
            # Determine device type
            device_type = "physical"
            try:
                lower_serial = serial.lower()
                lower_manu = manufacturer.lower()
                lower_char = characteristics.lower()
                lower_hw = hardware.lower()
                
                is_qemu = kernel_qemu.strip() == "1" or boot_qemu.strip() == "1"
                looks_like_emulator = any([
                    "emulator" in lower_serial,
                    lower_serial.startswith("127.0.0.1:"),
                    lower_serial.startswith("localhost:"),
                    "emulator" in lower_char or "sdk" in lower_char,
                    "goldfish" in lower_hw or "ranchu" in lower_hw,
                    any(v in lower_manu for v in ["genymotion", "bluestacks", "virtualbox", "nox", "mumu", "ldplayer"])
                ])
                
                if is_qemu or looks_like_emulator:
                    device_type = "emulator"
            except Exception:
                pass
            
            # Check root access
            has_root = self.check_root_access(serial)
            
            device_name = f"{brand} {model}".strip()
            if device_name == "Unknown Unknown":
                device_name = serial
            
            return {
                "id": serial,
                "name": device_name,
                "type": device_type,
                "brand": brand,
                "model": model,
                "android_version": android_version,
                "sdk_version": sdk_version,
                "architecture": abi,
                "serial": serial,
                "state": "online",
                "has_root": has_root,
                "manufacturer": manufacturer
            }
        except Exception as e:
            logger.error(f"Failed to get device info for {serial}: {str(e)}")
            return {
                "id": serial,
                "name": serial,
                "type": "unknown",
                "brand": "Unknown",
                "model": "Unknown",
                "android_version": "Unknown",
                "sdk_version": "Unknown",
                "architecture": "Unknown",
                "serial": serial,
                "state": "error",
                "has_root": False,
                "manufacturer": "Unknown"
            }
    
    def _get_property(self, serial: str, prop_name: str, default: str = "") -> str:
        """Get a system property from the device"""
        try:
            result = self._run_shell_command(serial, f"getprop {prop_name}", timeout=5)
            return result.strip() if result else default
        except Exception as e:
            logger.debug(f"Failed to get property {prop_name}: {str(e)}")
            return default
    
    def get_device(self, serial: str):
        """
        Get device object - for compatibility with old API
        Returns a simple object with serial for method chaining
        """
        if not self._validate_serial(serial):
            logger.error(f"Invalid device serial: {serial}")
            return None
        
        # Check if device exists
        result = self._run_adb_command(['adb', 'devices'], timeout=5)
        if result.returncode != 0 or serial not in result.stdout:
            logger.warning(f"Device {serial} not found")
            return None
        
        logger.info(f"Connected to device {serial}")
        # Return a device wrapper object
        return DeviceWrapper(serial, self)
    
    def execute_shell(self, serial: str, command: str, timeout: int = 30) -> Optional[str]:
        """Execute a shell command on the device"""
        try:
            result = self._run_shell_command(serial, command, timeout=timeout)
            if LOG_STREAMER_AVAILABLE:
                log_streamer.add_log(serial, "adb_operations", f"shell: {command}", "debug")
            logger.debug(f"Executed command on {serial}: {command}")
            return result
        except Exception as e:
            logger.error(f"Failed to execute shell command on {serial}: {str(e)}")
            return None
    
    def push_file(self, serial: str, local_path: str, remote_path: str) -> bool:
        """Push a file to the device"""
        try:
            if not self._validate_serial(serial):
                logger.error(f"Invalid device serial: {serial}")
                return False
            
            result = self._run_adb_command(
                ['adb', '-s', serial, 'push', local_path, remote_path],
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully pushed {local_path} to {serial}:{remote_path}")
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(serial, "adb_operations", f"push {local_path} {remote_path}", "info")
                return True
            else:
                logger.error(f"Failed to push file: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Failed to push file to {serial}: {str(e)}")
            return False
    
    def check_root_access(self, serial: str) -> bool:
        """Check if device has root access"""
        try:
            result = self._run_shell_command(serial, "su -c 'id'", timeout=5)
            if result and "uid=0" in result:
                logger.info(f"Device {serial} has root access")
                return True
            logger.info(f"Device {serial} does not have root access")
            return False
        except Exception as e:
            logger.debug(f"Root check failed for {serial}: {str(e)}")
            return False
    
    def is_adb_available(self) -> bool:
        """Check if ADB server is available"""
        try:
            result = self._run_adb_command(['adb', 'start-server'], timeout=10)
            if result.returncode == 0:
                logger.info("ADB server is available")
                return True
            else:
                logger.warning(f"ADB server not available: {result.stderr}")
                return False
        except Exception as e:
            logger.warning(f"ADB server not available: {str(e)}")
            return False
    
    def restart_adb_server(self) -> Dict[str, any]:
        """Restart the ADB server"""
        try:
            logger.info("Restarting ADB server")
            
            # Kill the ADB server
            kill_result = self._run_adb_command(['adb', 'kill-server'], timeout=5)
            
            if kill_result.returncode != 0:
                logger.warning(f"ADB kill-server returned non-zero: {kill_result.stderr}")
            
            logger.info("ADB server killed, waiting before restart")
            import time
            time.sleep(1)
            
            # Start the ADB server
            start_result = self._run_adb_command(['adb', 'start-server'], timeout=10)
            
            if start_result.returncode != 0:
                logger.error(f"Failed to start ADB server: {start_result.stderr}")
                return {
                    "success": False,
                    "message": f"Failed to start ADB server: {start_result.stderr}"
                }
            
            logger.info("ADB server started successfully")
            time.sleep(1)
            
            # Verify connection
            if self.is_adb_available():
                logger.info("ADB server restarted successfully")
                return {
                    "success": True,
                    "message": "ADB server restarted successfully"
                }
            else:
                logger.error("ADB server started but connection verification failed")
                return {
                    "success": False,
                    "message": "ADB server started but connection verification failed"
                }
                
        except Exception as e:
            logger.error(f"Failed to restart ADB server: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to restart ADB server: {str(e)}"
            }


class DeviceWrapper:
    """Wrapper class to maintain compatibility with old ppadb API"""
    
    def __init__(self, serial: str, adb_manager):
        self.serial = serial
        self.adb_manager = adb_manager
    
    def shell(self, command: str) -> str:
        """Execute shell command on device"""
        return self.adb_manager.execute_shell(self.serial, command) or ""
    
    def push(self, local_path: str, remote_path: str):
        """Push file to device"""
        success = self.adb_manager.push_file(self.serial, local_path, remote_path)
        if not success:
            raise RuntimeError(f"Failed to push {local_path} to {remote_path}")
