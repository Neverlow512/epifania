import frida
import time
from typing import List, Dict, Optional
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")


class DeviceManager:
    def __init__(self):
        self.frida_manager = frida.get_device_manager()
        self.adb_manager = ADBManager()
        self._device_cache = {}
        self._cache_ttl = 30
        logger.info("DeviceManager initialized")
    
    def list_devices(self) -> List[Dict[str, str]]:
        try:
            logger.info("Enumerating devices via ADB")
            adb_devices = self.adb_manager.list_devices()
            
            # Enrich with Frida information
            frida_devices = self.frida_manager.enumerate_devices()
            frida_map = {d.id: d for d in frida_devices}
            
            enriched_devices = []
            for adb_dev in adb_devices:
                device_info = adb_dev.copy()
                
                # Check if Frida can see this device
                frida_id = adb_dev["serial"]
                if frida_id in frida_map:
                    device_info["frida_available"] = True
                    device_info["frida_name"] = frida_map[frida_id].name
                else:
                    device_info["frida_available"] = False
                    device_info["frida_name"] = None
                
                enriched_devices.append(device_info)
            
            logger.info(f"Enumerated {len(enriched_devices)} device(s)")
            return enriched_devices
        except Exception as e:
            logger.error(f"Failed to enumerate devices: {str(e)}")
            raise RuntimeError(f"Failed to enumerate devices: {str(e)}")
    
    def is_device_connected(self, device_serial: str) -> bool:
        try:
            result = self.adb_manager._run_adb_command(['adb', 'devices'], timeout=5)
            if result.returncode != 0:
                return False
            for line in result.stdout.strip().split('\n'):
                if line.startswith('List of devices') or not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 2 and parts[0] == device_serial and parts[1] == 'device':
                    return True
            return False
        except Exception:
            return False

    def get_device_details(self, device_serial: str, use_cache: bool = True) -> Optional[Dict[str, any]]:
        try:
            logger.info(f"Getting details for device {device_serial}")
            
            if use_cache:
                cached = self._device_cache.get(device_serial)
                if cached and (time.time() - cached['timestamp']) < self._cache_ttl:
                    logger.debug(f"Using cached device info for {device_serial}")
                    return cached['data']
            
            adb_devices = self.adb_manager.list_devices()
            device_info = None
            
            for dev in adb_devices:
                if dev["serial"] == device_serial:
                    device_info = dev.copy()
                    break
            
            if not device_info:
                logger.warning(f"Device {device_serial} not found")
                self._device_cache.pop(device_serial, None)
                return None
            
            frida_devices = self.frida_manager.enumerate_devices()
            frida_map = {d.id: d for d in frida_devices}
            
            if device_serial in frida_map:
                device_info["frida_available"] = True
                device_info["frida_name"] = frida_map[device_serial].name
            else:
                device_info["frida_available"] = False
                device_info["frida_name"] = None
            
            self._device_cache[device_serial] = {
                'data': device_info,
                'timestamp': time.time()
            }
            
            logger.info(f"Retrieved details for device {device_serial}")
            return device_info
        except Exception as e:
            logger.error(f"Failed to get device details for {device_serial}: {str(e)}")
            return None
    
    def invalidate_cache(self, device_serial: str = None):
        if device_serial:
            self._device_cache.pop(device_serial, None)
        else:
            self._device_cache.clear()
    
    def verify_device_connection(self, device_serial: str) -> Dict[str, any]:
        try:
            logger.info(f"Verifying connection for device {device_serial}")
            
            result = self.adb_manager.execute_shell(device_serial, "echo 'test'")
            
            if result and "test" in result:
                logger.info(f"Device {device_serial} is connected and reachable")
                return {
                    "connected": True,
                    "message": "Device is connected and reachable"
                }
            else:
                logger.warning(f"Device {device_serial} connection test failed")
                return {
                    "connected": False,
                    "message": "Device connection test failed"
                }
        except Exception as e:
            logger.error(f"Failed to verify device connection: {str(e)}")
            return {
                "connected": False,
                "message": f"Connection verification failed: {str(e)}"
            }

