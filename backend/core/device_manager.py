import frida
from typing import List, Dict
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

