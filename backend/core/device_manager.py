import frida
from typing import List, Dict, Optional
from core.logger import get_logger
from core.adb_manager import ADBManager

logger = get_logger(__name__, "device")


class DeviceManager:
    def __init__(self):
        self.frida_manager = frida.get_device_manager()
        self.adb_manager = ADBManager()
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
    
    def get_device_details(self, device_serial: str) -> Optional[Dict[str, any]]:
        try:
            logger.info(f"Getting details for device {device_serial}")
            
            adb_devices = self.adb_manager.list_devices()
            device_info = None
            
            for dev in adb_devices:
                if dev["serial"] == device_serial:
                    device_info = dev.copy()
                    break
            
            if not device_info:
                logger.warning(f"Device {device_serial} not found")
                return None
            
            frida_devices = self.frida_manager.enumerate_devices()
            frida_map = {d.id: d for d in frida_devices}
            
            if device_serial in frida_map:
                device_info["frida_available"] = True
                device_info["frida_name"] = frida_map[device_serial].name
            else:
                device_info["frida_available"] = False
                device_info["frida_name"] = None
            
            logger.info(f"Retrieved details for device {device_serial}")
            return device_info
        except Exception as e:
            logger.error(f"Failed to get device details for {device_serial}: {str(e)}")
            return None
    
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

