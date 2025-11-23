from ppadb.client import Client as AdbClient
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
        self.client = None
        self._connect()
    
    def _connect(self):
        try:
            self.client = AdbClient(host=self.host, port=self.port)
            logger.info(f"Connected to ADB server at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to ADB server: {str(e)}")
            raise RuntimeError(f"ADB connection failed: {str(e)}")
    
    def list_devices(self) -> List[Dict[str, str]]:
        try:
            if not self.client:
                self._connect()
            
            devices = self.client.devices()
            device_list = []
            
            for device in devices:
                device_info = self._get_device_info(device)
                device_list.append(device_info)
            
            logger.info(f"Found {len(device_list)} ADB device(s)")
            return device_list
        except Exception as e:
            logger.error(f"Failed to list ADB devices: {str(e)}")
            return []
    
    def _get_device_info(self, device) -> Dict[str, str]:
        try:
            serial = device.serial
            
            # Get device properties
            brand = self._get_property(device, "ro.product.brand", "Unknown")
            model = self._get_property(device, "ro.product.model", "Unknown")
            android_version = self._get_property(device, "ro.build.version.release", "Unknown")
            sdk_version = self._get_property(device, "ro.build.version.sdk", "Unknown")
            abi = self._get_property(device, "ro.product.cpu.abi", "Unknown")
            manufacturer = self._get_property(device, "ro.product.manufacturer", "Unknown")
            characteristics = self._get_property(device, "ro.build.characteristics", "")
            hardware = self._get_property(device, "ro.hardware", "")
            kernel_qemu = self._get_property(device, "ro.kernel.qemu", "0")
            boot_qemu = self._get_property(device, "ro.boot.qemu", "0")
            
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
                # Default to previously determined type on any detection error
                pass
            
            # Check root access
            has_root = self.check_root_access(device)
            
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
            logger.error(f"Failed to get device info for {device.serial}: {str(e)}")
            return {
                "id": device.serial,
                "name": device.serial,
                "type": "unknown",
                "brand": "Unknown",
                "model": "Unknown",
                "android_version": "Unknown",
                "sdk_version": "Unknown",
                "architecture": "Unknown",
                "serial": device.serial,
                "state": "error",
                "has_root": False
            }
    
    def _get_property(self, device, prop_name: str, default: str = "") -> str:
        try:
            result = device.shell(f"getprop {prop_name}")
            return result.strip() if result else default
        except Exception as e:
            logger.debug(f"Failed to get property {prop_name}: {str(e)}")
            return default
    
    def get_device(self, serial: str):
        try:
            if not self.client:
                self._connect()
            
            device = self.client.device(serial)
            if device:
                logger.info(f"Connected to device {serial}")
                return device
            else:
                logger.warning(f"Device {serial} not found")
                return None
        except Exception as e:
            logger.error(f"Failed to get device {serial}: {str(e)}")
            return None
    
    def execute_shell(self, serial: str, command: str) -> Optional[str]:
        try:
            device = self.get_device(serial)
            if device:
                result = device.shell(command)
                if LOG_STREAMER_AVAILABLE:
                    log_streamer.add_log(serial, "adb_operations", f"shell: {command}", "debug")
                logger.debug(f"Executed command on {serial}: {command}")
                return result
            return None
        except Exception as e:
            logger.error(f"Failed to execute shell command on {serial}: {str(e)}")
            return None
    
    def check_root_access(self, device) -> bool:
        try:
            result = device.shell("su -c 'id'")
            if result and "uid=0" in result:
                logger.info(f"Device {device.serial} has root access")
                return True
            logger.info(f"Device {device.serial} does not have root access")
            return False
        except Exception as e:
            logger.debug(f"Root check failed for {device.serial}: {str(e)}")
            return False
    
    def is_adb_available(self) -> bool:
        try:
            if not self.client:
                self._connect()
            version = self.client.version()
            logger.info(f"ADB server version: {version}")
            return True
        except Exception as e:
            logger.warning(f"ADB server not available: {str(e)}")
            return False
    
    def restart_adb_server(self) -> Dict[str, any]:
        try:
            logger.info("Restarting ADB server")
            
            # Kill the ADB server
            import subprocess
            kill_result = subprocess.run(
                ["adb", "kill-server"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if kill_result.returncode != 0:
                logger.warning(f"ADB kill-server returned non-zero: {kill_result.stderr}")
            
            logger.info("ADB server killed, waiting before restart")
            import time
            time.sleep(1)
            
            # Start the ADB server
            start_result = subprocess.run(
                ["adb", "start-server"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if start_result.returncode != 0:
                logger.error(f"Failed to start ADB server: {start_result.stderr}")
                return {
                    "success": False,
                    "message": f"Failed to start ADB server: {start_result.stderr}"
                }
            
            logger.info("ADB server started, reconnecting client")
            time.sleep(1)
            
            # Reconnect the client
            self._connect()
            
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
                
        except subprocess.TimeoutExpired:
            logger.error("ADB restart timed out")
            return {
                "success": False,
                "message": "ADB restart operation timed out"
            }
        except Exception as e:
            logger.error(f"Failed to restart ADB server: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to restart ADB server: {str(e)}"
            }

